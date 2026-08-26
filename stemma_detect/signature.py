from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Protocol

from stemma_detect.result import ProbeResult

Validator = Callable[[bytes], bool]


class SignatureCheck(Protocol):
    """One weighted operation in a device signature."""

    label: str
    length: int
    validator: Validator
    show_value: bool
    required: bool
    weight: int

    def read(self, bus, address: int) -> bytes: ...


@dataclass(frozen=True)
class RegisterCheck:
    """One safe, read-only register check in a device signature."""

    label: str
    register: int
    length: int
    validator: Validator
    show_value: bool = False
    required: bool = True
    weight: int = 1

    def __post_init__(self) -> None:
        if self.weight < 1:
            raise ValueError("register check weight must be positive")

    def read(self, bus, address: int) -> bytes:
        return bus.read_register(address, self.register, self.length)


@dataclass(frozen=True)
class CommandCheck:
    """A write-then-read command used as weighted signature evidence."""

    label: str
    command: bytes
    length: int
    validator: Validator
    delay_ms: float = 0
    show_value: bool = False
    required: bool = True
    weight: int = 1

    def __post_init__(self) -> None:
        if not self.command:
            raise ValueError("command must not be empty")
        if self.length < 1:
            raise ValueError("command response length must be positive")
        if self.delay_ms < 0:
            raise ValueError("command delay must not be negative")
        if self.weight < 1:
            raise ValueError("command check weight must be positive")

    def read(self, bus, address: int) -> bytes:
        return bus.write_then_read(
            address,
            self.command,
            self.length,
            delay_ms=self.delay_ms,
        )


def command_response(
    label: str,
    command: bytes,
    length: int,
    validator: Validator,
    *,
    delay_ms: float = 0,
    show_value: bool = False,
    required: bool = True,
    weight: int = 1,
) -> CommandCheck:
    """Build a check for a safe command with a validated response."""

    return CommandCheck(
        label,
        command,
        length,
        validator,
        delay_ms,
        show_value,
        required,
        weight,
    )


def exact(
    label: str,
    register: int,
    expected: bytes,
    *,
    mask: bytes | None = None,
    show_value: bool = False,
    required: bool = True,
    weight: int = 1,
) -> RegisterCheck:
    """Match an exact value, optionally considering only selected bits."""

    if not expected:
        raise ValueError("expected value must not be empty")
    if mask is not None and len(mask) != len(expected):
        raise ValueError("mask and expected value must have equal lengths")
    if mask is not None and any(
        value & ~selected for value, selected in zip(expected, mask, strict=True)
    ):
        raise ValueError("expected value contains bits outside the mask")

    def matches(value: bytes) -> bool:
        if mask is None:
            return value == expected
        return (
            bytes(actual & selected for actual, selected in zip(value, mask, strict=True))
            == expected
        )

    return RegisterCheck(
        label,
        register,
        len(expected),
        matches,
        show_value,
        required,
        weight,
    )


def one_of(
    label: str,
    register: int,
    expected: tuple[bytes, ...],
    *,
    show_value: bool = False,
    required: bool = True,
    weight: int = 1,
) -> RegisterCheck:
    """Match any one of several exact register values."""

    if not expected or not expected[0]:
        raise ValueError("expected values must not be empty")
    length = len(expected[0])
    if any(len(value) != length for value in expected):
        raise ValueError("expected values must have equal lengths")
    return RegisterCheck(
        label,
        register,
        length,
        lambda value: value in expected,
        show_value,
        required,
        weight,
    )


def not_blank(
    label: str,
    register: int,
    length: int,
    *,
    show_value: bool = False,
    required: bool = True,
    weight: int = 1,
) -> RegisterCheck:
    """Reject calibration or factory-data blocks containing only 0x00 or 0xFF."""

    if length < 1:
        raise ValueError("length must be positive")
    return RegisterCheck(
        label,
        register,
        length,
        lambda value: value not in (bytes(length), b"\xff" * length),
        show_value=show_value,
        required=required,
        weight=weight,
    )


@dataclass(frozen=True)
class DeviceSignature:
    """Weighted read-only evidence used to identify a device."""

    checks: tuple[SignatureCheck, ...]
    match_threshold: int | None = None

    def __post_init__(self) -> None:
        if not self.checks:
            raise ValueError("device signature must contain at least one check")
        if self.match_threshold is not None and not 1 <= self.match_threshold <= self.max_score:
            raise ValueError("match threshold must be between one and the maximum score")

    @property
    def max_score(self) -> int:
        return sum(check.weight for check in self.checks)

    def probe(self, bus, address: int) -> ProbeResult:
        evidence = {}
        score = 0
        missed = []
        for check in self.checks:
            value = check.read(bus, address)
            if len(value) != check.length or not check.validator(value):
                if check.required:
                    return ProbeResult.no_match(
                        {
                            "failed": check.label,
                            check.label: _format_value(value),
                        },
                        score=score,
                        max_score=self.max_score,
                    )
                missed.append(check.label)
                continue
            score += check.weight
            if check.show_value:
                evidence[check.label] = _format_value(value)

        evidence["signature"] = f"{score}/{self.max_score}"
        if missed:
            evidence["missed"] = ",".join(missed)
        threshold = self.match_threshold or self.max_score
        factory = ProbeResult.match if score >= threshold else ProbeResult.possible
        return factory(evidence, score=score, max_score=self.max_score)


def _format_value(value: bytes) -> str:
    return "0x" + value.hex().upper()

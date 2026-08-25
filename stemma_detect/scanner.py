from __future__ import annotations

import errno
from collections.abc import Callable
from dataclasses import dataclass

from .bus import I2CBus
from .catalog import Chip
from .result import Confidence, ProbeResult


@dataclass(frozen=True)
class Detection:
    chip: Chip
    address: int
    result: ProbeResult

    @property
    def name(self) -> str:
        return self.result.name or self.chip.name


@dataclass(frozen=True)
class ProbeDiagnostic:
    chip: Chip
    address: int
    result: ProbeResult | None = None
    error: Exception | None = None

    @property
    def not_detected(self) -> bool:
        return isinstance(self.error, OSError) and self.error.errno in (
            errno.ENXIO,
            getattr(errno, "EREMOTEIO", 121),
        )

    @property
    def outcome(self) -> str:
        if self.error is not None:
            return "not_detected" if self.not_detected else "error"
        if self.result is None:
            raise RuntimeError("probe diagnostic has neither a result nor an error")
        return self.result.confidence.name.lower()


def scan(
    bus: I2CBus,
    chips: tuple[Chip, ...],
    *,
    diagnostic: Callable[[ProbeDiagnostic], None] | None = None,
) -> tuple[Detection, ...]:
    detections = []

    for address in sorted({address for chip in chips for address in chip.addresses}):
        address_detections = []
        candidates = [chip for chip in chips if address in chip.addresses]
        candidates.sort(
            key=lambda chip: (
                -chip.probe_confidence.value,
                chip.probe_risk,
                chip.address_kind(address) != "default",
                chip.name,
            )
        )

        for chip in candidates:
            try:
                result = chip.probe(bus, address)
            except (OSError, RuntimeError, ValueError) as error:
                if diagnostic:
                    diagnostic(ProbeDiagnostic(chip, address, error=error))
                continue

            if not isinstance(result, ProbeResult):
                raise TypeError(f"{chip.name}.probe() did not return ProbeResult")
            if diagnostic:
                diagnostic(ProbeDiagnostic(chip, address, result=result))
            if result.confidence is Confidence.NO_MATCH:
                continue

            detection = Detection(chip, address, result)
            if result.confidence is Confidence.MATCH:
                # A definitive match supersedes earlier possible matches and
                # prevents any remaining candidates from touching this address.
                address_detections = [detection]
                break

            address_detections.append(detection)

        detections.extend(address_detections)

    return tuple(detections)

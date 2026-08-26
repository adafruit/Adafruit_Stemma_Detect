from __future__ import annotations

import errno
from collections.abc import Callable
from dataclasses import dataclass, replace

from .bus import I2CBusProtocol
from .catalog import Chip
from .mux import Multiplexer, MuxHop, discover_multiplexers
from .result import Confidence, ProbeResult


@dataclass(frozen=True)
class Detection:
    chip: Chip
    address: int
    result: ProbeResult
    path: tuple[MuxHop, ...] = ()

    @property
    def name(self) -> str:
        return self.result.name or self.chip.name


@dataclass(frozen=True)
class ProbeDiagnostic:
    chip: Chip
    address: int
    result: ProbeResult | None = None
    error: Exception | None = None
    path: tuple[MuxHop, ...] = ()

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
    bus: I2CBusProtocol,
    chips: tuple[Chip, ...],
    *,
    diagnostic: Callable[[ProbeDiagnostic], None] | None = None,
    path: tuple[MuxHop, ...] = (),
    excluded_addresses: frozenset[int] = frozenset(),
) -> tuple[Detection, ...]:
    detections = []

    for address in sorted({address for chip in chips for address in chip.addresses}):
        if address in excluded_addresses:
            continue
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
                    diagnostic(ProbeDiagnostic(chip, address, error=error, path=path))
                continue

            if not isinstance(result, ProbeResult):
                raise TypeError(f"{chip.name}.probe() did not return ProbeResult")
            if result.confidence is not Confidence.NO_MATCH and chip.default_addresses:
                address_kind = chip.address_kind(address)
                result = replace(
                    result,
                    evidence={**result.evidence, "address": address_kind or "unknown"},
                )
                result = result.with_score_bonus(
                    earned=int(address_kind == "default"),
                    available=1,
                )
            if diagnostic:
                diagnostic(ProbeDiagnostic(chip, address, result=result, path=path))
            if result.confidence is Confidence.NO_MATCH:
                continue

            detection = Detection(chip, address, result, path)
            if result.confidence is Confidence.MATCH:
                # A definitive match supersedes earlier possible matches and
                # prevents any remaining candidates from touching this address.
                address_detections = [detection]
                break

            address_detections.append(detection)

        # Ask about the strongest signatures first. This also makes the normal
        # report put richer possible matches ahead of address-only guesses.
        address_detections.sort(
            key=lambda detection: (
                -(detection.result.score if detection.result.score is not None else -1)
            )
        )
        detections.extend(address_detections)

    return tuple(detections)


@dataclass(frozen=True)
class ScanReport:
    detections: tuple[Detection, ...]
    multiplexers: tuple[Multiplexer, ...] = ()


def scan_all(
    bus: I2CBusProtocol,
    chips: tuple[Chip, ...],
    *,
    diagnostic: Callable[[ProbeDiagnostic], None] | None = None,
) -> ScanReport:
    """Scan the root bus and every channel of conservatively detected muxes."""

    multiplexers = discover_multiplexers(bus)
    if not multiplexers:
        return ScanReport(scan(bus, chips, diagnostic=diagnostic))

    detections = []
    try:
        for mux in multiplexers:
            mux.disable(bus)

        mux_addresses = frozenset(mux.address for mux in multiplexers)
        root_detections = scan(
            bus,
            chips,
            diagnostic=diagnostic,
            excluded_addresses=mux_addresses,
        )
        detections.extend(root_detections)
        root_devices = {(item.name, item.address) for item in root_detections}

        for mux in multiplexers:
            for channel in range(mux.channels):
                mux.select(bus, channel)
                path = (MuxHop(mux.address, channel),)
                channel_detections = scan(
                    bus,
                    chips,
                    diagnostic=diagnostic,
                    path=path,
                    excluded_addresses=mux_addresses,
                )
                detections.extend(
                    item
                    for item in channel_detections
                    if (item.name, item.address) not in root_devices
                )
                mux.disable(bus)
    finally:
        for mux in multiplexers:
            mux.restore(bus)

    return ScanReport(tuple(detections), multiplexers)

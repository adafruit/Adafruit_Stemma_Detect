from __future__ import annotations

import errno
from collections.abc import Callable
from dataclasses import dataclass, replace

from .bus import I2CBusProtocol
from .catalog import Chip
from .mux import Multiplexer, MuxHop, discover_multiplexers
from .result import Confidence, ProbeResult

MAX_MUX_DEPTH = 8


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
    max_mux_depth: int = MAX_MUX_DEPTH,
) -> ScanReport:
    """Scan the root bus and recursively traverse compatible mux channels."""

    if max_mux_depth < 0:
        raise ValueError("maximum mux depth must not be negative")

    detections, multiplexers = _scan_segment(
        bus,
        chips,
        diagnostic=diagnostic,
        path=(),
        upstream_mux_addresses=frozenset(),
        inherited_devices=frozenset(),
        max_mux_depth=max_mux_depth,
    )
    return ScanReport(tuple(detections), tuple(multiplexers))


def _scan_segment(
    bus: I2CBusProtocol,
    chips: tuple[Chip, ...],
    *,
    diagnostic: Callable[[ProbeDiagnostic], None] | None,
    path: tuple[MuxHop, ...],
    upstream_mux_addresses: frozenset[int],
    inherited_devices: frozenset[tuple[str, int]],
    max_mux_depth: int,
) -> tuple[list[Detection], list[Multiplexer]]:
    """Scan one electrically visible segment and descend through its muxes."""

    local_muxes = [
        replace(mux, path=path)
        for mux in discover_multiplexers(
            bus,
            excluded_addresses=upstream_mux_addresses,
        )
    ]
    visible_mux_addresses = upstream_mux_addresses | frozenset(mux.address for mux in local_muxes)
    detections = []
    multiplexers = list(local_muxes)

    try:
        for mux in local_muxes:
            mux.disable(bus)

        segment_detections = scan(
            bus,
            chips,
            diagnostic=diagnostic,
            path=path,
            excluded_addresses=visible_mux_addresses,
        )
        segment_detections = tuple(
            item
            for item in segment_detections
            if (item.name, item.address) not in inherited_devices
        )
        detections.extend(segment_detections)
        descendant_inherited = inherited_devices | frozenset(
            (item.name, item.address) for item in segment_detections
        )

        if len(path) < max_mux_depth:
            for mux in local_muxes:
                for channel in range(mux.channels):
                    mux.select(bus, channel)
                    child_path = path + (MuxHop(mux.address, channel),)
                    child_detections, child_muxes = _scan_segment(
                        bus,
                        chips,
                        diagnostic=diagnostic,
                        path=child_path,
                        upstream_mux_addresses=visible_mux_addresses,
                        inherited_devices=descendant_inherited,
                        max_mux_depth=max_mux_depth,
                    )
                    detections.extend(child_detections)
                    multiplexers.extend(child_muxes)
                    mux.disable(bus)
    finally:
        for mux in local_muxes:
            mux.restore(bus)

    return detections, multiplexers

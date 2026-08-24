from __future__ import annotations

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


def scan(
    bus: I2CBus,
    chips: tuple[Chip, ...],
) -> tuple[Detection, ...]:
    detections = []

    for address in sorted({address for chip in chips for address in chip.addresses}):
        address_detections = []
        candidates = [chip for chip in chips if address in chip.addresses]
        candidates.sort(key=lambda chip: (-chip.probe_confidence.value, chip.name))

        for chip in candidates:
            try:
                result = chip.probe(bus, address)
            except (OSError, RuntimeError, ValueError):
                continue

            if not isinstance(result, ProbeResult):
                raise TypeError(f"{chip.name}.probe() did not return ProbeResult")
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

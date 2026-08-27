from __future__ import annotations

import json

from .installer import driver_version
from .mux import MuxHop
from .scanner import ScanReport

SCHEMA_VERSION = 1


def _address_fields(address: int) -> dict[str, int | str]:
    return {
        "address": address,
        "address_hex": f"0x{address:02X}",
    }


def _path_data(path: tuple[MuxHop, ...]) -> list[dict[str, int | str]]:
    return [
        {
            **_address_fields(hop.address),
            "channel": hop.channel,
        }
        for hop in path
    ]


def report_to_dict(report: ScanReport, *, bus: int | None = None) -> dict[str, object]:
    """Convert a scan report to the stable, JSON-compatible output schema."""

    package_versions = {
        detection.chip.package: driver_version(detection.chip.package)
        for detection in report.detections
    }
    multiplexers = [
        {
            "name": mux.name,
            **_address_fields(mux.address),
            "channels": mux.channels,
            "path": _path_data(mux.path),
        }
        for mux in report.multiplexers
    ]
    detections = []
    for detection in report.detections:
        installed_version = package_versions[detection.chip.package]
        detections.append(
            {
                "name": detection.name,
                "family": detection.chip.name,
                "confidence": detection.result.confidence.name.lower(),
                **_address_fields(detection.address),
                "address_kind": detection.chip.address_kind(detection.address),
                "path": _path_data(detection.path),
                "probe_risk": detection.chip.probe_risk.name.lower(),
                "evidence": dict(detection.result.evidence),
                "score": detection.result.score,
                "max_score": detection.result.max_score,
                "driver": {
                    "package": detection.chip.package,
                    "installed": installed_version is not None,
                    "version": installed_version,
                },
            }
        )

    return {
        "schema_version": SCHEMA_VERSION,
        "bus": bus,
        "multiplexers": multiplexers,
        "detections": detections,
    }


def report_to_json(
    report: ScanReport,
    *,
    bus: int | None = None,
    indent: int | None = 2,
) -> str:
    """Serialize a scan report, optionally changing or disabling indentation."""

    return json.dumps(report_to_dict(report, bus=bus), indent=indent)

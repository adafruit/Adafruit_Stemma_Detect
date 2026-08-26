from __future__ import annotations

import importlib
import pkgutil
import re
from collections.abc import Callable
from dataclasses import dataclass
from types import ModuleType

from . import chips
from .bus import I2CBusProtocol
from .result import Confidence, ProbeResult, ProbeRisk

PACKAGE_PATTERN = re.compile(r"^adafruit-circuitpython-[a-z0-9][a-z0-9-]*$")


@dataclass(frozen=True)
class Chip:
    name: str
    addresses: tuple[int, ...]
    package: str
    probe: Callable[[I2CBusProtocol, int], ProbeResult]
    probe_confidence: Confidence
    default_addresses: tuple[int, ...] = ()
    probe_risk: ProbeRisk = ProbeRisk.REGISTER

    def address_kind(self, address: int) -> str | None:
        if address in self.default_addresses:
            return "default"
        if self.default_addresses and address in self.addresses:
            return "alternate"
        return None


def _load_chip(module: ModuleType) -> Chip:
    name = module.__name__.rsplit(".", 1)[-1]
    addresses = tuple(module.ADDRESSES)
    default_addresses = tuple(getattr(module, "DEFAULT_ADDRESSES", ()))
    if not default_addresses and len(addresses) == 1:
        default_addresses = addresses
    package = module.PACKAGE
    probe = module.probe
    probe_confidence = module.PROBE_CONFIDENCE
    probe_risk = getattr(
        module,
        "PROBE_RISK",
        getattr(probe, "probe_risk", ProbeRisk.REGISTER),
    )

    if not addresses or any(not 0x08 <= address <= 0x77 for address in addresses):
        raise ValueError(f"{name}: invalid I2C address list")
    if any(address not in addresses for address in default_addresses):
        raise ValueError(f"{name}: default address is not in I2C address list")
    if not PACKAGE_PATTERN.fullmatch(package):
        raise ValueError(f"{name}: package is not an Adafruit CircuitPython distribution")
    if not callable(probe):
        raise ValueError(f"{name}: probe must be callable")
    if probe_confidence not in (Confidence.POSSIBLE, Confidence.MATCH):
        raise ValueError(f"{name}: invalid probe confidence")
    if not isinstance(probe_risk, ProbeRisk):
        raise ValueError(f"{name}: invalid probe risk")

    return Chip(
        name,
        addresses,
        package,
        probe,
        probe_confidence,
        default_addresses,
        probe_risk,
    )


def discover_chips() -> tuple[Chip, ...]:
    found = []
    for info in pkgutil.iter_modules(chips.__path__, f"{chips.__name__}."):
        if not info.name.rsplit(".", 1)[-1].startswith("_"):
            found.append(_load_chip(importlib.import_module(info.name)))
    return tuple(sorted(found, key=lambda chip: chip.name))

from __future__ import annotations

import importlib
import pkgutil
import re
from collections.abc import Callable
from dataclasses import dataclass
from types import ModuleType

from . import chips
from .bus import I2CBus
from .result import Confidence, ProbeResult

PACKAGE_PATTERN = re.compile(r"^adafruit-circuitpython-[a-z0-9][a-z0-9-]*$")


@dataclass(frozen=True)
class Chip:
    name: str
    addresses: tuple[int, ...]
    package: str
    probe: Callable[[I2CBus, int], ProbeResult]
    probe_confidence: Confidence
    product_url: str | None = None


def _load_chip(module: ModuleType) -> Chip:
    name = module.__name__.rsplit(".", 1)[-1]
    addresses = tuple(module.ADDRESSES)
    package = module.PACKAGE
    probe = module.probe
    probe_confidence = module.PROBE_CONFIDENCE
    product_url = getattr(module, "PRODUCT_URL", None)

    if not addresses or any(not 0x08 <= address <= 0x77 for address in addresses):
        raise ValueError(f"{name}: invalid I2C address list")
    if not PACKAGE_PATTERN.fullmatch(package):
        raise ValueError(f"{name}: package is not an Adafruit CircuitPython distribution")
    if not callable(probe):
        raise ValueError(f"{name}: probe must be callable")
    if probe_confidence not in (Confidence.POSSIBLE, Confidence.MATCH):
        raise ValueError(f"{name}: invalid probe confidence")

    return Chip(name, addresses, package, probe, probe_confidence, product_url)


def discover_chips() -> tuple[Chip, ...]:
    found = []
    for info in pkgutil.iter_modules(chips.__path__, f"{chips.__name__}."):
        if not info.name.rsplit(".", 1)[-1].startswith("_"):
            found.append(_load_chip(importlib.import_module(info.name)))
    return tuple(sorted(found, key=lambda chip: chip.name))

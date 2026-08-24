from __future__ import annotations

import shlex
import sys

from .catalog import PACKAGE_PATTERN, Chip
from .runtime import SHELL


def install(chip: Chip) -> None:
    if not PACKAGE_PATTERN.fullmatch(chip.package):
        raise ValueError(f"Refusing untrusted package name: {chip.package!r}")

    command = shlex.join([sys.executable, "-m", "pip", "install", chip.package])
    if not SHELL.run_command(command):
        raise RuntimeError(f"Driver installation failed: {chip.package}")

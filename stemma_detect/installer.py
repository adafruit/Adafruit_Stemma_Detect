from __future__ import annotations

import shlex
import sys
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from enum import Enum
from importlib.metadata import PackageNotFoundError, version

from .catalog import PACKAGE_PATTERN, Chip
from .mux import MuxHop
from .scanner import Detection, ScanReport

PossibleMatchConfirmation = Callable[[Detection], bool]


class InstallOutcome(str, Enum):
    """Outcome of one driver-package installation plan item."""

    INSTALLED = "installed"
    ALREADY_INSTALLED = "already_installed"
    FAILED = "failed"


@dataclass(frozen=True)
class InstallPlanItem:
    """One deduplicated CircuitPython package in an installation plan."""

    package: str
    detections: tuple[Detection, ...]
    installed_version: str | None = None

    @property
    def needs_install(self) -> bool:
        """Return whether the package is absent from the current environment."""

        return self.installed_version is None


@dataclass(frozen=True)
class InstallResult:
    """Structured result from processing one installation plan item."""

    package: str
    detections: tuple[Detection, ...]
    outcome: InstallOutcome
    version: str | None = None
    error: str | None = None


def driver_version(package: str) -> str | None:
    """Return the installed distribution version, or ``None`` when absent."""

    try:
        return version(package)
    except PackageNotFoundError:
        return None


def create_install_plan(
    report: ScanReport,
    *,
    confirm_possible: PossibleMatchConfirmation | None = None,
) -> tuple[InstallPlanItem, ...]:
    """Plan driver installations for definitive and explicitly confirmed matches.

    ``confirm_possible`` is called only for possible detections. It should return
    true when the application knows that candidate is present. If it confirms
    multiple candidates at the same address and mux path, planning fails rather
    than choosing one based on ordering.
    """

    selected: list[Detection] = []
    claimed_locations: dict[tuple[tuple[MuxHop, ...], int], Detection] = {}
    for detection in report:
        if not detection.is_definitive and not (
            confirm_possible is not None and confirm_possible(detection)
        ):
            continue
        location = (detection.path, detection.address)
        previous = claimed_locations.get(location)
        if previous is not None and previous.name != detection.name:
            raise ValueError(
                "multiple confirmed sensors claim "
                f"{detection.address_hex} on the same mux path: "
                f"{previous.name}, {detection.name}"
            )
        claimed_locations[location] = detection
        selected.append(detection)

    grouped: dict[str, list[Detection]] = {}
    for detection in selected:
        grouped.setdefault(detection.driver_package, []).append(detection)

    return tuple(
        InstallPlanItem(package, tuple(detections), driver_version(package))
        for package, detections in grouped.items()
    )


def install_drivers(plan: Iterable[InstallPlanItem]) -> tuple[InstallResult, ...]:
    """Execute an installation plan and return one result per package.

    Failures are captured in the returned results so one package does not hide
    the outcome of later items.
    """

    results = []
    for item in plan:
        if item.installed_version is not None:
            results.append(
                InstallResult(
                    item.package,
                    item.detections,
                    InstallOutcome.ALREADY_INSTALLED,
                    version=item.installed_version,
                )
            )
            continue
        try:
            _install_package(item.package)
        except (RuntimeError, ValueError) as error:
            results.append(
                InstallResult(
                    item.package,
                    item.detections,
                    InstallOutcome.FAILED,
                    error=str(error),
                )
            )
            continue
        results.append(
            InstallResult(
                item.package,
                item.detections,
                InstallOutcome.INSTALLED,
                version=driver_version(item.package),
            )
        )
    return tuple(results)


def _run_command(command: str) -> bool:
    # Keep Adafruit_Python_Shell lazy so detection-only library imports do not
    # initialize command-running machinery.
    from .runtime import SHELL  # noqa: PLC0415

    return SHELL.run_command(command)


def _install_package(package: str) -> None:
    if not PACKAGE_PATTERN.fullmatch(package):
        raise ValueError(f"Refusing untrusted package name: {package!r}")

    command = shlex.join([sys.executable, "-m", "pip", "install", package])
    if not _run_command(command):
        raise RuntimeError(f"Driver installation failed: {package}")


def install(chip: Chip) -> None:
    """Install one chip's driver, retained for backward compatibility."""

    _install_package(chip.package)

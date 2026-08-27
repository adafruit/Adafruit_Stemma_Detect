"""Adafruit STEMMA QT sensor detection."""

from ._version import __version__
from .bus import I2CBus, I2CBusProtocol, I2CTransaction
from .catalog import Chip, discover_chips
from .installer import (
    InstallOutcome,
    InstallPlanItem,
    InstallResult,
    PossibleMatchConfirmation,
    create_install_plan,
    driver_version,
    install_drivers,
)
from .mux import Multiplexer, MuxHop
from .result import Confidence, ProbeResult, ProbeRisk
from .scanner import MAX_MUX_DEPTH, Detection, ProbeDiagnostic, ScanReport, detect, scan, scan_all
from .serialization import SCHEMA_VERSION, report_to_dict, report_to_json

__all__ = (
    "Chip",
    "Confidence",
    "Detection",
    "I2CBus",
    "I2CBusProtocol",
    "I2CTransaction",
    "InstallOutcome",
    "InstallPlanItem",
    "InstallResult",
    "MAX_MUX_DEPTH",
    "Multiplexer",
    "MuxHop",
    "ProbeDiagnostic",
    "ProbeResult",
    "ProbeRisk",
    "PossibleMatchConfirmation",
    "SCHEMA_VERSION",
    "ScanReport",
    "discover_chips",
    "detect",
    "create_install_plan",
    "driver_version",
    "install_drivers",
    "report_to_dict",
    "report_to_json",
    "scan",
    "scan_all",
    "__version__",
)

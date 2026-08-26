"""Adafruit STEMMA QT sensor detection."""

from .bus import I2CBus, I2CBusProtocol
from .catalog import Chip, discover_chips
from .mux import Multiplexer, MuxHop
from .scanner import Detection, ProbeDiagnostic, ScanReport, scan, scan_all
from .serialization import SCHEMA_VERSION, report_to_dict, report_to_json

__version__ = "0.1.0"

__all__ = (
    "Chip",
    "Detection",
    "I2CBus",
    "I2CBusProtocol",
    "Multiplexer",
    "MuxHop",
    "ProbeDiagnostic",
    "SCHEMA_VERSION",
    "ScanReport",
    "discover_chips",
    "report_to_dict",
    "report_to_json",
    "scan",
    "scan_all",
)

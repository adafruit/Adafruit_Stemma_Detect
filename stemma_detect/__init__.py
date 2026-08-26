"""Adafruit STEMMA QT sensor detection."""

from .bus import I2CBus, I2CBusProtocol
from .catalog import Chip, discover_chips
from .mux import Multiplexer, MuxHop
from .scanner import Detection, ProbeDiagnostic, ScanReport, scan, scan_all

__version__ = "0.1.0"

__all__ = (
    "Chip",
    "Detection",
    "I2CBus",
    "I2CBusProtocol",
    "Multiplexer",
    "MuxHop",
    "ProbeDiagnostic",
    "ScanReport",
    "discover_chips",
    "scan",
    "scan_all",
)

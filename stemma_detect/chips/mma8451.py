from stemma_detect.result import Confidence
from stemma_detect.signature import DeviceSignature, exact

ADDRESSES = (0x1C, 0x1D)
DEFAULT_ADDRESSES = (0x1D,)
PACKAGE = "adafruit-circuitpython-mma8451"
PROBE_CONFIDENCE = Confidence.MATCH

SIGNATURE = DeviceSignature((exact("chip_id", 0x0D, b"\x1a", show_value=True, weight=10),))
probe = SIGNATURE.probe

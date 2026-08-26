from stemma_detect.result import Confidence
from stemma_detect.signature import DeviceSignature, exact

ADDRESSES = (0x5C, 0x5D)
DEFAULT_ADDRESSES = (0x5C,)
PACKAGE = "adafruit-circuitpython-lps28"
PROBE_CONFIDENCE = Confidence.MATCH

SIGNATURE = DeviceSignature((exact("chip_id", 0x0F, b"\xb4", show_value=True, weight=10),))
probe = SIGNATURE.probe

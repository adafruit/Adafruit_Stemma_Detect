from stemma_detect.result import Confidence
from stemma_detect.signature import DeviceSignature, exact

ADDRESSES = (0x76, 0x77)
DEFAULT_ADDRESSES = (0x77,)
PACKAGE = "adafruit-circuitpython-spa06-003"
PROBE_CONFIDENCE = Confidence.MATCH

SIGNATURE = DeviceSignature((exact("chip_id", 0x0D, b"\x11", show_value=True, weight=10),))
probe = SIGNATURE.probe

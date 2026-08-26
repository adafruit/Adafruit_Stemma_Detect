from stemma_detect.result import Confidence
from stemma_detect.signature import DeviceSignature, exact

ADDRESSES = (0x44,)
PACKAGE = "adafruit-circuitpython-opt4048"
PROBE_CONFIDENCE = Confidence.MATCH

SIGNATURE = DeviceSignature((exact("device_id", 0x11, b"\x08\x21", show_value=True, weight=12),))
probe = SIGNATURE.probe

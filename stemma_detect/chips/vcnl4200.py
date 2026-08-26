from stemma_detect.result import Confidence
from stemma_detect.signature import DeviceSignature, exact

ADDRESSES = (0x51,)
PACKAGE = "adafruit-circuitpython-vcnl4200"
PROBE_CONFIDENCE = Confidence.MATCH

SIGNATURE = DeviceSignature((exact("device_id", 0x0E, b"\x58\x10", show_value=True, weight=12),))
probe = SIGNATURE.probe

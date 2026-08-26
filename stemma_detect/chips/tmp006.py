from stemma_detect.result import Confidence
from stemma_detect.signature import DeviceSignature, exact

ADDRESSES = tuple(range(0x40, 0x48))
DEFAULT_ADDRESSES = (0x40,)
PACKAGE = "adafruit-circuitpython-tmp006"
PROBE_CONFIDENCE = Confidence.MATCH

SIGNATURE = DeviceSignature((exact("device_id", 0xFF, b"\x00\x67", show_value=True, weight=10),))
probe = SIGNATURE.probe

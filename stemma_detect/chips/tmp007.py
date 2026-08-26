from stemma_detect.result import Confidence
from stemma_detect.signature import DeviceSignature, exact

ADDRESSES = tuple(range(0x40, 0x48))
DEFAULT_ADDRESSES = (0x40,)
PACKAGE = "adafruit-circuitpython-tmp007"
PROBE_CONFIDENCE = Confidence.MATCH

SIGNATURE = DeviceSignature((exact("device_id", 0x1F, b"\x00\x78", show_value=True, weight=10),))
probe = SIGNATURE.probe

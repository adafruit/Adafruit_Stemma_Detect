from stemma_detect.result import Confidence
from stemma_detect.signature import DeviceSignature, exact

ADDRESSES = (0x39,)
PACKAGE = "adafruit-circuitpython-tcs3430"
PROBE_CONFIDENCE = Confidence.MATCH

SIGNATURE = DeviceSignature((exact("chip_id", 0x92, b"\xdc", show_value=True, weight=10),))
probe = SIGNATURE.probe

from stemma_detect.result import Confidence
from stemma_detect.signature import DeviceSignature, exact

ADDRESSES = (0x21,)
PACKAGE = "adafruit-circuitpython-fxas21002c"
PROBE_CONFIDENCE = Confidence.MATCH

SIGNATURE = DeviceSignature((exact("chip_id", 0x0C, b"\xd7", show_value=True, weight=10),))
probe = SIGNATURE.probe

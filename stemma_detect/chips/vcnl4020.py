from stemma_detect.result import Confidence
from stemma_detect.signature import DeviceSignature, exact

ADDRESSES = (0x13,)
PACKAGE = "adafruit-circuitpython-vcnl4020"
PROBE_CONFIDENCE = Confidence.MATCH

SIGNATURE = DeviceSignature((exact("product_revision", 0x81, b"\x21", show_value=True, weight=10),))
probe = SIGNATURE.probe

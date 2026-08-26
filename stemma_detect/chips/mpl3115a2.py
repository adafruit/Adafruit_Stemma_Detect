from stemma_detect.result import Confidence
from stemma_detect.signature import DeviceSignature, exact

ADDRESSES = (0x60,)
PACKAGE = "adafruit-circuitpython-mpl3115a2"
PROBE_CONFIDENCE = Confidence.MATCH

SIGNATURE = DeviceSignature((exact("chip_id", 0x0C, b"\xc4", show_value=True, weight=10),))
probe = SIGNATURE.probe

from stemma_detect.result import Confidence
from stemma_detect.signature import DeviceSignature, exact

ADDRESSES = (0x5A,)
PACKAGE = "adafruit-circuitpython-sths34pf80"
PROBE_CONFIDENCE = Confidence.MATCH

SIGNATURE = DeviceSignature((exact("chip_id", 0x0F, b"\xd3", show_value=True, weight=10),))
probe = SIGNATURE.probe

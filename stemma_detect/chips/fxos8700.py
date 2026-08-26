from stemma_detect.result import Confidence
from stemma_detect.signature import DeviceSignature, exact

ADDRESSES = (0x1F,)
PACKAGE = "adafruit-circuitpython-fxos8700"
PROBE_CONFIDENCE = Confidence.MATCH

SIGNATURE = DeviceSignature((exact("chip_id", 0x0D, b"\xc7", show_value=True, weight=10),))
probe = SIGNATURE.probe

from stemma_detect.result import Confidence
from stemma_detect.signature import DeviceSignature, exact

ADDRESSES = (0x1E,)
PACKAGE = "adafruit-circuitpython-lsm303dlh-mag"
PROBE_CONFIDENCE = Confidence.MATCH

# The three identification registers contain the ASCII string "H43".
SIGNATURE = DeviceSignature((exact("chip_id", 0x0A, b"H43", show_value=True, weight=12),))
probe = SIGNATURE.probe

from stemma_detect.chips._possible import address_read_probe
from stemma_detect.result import Confidence

ADDRESSES = (0x44,)
PACKAGE = "adafruit-circuitpython-opt4048"
PROBE_CONFIDENCE = Confidence.POSSIBLE
probe = address_read_probe

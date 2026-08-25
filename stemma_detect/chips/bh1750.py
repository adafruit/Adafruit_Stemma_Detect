from stemma_detect.chips._possible import address_read_probe
from stemma_detect.result import Confidence

ADDRESSES = (0x23, 0x5C)
DEFAULT_ADDRESSES = (0x23,)
PACKAGE = "adafruit-circuitpython-bh1750"
PROBE_CONFIDENCE = Confidence.POSSIBLE
probe = address_read_probe

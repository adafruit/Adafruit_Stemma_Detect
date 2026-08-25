from stemma_detect.chips._possible import address_read_probe
from stemma_detect.result import Confidence

ADDRESSES = (0x5C, 0x5D)
DEFAULT_ADDRESSES = (0x5D,)
PACKAGE = "adafruit-circuitpython-lps2x"
PROBE_CONFIDENCE = Confidence.POSSIBLE
probe = address_read_probe

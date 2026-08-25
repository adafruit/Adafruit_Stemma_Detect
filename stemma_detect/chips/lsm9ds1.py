from stemma_detect.chips._possible import address_read_probe
from stemma_detect.result import Confidence

ADDRESSES = (0x6A, 0x6B)
DEFAULT_ADDRESSES = (0x6B,)
PACKAGE = "adafruit-circuitpython-lsm9ds1"
PROBE_CONFIDENCE = Confidence.POSSIBLE
probe = address_read_probe

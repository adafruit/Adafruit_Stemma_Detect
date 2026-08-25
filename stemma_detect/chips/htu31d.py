from stemma_detect.chips._possible import address_read_probe
from stemma_detect.result import Confidence

ADDRESSES = (0x40, 0x41)
DEFAULT_ADDRESSES = (0x40,)
PACKAGE = "adafruit-circuitpython-htu31d"
PROBE_CONFIDENCE = Confidence.POSSIBLE
probe = address_read_probe

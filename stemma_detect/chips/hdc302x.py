from stemma_detect.chips._possible import address_read_probe
from stemma_detect.result import Confidence

ADDRESSES = tuple(range(0x44, 0x48))
DEFAULT_ADDRESSES = (0x44,)
PACKAGE = "adafruit-circuitpython-hdc302x"
PROBE_CONFIDENCE = Confidence.POSSIBLE
probe = address_read_probe

from stemma_detect.chips._possible import address_read_probe
from stemma_detect.result import Confidence

ADDRESSES = tuple(range(0x28, 0x2C))
DEFAULT_ADDRESSES = (0x28,)
PACKAGE = "adafruit-circuitpython-ds3502"
PROBE_CONFIDENCE = Confidence.POSSIBLE
probe = address_read_probe

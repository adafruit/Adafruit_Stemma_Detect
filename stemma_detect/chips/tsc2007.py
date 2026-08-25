from stemma_detect.chips._possible import address_read_probe
from stemma_detect.result import Confidence

ADDRESSES = tuple(range(0x48, 0x4C))
DEFAULT_ADDRESSES = (0x48,)
PACKAGE = "adafruit-circuitpython-tsc2007"
PROBE_CONFIDENCE = Confidence.POSSIBLE
probe = address_read_probe

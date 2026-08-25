from stemma_detect.chips._possible import address_read_probe
from stemma_detect.result import Confidence

ADDRESSES = tuple(range(0x40, 0x50))
DEFAULT_ADDRESSES = (0x40,)
PACKAGE = "adafruit-circuitpython-ina219"
PROBE_CONFIDENCE = Confidence.POSSIBLE
probe = address_read_probe

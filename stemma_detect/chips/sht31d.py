from stemma_detect.chips._possible import address_read_probe
from stemma_detect.result import Confidence

ADDRESSES = (0x44, 0x45)
DEFAULT_ADDRESSES = (0x44,)
PACKAGE = "adafruit-circuitpython-sht31d"
PROBE_CONFIDENCE = Confidence.POSSIBLE
probe = address_read_probe

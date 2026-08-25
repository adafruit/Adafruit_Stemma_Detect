from stemma_detect.chips._possible import address_read_probe
from stemma_detect.result import Confidence

ADDRESSES = (0x76, 0x77)
DEFAULT_ADDRESSES = (0x77,)
PACKAGE = "adafruit-circuitpython-spa06-003"
PROBE_CONFIDENCE = Confidence.POSSIBLE
probe = address_read_probe

from stemma_detect.chips._possible import address_read_probe
from stemma_detect.result import Confidence

ADDRESSES = (0x1D, 0x53)
DEFAULT_ADDRESSES = (0x53,)
PACKAGE = "adafruit-circuitpython-adxl37x"
PROBE_CONFIDENCE = Confidence.POSSIBLE
probe = address_read_probe

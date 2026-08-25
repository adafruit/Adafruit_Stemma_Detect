from stemma_detect.chips._possible import address_read_probe
from stemma_detect.result import Confidence

ADDRESSES = (0x3A,)
PACKAGE = "adafruit-circuitpython-mlx90632"
PROBE_CONFIDENCE = Confidence.POSSIBLE
probe = address_read_probe

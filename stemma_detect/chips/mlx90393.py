from stemma_detect.chips._possible import address_read_probe
from stemma_detect.result import Confidence

ADDRESSES = tuple(range(0x0C, 0x10))
DEFAULT_ADDRESSES = (0x0C,)
PACKAGE = "adafruit-circuitpython-mlx90393"
PROBE_CONFIDENCE = Confidence.POSSIBLE
probe = address_read_probe

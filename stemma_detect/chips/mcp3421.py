from stemma_detect.chips._possible import address_read_probe
from stemma_detect.result import Confidence

ADDRESSES = tuple(range(0x68, 0x70))
DEFAULT_ADDRESSES = (0x68,)
PACKAGE = "adafruit-circuitpython-mcp3421"
PROBE_CONFIDENCE = Confidence.POSSIBLE
probe = address_read_probe

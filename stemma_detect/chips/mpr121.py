from stemma_detect.chips._possible import address_read_probe
from stemma_detect.result import Confidence

ADDRESSES = tuple(range(0x5A, 0x5E))
DEFAULT_ADDRESSES = (0x5A,)
PACKAGE = "adafruit-circuitpython-mpr121"
PROBE_CONFIDENCE = Confidence.POSSIBLE
probe = address_read_probe

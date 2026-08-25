from stemma_detect.chips._possible import address_read_probe
from stemma_detect.result import Confidence

ADDRESSES = (0x59,)
PACKAGE = "adafruit-circuitpython-sgp40"
PROBE_CONFIDENCE = Confidence.POSSIBLE
probe = address_read_probe

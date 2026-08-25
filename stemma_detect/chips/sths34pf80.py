from stemma_detect.chips._possible import address_read_probe
from stemma_detect.result import Confidence

ADDRESSES = (0x5A,)
PACKAGE = "adafruit-circuitpython-sths34pf80"
PROBE_CONFIDENCE = Confidence.POSSIBLE
probe = address_read_probe

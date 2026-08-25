from stemma_detect.chips._possible import address_read_probe
from stemma_detect.result import Confidence

ADDRESSES = (0x70,)
PACKAGE = "adafruit-circuitpython-shtc3"
PROBE_CONFIDENCE = Confidence.POSSIBLE
probe = address_read_probe

from stemma_detect.chips._possible import address_read_probe
from stemma_detect.result import Confidence

ADDRESSES = (0x61,)
PACKAGE = "adafruit-circuitpython-scd30"
PROBE_CONFIDENCE = Confidence.POSSIBLE
probe = address_read_probe

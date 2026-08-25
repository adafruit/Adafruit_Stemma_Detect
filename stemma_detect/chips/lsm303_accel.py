from stemma_detect.chips._possible import address_read_probe
from stemma_detect.result import Confidence

ADDRESSES = (0x19,)
PACKAGE = "adafruit-circuitpython-lsm303-accel"
PROBE_CONFIDENCE = Confidence.POSSIBLE
probe = address_read_probe

from stemma_detect.chips._possible import address_read_probe
from stemma_detect.result import Confidence

ADDRESSES = (0x74,)
PACKAGE = "adafruit-circuitpython-as7331"
PROBE_CONFIDENCE = Confidence.POSSIBLE
probe = address_read_probe

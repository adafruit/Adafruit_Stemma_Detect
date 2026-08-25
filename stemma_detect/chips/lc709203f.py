from stemma_detect.chips._possible import address_read_probe
from stemma_detect.result import Confidence

ADDRESSES = (0x0B,)
PACKAGE = "adafruit-circuitpython-lc709203f"
PROBE_CONFIDENCE = Confidence.POSSIBLE
probe = address_read_probe

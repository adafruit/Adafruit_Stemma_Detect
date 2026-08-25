from stemma_detect.chips._possible import address_read_probe
from stemma_detect.result import Confidence

ADDRESSES = (
    *range(0x28, 0x2F),
    0x37,
    *range(0x48, 0x50),
    *range(0x70, 0x78),
)
DEFAULT_ADDRESSES = (0x37,)
PACKAGE = "adafruit-circuitpython-pct2075"
PROBE_CONFIDENCE = Confidence.POSSIBLE
probe = address_read_probe

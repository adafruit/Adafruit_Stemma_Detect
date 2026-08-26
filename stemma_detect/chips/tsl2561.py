from stemma_detect.result import Confidence
from stemma_detect.signature import DeviceSignature, exact

ADDRESSES = (0x29, 0x39, 0x49)
DEFAULT_ADDRESSES = (0x39,)
PACKAGE = "adafruit-circuitpython-tsl2561"
PROBE_CONFIDENCE = Confidence.MATCH

# TSL2561 register reads include the 0x80 command bit. The upper nibble of
# the read-only ID register is the fixed part number; the lower nibble varies
# with the silicon revision.
SIGNATURE = DeviceSignature(
    (exact("chip_id", 0x8A, b"\x50", mask=b"\xf0", show_value=True, weight=10),)
)
probe = SIGNATURE.probe

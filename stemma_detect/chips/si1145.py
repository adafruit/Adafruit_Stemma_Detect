from stemma_detect.result import Confidence
from stemma_detect.signature import DeviceSignature, exact

ADDRESSES = (0x60,)
PACKAGE = "adafruit-circuitpython-si1145"
PROBE_CONFIDENCE = Confidence.MATCH

# PART_ID, REV_ID, and SEQ_ID are three adjacent read-only registers.
SIGNATURE = DeviceSignature(
    (exact("device_info", 0x00, b"\x45\x00\x08", show_value=True, weight=12),)
)
probe = SIGNATURE.probe

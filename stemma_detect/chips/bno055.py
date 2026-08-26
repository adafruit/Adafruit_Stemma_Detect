from stemma_detect.result import Confidence
from stemma_detect.signature import DeviceSignature, exact, not_blank

ADDRESSES = (0x28, 0x29)
DEFAULT_ADDRESSES = (0x28,)
PACKAGE = "adafruit-circuitpython-bno055"
PROBE_CONFIDENCE = Confidence.MATCH

SIGNATURE = DeviceSignature(
    (
        exact("chip_id", 0x00, b"\xa0", show_value=True, weight=10),
        exact("accelerometer_id", 0x01, b"\xfb", required=False, weight=4),
        exact("magnetometer_id", 0x02, b"\x32", required=False, weight=4),
        exact("gyroscope_id", 0x03, b"\x0f", required=False, weight=4),
        not_blank(
            "software_revision",
            0x04,
            2,
            show_value=True,
            required=False,
            weight=2,
        ),
    ),
    match_threshold=18,
)


def probe(bus, address):
    return SIGNATURE.probe(bus, address)

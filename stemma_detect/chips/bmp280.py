from stemma_detect.result import Confidence
from stemma_detect.signature import DeviceSignature, exact, not_blank

ADDRESSES = (0x76, 0x77)
PACKAGE = "adafruit-circuitpython-bmp280"
PROBE_CONFIDENCE = Confidence.MATCH

SIGNATURE = DeviceSignature(
    (
        exact("chip_id", 0xD0, b"\x58", show_value=True, weight=10),
        exact(
            "status_reserved",
            0xF3,
            b"\x00",
            mask=b"\xf6",
            required=False,
            weight=2,
        ),
        not_blank("calibration", 0x88, 24, required=False, weight=3),
    ),
    match_threshold=15,
)


def probe(bus, address):
    return SIGNATURE.probe(bus, address)

from stemma_detect.result import Confidence
from stemma_detect.signature import DeviceSignature, exact, not_blank, one_of

ADDRESSES = (0x76, 0x77)
PACKAGE = "adafruit-circuitpython-bme680"
PROBE_CONFIDENCE = Confidence.MATCH

SIGNATURE = DeviceSignature(
    (
        exact("chip_id", 0xD0, b"\x61", show_value=True, weight=10),
        one_of(
            "variant",
            0xF0,
            (b"\x00", b"\x01"),
            show_value=True,
            required=False,
            weight=3,
        ),
        not_blank("calibration_1", 0x89, 25, required=False, weight=3),
        not_blank("calibration_2", 0xE1, 16, required=False, weight=3),
    ),
    match_threshold=16,
)


def probe(bus, address):
    return SIGNATURE.probe(bus, address)

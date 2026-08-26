from stemma_detect.result import Confidence
from stemma_detect.signature import DeviceSignature, exact

ADDRESSES = tuple(range(0x40, 0x44))
DEFAULT_ADDRESSES = (0x40,)
PACKAGE = "adafruit-circuitpython-ina3221"
PROBE_CONFIDENCE = Confidence.MATCH

SIGNATURE = DeviceSignature(
    (
        exact("die_id", 0xFF, b"\x32\x20", show_value=True, weight=10),
        exact(
            "manufacturer_id",
            0xFE,
            b"\x54\x49",
            show_value=True,
            required=False,
            weight=7,
        ),
    ),
    match_threshold=17,
)


def probe(bus, address):
    return SIGNATURE.probe(bus, address)

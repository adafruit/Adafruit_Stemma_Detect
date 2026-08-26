from stemma_detect.result import Confidence
from stemma_detect.signature import DeviceSignature, exact

ADDRESSES = (0x29,)
PACKAGE = "adafruit-circuitpython-ltr329-ltr303"
PROBE_CONFIDENCE = Confidence.MATCH

SIGNATURE = DeviceSignature(
    (
        exact(
            "part_id",
            0x86,
            b"\xa0",
            mask=b"\xf0",
            show_value=True,
            weight=10,
        ),
        exact(
            "manufacturer_id",
            0x87,
            b"\x05",
            show_value=True,
            required=False,
            weight=6,
        ),
    ),
    match_threshold=16,
)


def probe(bus, address):
    return SIGNATURE.probe(bus, address)

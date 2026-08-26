from dataclasses import replace

from stemma_detect.result import Confidence
from stemma_detect.signature import DeviceSignature, exact, not_blank, one_of

ADDRESSES = (0x76, 0x77)
DEFAULT_ADDRESSES = (0x77,)
PACKAGE = "adafruit-circuitpython-bmp3xx"
PROBE_CONFIDENCE = Confidence.MATCH
NAMES = {
    0x50: "bmp388",
    0x60: "bmp390",
}

SIGNATURE = DeviceSignature(
    (
        one_of("chip_id", 0x00, (b"\x50", b"\x60"), show_value=True, weight=10),
        exact(
            "error_reserved",
            0x02,
            b"\x00",
            mask=b"\xf8",
            required=False,
            weight=2,
        ),
        exact(
            "status_reserved",
            0x03,
            b"\x00",
            mask=b"\x8f",
            required=False,
            weight=2,
        ),
        not_blank("calibration", 0x31, 21, required=False, weight=5),
    ),
    match_threshold=15,
)


def probe(bus, address):
    result = SIGNATURE.probe(bus, address)
    if result.confidence is Confidence.NO_MATCH:
        return result
    chip_id = int(result.evidence["chip_id"], 16)
    return replace(result, name=NAMES[chip_id])

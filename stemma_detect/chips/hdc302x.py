from stemma_detect.chips._sensirion import valid_crc_words
from stemma_detect.result import Confidence, ProbeRisk
from stemma_detect.signature import DeviceSignature, command_response

ADDRESSES = tuple(range(0x44, 0x48))
DEFAULT_ADDRESSES = (0x44,)
PACKAGE = "adafruit-circuitpython-hdc302x"
PROBE_CONFIDENCE = Confidence.MATCH
PROBE_RISK = ProbeRisk.COMMAND


def _valid_manufacturer_id(response):
    return valid_crc_words(response) and response[:2] == b"\x30\x00"


SIGNATURE = DeviceSignature(
    (
        command_response(
            "manufacturer_id",
            b"\x37\x81",
            3,
            _valid_manufacturer_id,
            show_value=True,
            weight=12,
        ),
    )
)
probe = SIGNATURE.probe

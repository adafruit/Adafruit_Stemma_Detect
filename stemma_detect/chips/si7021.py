from stemma_detect.chips._sensirion import valid_crc_words
from stemma_detect.result import Confidence, ProbeRisk
from stemma_detect.signature import DeviceSignature, command_response

ADDRESSES = (0x40,)
PACKAGE = "adafruit-circuitpython-si7021"
PROBE_CONFIDENCE = Confidence.MATCH
PROBE_RISK = ProbeRisk.COMMAND


def _valid_electronic_id(response):
    return valid_crc_words(response) and response[0] == 0x15


SIGNATURE = DeviceSignature(
    (
        command_response(
            "electronic_id",
            b"\xfc\xc9",
            6,
            _valid_electronic_id,
            show_value=True,
            weight=12,
        ),
    )
)
probe = SIGNATURE.probe

from stemma_detect.chips._sensirion import crc_payload, valid_crc_words
from stemma_detect.result import Confidence, ProbeRisk
from stemma_detect.signature import DeviceSignature, command_response

ADDRESSES = (0x59,)
PACKAGE = "adafruit-circuitpython-sgp40"
PROBE_CONFIDENCE = Confidence.MATCH
PROBE_RISK = ProbeRisk.COMMAND


def _valid_serial(response):
    return valid_crc_words(response) and crc_payload(response)[:2] == b"\x00\x00"


def _valid_feature_set(response):
    return valid_crc_words(response) and response[:1] == b"\x32"


SIGNATURE = DeviceSignature(
    (
        command_response(
            "serial_number",
            b"\x36\x82",
            9,
            _valid_serial,
            delay_ms=10,
            weight=4,
        ),
        command_response(
            "feature_set",
            b"\x20\x2f",
            3,
            _valid_feature_set,
            delay_ms=10,
            show_value=True,
            weight=12,
        ),
    )
)
probe = SIGNATURE.probe

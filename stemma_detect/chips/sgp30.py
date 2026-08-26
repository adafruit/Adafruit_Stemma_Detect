from stemma_detect.chips._sensirion import valid_crc_words
from stemma_detect.result import Confidence, ProbeRisk
from stemma_detect.signature import DeviceSignature, command_response

ADDRESSES = (0x58,)
PACKAGE = "adafruit-circuitpython-sgp30"
PROBE_CONFIDENCE = Confidence.MATCH
PROBE_RISK = ProbeRisk.COMMAND


def _valid_feature_set(response):
    return valid_crc_words(response) and int.from_bytes(response[:2], "big") in (0x0020, 0x0022)


SIGNATURE = DeviceSignature(
    (
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

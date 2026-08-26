from stemma_detect.chips._sensirion import valid_crc_words
from stemma_detect.result import Confidence, ProbeRisk
from stemma_detect.signature import DeviceSignature, command_response

ADDRESSES = (0x70,)
PACKAGE = "adafruit-circuitpython-shtc3"
PROBE_CONFIDENCE = Confidence.MATCH
PROBE_RISK = ProbeRisk.COMMAND


def _valid_chip_id(response):
    return valid_crc_words(response) and int.from_bytes(response[:2], "big") & 0x083F == 0x0807


SIGNATURE = DeviceSignature(
    (
        command_response(
            "chip_id",
            b"\xef\xc8",
            3,
            _valid_chip_id,
            delay_ms=1,
            show_value=True,
            weight=12,
        ),
    )
)
probe = SIGNATURE.probe

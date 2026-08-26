from stemma_detect.chips._sensirion import crc8
from stemma_detect.result import Confidence, ProbeRisk
from stemma_detect.signature import DeviceSignature, command_response

ADDRESSES = (0x1A,)
PACKAGE = "adafruit-circuitpython-ags02ma"
PROBE_CONFIDENCE = Confidence.MATCH
PROBE_RISK = ProbeRisk.COMMAND


def _valid_firmware(response):
    return crc8(response) == 0 and response[:4] not in (b"\x00" * 4, b"\xff" * 4)


SIGNATURE = DeviceSignature(
    (
        command_response(
            "firmware_version",
            b"\x11",
            5,
            _valid_firmware,
            delay_ms=30,
            show_value=True,
            weight=12,
        ),
    )
)
probe = SIGNATURE.probe

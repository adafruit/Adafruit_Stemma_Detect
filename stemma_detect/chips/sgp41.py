from stemma_detect.chips._sensirion import valid_nonblank_crc_words
from stemma_detect.result import Confidence, ProbeRisk
from stemma_detect.signature import DeviceSignature, command_response

ADDRESSES = (0x59,)
PACKAGE = "adafruit-circuitpython-sgp41"
PROBE_CONFIDENCE = Confidence.MATCH
PROBE_RISK = ProbeRisk.COMMAND

SIGNATURE = DeviceSignature(
    (
        command_response(
            "serial_number",
            b"\x36\x82",
            9,
            valid_nonblank_crc_words,
            delay_ms=1,
            show_value=True,
            weight=10,
        ),
    )
)
probe = SIGNATURE.probe

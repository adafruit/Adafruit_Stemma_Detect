from stemma_detect.chips._sensirion import valid_crc_words
from stemma_detect.result import Confidence, ProbeResult, ProbeRisk

ADDRESSES = (0x62,)
PACKAGE = "adafruit-circuitpython-scd4x"
PROBE_CONFIDENCE = Confidence.MATCH
PROBE_RISK = ProbeRisk.COMMAND

_VARIANTS = {0x0: "scd40", 0x1: "scd41", 0x5: "scd43"}


def _word(response):
    return int.from_bytes(response[:2], "big")


def probe(bus, address):
    # Data-ready status is available during periodic measurement. Bits 15:11
    # are reserved and must be zero, adding structural evidence beyond the CRC.
    status = bus.write_then_read(address, b"\xe4\xb8", 3, delay_ms=1)
    if not valid_crc_words(status) or _word(status) & 0xF800:
        return ProbeResult.no_match({"failed": "data_ready_status"}, score=0, max_score=14)

    evidence = {"signature": "10/14"}
    name = None
    score = 10
    try:
        variant = bus.write_then_read(address, b"\x20\x2f", 3, delay_ms=1)
    except OSError:
        variant = b""
    if valid_crc_words(variant):
        variant_word = _word(variant)
        variant_code = variant_word >> 12
        if variant_code in _VARIANTS and variant_word & 0x0FFF == 0:
            name = _VARIANTS[variant_code]
            score = 14
            evidence["sensor_variant"] = name.upper()
            evidence["signature"] = "14/14"

    return ProbeResult.match(evidence, name=name, score=score, max_score=14)

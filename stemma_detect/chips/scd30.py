from stemma_detect.chips._sensirion import valid_crc_words
from stemma_detect.result import Confidence, ProbeResult, ProbeRisk

ADDRESSES = (0x61,)
PACKAGE = "adafruit-circuitpython-scd30"
PROBE_CONFIDENCE = Confidence.MATCH
PROBE_RISK = ProbeRisk.COMMAND


def probe(bus, address):
    # SCD30 requires a STOP and delay between its command write and response read.
    response = bus.write_then_read(address, b"\xd1\x00", 3, delay_ms=10)
    if not valid_crc_words(response):
        return ProbeResult.no_match({"failed": "firmware_version"}, score=0, max_score=12)

    major, minor = response[:2]
    if (major, minor) in ((0, 0), (0xFF, 0xFF)):
        return ProbeResult.no_match({"failed": "firmware_version"}, score=6, max_score=12)
    return ProbeResult.match(
        {"firmware_version": f"{major}.{minor}", "signature": "12/12"},
        score=12,
        max_score=12,
    )

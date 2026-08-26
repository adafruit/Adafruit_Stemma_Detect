from stemma_detect.chips._sensirion import crc_payload, valid_crc_words
from stemma_detect.result import Confidence, ProbeResult, ProbeRisk

ADDRESSES = (0x6B, 0x6C)
DEFAULT_ADDRESSES = ADDRESSES
PACKAGE = "adafruit-circuitpython-sen6x"
PROBE_CONFIDENCE = Confidence.MATCH
PROBE_RISK = ProbeRisk.COMMAND


def probe(bus, address):
    # Get Product Name is explicitly available in both idle and measurement mode.
    response = bus.write_then_read(address, b"\xd0\x14", 48, delay_ms=20)
    if not valid_crc_words(response):
        return ProbeResult.no_match({"failed": "product_name"}, score=0, max_score=14)

    raw_name = crc_payload(response).split(b"\x00", 1)[0]
    try:
        product_name = raw_name.decode("ascii")
    except UnicodeDecodeError:
        product_name = ""
    if not product_name.startswith("SEN6") or not product_name.isalnum():
        return ProbeResult.no_match({"failed": "product_name"}, score=6, max_score=14)

    return ProbeResult.match(
        {"product_name": product_name, "signature": "14/14"},
        name=product_name.lower(),
        score=14,
        max_score=14,
    )

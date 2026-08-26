from stemma_detect.result import Confidence, ProbeResult

ADDRESSES = (0x13,)
PACKAGE = "adafruit-circuitpython-vcnl4010"
PROBE_CONFIDENCE = Confidence.POSSIBLE


def probe(bus, address):
    product_revision = bus.read_register(address, 0x81, 1)[0]
    evidence = {"product_revision": f"0x{product_revision:02X}"}
    if product_revision == 0x21:
        # VCNL4010 and VCNL4020 share this ID but require different drivers.
        return ProbeResult.possible(evidence, score=8, max_score=10)
    return ProbeResult.no_match(evidence, score=0, max_score=10)

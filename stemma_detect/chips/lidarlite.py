from stemma_detect.result import Confidence, ProbeResult

ADDRESSES = (0x62,)
PACKAGE = "adafruit-circuitpython-lidarlite"
PROBE_CONFIDENCE = Confidence.POSSIBLE


def probe(bus, address):
    unit_id = bus.read_register(address, 0x16, 2)
    evidence = {"unit_id": unit_id.hex().upper()}
    if unit_id in (b"\x00\x00", b"\xff\xff"):
        return ProbeResult.no_match(evidence, score=0, max_score=10)
    return ProbeResult.possible(evidence, score=7, max_score=10)

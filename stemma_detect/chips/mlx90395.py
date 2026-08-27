from stemma_detect.result import Confidence, ProbeResult

ADDRESSES = (0x0C, 0x18)
DEFAULT_ADDRESSES = (0x0C,)
PACKAGE = "adafruit-circuitpython-mlx90395"
PROBE_CONFIDENCE = Confidence.POSSIBLE


def probe(bus, address):
    # The three read-only ID words occupy byte addresses 0x4C through 0x51.
    unique_id = bus.read_register(address, 0x4C, 6)
    evidence = {"unique_id": "0x" + unique_id.hex().upper()}
    if unique_id in (bytes(6), b"\xff" * 6):
        return ProbeResult.no_match(evidence, score=0, max_score=10)
    return ProbeResult.possible(evidence, score=8, max_score=10)

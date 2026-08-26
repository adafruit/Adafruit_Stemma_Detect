from stemma_detect.result import Confidence, ProbeResult

ADDRESSES = tuple(range(0x48, 0x50))
DEFAULT_ADDRESSES = (0x48,)
PACKAGE = "adafruit-circuitpython-tc74"
PROBE_CONFIDENCE = Confidence.POSSIBLE


def probe(bus, address):
    temperature = int.from_bytes(bus.read_register(address, 0x00, 1), "big", signed=True)
    config = bus.read_register(address, 0x01, 1)[0]
    evidence = {"temperature": str(temperature), "config": f"0x{config:02X}"}
    if not -40 <= temperature <= 125 or config & 0x3F:
        return ProbeResult.no_match(evidence, score=0, max_score=8)
    return ProbeResult.possible(evidence, score=5, max_score=8)

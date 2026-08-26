from stemma_detect.result import Confidence, ProbeResult

ADDRESSES = (0x58, 0x59, 0x5A, 0x5B)
DEFAULT_ADDRESSES = (0x58,)
PACKAGE = "adafruit-circuitpython-aw9523"
PROBE_CONFIDENCE = Confidence.MATCH


def probe(bus, address):
    chip_id = bus.read_register(address, 0x10, 1)
    evidence = {"chip_id": f"0x{chip_id[0]:02X}"}
    if chip_id == b"\x23":
        return ProbeResult.match(evidence, score=10, max_score=10)
    return ProbeResult.no_match(evidence, score=0, max_score=10)

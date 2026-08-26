from stemma_detect.result import Confidence, ProbeResult, ProbeRisk

ADDRESSES = (0x5C, 0x5D)
DEFAULT_ADDRESSES = (0x5D,)
PACKAGE = "adafruit-circuitpython-lps35hw"
PROBE_CONFIDENCE = Confidence.POSSIBLE
PROBE_RISK = ProbeRisk.REGISTER


def probe(bus, address: int) -> ProbeResult:
    chip_id = bus.read_register(address, 0x0F, 1)[0]
    evidence = {"chip_id": f"0x{chip_id:02X}"}
    # LPS35HW and members of the LPS22 family share this identity value but use
    # different CircuitPython packages, so the exact register is still only a
    # possible match.
    if chip_id == 0xB1:
        return ProbeResult.possible(evidence, score=8, max_score=10)
    return ProbeResult.no_match(evidence, score=0, max_score=10)

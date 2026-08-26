from stemma_detect.result import Confidence, ProbeResult

ADDRESSES = (0x18,)
PACKAGE = "adafruit-circuitpython-mprls"
PROBE_CONFIDENCE = Confidence.POSSIBLE


def probe(bus, address):
    status = bus.read(address, 1)[0]
    evidence = {"status": f"0x{status:02X}"}
    # Bits 7, 4, 3, and 1 are reserved in the MPR status byte.
    if status & 0x9A:
        return ProbeResult.no_match(evidence, score=0, max_score=8)
    return ProbeResult.possible(evidence, score=5, max_score=8)

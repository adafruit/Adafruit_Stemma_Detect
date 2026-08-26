from stemma_detect.result import Confidence, ProbeResult

ADDRESSES = (0x60,)
PACKAGE = "adafruit-circuitpython-mpl115a2"
PROBE_CONFIDENCE = Confidence.POSSIBLE


def probe(bus, address):
    coefficients = bus.read_register(address, 0x04, 8)
    evidence = {"calibration": coefficients.hex().upper()}
    if coefficients in (b"\x00" * 8, b"\xff" * 8):
        return ProbeResult.no_match(evidence, score=0, max_score=8)
    # The lowest two bits of the final C12 coefficient word are unused.
    if coefficients[-1] & 0x03:
        return ProbeResult.no_match(evidence, score=0, max_score=8)
    return ProbeResult.possible(evidence, score=6, max_score=8)

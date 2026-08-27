from stemma_detect.result import Confidence, ProbeResult, ProbeRisk

ADDRESSES = tuple(range(0x48, 0x4C))
DEFAULT_ADDRESSES = (0x48,)
PACKAGE = "adafruit-circuitpython-tsc2007"
PROBE_CONFIDENCE = Confidence.POSSIBLE
PROBE_RISK = ProbeRisk.COMMAND


def probe(bus, address):
    # Request X and Y in 12-bit mode, then leave the converter powered down.
    # Every result is left-aligned, so the final response nibble must be zero.
    commands = (("x", b"\xc4"), ("y", b"\xd4"), ("temperature", b"\x00"))
    evidence = {}
    for label, command in commands:
        response = bus.write_then_read(address, command, 2)
        evidence[label] = "0x" + response.hex().upper()
        if len(response) != 2 or response[1] & 0x0F:
            return ProbeResult.no_match(evidence, score=0, max_score=10)
    return ProbeResult.possible(evidence, score=8, max_score=10)

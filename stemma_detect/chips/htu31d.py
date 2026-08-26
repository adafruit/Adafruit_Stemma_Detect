from stemma_detect.result import Confidence, ProbeResult, ProbeRisk

ADDRESSES = (0x40, 0x41)
DEFAULT_ADDRESSES = (0x40,)
PACKAGE = "adafruit-circuitpython-htu31d"
PROBE_CONFIDENCE = Confidence.POSSIBLE
PROBE_RISK = ProbeRisk.COMMAND


def probe(bus, address):
    serial = bus.write_then_read(address, b"\x0a", 4)
    evidence = {"serial_number": "0x" + serial.hex().upper()}
    if serial in (bytes(4), b"\xff" * 4):
        return ProbeResult.no_match(evidence, score=0, max_score=10)
    return ProbeResult.possible(evidence, score=7, max_score=10)

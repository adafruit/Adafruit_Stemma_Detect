from stemma_detect.result import Confidence, ProbeResult

ADDRESSES = tuple(range(0x28, 0x2C))
DEFAULT_ADDRESSES = (0x28,)
PACKAGE = "adafruit-circuitpython-ds3502"
PROBE_CONFIDENCE = Confidence.POSSIBLE


def probe(bus, address):
    wiper = bus.read_register(address, 0x00, 1)[0]
    control = bus.read_register(address, 0x02, 1)[0]
    evidence = {
        "wiper": str(wiper & 0x7F),
        "control": f"0x{control:02X}",
    }
    # The wiper is seven bits. Only the control register's mode bit is
    # implemented; its lower seven bits are reserved.
    if wiper & 0x80 or control & 0x7F:
        return ProbeResult.no_match(evidence, score=0, max_score=10)
    return ProbeResult.possible(evidence, score=7, max_score=10)

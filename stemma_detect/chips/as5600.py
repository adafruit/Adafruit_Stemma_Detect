from stemma_detect.result import Confidence, ProbeResult

ADDRESSES = (0x36,)
PACKAGE = "adafruit-circuitpython-as5600"
PROBE_CONFIDENCE = Confidence.POSSIBLE


def probe(bus, address):
    burn_count = bus.read_register(address, 0x00, 1)[0]
    status = bus.read_register(address, 0x0B, 1)[0]
    raw_angle = bus.read_register(address, 0x0C, 2)
    angle = bus.read_register(address, 0x0E, 2)
    evidence = {
        "burn_count": str(burn_count),
        "status": f"0x{status:02X}",
        "raw_angle": f"0x{int.from_bytes(raw_angle, 'big'):04X}",
        "angle": f"0x{int.from_bytes(angle, 'big'):04X}",
    }
    if burn_count > 3 or status & 0xC7 or raw_angle[0] & 0xF0 or angle[0] & 0xF0:
        return ProbeResult.no_match(evidence, score=0, max_score=10)
    return ProbeResult.possible(evidence, score=8, max_score=10)

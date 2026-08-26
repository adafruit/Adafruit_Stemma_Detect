from stemma_detect.result import Confidence, ProbeResult, ProbeRisk

ADDRESSES = (0x39,)
PACKAGE = "adafruit-circuitpython-as7343"
PROBE_CONFIDENCE = Confidence.MATCH
PROBE_RISK = ProbeRisk.COMMAND


def probe(bus, address):
    config = bus.read_register(address, 0xBF, 1)[0]
    try:
        bus.write(address, bytes((0xBF, config | 0x10)))
        identity = bus.read_register(address, 0x58, 3)
    finally:
        bus.write(address, bytes((0xBF, config)))

    evidence = {
        "aux_id": f"0x{identity[0]:02X}",
        "revision_id": f"0x{identity[1]:02X}",
        "chip_id": f"0x{identity[2]:02X}",
    }
    if identity[2] == 0x81:
        return ProbeResult.match(evidence, score=12, max_score=12)
    return ProbeResult.no_match(evidence, score=0, max_score=12)

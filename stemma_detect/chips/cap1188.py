from stemma_detect.result import Confidence, ProbeResult

ADDRESSES = (0x29,)
PACKAGE = "adafruit-circuitpython-cap1188"
PROBE_CONFIDENCE = Confidence.MATCH


def probe(bus, address):
    identity = bus.read_register(address, 0xFD, 3)
    evidence = {
        "product_id": f"0x{identity[0]:02X}",
        "manufacturer_id": f"0x{identity[1]:02X}",
        "revision": f"0x{identity[2]:02X}",
    }
    if identity[:2] == b"\x50\x5d":
        return ProbeResult.match(evidence, score=14, max_score=14)
    return ProbeResult.no_match(evidence, score=0, max_score=14)

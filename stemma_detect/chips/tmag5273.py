from stemma_detect.result import Confidence, ProbeResult

ADDRESSES = (0x35,)
PACKAGE = "adafruit-circuitpython-tmag5273"
PROBE_CONFIDENCE = Confidence.MATCH


def probe(bus, address):
    device_id = bus.read_register(address, 0x0D, 1)[0]
    manufacturer_id = bus.read_register(address, 0x0E, 2)
    version = device_id & 0x03
    evidence = {
        "device_id": f"0x{device_id:02X}",
        "manufacturer_id": f"0x{int.from_bytes(manufacturer_id, 'little'):04X}",
    }

    if manufacturer_id != b"\x49\x54" or version not in (1, 2):
        return ProbeResult.no_match(evidence, score=0, max_score=14)

    return ProbeResult.match(
        evidence,
        name=f"tmag5273_a{version}",
        score=14,
        max_score=14,
    )

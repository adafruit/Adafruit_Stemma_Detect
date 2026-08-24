from stemma_detect.result import Confidence, ProbeResult

ADDRESSES = tuple(range(0x40, 0x50))
PACKAGE = "adafruit-circuitpython-ina228"
PROBE_CONFIDENCE = Confidence.MATCH


def probe(bus, address):
    manufacturer_id = bus.read_register(address, 0x3E, 2)
    device_id = bus.read_register(address, 0x3F, 2)
    if manufacturer_id != b"\x54\x49" or len(device_id) != 2:
        return ProbeResult.no_match()
    part = int.from_bytes(device_id, "big") >> 4
    return ProbeResult.match({"device_id": "0x228"}) if part == 0x228 else ProbeResult.no_match()

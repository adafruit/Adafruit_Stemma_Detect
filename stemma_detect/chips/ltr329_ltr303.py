from stemma_detect.result import Confidence, ProbeResult

ADDRESSES = (0x29,)
PACKAGE = "adafruit-circuitpython-ltr329-ltr303"
PROBE_CONFIDENCE = Confidence.MATCH


def probe(bus, address):
    part_id = bus.read_register(address, 0x86, 1)
    manufacturer_id = bus.read_register(address, 0x87, 1)
    if part_id != b"\xa0" or manufacturer_id != b"\x05":
        return ProbeResult.no_match()
    return ProbeResult.match(
        {
            "part_id": "0xA0",
            "manufacturer_id": "0x05",
        }
    )

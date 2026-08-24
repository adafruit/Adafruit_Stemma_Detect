from stemma_detect.result import Confidence, ProbeResult

ADDRESSES = tuple(range(0x18, 0x20))
PACKAGE = "adafruit-circuitpython-mcp9808"
PROBE_CONFIDENCE = Confidence.MATCH


def probe(bus, address):
    manufacturer_id = bus.read_register(address, 0x06, 2)
    device_id = bus.read_register(address, 0x07, 2)
    if manufacturer_id != b"\x00\x54" or device_id[0] != 0x04:
        return ProbeResult.no_match()
    return ProbeResult.match(
        {
            "device_id": f"0x{device_id[0]:02X}",
            "revision": f"0x{device_id[1]:02X}",
        }
    )

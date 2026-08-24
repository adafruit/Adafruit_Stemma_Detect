from stemma_detect.result import Confidence, ProbeResult

ADDRESSES = tuple(range(0x60, 0x68))
PACKAGE = "adafruit-circuitpython-mcp9600"
PROBE_CONFIDENCE = Confidence.MATCH


def probe(bus, address):
    version = bus.read_register(address, 0x20, 2)
    if len(version) != 2 or version[0] not in (0x40, 0x41):
        return ProbeResult.no_match()
    return ProbeResult.match(
        {"device_id": f"0x{version[0]:02X}", "revision": f"0x{version[1]:02X}"}
    )

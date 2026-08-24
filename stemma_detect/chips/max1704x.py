from stemma_detect.result import Confidence, ProbeResult

ADDRESSES = (0x36,)
PACKAGE = "adafruit-circuitpython-max1704x"
PROBE_CONFIDENCE = Confidence.MATCH


def probe(bus, address):
    version = bus.read_register(address, 0x08, 2)
    if len(version) != 2 or int.from_bytes(version, "big") & 0xFFF0 != 0x0010:
        return ProbeResult.no_match()
    return ProbeResult.match({"version": f"0x{int.from_bytes(version, 'big'):04X}"})

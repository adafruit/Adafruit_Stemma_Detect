from stemma_detect.result import Confidence, ProbeResult

ADDRESSES = (0x39,)
PACKAGE = "adafruit-circuitpython-apds9999"
PROBE_CONFIDENCE = Confidence.MATCH


def probe(bus, address):
    part_id = bus.read_register(address, 0x06, 1)
    return ProbeResult.match({"part_id": "0xC2"}) if part_id == b"\xc2" else ProbeResult.no_match()

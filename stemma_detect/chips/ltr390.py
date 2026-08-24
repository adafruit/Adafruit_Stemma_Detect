from stemma_detect.result import Confidence, ProbeResult

ADDRESSES = (0x53,)
PACKAGE = "adafruit-circuitpython-ltr390"
PROBE_CONFIDENCE = Confidence.MATCH


def probe(bus, address):
    part_id = bus.read_register(address, 0x06, 1)
    return ProbeResult.match({"part_id": "0xB2"}) if part_id == b"\xb2" else ProbeResult.no_match()

from stemma_detect.result import Confidence, ProbeResult

ADDRESSES = (0x26,)
PACKAGE = "adafruit-circuitpython-msa301"
PROBE_CONFIDENCE = Confidence.MATCH


def probe(bus, address):
    part_id = bus.read_register(address, 0x01, 1)
    return ProbeResult.match({"part_id": "0x13"}) if part_id == b"\x13" else ProbeResult.no_match()

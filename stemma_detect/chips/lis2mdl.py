from stemma_detect.result import Confidence, ProbeResult

ADDRESSES = (0x1E,)
PACKAGE = "adafruit-circuitpython-lis2mdl"
PROBE_CONFIDENCE = Confidence.MATCH


def probe(bus, address):
    chip_id = bus.read_register(address, 0x4F, 1)
    return ProbeResult.match({"chip_id": "0x40"}) if chip_id == b"\x40" else ProbeResult.no_match()

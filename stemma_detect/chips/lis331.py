from stemma_detect.result import Confidence, ProbeResult

ADDRESSES = (0x18, 0x19)
PACKAGE = "adafruit-circuitpython-lis331"
PROBE_CONFIDENCE = Confidence.MATCH


def probe(bus, address):
    chip_id = bus.read_register(address, 0x0F, 1)
    return ProbeResult.match({"chip_id": "0x32"}) if chip_id == b"\x32" else ProbeResult.no_match()

from stemma_detect.result import Confidence, ProbeResult

ADDRESSES = (0x5F,)
PACKAGE = "adafruit-circuitpython-hts221"
PROBE_CONFIDENCE = Confidence.MATCH


def probe(bus, address):
    chip_id = bus.read_register(address, 0x0F, 1)
    return ProbeResult.match({"chip_id": "0xBC"}) if chip_id == b"\xbc" else ProbeResult.no_match()

from stemma_detect.result import Confidence, ProbeResult

ADDRESSES = (0x28, 0x29)
PACKAGE = "adafruit-circuitpython-bno055"
PROBE_CONFIDENCE = Confidence.MATCH


def probe(bus, address):
    chip_id = bus.read_register(address, 0x00, 1)
    return ProbeResult.match({"chip_id": "0xA0"}) if chip_id == b"\xa0" else ProbeResult.no_match()

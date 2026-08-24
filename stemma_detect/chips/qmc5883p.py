from stemma_detect.result import Confidence, ProbeResult

ADDRESSES = (0x3C,)
PACKAGE = "adafruit-circuitpython-qmc5883p"
PROBE_CONFIDENCE = Confidence.MATCH


def probe(bus, address):
    chip_id = bus.read_register(address, 0x00, 1)
    return ProbeResult.match({"chip_id": "0x80"}) if chip_id == b"\x80" else ProbeResult.no_match()

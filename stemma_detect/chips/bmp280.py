from stemma_detect.result import Confidence, ProbeResult

ADDRESSES = (0x76, 0x77)
PACKAGE = "adafruit-circuitpython-bmp280"
PROBE_CONFIDENCE = Confidence.MATCH


def probe(bus, address):
    chip_id = bus.read_register(address, 0xD0, 1)
    return ProbeResult.match({"chip_id": "0x58"}) if chip_id == b"\x58" else ProbeResult.no_match()

from stemma_detect.result import Confidence, ProbeResult

ADDRESSES = (0x1C, 0x1E)
PACKAGE = "adafruit-circuitpython-lis3mdl"
PROBE_CONFIDENCE = Confidence.MATCH


def probe(bus, address):
    chip_id = bus.read_register(address, 0x0F, 1)
    return ProbeResult.match({"chip_id": "0x3D"}) if chip_id == b"\x3d" else ProbeResult.no_match()

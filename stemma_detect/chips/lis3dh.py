from stemma_detect.result import Confidence, ProbeResult

ADDRESSES = (0x18, 0x19)
PACKAGE = "adafruit-circuitpython-lis3dh"
PROBE_CONFIDENCE = Confidence.MATCH


def probe(bus, address):
    device_id = bus.read_register(address, 0x0F, 1)
    return (
        ProbeResult.match({"device_id": "0x33"}) if device_id == b"\x33" else ProbeResult.no_match()
    )

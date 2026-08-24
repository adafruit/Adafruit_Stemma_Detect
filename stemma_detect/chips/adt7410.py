from stemma_detect.result import Confidence, ProbeResult

ADDRESSES = tuple(range(0x48, 0x4C))
PACKAGE = "adafruit-circuitpython-adt7410"
PROBE_CONFIDENCE = Confidence.MATCH


def probe(bus, address):
    device_id = bus.read_register(address, 0x0B, 1)
    return (
        ProbeResult.match({"device_id": "0xCB"}) if device_id == b"\xcb" else ProbeResult.no_match()
    )

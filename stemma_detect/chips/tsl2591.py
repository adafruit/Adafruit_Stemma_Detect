from stemma_detect.result import Confidence, ProbeResult

ADDRESSES = (0x29,)
PACKAGE = "adafruit-circuitpython-tsl2591"
PROBE_CONFIDENCE = Confidence.MATCH


def probe(bus, address):
    device_id = bus.read_register(address, 0xB2, 1)
    return (
        ProbeResult.match({"device_id": "0x50"}) if device_id == b"\x50" else ProbeResult.no_match()
    )

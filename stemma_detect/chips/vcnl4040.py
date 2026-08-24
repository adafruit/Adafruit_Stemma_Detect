from stemma_detect.result import Confidence, ProbeResult

ADDRESSES = (0x60,)
PACKAGE = "adafruit-circuitpython-vcnl4040"
PROBE_CONFIDENCE = Confidence.MATCH


def probe(bus, address):
    device_id = bus.read_register(address, 0x0C, 2)
    return (
        ProbeResult.match({"device_id": "0x0186"})
        if device_id == b"\x86\x01"
        else ProbeResult.no_match()
    )

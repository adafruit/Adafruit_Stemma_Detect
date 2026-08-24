from stemma_detect.result import Confidence, ProbeResult

ADDRESSES = (0x5A, 0x5B)
PACKAGE = "adafruit-circuitpython-ccs811"
PROBE_CONFIDENCE = Confidence.MATCH


def probe(bus, address):
    hardware_id = bus.read_register(address, 0x20, 1)
    return (
        ProbeResult.match({"hardware_id": "0x81"})
        if hardware_id == b"\x81"
        else ProbeResult.no_match()
    )

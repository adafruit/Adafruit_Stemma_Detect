from stemma_detect.result import Confidence, ProbeResult

ADDRESSES = (0x10,)
PACKAGE = "adafruit-circuitpython-veml6075"
PROBE_CONFIDENCE = Confidence.MATCH


def probe(bus, address):
    revision_id = bus.read_register(address, 0x0C, 2)
    return (
        ProbeResult.match({"revision_id": "0x0026"})
        if revision_id == b"\x26\x00"
        else ProbeResult.no_match()
    )

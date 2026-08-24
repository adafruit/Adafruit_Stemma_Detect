from stemma_detect.result import Confidence, ProbeResult

ADDRESSES = (0x30,)
PACKAGE = "adafruit-circuitpython-mmc56x3"
PROBE_CONFIDENCE = Confidence.MATCH


def probe(bus, address):
    product_id = bus.read_register(address, 0x39, 1)
    return (
        ProbeResult.match({"product_id": "0x10"})
        if product_id == b"\x10"
        else ProbeResult.no_match()
    )

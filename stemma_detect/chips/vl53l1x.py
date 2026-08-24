from stemma_detect.result import Confidence, ProbeResult

ADDRESSES = (0x29,)
PACKAGE = "adafruit-circuitpython-vl53l1x"
PROBE_CONFIDENCE = Confidence.MATCH


def probe(bus, address):
    model_info = bus.write_then_read(address, b"\x01\x0f", 3)
    return (
        ProbeResult.match({"model_id": "0xEACC10"})
        if model_info == b"\xea\xcc\x10"
        else ProbeResult.no_match()
    )

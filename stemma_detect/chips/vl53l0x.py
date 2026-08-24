from stemma_detect.result import Confidence, ProbeResult

ADDRESSES = (0x29,)
PACKAGE = "adafruit-circuitpython-vl53l0x"
PROBE_CONFIDENCE = Confidence.MATCH


def probe(bus, address):
    model = bytes(bus.read_register(address, register, 1)[0] for register in (0xC0, 0xC1, 0xC2))
    return (
        ProbeResult.match({"model_id": "0xEEAA10"})
        if model == b"\xee\xaa\x10"
        else ProbeResult.no_match()
    )

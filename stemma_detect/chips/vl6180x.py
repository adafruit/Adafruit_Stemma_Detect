from stemma_detect.result import Confidence, ProbeResult

ADDRESSES = (0x29,)
PACKAGE = "adafruit-circuitpython-vl6180x"
PROBE_CONFIDENCE = Confidence.MATCH


def probe(bus, address):
    # VL6180X registers use a two-byte, big-endian address.
    bus.write(address, b"\x00\x00")
    model_id = bus.read(address, 1)
    return (
        ProbeResult.match({"model_id": "0xB4"}) if model_id == b"\xb4" else ProbeResult.no_match()
    )

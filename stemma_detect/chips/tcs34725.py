from stemma_detect.result import Confidence, ProbeResult

ADDRESSES = (0x29,)
PACKAGE = "adafruit-circuitpython-tcs34725"
PROBE_CONFIDENCE = Confidence.MATCH


def probe(bus, address):
    sensor_id = bus.read_register(address, 0x92, 1)
    if sensor_id not in (b"\x10", b"\x44", b"\x4d"):
        return ProbeResult.no_match()
    return ProbeResult.match({"sensor_id": f"0x{sensor_id[0]:02X}"})

from stemma_detect.result import Confidence, ProbeResult

ADDRESSES = tuple(range(0x48, 0x4C))
PACKAGE = "adafruit-circuitpython-tmp117"
PROBE_CONFIDENCE = Confidence.MATCH


def probe(bus, address):
    device_id = bus.read_register(address, 0x0F, 2)
    if len(device_id) != 2 or int.from_bytes(device_id, "big") & 0x0FFF != 0x0117:
        return ProbeResult.no_match()
    return ProbeResult.match({"device_id": f"0x{int.from_bytes(device_id, 'big'):04X}"})

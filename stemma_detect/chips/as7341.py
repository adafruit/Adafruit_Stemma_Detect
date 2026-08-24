from stemma_detect.result import Confidence, ProbeResult

ADDRESSES = (0x39,)
PACKAGE = "adafruit-circuitpython-as7341"
PROBE_CONFIDENCE = Confidence.MATCH


def probe(bus, address):
    device_id = bus.read_register(address, 0x92, 1)
    if len(device_id) != 1 or device_id[0] >> 2 != 0x09:
        return ProbeResult.no_match()
    return ProbeResult.match({"device_id": f"0x{device_id[0]:02X}"})

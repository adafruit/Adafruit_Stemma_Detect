from stemma_detect.result import Confidence, ProbeResult

ADDRESSES = (0x39,)
PACKAGE = "adafruit-circuitpython-apds9960"
PROBE_CONFIDENCE = Confidence.MATCH


def probe(bus, address):
    device_id = bus.read_register(address, 0x92, 1)
    return (
        ProbeResult.match({"device_id": f"0x{device_id[0]:02X}"})
        if device_id in (b"\xa8", b"\xab")
        else ProbeResult.no_match()
    )

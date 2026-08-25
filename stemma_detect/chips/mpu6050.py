from stemma_detect.result import Confidence, ProbeResult

ADDRESSES = (0x68, 0x69)
DEFAULT_ADDRESSES = (0x68,)
PACKAGE = "adafruit-circuitpython-mpu6050"
PROBE_CONFIDENCE = Confidence.MATCH


def probe(bus, address):
    device_id = bus.read_register(address, 0x75, 1)
    return (
        ProbeResult.match({"device_id": "0x68"}) if device_id == b"\x68" else ProbeResult.no_match()
    )

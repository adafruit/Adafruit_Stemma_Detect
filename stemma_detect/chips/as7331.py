from stemma_detect.result import Confidence, ProbeResult

ADDRESSES = (0x74,)
PACKAGE = "adafruit-circuitpython-as7331"
PROBE_CONFIDENCE = Confidence.MATCH


def probe(bus, address):
    device_id = bus.read_register(address, 0x02, 1)[0]
    evidence = {"device_id": f"0x{device_id:02X}"}
    if device_id == 0x21:
        return ProbeResult.match(evidence, score=10, max_score=10)
    return ProbeResult.no_match(evidence, score=0, max_score=10)

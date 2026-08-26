from stemma_detect.result import Confidence, ProbeResult

ADDRESSES = (0x6B,)
PACKAGE = "adafruit-circuitpython-lsm9ds0"
PROBE_CONFIDENCE = Confidence.MATCH


def probe(bus, address):
    gyro_id = bus.read_register(address, 0x0F, 1)
    xm_id = bus.read_register(0x1D, 0x0F, 1)
    evidence = {"xm_id": f"0x{xm_id[0]:02X}", "gyro_id": f"0x{gyro_id[0]:02X}"}
    if xm_id == b"\x49" and gyro_id == b"\xd4":
        return ProbeResult.match(evidence, score=16, max_score=16)
    return ProbeResult.no_match(evidence, score=0, max_score=16)

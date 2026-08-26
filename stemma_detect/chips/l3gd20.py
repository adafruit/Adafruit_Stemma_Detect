from stemma_detect.result import Confidence, ProbeResult

ADDRESSES = (0x6A, 0x6B)
DEFAULT_ADDRESSES = (0x6B,)
PACKAGE = "adafruit-circuitpython-l3gd20"
PROBE_CONFIDENCE = Confidence.MATCH


def probe(bus, address):
    chip_id = bus.read_register(address, 0x0F, 1)[0]
    evidence = {"chip_id": f"0x{chip_id:02X}"}
    if chip_id == 0xD7 or (chip_id == 0xD4 and address == 0x6A):
        return ProbeResult.match(evidence, score=10, max_score=10)
    if chip_id == 0xD4:
        # The gyro half of an LSM9DS0 has this ID at its default 0x6B.
        return ProbeResult.possible(evidence, score=8, max_score=10)
    return ProbeResult.no_match(evidence, score=0, max_score=10)

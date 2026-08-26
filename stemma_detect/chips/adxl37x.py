from stemma_detect.result import Confidence, ProbeResult

ADDRESSES = (0x1D, 0x53)
DEFAULT_ADDRESSES = (0x53,)
PACKAGE = "adafruit-circuitpython-adxl37x"
PROBE_CONFIDENCE = Confidence.POSSIBLE


def probe(bus, address):
    # ADXL375 shares its 0xE5 device ID with the ADXL34x family, which uses a
    # different CircuitPython package. The ID is strong evidence, not proof.
    chip_id = bus.read_register(address, 0x00, 1)[0]
    evidence = {"chip_id": f"0x{chip_id:02X}"}
    if chip_id == 0xE5:
        return ProbeResult.possible(evidence, score=8, max_score=10)
    return ProbeResult.no_match(evidence, score=0, max_score=10)

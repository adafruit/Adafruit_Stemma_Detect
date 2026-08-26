from stemma_detect.result import Confidence, ProbeResult

ADDRESSES = (0x1D, 0x53)
DEFAULT_ADDRESSES = (0x53,)
PACKAGE = "adafruit-circuitpython-adxl34x"
PROBE_CONFIDENCE = Confidence.POSSIBLE


def probe(bus, address):
    # ADXL343 and ADXL345 share this driver and 0xE5 device ID. ADXL375 also
    # reports 0xE5 but needs adafruit-circuitpython-adxl37x, so remain possible.
    chip_id = bus.read_register(address, 0x00, 1)[0]
    evidence = {"chip_id": f"0x{chip_id:02X}"}
    if chip_id == 0xE5:
        return ProbeResult.possible(evidence, score=8, max_score=10)
    return ProbeResult.no_match(evidence, score=0, max_score=10)

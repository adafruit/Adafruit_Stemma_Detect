from stemma_detect.result import Confidence, ProbeResult

ADDRESSES = (0x5C, 0x5D)
DEFAULT_ADDRESSES = (0x5D,)
PACKAGE = "adafruit-circuitpython-lps2x"
PROBE_CONFIDENCE = Confidence.MATCH


def probe(bus, address):
    chip_id = bus.read_register(address, 0x0F, 1)[0]
    evidence = {"chip_id": f"0x{chip_id:02X}"}

    # LPS25HB has a unique ID and shares the LPS2x driver with LPS22HB.
    if chip_id == 0xBD:
        return ProbeResult.match(evidence, name="lps25", score=10, max_score=10)

    # LPS22HB and LPS35HW both report 0xB1 but require different drivers.
    if chip_id == 0xB1:
        return ProbeResult.possible(evidence, score=8, max_score=10)

    return ProbeResult.no_match(evidence, score=0, max_score=10)

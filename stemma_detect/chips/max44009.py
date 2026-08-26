from stemma_detect.result import Confidence, ProbeResult

ADDRESSES = (0x4A, 0x4B)
DEFAULT_ADDRESSES = (0x4A,)
PACKAGE = "adafruit-circuitpython-max44009"
PROBE_CONFIDENCE = Confidence.POSSIBLE


def probe(bus, address):
    config = bus.read_register(address, 0x02, 1)[0]
    lux = bus.read_register(address, 0x03, 2)
    evidence = {"config": f"0x{config:02X}", "lux_raw": lux.hex().upper()}
    # Configuration bits 5:4 and the upper nibble of LUX_LOW are reserved.
    if config & 0x30 or lux[1] & 0xF0:
        return ProbeResult.no_match(evidence, score=0, max_score=8)
    return ProbeResult.possible(evidence, score=6, max_score=8)

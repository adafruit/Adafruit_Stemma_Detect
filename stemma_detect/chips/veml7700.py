from stemma_detect.result import Confidence, ProbeResult

ADDRESSES = (0x10,)
PACKAGE = "adafruit-circuitpython-veml7700"
PROBE_CONFIDENCE = Confidence.POSSIBLE

_VALID_INTEGRATION_TIMES = frozenset((0x0, 0x1, 0x2, 0x3, 0x8, 0xC))


def probe(bus, address):
    config = int.from_bytes(bus.read_register(address, 0x00, 2), "little")
    power_save = int.from_bytes(bus.read_register(address, 0x03, 2), "little")
    interrupt = int.from_bytes(bus.read_register(address, 0x06, 2), "little")
    integration_time = config >> 6 & 0x0F
    evidence = {
        "config": f"0x{config:04X}",
        "power_save": f"0x{power_save:04X}",
        "interrupt": f"0x{interrupt:04X}",
    }
    if config & 0xE40C or integration_time not in _VALID_INTEGRATION_TIMES:
        return ProbeResult.no_match(evidence, score=0, max_score=10)
    if power_save & 0xFFF8 or interrupt & 0x3FFF:
        return ProbeResult.no_match(evidence, score=0, max_score=10)
    return ProbeResult.possible(evidence, score=8, max_score=10)

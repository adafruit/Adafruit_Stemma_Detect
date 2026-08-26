from stemma_detect.result import Confidence, ProbeResult

ADDRESSES = tuple(range(0x40, 0x50))
DEFAULT_ADDRESSES = (0x40,)
PACKAGE = "adafruit-circuitpython-ina219"
PROBE_CONFIDENCE = Confidence.POSSIBLE

_VALID_ADC_MODES = frozenset((0, 1, 2, 3, *range(9, 16)))


def probe(bus, address):
    config = int.from_bytes(bus.read_register(address, 0x00, 2), "big")
    bus_voltage = int.from_bytes(bus.read_register(address, 0x02, 2), "big")
    bus_adc = config >> 7 & 0x0F
    shunt_adc = config >> 3 & 0x0F
    evidence = {
        "config": f"0x{config:04X}",
        "bus_voltage": f"0x{bus_voltage:04X}",
    }
    if config & 0x4000 or bus_voltage & 0x0004:
        return ProbeResult.no_match(evidence, score=0, max_score=10)
    if bus_adc not in _VALID_ADC_MODES or shunt_adc not in _VALID_ADC_MODES:
        return ProbeResult.no_match(evidence, score=0, max_score=10)
    return ProbeResult.possible(evidence, score=7, max_score=10)

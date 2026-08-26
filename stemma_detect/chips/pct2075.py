from stemma_detect.result import Confidence, ProbeResult

ADDRESSES = (
    *range(0x28, 0x2F),
    0x37,
    *range(0x48, 0x50),
    *range(0x70, 0x78),
)
DEFAULT_ADDRESSES = (0x37,)
PACKAGE = "adafruit-circuitpython-pct2075"
PROBE_CONFIDENCE = Confidence.POSSIBLE


def probe(bus, address):
    temperature = bus.read_register(address, 0x00, 2)
    config = bus.read_register(address, 0x01, 1)[0]
    idle_time = bus.read_register(address, 0x04, 1)[0]
    evidence = {
        "temperature_raw": f"0x{int.from_bytes(temperature, 'big'):04X}",
        "config": f"0x{config:02X}",
        "idle_time": str(idle_time),
    }
    if temperature[1] & 0x1F or config & 0xE0 or idle_time & 0xE0:
        return ProbeResult.no_match(evidence, score=0, max_score=10)
    return ProbeResult.possible(evidence, score=7, max_score=10)

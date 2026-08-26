from stemma_detect.result import Confidence, ProbeResult, ProbeRisk

ADDRESSES = tuple(range(0x0C, 0x10))
DEFAULT_ADDRESSES = (0x0C,)
PACKAGE = "adafruit-circuitpython-mlx90393"
PROBE_CONFIDENCE = Confidence.POSSIBLE
PROBE_RISK = ProbeRisk.COMMAND


def probe(bus, address):
    # Read the factory temperature-reference word. A successful MLX90393
    # register read returns a status byte followed by two data bytes.
    response = bus.write_then_read(address, b"\x50\x90", 3)
    status = response[0]
    temperature_reference = int.from_bytes(response[1:], "big")
    evidence = {
        "status": f"0x{status:02X}",
        "temperature_reference": f"0x{temperature_reference:04X}",
    }
    if status & 0x03 != 0x03 or temperature_reference in (0x0000, 0xFFFF):
        return ProbeResult.no_match(evidence, score=0, max_score=10)
    return ProbeResult.possible(evidence, score=7, max_score=10)

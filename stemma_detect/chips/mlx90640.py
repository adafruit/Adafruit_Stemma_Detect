from stemma_detect.result import Confidence, ProbeResult, ProbeRisk

ADDRESSES = (0x33,)
PACKAGE = "adafruit-circuitpython-mlx90640"
PROBE_CONFIDENCE = Confidence.POSSIBLE
PROBE_RISK = ProbeRisk.COMMAND


def probe(bus, address):
    # MLX90640 uses 16-bit register addresses. These three EEPROM words form a
    # factory-programmed serial number, but there is no fixed model ID.
    serial = bus.write_then_read(address, b"\x24\x07", 6)
    evidence = {"serial_number": "0x" + serial.hex().upper()}
    if serial in (bytes(6), b"\xff" * 6):
        return ProbeResult.no_match(evidence, score=0, max_score=10)
    return ProbeResult.possible(evidence, score=7, max_score=10)

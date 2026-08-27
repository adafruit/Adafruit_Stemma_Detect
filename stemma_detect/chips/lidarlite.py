from stemma_detect.result import Confidence, ProbeResult

ADDRESSES = (0x62,)
PACKAGE = "adafruit-circuitpython-lidarlite"
PROBE_CONFIDENCE = Confidence.POSSIBLE


def _read_register_with_stop(bus, address, register, length):
    # LIDAR-Lite v3 does not support a repeated START between these phases.
    bus.write(address, bytes((register,)))
    return bus.read(address, length)


def probe(bus, address):
    status = _read_register_with_stop(bus, address, 0x01, 1)[0]
    unit_id = _read_register_with_stop(bus, address, 0x16, 2)
    i2c_config = _read_register_with_stop(bus, address, 0x1E, 1)[0]
    evidence = {
        "unit_id": "0x" + unit_id.hex().upper(),
        "status": f"0x{status:02X}",
        "i2c_config": f"0x{i2c_config:02X}",
    }
    if unit_id in (b"\x00\x00", b"\xff\xff"):
        return ProbeResult.no_match(evidence, score=0, max_score=10)
    # Status bit 7 and I2C_CONFIG bits 7:6 are unused across v3 and v3HP.
    # Treat them as supporting evidence instead of rejecting configured units.
    score = 7 + (status & 0x80 == 0) + (i2c_config & 0xC0 == 0)
    return ProbeResult.possible(evidence, score=score, max_score=10)

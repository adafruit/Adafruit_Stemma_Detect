from stemma_detect.result import Confidence, ProbeResult, ProbeRisk

ADDRESSES = (0x44,)
PACKAGE = "adafruit-circuitpython-sht4x"
PROBE_CONFIDENCE = Confidence.MATCH
PROBE_RISK = ProbeRisk.COMMAND


def _crc8(data):
    crc = 0xFF
    for value in data:
        crc ^= value
        for _ in range(8):
            crc = ((crc << 1) ^ 0x31) & 0xFF if crc & 0x80 else (crc << 1) & 0xFF
    return crc


def probe(bus, address):
    response = bus.write_then_read(address, b"\x89", 6, delay_ms=10)
    valid = _crc8(response[0:2]) == response[2] and _crc8(response[3:5]) == response[5]
    return (
        ProbeResult.match({"serial": (response[0:2] + response[3:5]).hex()})
        if valid
        else ProbeResult.no_match()
    )

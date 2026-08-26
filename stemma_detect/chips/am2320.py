from stemma_detect.result import Confidence, ProbeResult, ProbeRisk

ADDRESSES = (0x5C,)
PACKAGE = "adafruit-circuitpython-am2320"
PROBE_CONFIDENCE = Confidence.MATCH
PROBE_RISK = ProbeRisk.COMMAND


def _crc16(data):
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = (crc >> 1) ^ 0xA001 if crc & 1 else crc >> 1
    return crc


def probe(bus, address):
    try:
        bus.write(address, b"\x00")
    except OSError:
        # AM2320 commonly NACKs its wake-up write while leaving sleep mode.
        pass
    response = bus.write_then_read(address, b"\x03\x08\x07", 11, delay_ms=2)
    evidence = {"identity": response.hex().upper()}
    if (
        response[:2] == b"\x03\x07"
        and response[2:9] not in (b"\x00" * 7, b"\xff" * 7)
        and int.from_bytes(response[-2:], "little") == _crc16(response[:-2])
    ):
        return ProbeResult.match(evidence, score=14, max_score=14)
    return ProbeResult.no_match(evidence, score=0, max_score=14)

from stemma_detect.result import Confidence, ProbeResult, ProbeRisk

ADDRESSES = (0x0B,)
PACKAGE = "adafruit-circuitpython-lc709203f"
PROBE_CONFIDENCE = Confidence.MATCH
PROBE_RISK = ProbeRisk.REGISTER


def _crc8(data):
    crc = 0
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = ((crc << 1) ^ 0x07) if crc & 0x80 else crc << 1
            crc &= 0xFF
    return crc


def _read_word(bus, address, register):
    response = bus.read_register(address, register, 3)
    pec_input = bytes((address << 1, register, (address << 1) | 1)) + response[:2]
    if len(response) != 3 or _crc8(pec_input) != response[2]:
        return None
    return int.from_bytes(response[:2], "little")


def probe(bus, address):
    # Parameter Number has two documented immutable values. Validate SMBus PEC
    # on it and the independent IC Version register.
    parameter = _read_word(bus, address, 0x1A)
    if parameter not in (0x0301, 0x0504):
        return ProbeResult.no_match({"failed": "parameter_number"}, score=0, max_score=14)

    version = _read_word(bus, address, 0x11)
    if version in (None, 0x0000, 0xFFFF):
        return ProbeResult.no_match({"failed": "ic_version"}, score=9, max_score=14)
    return ProbeResult.match(
        {
            "parameter_number": f"0x{parameter:04X}",
            "ic_version": f"0x{version:04X}",
            "signature": "14/14",
        },
        score=14,
        max_score=14,
    )

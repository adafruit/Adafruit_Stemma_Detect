from stemma_detect.result import Confidence, ProbeResult, ProbeRisk

ADDRESSES = (0x76,)
PACKAGE = "adafruit-circuitpython-ms8607"
PROBE_CONFIDENCE = Confidence.MATCH
PROBE_RISK = ProbeRisk.COMMAND

_HUMIDITY_ADDRESS = 0x40
_PROM_COMMANDS = range(0xA0, 0xAE, 2)


def _crc4(words: tuple[int, ...], *, crc_word: int, crc_mask: int) -> int:
    """Return the MS8607 PROM CRC-4 for seven 16-bit words."""

    data = list(words) + [0]
    data[crc_word] &= crc_mask
    remainder = 0
    for byte_index in range(16):
        word = data[byte_index // 2]
        remainder ^= word & 0xFF if byte_index & 1 else word >> 8
        for _ in range(8):
            if remainder & 0x8000:
                remainder = (remainder << 1) ^ 0x3000
            else:
                remainder <<= 1
            remainder &= 0xFFFF
    return (remainder >> 12) & 0x0F


def _read_prom(bus, address: int) -> tuple[int, ...]:
    return tuple(
        int.from_bytes(bus.write_then_read(address, bytes((command,)), 2), "big")
        for command in _PROM_COMMANDS
    )


def _not_blank(words: tuple[int, ...]) -> bool:
    return any(word != 0x0000 for word in words) and any(word != 0xFFFF for word in words)


def probe(bus, address: int) -> ProbeResult:
    pressure_prom = _read_prom(bus, address)
    humidity_prom = _read_prom(bus, _HUMIDITY_ADDRESS)
    pressure_crc = pressure_prom[0] >> 12
    humidity_crc = humidity_prom[6] & 0x0F
    pressure_valid = (
        _not_blank(pressure_prom)
        and _crc4(pressure_prom, crc_word=0, crc_mask=0x0FFF) == pressure_crc
    )
    humidity_valid = (
        _not_blank(humidity_prom)
        and _crc4(humidity_prom, crc_word=6, crc_mask=0xFFF0) == humidity_crc
    )
    evidence = {
        "pressure_prom_crc": "valid" if pressure_valid else "invalid",
        "humidity_prom_crc": "valid" if humidity_valid else "invalid",
    }
    if pressure_valid and humidity_valid:
        return ProbeResult.match(evidence, score=18, max_score=18)
    return ProbeResult.no_match(evidence, score=0, max_score=18)

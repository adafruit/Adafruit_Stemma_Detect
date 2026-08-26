"""Small shared validators for Sensirion command responses."""


def crc8(data: bytes) -> int:
    """Return Sensirion CRC-8 (polynomial 0x31, initial value 0xFF)."""

    crc = 0xFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = ((crc << 1) ^ 0x31) if crc & 0x80 else crc << 1
            crc &= 0xFF
    return crc


def valid_crc_words(response: bytes) -> bool:
    """Validate one or more two-byte words followed by individual CRC bytes."""

    return (
        bool(response)
        and len(response) % 3 == 0
        and all(
            crc8(response[offset : offset + 2]) == response[offset + 2]
            for offset in range(0, len(response), 3)
        )
    )


def crc_payload(response: bytes) -> bytes:
    """Remove the CRC byte following each two-byte response word."""

    return b"".join(response[offset : offset + 2] for offset in range(0, len(response), 3))


def valid_nonblank_crc_words(response: bytes) -> bool:
    """Validate CRC words containing factory data rather than blank storage."""

    if not valid_crc_words(response):
        return False
    payload = crc_payload(response)
    return payload not in (bytes(len(payload)), b"\xff" * len(payload))

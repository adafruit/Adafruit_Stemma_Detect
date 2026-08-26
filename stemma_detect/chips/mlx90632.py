from stemma_detect.result import Confidence, ProbeResult, ProbeRisk

ADDRESSES = (0x3A,)
PACKAGE = "adafruit-circuitpython-mlx90632"
PROBE_CONFIDENCE = Confidence.MATCH
PROBE_RISK = ProbeRisk.COMMAND


def _read_register(bus, address, register, length=2):
    return bus.write_then_read(address, register.to_bytes(2, "big"), length)


def probe(bus, address):
    product_id = _read_register(bus, address, 0x2405, 6)
    if product_id in (bytes(6), b"\xff" * 6):
        return ProbeResult.no_match({"failed": "product_id"}, score=0, max_score=14)

    product_code = int.from_bytes(_read_register(bus, address, 0x2409), "big")
    # Bits 15:10 are reserved; bits 6:0 encode a documented accuracy class.
    if product_code & 0xFC00 or product_code & 0x7F not in (1, 2):
        return ProbeResult.no_match({"failed": "product_code"}, score=6, max_score=14)

    eeprom_version = int.from_bytes(_read_register(bus, address, 0x240B), "big")
    if eeprom_version in (0x0000, 0xFFFF):
        return ProbeResult.no_match({"failed": "eeprom_version"}, score=11, max_score=14)

    return ProbeResult.match(
        {
            "product_id": "0x" + product_id.hex().upper(),
            "product_code": f"0x{product_code:04X}",
            "eeprom_version": f"0x{eeprom_version:04X}",
            "signature": "14/14",
        },
        score=14,
        max_score=14,
    )

from stemma_detect.result import Confidence, ProbeResult

ADDRESSES = (0x5A,)
PACKAGE = "adafruit-circuitpython-mlx90614"
PROBE_CONFIDENCE = Confidence.MATCH


def _pec(data):
    crc = 0
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = ((crc << 1) ^ 0x07) & 0xFF if crc & 0x80 else (crc << 1) & 0xFF
    return crc


def probe(bus, address):
    words = []
    for register in range(0x3C, 0x40):
        response = bus.read_register(address, register, 3)
        pec_input = bytes((address << 1, register, address << 1 | 1)) + response[:2]
        if len(response) != 3 or _pec(pec_input) != response[2]:
            return ProbeResult.no_match({"failed": f"id_{register - 0x3B}"}, score=0, max_score=16)
        words.append(response[:2])

    identity = b"".join(words)
    evidence = {"factory_id": identity.hex().upper()}
    if identity in (b"\x00" * 8, b"\xff" * 8):
        return ProbeResult.no_match(evidence, score=0, max_score=16)
    return ProbeResult.match(evidence, score=16, max_score=16)

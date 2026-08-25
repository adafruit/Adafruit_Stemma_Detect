from stemma_detect.result import Confidence, ProbeResult, ProbeRisk

ADDRESSES = (0x64,)
PACKAGE = "adafruit-circuitpython-stcc4"
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
    response = bus.write_then_read(address, b"\x36\x5b", 6)
    if len(response) != 6:
        return ProbeResult.no_match()
    if _crc8(response[0:2]) != response[2] or _crc8(response[3:5]) != response[5]:
        return ProbeResult.no_match()
    product_id = int.from_bytes(response[0:2] + response[3:5], "big")
    return (
        ProbeResult.match({"product_id": "0x0901018A"})
        if product_id == 0x0901018A
        else ProbeResult.no_match()
    )

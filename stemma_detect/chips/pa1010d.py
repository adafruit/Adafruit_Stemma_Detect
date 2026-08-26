from stemma_detect.result import Confidence, ProbeResult

ADDRESSES = (0x10,)
PACKAGE = "adafruit-circuitpython-gps"
PROBE_CONFIDENCE = Confidence.MATCH


def _valid_nmea_sentence(data: bytes) -> bytes | None:
    search_from = 0
    while True:
        start = data.find(b"$", search_from)
        if start < 0:
            return None
        star = data.find(b"*", start + 1)
        if star < 0 or star + 2 >= len(data):
            return None
        payload = data[start + 1 : star]
        try:
            expected = int(data[star + 1 : star + 3], 16)
        except ValueError:
            search_from = start + 1
            continue
        checksum = 0
        for value in payload:
            checksum ^= value
        if checksum == expected and b"," in payload and len(payload.split(b",", 1)[0]) == 5:
            return data[start : star + 3]
        search_from = start + 1


def probe(bus, address):
    data = bus.read(address, 128)
    sentence = _valid_nmea_sentence(data)
    if sentence is None:
        return ProbeResult.no_match({"nmea_checksum": "not detected"}, score=0, max_score=12)
    sentence_type = sentence[1:6].decode("ascii", errors="replace")
    return ProbeResult.match(
        {"nmea_checksum": "valid", "sentence_type": sentence_type},
        score=12,
        max_score=12,
    )

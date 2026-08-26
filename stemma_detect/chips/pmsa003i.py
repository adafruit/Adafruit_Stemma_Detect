from stemma_detect.result import Confidence, ProbeResult, ProbeRisk

ADDRESSES = (0x12,)
PACKAGE = "adafruit-circuitpython-pm25"
PROBE_CONFIDENCE = Confidence.MATCH
PROBE_RISK = ProbeRisk.PASSIVE


def probe(bus, address):
    """Validate one complete Plantower data frame without changing sensor state."""

    frame = bus.read(address, 32)
    evidence = {}
    score = 0
    max_score = 12

    if len(frame) != 32 or frame[:2] != b"BM":
        return ProbeResult.no_match({"failed": "frame_header"}, score=score, max_score=max_score)
    score += 4

    frame_length = int.from_bytes(frame[2:4], "big")
    evidence["frame_length"] = str(frame_length)
    if frame_length != 28:
        return ProbeResult.no_match(
            evidence | {"failed": "frame_length"}, score=score, max_score=max_score
        )
    score += 3

    expected_checksum = int.from_bytes(frame[30:32], "big")
    actual_checksum = sum(frame[:30]) & 0xFFFF
    if actual_checksum != expected_checksum:
        return ProbeResult.no_match(
            evidence | {"failed": "checksum"}, score=score, max_score=max_score
        )
    score += 5
    evidence["signature"] = f"{score}/{max_score}"
    return ProbeResult.match(evidence, score=score, max_score=max_score)

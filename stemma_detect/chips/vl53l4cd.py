from stemma_detect.result import Confidence, ProbeResult, ProbeRisk

ADDRESSES = (0x29,)
PACKAGE = "adafruit-circuitpython-vl53l4cd"
PROBE_CONFIDENCE = Confidence.MATCH
PROBE_RISK = ProbeRisk.COMMAND


def probe(bus, address):
    model_info = bus.write_then_read(address, b"\x01\x0f", 2)
    return (
        ProbeResult.match({"model_id": "0xEBAA"})
        if model_info == b"\xeb\xaa"
        else ProbeResult.no_match()
    )

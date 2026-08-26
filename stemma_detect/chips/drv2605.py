from stemma_detect.result import Confidence, ProbeResult

ADDRESSES = (0x5A,)
PACKAGE = "adafruit-circuitpython-drv2605"
PROBE_CONFIDENCE = Confidence.MATCH
NAMES = {
    3: "drv2605",
    7: "drv2605l",
}


def probe(bus, address):
    status = bus.read_register(address, 0x00, 1)[0]
    device_id = status >> 5
    evidence = {
        "device_id": f"0x{device_id:X}",
        "status": f"0x{status:02X}",
    }
    if device_id in NAMES:
        return ProbeResult.match(
            evidence,
            name=NAMES[device_id],
            score=10,
            max_score=10,
        )
    return ProbeResult.no_match(evidence, score=0, max_score=10)

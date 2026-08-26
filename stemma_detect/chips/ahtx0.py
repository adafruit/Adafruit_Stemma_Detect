from stemma_detect.result import Confidence, ProbeResult

# The AHT10 and AHT20 share this address, status format, and CircuitPython driver.
ADDRESSES = (0x38,)
PACKAGE = "adafruit-circuitpython-ahtx0"
PROBE_CONFIDENCE = Confidence.POSSIBLE


def probe(bus, address):
    status = bus.read(address, 1)[0]
    return ProbeResult.possible(
        {"status": f"0x{status:02X}"},
        score=1,
        max_score=1,
    )

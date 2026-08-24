from stemma_detect.result import Confidence, ProbeResult

ADDRESSES = (0x38,)
PACKAGE = "adafruit-circuitpython-ahtx0"
PROBE_CONFIDENCE = Confidence.POSSIBLE
PRODUCT_URL = "https://www.adafruit.com/product/4566"


def probe(bus, address):
    status = bus.read(address, 1)[0]
    return ProbeResult.possible({"status": f"0x{status:02X}"})

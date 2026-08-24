from stemma_detect.result import Confidence, ProbeResult

ADDRESSES = tuple(range(0x48, 0x50))
PACKAGE = "adafruit-circuitpython-pcf8591"
PROBE_CONFIDENCE = Confidence.POSSIBLE
PRODUCT_URL = "https://www.adafruit.com/product/4648"


def probe(bus, address):
    # The PCF8591 has no identity register. A successful read confirms only
    # that something responded at one of its possible addresses.
    value = bus.read(address, 1)[0]
    return ProbeResult.possible({"conversion": f"0x{value:02X}"})

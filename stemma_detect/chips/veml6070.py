from stemma_detect.result import Confidence, ProbeResult

ADDRESSES = (0x38,)
PACKAGE = "adafruit-circuitpython-veml6070"
PROBE_CONFIDENCE = Confidence.POSSIBLE


def probe(bus, address):
    # The command address is write-only; an empty transaction confirms that it
    # ACKs without changing configuration.
    bus.write(address, b"")
    low = bus.read(0x39, 1)
    high = bus.read(0x3B, 1)
    return ProbeResult.possible(
        {"uv_raw": f"0x{high[0]:02X}{low[0]:02X}"},
        score=6,
        max_score=8,
    )

from stemma_detect.result import Confidence, ProbeResult

ADDRESSES = (0x46, 0x47)
PACKAGE = "adafruit-circuitpython-bmp5xx"
PROBE_CONFIDENCE = Confidence.MATCH
NAMES = {
    0x51: "bmp585",
}


def probe(bus, address):
    chip_id = bus.read_register(address, 0x01, 1)
    if chip_id not in (b"\x50", b"\x51"):
        return ProbeResult.no_match()
    return ProbeResult.match(
        {"chip_id": f"0x{chip_id[0]:02X}"},
        name=NAMES.get(chip_id[0]),
    )

from stemma_detect.result import Confidence, ProbeResult

ADDRESSES = (0x76, 0x77)
PACKAGE = "adafruit-circuitpython-bmp3xx"
PROBE_CONFIDENCE = Confidence.MATCH
NAMES = {
    0x50: "bmp388",
    0x60: "bmp390",
}


def probe(bus, address):
    chip_id = bus.read_register(address, 0x00, 1)
    if len(chip_id) != 1 or chip_id[0] not in NAMES:
        return ProbeResult.no_match()
    return ProbeResult.match(
        {"chip_id": f"0x{chip_id[0]:02X}"},
        name=NAMES[chip_id[0]],
    )

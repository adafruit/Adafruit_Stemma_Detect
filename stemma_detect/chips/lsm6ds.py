from stemma_detect.result import Confidence, ProbeResult

ADDRESSES = (0x6A, 0x6B)
PACKAGE = "adafruit-circuitpython-lsm6ds"
PROBE_CONFIDENCE = Confidence.MATCH
NAMES = {
    0x6B: "ism330dhcx",
}


def probe(bus, address):
    chip_id = bus.read_register(address, 0x0F, 1)
    if chip_id not in (b"\x69", b"\x6a", b"\x6b", b"\x6c"):
        return ProbeResult.no_match()
    return ProbeResult.match(
        {"chip_id": f"0x{chip_id[0]:02X}"},
        name=NAMES.get(chip_id[0]),
    )

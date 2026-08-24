from stemma_detect.result import Confidence, ProbeResult

ADDRESSES = (0x68, 0x69)
PACKAGE = "adafruit-circuitpython-icm20x"
PROBE_CONFIDENCE = Confidence.MATCH
NAMES = {
    0xE1: "icm20649",
    0xEA: "icm20948",
}


def probe(bus, address):
    device_id = bus.read_register(address, 0x00, 1)
    if len(device_id) != 1 or device_id[0] not in NAMES:
        return ProbeResult.no_match()
    return ProbeResult.match(
        {"device_id": f"0x{device_id[0]:02X}"},
        name=NAMES[device_id[0]],
    )

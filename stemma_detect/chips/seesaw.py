from stemma_detect.result import Confidence, ProbeResult, ProbeRisk

# Known defaults used by Adafruit seesaw products. Addresses 0x37 and 0x3B
# are common alternates used to place a second rotary encoder or arcade board
# on the same bus.
ADDRESSES = (0x2E, 0x30, 0x36, 0x37, 0x3A, 0x3B, 0x49, 0x50, 0x5E)
DEFAULT_ADDRESSES = (0x2E, 0x30, 0x36, 0x3A, 0x49, 0x50, 0x5E)
PACKAGE = "adafruit-circuitpython-seesaw"
PROBE_CONFIDENCE = Confidence.MATCH
PROBE_RISK = ProbeRisk.COMMAND

HARDWARE_IDS = {
    0x46,  # ATtiny416
    0x55,  # SAMD09
    0x84,  # ATtiny806
    0x85,  # ATtiny807
    0x86,  # ATtiny816
    0x87,  # ATtiny817
    0x88,  # ATtiny1616
    0x89,  # ATtiny1617
}
PRODUCT_NAMES = {
    5681: "attiny816_seesaw",
    5690: "attiny1616_seesaw",
    5743: "mini_gamepad",
}


def probe(bus, address):
    hardware_id = bus.write_then_read(address, b"\x00\x01", 1, delay_ms=8)[0]
    version = int.from_bytes(
        bus.write_then_read(address, b"\x00\x02", 4, delay_ms=8),
        "big",
    )
    product_id = version >> 16
    evidence = {
        "hardware_id": f"0x{hardware_id:02X}",
        "product_id": str(product_id),
        "firmware_version": f"0x{version & 0xFFFF:04X}",
    }
    if hardware_id in HARDWARE_IDS and version not in (0, 0xFFFFFFFF):
        return ProbeResult.match(
            evidence,
            name=PRODUCT_NAMES.get(product_id),
            score=14,
            max_score=14,
        )
    return ProbeResult.no_match(evidence, score=0, max_score=14)

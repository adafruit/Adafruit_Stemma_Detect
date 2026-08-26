from stemma_detect.result import Confidence, ProbeResult

ADDRESSES = (0x15,)
PACKAGE = "adafruit-circuitpython-cst8xx"
PROBE_CONFIDENCE = Confidence.MATCH

CHIP_ID_NAMES = {
    0xB4: "cst816s",
    0xB5: "cst816t",
    0xB6: "cst816d",
    0xB7: "cst820",
}
CHIP_TYPE_NAMES = {
    0x11: "cst826",
    0x13: "cst836",
}


def probe(bus, address):
    # Firmware version through chip type, matching the official driver's
    # non-destructive constructor-time identity read.
    identity = bus.read_register(address, 0xA6, 6)
    chip_id = identity[1]
    chip_type = identity[5]
    firmware_present = identity[2] != 0 or identity[3] != 0
    name = CHIP_ID_NAMES.get(chip_id) or CHIP_TYPE_NAMES.get(chip_type)
    evidence = {
        "firmware_version": f"0x{identity[0]:02X}",
        "chip_id": f"0x{chip_id:02X}",
        "model_id": f"0x{identity[2]:02X}",
        "project_id": f"0x{identity[3]:02X}",
        "chip_type": f"0x{chip_type:02X}",
    }

    # Some newer CST8xx controllers report zero in the legacy chip-ID
    # register; model/project data is the official driver's fallback.
    if name is not None or (chip_id == 0 and firmware_present):
        return ProbeResult.match(
            evidence,
            name=name,
            score=16,
            max_score=16,
        )
    return ProbeResult.no_match(evidence, score=0, max_score=16)

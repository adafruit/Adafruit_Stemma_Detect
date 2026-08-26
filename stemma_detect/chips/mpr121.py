from stemma_detect.result import Confidence, ProbeResult

ADDRESSES = tuple(range(0x5A, 0x5E))
DEFAULT_ADDRESSES = (0x5A,)
PACKAGE = "adafruit-circuitpython-mpr121"
PROBE_CONFIDENCE = Confidence.POSSIBLE


def probe(bus, address):
    touch_status = int.from_bytes(bus.read_register(address, 0x00, 2), "little")
    filtered_data = bus.read_register(address, 0x04, 24)
    electrode_config = bus.read_register(address, 0x5E, 1)[0]
    readings = tuple(
        int.from_bytes(filtered_data[offset : offset + 2], "little")
        for offset in range(0, len(filtered_data), 2)
    )
    evidence = {
        "touch_status": f"0x{touch_status:04X}",
        "electrode_count": str(electrode_config & 0x0F),
    }
    # Only 12 touch bits and 10 data bits per electrode are implemented. The
    # low ECR nibble selects at most 12 enabled electrodes.
    if touch_status & 0xF000 or any(reading > 0x03FF for reading in readings):
        return ProbeResult.no_match(evidence, score=0, max_score=10)
    if electrode_config & 0x0F > 12:
        return ProbeResult.no_match(evidence, score=0, max_score=10)
    return ProbeResult.possible(evidence, score=8, max_score=10)

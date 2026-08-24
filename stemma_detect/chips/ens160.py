from stemma_detect.result import Confidence, ProbeResult

ADDRESSES = (0x52, 0x53)
PACKAGE = "adafruit-circuitpython-ens160"
PROBE_CONFIDENCE = Confidence.MATCH


def probe(bus, address):
    part_id = bus.read_register(address, 0x00, 2)
    if part_id not in (b"\x60\x01", b"\x61\x01"):
        return ProbeResult.no_match()
    return ProbeResult.match({"part_id": f"0x{int.from_bytes(part_id, 'little'):04X}"})

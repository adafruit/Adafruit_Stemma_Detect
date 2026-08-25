from stemma_detect.result import ProbeResult, ProbeRisk


def address_read_probe(bus, address):
    """Confirm an address responds without claiming a unique identity."""
    response = bus.read(address, 1)
    return ProbeResult.possible({"response": f"0x{response[0]:02X}"})


address_read_probe.probe_risk = ProbeRisk.PASSIVE

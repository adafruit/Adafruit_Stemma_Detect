from stemma_detect.result import Confidence, ProbeResult, ProbeRisk

ADDRESSES = (0x49,)
PACKAGE = "adafruit-circuitpython-as726x"
PROBE_CONFIDENCE = Confidence.MATCH
PROBE_RISK = ProbeRisk.COMMAND

_STATUS_REGISTER = 0x00
_WRITE_REGISTER = 0x01
_READ_REGISTER = 0x02
_TX_VALID = 0x02
_RX_VALID = 0x01
_MAX_POLLS = 20


def _virtual_read(bus, address, register):
    for _ in range(_MAX_POLLS):
        if not bus.read_register(address, _STATUS_REGISTER, 1)[0] & _TX_VALID:
            break
    else:
        raise RuntimeError("AS726x virtual register write remained busy")

    bus.write(address, bytes((_WRITE_REGISTER, register)))
    for _ in range(_MAX_POLLS):
        if bus.read_register(address, _STATUS_REGISTER, 1)[0] & _RX_VALID:
            return bus.read_register(address, _READ_REGISTER, 1)[0]
    raise RuntimeError("AS726x virtual register read timed out")


def probe(bus, address):
    device_type = _virtual_read(bus, address, 0x00)
    hardware_version = _virtual_read(bus, address, 0x01)
    evidence = {
        "device_type": f"0x{device_type:02X}",
        "hardware_version": f"0x{hardware_version:02X}",
    }
    if (device_type, hardware_version) == (0x40, 0x3E):
        return ProbeResult.match(evidence, score=14, max_score=14)
    return ProbeResult.no_match(evidence, score=0, max_score=14)

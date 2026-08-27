from stemma_detect.result import Confidence, ProbeResult

ADDRESSES = tuple(range(0x68, 0x70))
DEFAULT_ADDRESSES = (0x68,)
PACKAGE = "adafruit-circuitpython-mcp3421"
PROBE_CONFIDENCE = Confidence.POSSIBLE


def _has_repeated_sign_bits(value, mask):
    return value & mask in (0, mask)


def probe(bus, address):
    # The MCP3421 appends its configuration byte to conversion data and keeps
    # repeating it if the controller clocks additional bytes.
    response = bus.read(address, 4)
    evidence = {"conversion_frame": "0x" + response.hex().upper()}
    if len(response) != 4:
        return ProbeResult.no_match(evidence, score=0, max_score=10)

    config = response[3]
    resolution = config >> 2 & 0x03
    valid = config & 0x60 == 0
    if resolution == 3:  # 18-bit: three data bytes, then configuration
        valid &= _has_repeated_sign_bits(response[0], 0xFC)
    else:  # 12/14/16-bit: two data bytes, then repeated configuration
        sign_mask = (0xF0, 0xC0, 0x00)[resolution]
        valid &= response[2] == config
        valid &= not sign_mask or _has_repeated_sign_bits(response[0], sign_mask)

    evidence["config"] = f"0x{config:02X}"
    if not valid:
        return ProbeResult.no_match(evidence, score=0, max_score=10)
    return ProbeResult.possible(evidence, score=8, max_score=10)

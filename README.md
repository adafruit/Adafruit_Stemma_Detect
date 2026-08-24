# Adafruit STEMMA Detect

Detect selected Adafruit STEMMA QT sensors on a Raspberry Pi and optionally install their CircuitPython drivers.

This project is currently an alpha proof of concept. It recognizes only sensors with bundled probe modules; it is not a universal I²C device identifier.

Each sensor definition contains only:

- `ADDRESSES`
- `PACKAGE`
- `PROBE_CONFIDENCE`
- `probe(bus, address)`
- optional `PRODUCT_URL`

The scanner uses `smbus2` for I²C access and Adafruit Python Shell for prompts and streaming installation commands. Individual CircuitPython drivers are imported neither by the scanner nor by chip definitions.

## Run from a checkout

```sh
python3 -m venv --system-site-packages .venv
.venv/bin/python -m pip install -e .
.venv/bin/stemma-scan --bus 1
```

Use `--install` to install drivers for definitive matches:

```sh
.venv/bin/stemma-scan --bus 1 --install
```

Address-only or otherwise ambiguous results are reported but not installed.

To be prompted before installing a driver for each possible match, use:

```sh
.venv/bin/stemma-scan --bus 1 --install --prompt-possible-matches
```

Possible matches default to “no.” This is important because several unrelated devices can share the same I²C address.

The complete scan finishes before any prompts are shown. Definitive-capable probes run before possible-only probes at each address. A definitive match claims its I²C address immediately, so possible-only candidates are neither probed nor presented. If no definitive probe matches, the possible candidates are collected. A declined candidate is removed from the results; once one is confirmed, it is retained and all remaining candidates at that address are removed without further prompts.

## Supported sensors so far

- AHT20 (possible match only)
- BME280
- BMP280
- PCF8591 (possible match only)
- SHT4x family
- VL6180X

## Add a sensor

Add one module under `stemma_detect/chips/`. Modules are discovered automatically, so no registry edit is needed.

```python
from stemma_detect.result import Confidence, ProbeResult

ADDRESSES = (0x44,)
PACKAGE = "adafruit-circuitpython-example"
PROBE_CONFIDENCE = Confidence.MATCH
PRODUCT_URL = "https://www.adafruit.com/product/1234"


def probe(bus, address):
    value = bus.read_register(address, 0x00, 1)
    return ProbeResult.match({"id": value.hex()}) if value == b"\x12" else ProbeResult.no_match()
```

Keep probes short, non-destructive, and independent of the package they are intended to install.

## Development

```sh
python3 -m unittest discover -s tests -v
ruff check .
ruff format --check .
```

See [CONTRIBUTING.md](CONTRIBUTING.md) before adding a sensor or opening a pull request.

## License

MIT, see [LICENSE](LICENSE).

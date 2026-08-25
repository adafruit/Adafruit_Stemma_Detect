Introduction
============

.. image:: https://readthedocs.org/projects/adafruit-stemma-detect/badge/?version=latest
    :target: https://circuitpython.readthedocs.io/projects/stemma-detect/en/latest/
    :alt: Documentation Status

.. image:: https://img.shields.io/discord/327254708534116352.svg
    :target: https://adafru.it/discord
    :alt: Discord

.. image:: https://github.com/adafruit/Adafruit_Stemma_Detect/workflows/Build%20CI/badge.svg
    :target: https://github.com/adafruit/Adafruit_Stemma_Detect/actions
    :alt: Build Status

.. image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
    :target: https://github.com/astral-sh/ruff
    :alt: Code Style: Ruff

Detect selected Adafruit STEMMA QT sensors on a Raspberry Pi and optionally install their CircuitPython drivers.
This project is currently an alpha proof of concept. It recognizes only sensors with bundled probe modules; it is not a universal I²C device identifier.

Each sensor definition contains only:

- `ADDRESSES`
- `DEFAULT_ADDRESSES` (optional for configurable-address sensors)
- `PACKAGE`
- `PROBE_CONFIDENCE`
- `PROBE_RISK` (optional for probes that send multi-byte addresses or commands)
- `probe(bus, address)`

The scanner uses `smbus2` for I²C access and Adafruit Python Shell for prompts and streaming installation commands. Individual CircuitPython drivers are imported neither by the scanner nor by chip definitions.

Dependencies
=============
This driver depends on:

* `Adafruit Python Shell <https://github.com/adafruit/Adafruit_Python_Shell>`_


Installing from PyPI
=====================

On supported GNU/Linux systems like the Raspberry Pi, you can install the driver locally `from
PyPI <https://pypi.org/project/adafruit-stemma-detect/>`_. To install for current user:

.. code-block:: shell

    pip3 install adafruit-stemma-detect

To install system-wide (this may be required in some cases):

.. code-block:: shell

    sudo pip3 install adafruit-stemma-detect

To install in a virtual environment in your current project:

.. code-block:: shell

    mkdir project-name && cd project-name
    python3 -m venv .env
    source .env/bin/activate
    pip3 install adafruit-stemma-detect

Running from a checkout
=======================

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

Possible candidates using their default address are prompted before candidates using an alternate
address. The prompt labels the address as default or alternate when that information is known.

Diagnostics
===========

Use ``--diagnostics`` to show every probe attempted, including its safety category, non-matches,
and I²C errors that are hidden during a normal scan:

```sh
.venv/bin/stemma-scan --bus 1 --diagnostics
```

An address that does not acknowledge an I²C transaction is reported as ``NOT DETECTED``. The
``ERROR`` label is reserved for unexpected failures. Successful transactions include their raw
write and read bytes so new or mismatched identity probes can be investigated without changing the
chip module.

Definitive probes run before possible-only probes at each address. Within each category, probes are
ordered from lowest to highest risk: passive reads, ordinary one-byte register reads, then commands
or multi-byte register addressing. A definitive match prevents all remaining probes from touching
that address.

Supported sensors so far
========================

The catalog currently contains 88 sensor definitions: 42 with definitive probes and 46 that
produce possible matches. Possible matches are never installed without
``--prompt-possible-matches`` and user confirmation.

Sensors with definitive probes include ADT7410, APDS9960, APDS9999, AS7341, BME280, BME680, BMP280,
BMP3xx, BMP5xx, BNO055, CCS811, DPS310, ENS160, HTS221, ICM20x, INA228, INA237/INA238,
INA260, LIS2MDL, LIS331, LIS3DH, LIS3MDL, LSM6DS, LTR329/LTR303, LTR390, MAX1704x, MCP9600, MCP9808,
MMC5603, MPU6050, MSA301, QMC5883P, SHT4x, STCC4, TCS34725, TMP117/TMP119, TSL2591,
VCNL4040, VL53L0X, VL53L1X, VL53L4CD, and VL6180X.

Possible-match definitions include ADXL34x, ADXL37x, AHT20, AS5600, AS7331,
BH1750, BNO08x, DS3502, HDC302x, HTU31D, INA219, LC709203F, LPS2x, LPS28, LPS35HW,
LSM303 accelerometer, LSM9DS1, MCP3421, MLX90393, MLX90632, MLX90640, MPR121,
MPRLS, MS8607, OPT4048, PA1010D, PCF8591, PCT2075, PMSA003I, SCD30, SCD4x, SEN6x,
SGP30, SGP40, SGP41, SHT31D, SHTC3, Si7021, SPA06-003, STHS34PF80, TLV493D, TSC2007,
VCNL4020, VCNL4030, VCNL4200, and VEML7700.

Adding a sensor
===============

Add one module under `stemma_detect/chips/`. Modules are discovered automatically, so no registry edit is needed.

```python
from stemma_detect.result import Confidence, ProbeResult, ProbeRisk

ADDRESSES = (0x44,)
DEFAULT_ADDRESSES = (0x44,)  # Optional; single addresses are defaults automatically.
PACKAGE = "adafruit-circuitpython-example"
PROBE_CONFIDENCE = Confidence.MATCH
PROBE_RISK = ProbeRisk.COMMAND  # Only needed for command or multi-byte-address probes.


def probe(bus, address):
    value = bus.read_register(address, 0x00, 1)
    return ProbeResult.match({"id": value.hex()}) if value == b"\x12" else ProbeResult.no_match()
```

Keep probes short, non-destructive, and independent of the package they are intended to install.
Most identity-register probes should omit ``PROBE_RISK`` and use the default register category.
Address-only definitions automatically use the passive category. Set ``ProbeRisk.COMMAND`` when a
probe transmits a command or a multi-byte register address that another chip could interpret as a
write.
Family probes may pass `name` to `ProbeResult.match()` when an identity register distinguishes a
specific chip. Ambiguous IDs should remain at the family level.

Development
===========

```sh
python3 -m unittest discover -s tests -v
ruff check .
ruff format --check .
```

Contributing
============

Contributions are welcome! Please read our `Code of Conduct
<https://github.com/adafruit/Adafruit_Stemma_Detect/blob/master/CODE_OF_CONDUCT.md>`_
before contributing to help this project stay welcoming

License
=======

MIT, see [LICENSE](LICENSE).

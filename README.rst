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

- ``ADDRESSES``
- ``DEFAULT_ADDRESSES`` (optional for configurable-address sensors)
- ``PACKAGE``
- ``PROBE_CONFIDENCE``
- ``PROBE_RISK`` (optional for probes that send multi-byte addresses or commands)
- ``probe(bus, address)``

Definitions may optionally express a device signature with the helpers in
``stemma_detect.signature``. A signature combines several safe, read-only characteristics, such as
an exact chip ID, reserved-bit patterns, revision values, and nonblank factory calibration data.
Checks carry weights so results can expose both a categorical confidence and an evidence score.

The scanner uses ``smbus2`` for I²C access and Adafruit Python Shell for prompts and streaming installation commands. Individual CircuitPython drivers are imported neither by the scanner nor by chip definitions.

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

.. code-block:: shell

    python3 -m venv --system-site-packages .venv
    .venv/bin/python -m pip install -e .
    .venv/bin/stemma-scan --bus 1

Use ``--install`` to install drivers for definitive matches:

.. code-block:: shell

    .venv/bin/stemma-scan --bus 1 --install

Address-only or otherwise ambiguous results are reported but not installed.

To be prompted before installing a driver for each possible match, use:

.. code-block:: shell

    .venv/bin/stemma-scan --bus 1 --install --prompt-possible-matches

Possible matches default to “no.” This is important because several unrelated devices can share the same I²C address.

The complete scan finishes before any prompts are shown. Definitive-capable probes run before possible-only probes at each address. A definitive match claims its I²C address immediately, so possible-only candidates are neither probed nor presented. If no definitive probe matches, the possible candidates are collected. A declined candidate is removed from the results; once one is confirmed, it is retained and all remaining candidates at that address are removed without further prompts.

Possible candidates using their default address are prompted before candidates using an alternate
address. The prompt labels the address as default or alternate when that information is known.

Multiplexers
============

The scanner automatically looks for PCA9546-compatible four-channel and PCA9548/TCA9548A-compatible
eight-channel multiplexers at ``0x70`` through ``0x77``. Each channel is scanned separately, and
the route is included in every result:

.. code-block:: text

    MUX: PCA9546 at 0x70 (4 channels)
    MATCH: VL53L4CD at 0x29 via mux 0x70 channel 2

No option or CircuitPython multiplexer driver is required. Detection and channel selection use the
project's small I²C bus interface, so this feature does not add Blinka as a dependency.

These multiplexers have no identity register. To reduce false identification, the scanner first
requires a plausible one-byte control value, then verifies that channel-selection writes read back
with the expected four- or eight-channel mask. The original control value is restored after probing
and again after the scan. This is still an active probe: an unrelated device at ``0x70`` through
``0x77`` with mux-like behavior could be changed. One level of multiplexers is currently supported.

Using as a library
==================

``scan_all`` returns structured detections and multiplexer topology without printing, prompting, or
installing drivers. Applications can supply an already-open object implementing
``I2CBusProtocol``, or use the included Linux ``smbus2`` adapter:

.. code-block:: python

    from stemma_detect import I2CBus, discover_chips, scan_all

    with I2CBus(1) as bus:
        report = scan_all(bus, discover_chips())

    for detection in report.detections:
        print(detection.name, detection.address, detection.path)

Diagnostics
===========

Use ``--diagnostics`` to show every probe attempted, including its safety category, non-matches,
and I²C errors that are hidden during a normal scan:

.. code-block:: shell

    .venv/bin/stemma-scan --bus 1 --diagnostics

An address that does not acknowledge an I²C transaction is reported as ``NOT DETECTED``. The
``ERROR`` label is reserved for unexpected failures. Successful transactions include their raw
write and read bytes so new or mismatched identity probes can be investigated without changing the
chip module.

Definitive probes run before possible-only probes at each address. Within each category, probes are
ordered from lowest to highest risk: passive reads, ordinary one-byte register reads, then commands
or multi-byte register addressing. A definitive match prevents all remaining probes from touching
that address.

Known limitations and planned work
==================================

The CLI is a consumer of the same detection API available to other programs. Library imports do not
scan hardware, print, prompt, install packages, or exit the process as a side effect. Diagnostics
and driver installation remain explicit opt-in operations.

The scanner cannot resolve two devices responding at the same address. They may corrupt each
other's identity responses and produce only ambiguous possible matches. Conflicting devices must be
readdressed or placed on separate multiplexer channels. Automatic mux scanning resolves conflicts
between different channels, but it cannot resolve a conflict between a root-bus device and a device
behind the mux, or nested muxes.

Adafruit's `Troublesome Chips guide
<https://learn.adafruit.com/i2c-addresses/troublesome-chips>`_ identifies devices with unusual I²C
behavior that can cause missed detections or communication failures:

- AGS20MA requires a 20--30 kHz bus.
- AM2320 automatically sleeps, making scans unreliable.
- ATECCx08 requires slow I²C communication when waking from sleep.
- BNO055 and BNO085 use clock stretching, can violate timing requirements, and may need resets.
- CCS811 uses clock stretching.
- LC709203F uses repeated starts, clock stretching, and sleep mode.
- Older MCP9600 devices can duplicate register data; MCP9600 and MCP9601 also use repeated starts
  and clock stretching and may ignore zero-length scan writes.
- PN532 uses clock stretching.

The current catalog includes BNO055, BNO08x/BNO085, CCS811, LC709203F, and MCP9600. A failed probe
for one of these chips does not necessarily mean the device is absent. Raspberry Pi users should
also consult Adafruit's `I²C clock stretching guide
<https://learn.adafruit.com/circuitpython-on-raspberrypi-linux/i2c-clock-stretching>`_.

Supported sensors so far
========================

The catalog currently contains 91 sensor definitions: 44 with definitive probes and 47 that
produce possible matches. Possible matches are never installed without
``--prompt-possible-matches`` and user confirmation.

Sensors with definitive probes include ADT7410, APDS9960, APDS9999, AS7341, BME280, BME680, BMP280,
BMP3xx, BMP5xx, BNO055, CCS811, DPS310, ENS160, HTS221, ICM20x, INA228, INA237/INA238,
INA260, INA3221, LIS2MDL, LIS331, LIS3DH, LIS3MDL, LSM6DS, LTR329/LTR303, LTR390, MAX1704x, MCP9600, MCP9808,
MMC5603, MPU6050, MSA301, QMC5883P, SHT4x, STCC4, TCS34725, TMP117/TMP119, TSL2591,
VCNL4040, VEML6075, VL53L0X, VL53L1X, VL53L4CD, and VL6180X.

Possible-match definitions include ADXL34x, ADXL37x, AHT20, AS5600, AS726x, AS7331,
BH1750, BNO08x, DS3502, HDC302x, HTU31D, INA219, LC709203F, LPS2x, LPS28, LPS35HW,
LSM303 accelerometer, LSM9DS1, MCP3421, MLX90393, MLX90632, MLX90640, MPR121,
MPRLS, MS8607, OPT4048, PA1010D, PCF8591, PCT2075, PMSA003I, SCD30, SCD4x, SEN6x,
SGP30, SGP40, SGP41, SHT31D, SHTC3, Si7021, SPA06-003, STHS34PF80, TLV493D, TSC2007,
VCNL4020, VCNL4030, VCNL4200, and VEML7700.

Adding a sensor
===============

Add one module under ``stemma_detect/chips/``. Modules are discovered automatically, so no registry edit is needed.

.. code-block:: python

    from stemma_detect.result import Confidence, ProbeResult, ProbeRisk

    ADDRESSES = (0x44,)
    DEFAULT_ADDRESSES = (0x44,)  # Optional; single addresses are defaults automatically.
    PACKAGE = "adafruit-circuitpython-example"
    PROBE_CONFIDENCE = Confidence.MATCH
    PROBE_RISK = ProbeRisk.COMMAND  # Only for commands or multi-byte addresses.

    def probe(bus, address):
        value = bus.read_register(address, 0x00, 1)
        if value == b"\x12":
            return ProbeResult.match({"id": value.hex()})
        return ProbeResult.no_match()

Keep probes short, non-destructive, and independent of the package they are intended to install.
Most identity-register probes should omit ``PROBE_RISK`` and use the default register category.
Address-only definitions automatically use the passive category. Set ``ProbeRisk.COMMAND`` when a
probe transmits a command or a multi-byte register address that another chip could interpret as a
write.
Family probes may pass ``name`` to ``ProbeResult.match()`` when an identity register distinguishes a
specific chip. Ambiguous IDs should remain at the family level.

When a sensor has several useful read-only registers, prefer a device signature over custom probe
logic:

.. code-block:: python

    from stemma_detect.result import Confidence
    from stemma_detect.signature import DeviceSignature, exact, not_blank

    ADDRESSES = (0x76, 0x77)
    PACKAGE = "adafruit-circuitpython-example"
    PROBE_CONFIDENCE = Confidence.MATCH

    SIGNATURE = DeviceSignature(
        (
            exact("chip_id", 0xD0, b"\x60", show_value=True, weight=10),
            exact(
                "status_reserved",
                0xF3,
                b"\x00",
                mask=b"\xF6",
                required=False,
                weight=2,
            ),
            not_blank("calibration", 0x88, 24, required=False, weight=3),
        ),
        match_threshold=15,
    )

    def probe(bus, address):
        return SIGNATURE.probe(bus, address)

Failure of a required check produces ``NO_MATCH``. Supporting checks contribute weight; missing
supporting evidence lowers the score and may reduce the result to ``POSSIBLE`` without rejecting it.
The scanner adds one weak point for a known default address but never lets that address bonus turn a
possible result into a definitive match. Only definitive ``MATCH`` results are installed
automatically.

Scores represent accumulated evidence, not a statistical probability. Weights should be kept
consistent across definitions: exact identity registers should dominate, while address responses
and default-address bonuses should remain weak evidence.

Only use documented, safe reads: avoid FIFO, read-to-clear, write-only, and command registers.
``not_blank`` is intended for factory-programmed blocks where all-zero and all-``0xFF`` data are
invalid; it should not be used for ordinary configuration or measurement registers.

Development
===========

.. code-block:: shell

    python3 -m unittest discover -s tests -v
    ruff check .
    ruff format --check .

Contributing
============

Contributions are welcome! Please read our `Code of Conduct
<https://github.com/adafruit/Adafruit_Stemma_Detect/blob/master/CODE_OF_CONDUCT.md>`_
before contributing to help this project stay welcoming

License
=======

MIT, see `LICENSE <LICENSE>`_.

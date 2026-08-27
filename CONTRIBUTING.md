# Contributing

Contributions are welcome. Please follow the [Adafruit Community Code of Conduct](CODE_OF_CONDUCT.md).

## Development setup

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -e ".[dev,docs]"
.venv/bin/pre-commit install
```

Before submitting a pull request, run:

```sh
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/python -m unittest discover -s tests -v
```

## Adding a sensor

Add one module to `stemma_detect/chips/`. It must define:

- `ADDRESSES`: valid 7-bit I²C addresses;
- `PACKAGE`: an `adafruit-circuitpython-*` distribution;
- `PROBE_CONFIDENCE`: the strongest result the probe can return;
- `probe(bus, address)`: returns a `ProbeResult`;

Probes must not import the driver they install. Prefer documented, read-only identity registers or commands. Avoid reset, calibration, configuration, measurement, or other state-changing operations. When a device cannot be identified safely, return `ProbeResult.possible()` rather than a definitive match.

Definitive-capable probes run before possible-only probes when devices share an address. A definitive match prevents possible-only candidates at that address from being probed. Otherwise, all possible candidates are collected before prompting. Declined candidates are removed; once one is accepted, it is retained and the remaining candidates at that address are removed without further prompts.

Add unit tests for the expected response and at least one non-matching response. When possible, also test on a Raspberry Pi with the Adafruit STEMMA QT product attached.

## Releases

See [VERSIONING.md](VERSIONING.md) for the versioning policy and release procedure. Releases are
published from GitHub through PyPI Trusted Publishing; do not store a PyPI API token in the
repository.

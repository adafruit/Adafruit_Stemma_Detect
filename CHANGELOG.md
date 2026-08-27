# Changelog

All notable user-visible changes are documented here. This project follows the
versioning policy in [VERSIONING.md](VERSIONING.md).

## [Unreleased]

### Changed

- Strengthened possible-match signatures for DS3502, LIDAR-Lite, MCP3421,
  MLX90395, and TSC2007 using documented register structure, device metadata,
  and conversion framing.

## [0.1.0] - 2026-08-26

Initial public release.

### Added

- Curated detection catalog with 122 Adafruit STEMMA QT-oriented driver definitions.
- Weighted multi-register signatures, CRC validation, family grouping, and explicit
  definitive versus possible results.
- Automatic traversal of nested PCA9546- and PCA9548-compatible I²C multiplexers.
- Command-line scanning, diagnostic transactions, possible-match confirmation, and
  automatic CircuitPython driver installation.
- Versioned JSON scan reports suitable for other programs.
- Public Python API for scanning, inspecting results, confirming expected possible
  matches, planning installations, and receiving structured installation outcomes.
- Raspberry Pi hardware validation and unit coverage for probes, mux traversal,
  serialization, installation, and CLI behavior.

[Unreleased]: https://github.com/makermelissa/Adafruit_Stemma_Detect/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/makermelissa/Adafruit_Stemma_Detect/releases/tag/v0.1.0

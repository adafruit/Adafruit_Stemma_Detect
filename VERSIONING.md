# Versioning policy

Adafruit STEMMA Detect uses [Semantic Versioning](https://semver.org/) and release tags
of the form `vMAJOR.MINOR.PATCH`.

While the project is below version 1.0:

- `MINOR` releases may add features or make necessary public API or JSON schema changes.
- `PATCH` releases contain backward-compatible fixes, catalog additions, and detection
  quality improvements.
- Deprecations should remain available for at least one subsequent minor release when
  practical.

Starting with version 1.0, incompatible public API changes require a major release.
Backward-compatible functionality uses a minor release, and backward-compatible fixes
use a patch release.

The JSON `schema_version` is independent of the package version. It changes only when a
consumer must handle the serialized report differently. A package release that changes
the JSON schema documents that change in the changelog.

## Release procedure

1. Confirm the working tree contains the intended release and all CI jobs pass.
2. Move relevant entries from `Unreleased` into a dated changelog section.
3. Update `stemma_detect/_version.py` and the changelog comparison links.
4. Build the wheel and source distribution, run `twine check`, and inspect their files.
5. Commit the release, create tag `vMAJOR.MINOR.PATCH`, and publish a GitHub release.
6. The release workflow verifies the tag, rebuilds the distributions, and publishes
   using the Adafruit organization's PyPI credentials.
7. Install the exact version from PyPI in a fresh environment and run an import and CLI
   smoke test.

PyPI release files are immutable. If a release is incorrect, publish a new version; do
not attempt to replace an existing file.

## PyPI configuration

The release workflow follows the convention used by Adafruit's other Python repositories
and reads these organization-managed GitHub Actions secrets:

- `pypi_username`
- `pypi_password`

Do not add PyPI credentials as repository secrets or commit them to the repository. Before
the first release, confirm that this repository has access to the Adafruit organization
secrets.

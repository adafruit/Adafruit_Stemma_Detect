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
6. Approve the protected GitHub `pypi` environment deployment. The release workflow
   verifies the tag, rebuilds the distributions, and publishes with PyPI Trusted
   Publishing.
7. Install the exact version from PyPI in a fresh environment and run an import and CLI
   smoke test.

PyPI release files are immutable. If a release is incorrect, publish a new version; do
not attempt to replace an existing file.

## One-time PyPI setup

Before publishing the first release, create a pending GitHub Trusted Publisher at
<https://pypi.org/manage/account/publishing/> with these values:

- PyPI project name: `adafruit-stemma-detect`
- GitHub owner: `makermelissa`
- GitHub repository: `Adafruit_Stemma_Detect`
- Workflow filename: `release.yml`
- Environment name: `pypi`

Create a matching `pypi` environment in the GitHub repository and require a maintainer's
approval before deployment. If the repository is transferred to the Adafruit organization,
update the PyPI Trusted Publisher to match the new GitHub owner before the next release.

# PyPI release workflow and placeholder

The workflow runs on `v*` tag pushes. The build job runs `uv build`, checks that both distribution filenames match the tag version and uploads `dist/`. The publish job downloads that artifact and uses the `pypi` environment with `id-token: write`. Trusted Publishing uses GitHub OIDC and produces PyPI attestations by default. [Release workflow](../../../.github/workflows/release.yml) · [PyPA publishing action](https://github.com/pypa/gh-action-pypi-publish/blob/v1.14.3/README.md#generating-and-uploading-attestations)

| Action | Version | Commit SHA | Release date (UTC) | Source |
| --- | --- | --- | --- | --- |
| `actions/checkout` | `v7.0.1` | `3d3c42e5aac5ba805825da76410c181273ba90b1` | 2026-07-20 | [Release](https://github.com/actions/checkout/releases/tag/v7.0.1) |
| `astral-sh/setup-uv` | `v10.4.0` | `1db35dd8eee11c5894872e0b383ae6c406cf738d` | 2026-11-20 | [Release](https://github.com/astral-sh/setup-uv/releases/tag/v10.4.0) |
| `actions/upload-artifact` | `v7.0.2` | `cf430e030ddbb5b0abf93d22962f4752f3646cd9` | 2026-10-07 | [Release](https://github.com/actions/upload-artifact/releases/tag/v7.0.2) |
| `actions/download-artifact` | `v8.0.2` | `9000827ccba6bdab643e8b6fd33ac0654aef8333` | 2026-10-07 | [Release](https://github.com/actions/download-artifact/releases/tag/v8.0.2) |
| `pypa/gh-action-pypi-publish` | `v1.14.3` | `7245906fb61fa33a13554f9d5fb856fe61758086` | 2026-10-20 | [Release](https://github.com/pypa/gh-action-pypi-publish/releases/tag/v1.14.3) |

Checkout and setup-uv match CI. The PyPA release was over 14 days old on 2026-11-23.

## Placeholder

The standalone `fazit` 0.0.0 project in the scratch directory contains `pyproject.toml`, the message-only CLI in `src/fazit/__init__.py`, a three-line README, the repository licence and a byte-identical copy of `release.yml`. It uses Python 3.12 or later and Hatchling 1.33.0.

`uv build` produced `fazit-0.0.0.tar.gz` and `fazit-0.0.0-py3-none-any.whl`. The installed wheel printed the development message and exited with status 0. The tag check accepted `v0.0.0` and rejected `v0.0.1` against those archives. The generated `dist/` directory was removed.

PyPI publication requires pushing `v0.0.0` to `rouxdutoit/fazit` on a commit containing the placeholder and its workflow.

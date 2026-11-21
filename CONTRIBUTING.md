# Contributing to Befund

Clone the repository and run `uv sync` from its root. The first setup downloads the packages needed to build and test Befund.

Run these checks before submitting a change. Open both reports with the network disconnected.

```sh
uv run ruff check .
uv run ruff format --check .
uv run pytest -q
uv run befund demo --lang de
uv run befund demo --lang en
```

Follow the repository's rules for code, report layout, wording and tests. [AGENTS.md](AGENTS.md)

- Record a new dependency in `DECISIONS.md` before adding it.
- Put every report string and printed message in both locale files. Command and option help stays in English.
- Add workloads, rules and mappings in the YAML files.
- Start each source file that supports comments with `SPDX-License-Identifier: AGPL-3.0-or-later` in its comment syntax.
- Use fictional data in tests and examples. Keep real tenant data out of the repository.
- Preserve the safeguard tests. Changes that weaken them cannot be accepted.

## Licence and sign-off

Contributions are accepted under AGPL-3.0-or-later. Add a `Signed-off-by:` line to every commit with `git commit -s`. This certifies that you meet the Developer Certificate of Origin 1.1. The sign-off is sufficient and no contributor licence agreement is required. [Developer Certificate of Origin](https://developercertificate.org/)

Befund is written with AI assistance. A commit made by a model names the model in a `Co-Authored-By` trailer.

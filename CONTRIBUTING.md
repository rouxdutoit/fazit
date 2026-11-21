# Contributing to Fazit

Clone the repository and run `uv sync` from its root. The first setup downloads the packages needed to build and test Fazit.

Run these checks before submitting a change. Open both reports with the network disconnected.

```sh
uv run ruff check .
uv run ruff format --check .
uv run pytest -q
uv run fazit demo --lang de
uv run fazit demo --lang en
```

Follow the repository's rules for code, report layout, wording and tests. [AGENTS.md](AGENTS.md)

- Record a new dependency in `DECISIONS.md` before adding it.
- Put every report string and printed message in both locale files. Command and option help stays in English.
- Add workloads, rules and mappings in the YAML files.
- Start each source file that supports comments with `SPDX-License-Identifier: AGPL-3.0-or-later` in its comment syntax.
- Use fictional data in tests and examples. Keep real tenant data out of the repository.
- Preserve the safeguard tests. Changes that weaken them cannot be accepted.

## Licence and sign-off

Contributions are accepted under AGPL-3.0-or-later. Starting with the first public release, contributors outside the maintainer team add a `Signed-off-by:` line to each commit with `git commit -s`. This sign-off certifies that the contribution meets the Developer Certificate of Origin 1.1 and is the only certification required. [Developer Certificate of Origin](https://developercertificate.org/)

The maintainers attest that they have the right to distribute the contributions in the initial repository history under AGPL-3.0-or-later.

Fazit is written with AI assistance. Use an `Assisted-by:` trailer to credit Codex and a `Co-Authored-By:` trailer to credit Claude. Name the model in the trailer.

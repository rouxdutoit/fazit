# Contributing to Fazit

Clone the repository and run `uv sync` from its root. The first setup downloads the packages needed to build and test Fazit.

Run these checks before submitting a change. Open both reports with the network disconnected.

```sh
uv run ruff check .
uv run ruff format --check .
uv run pytest -q
uv run fazit demo --lang de
uv run fazit demo --lang en
uv run python site/check_site.py
```

If report output changes, copy the HTML from the two demo runs above to `site/demo/de/index.html` and `site/demo/en/index.html`, using the matching language for each file.

Follow the repository's rules for code, report layout, wording and tests. [AGENTS.md](AGENTS.md)

- Record a new dependency in `DECISIONS.md` before adding it.
- Put every report string and printed message in both locale files. Command and option help stays in English.
- Add workloads, rules and mappings in the YAML files.
- Start each source file that supports comments with `SPDX-License-Identifier: AGPL-3.0-or-later` in its comment syntax.
- Use fictional data in tests and examples. Keep real tenant data out of the repository.
- Preserve the safeguard tests. Changes that weaken them cannot be accepted.

## Translating Fazit

Fazit is built to be translated. French and Italian come next, for organisations in Switzerland. Other European languages are welcome, ideally together with someone who knows the open source stack that public bodies in that country use.

A language is only released after a native speaker has reviewed it. Machine translation is fine for a first draft, never for the release.

1. Open an issue first. Name the language and the native speaker who will review it.
2. Copy `src/fazit/locales/en.yaml` to `src/fazit/locales/<code>.yaml`, using the two-letter ISO 639-1 code, and translate every value. The `format` block sets number, date and money formats. A test fails if a key is missing.
3. Add the language wherever English and German appear side by side in `src/fazit/rules/`: the `en:` and `de:` pairs in `status.yaml`, `risky_file_types.yaml` and the files in `mappings/`.
4. Add the code to `SUPPORTED_LANGUAGES` in `src/fazit/i18n.py` and to the language list in `src/fazit/rules.py`. Add it to the tests that loop over languages.
5. Translate `docs/interview-checklist.md` into `docs/interview-checklist.<code>.md`.
6. Run the checks above, then `uv run fazit demo --lang <code>`. Read the whole report with the reviewer before asking for a merge.

Keep the status names short and consistent: they appear in the readiness bar, the legend and every table. The website follows once the report is released in a language.

## How Fazit is made

Fazit is developed with AI assistance under the direction and responsibility of a human maintainer. Codex (GPT-6.2-Sol, at maximum reasoning) writes the code, and Claude checks every change and runs the tests before it is committed. Before each release, Claude Fable 5.2 and Codex GPT-6.2-Astra review the whole codebase independently, both at maximum effort, including security. Their reports are public. [Phase 1 reviews](https://github.com/rouxdutoit/fazit/tree/main/.planning/phases/01-demo-and-report)

## Licence and sign-off

Contributions are accepted under AGPL-3.0-or-later. Starting with the first public release, contributors outside the maintainer team add a `Signed-off-by:` line to each commit with `git commit -s`. This sign-off certifies that the contribution meets the Developer Certificate of Origin 1.1 and is the only certification required. [Developer Certificate of Origin](https://developercertificate.org/)

The maintainers attest that they have the right to distribute the contributions in the initial repository history under AGPL-3.0-or-later.

Use an `Assisted-by:` trailer to credit Codex and a `Co-Authored-By:` trailer to credit Claude. Name the model in the trailer.

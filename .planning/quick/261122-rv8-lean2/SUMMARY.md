---
quick_id: 261122-rv8
status: complete
date: 2026-11-22
---

# Release review round 2 lean pass

## Plan results

1. Cost lines, subtotals and totals keep exact fraction arithmetic. HTML cost attributes use the same cent rounding as the displayed amounts.
2. JSON and YAML syntax errors name the file and line. Composed YAML nodes identify known fields and lines for duplicate keys, ambiguous scalars, non-finite values and impossible dates. Strict scalar spelling is explicit. `parsing.py` went from 306 to 196 lines.
3. Unrecognised input keys identify the key's line. Input diagnostics omit synthetic paths and protect private key and value text. Scan extensions follow the additive schema in D19.
4. Call sites select the localised error keys explicitly. File-level errors carry no invented field.
5. Input names use one validation check. Six positive assignment rules opt in to partial evidence through `accept_partial_true`. Catalogue validation shares the two cached locale tables. Timestamp comparison uses `datetime` and rejects fractional seconds longer than six digits.
6. The four matrix runners run the default suite. The deep simulation runs on push on Ubuntu with Python 3.12.
7. Both READMEs use absolute GitHub links for repository files, including the language switch.
8. Removed the duplicate parser walks, precision bookkeeping, redundant status type checks and repeated report and diagnostic tests. `src/fazit/*.py` went from 3,642 to 3,486 lines. `tests/*.py`, including helpers, went from 7,902 to 7,887 lines.

## Files

- `.github/workflows/ci.yml` gates the deep simulation on the event and matrix entry.
- `README.md` updates the English repository links.
- `README.de.md` updates the German repository links.
- `site/demo/de/index.html` regenerates the German town openDesk demo.
- `site/demo/en/index.html` regenerates the English town openDesk demo.
- `src/fazit/catalogue.py` checks labels against the shared locale cache and selects the document error explicitly.
- `src/fazit/cli.py` selects option-specific error keys.
- `src/fazit/costs.py` drops input precision from cost results.
- `src/fazit/i18n.py` caches locale reads, formats explicit error keys and shares cent rounding between display and HTML attributes.
- `src/fazit/inputs.py` registers the input schema for YAML diagnostics and combines the name checks.
- `src/fazit/licences.py` passes the document root without a synthetic field path.
- `src/fazit/locales/de.yaml` supplies the German diagnostics.
- `src/fazit/locales/en.yaml` supplies the English diagnostics.
- `src/fazit/mappings.py` selects the profile option error and uses the document root.
- `src/fazit/model.py` compares validated timestamps and leaves JSON decoding and privacy checks to the parser.
- `src/fazit/parsing.py` uses decoder lines and composed YAML marks for diagnostics.
- `src/fazit/report.py` uses the shared HTML amount formatter.
- `src/fazit/risky_files.py` uses the document root in rule validation.
- `src/fazit/rules/status.yaml` marks the six partial-evidence assignment rules.
- `src/fazit/status.py` evaluates the rule flag and simplifies condition type checks.
- `src/fazit/templates/report.html.j2` uses the cent-precision formatter for cost attributes.
- `src/fazit/validation.py` distinguishes document errors from field errors without a synthetic path.
- `tests/test_cli.py` checks bilingual positions and consolidates the README and report rebuild cases.
- `tests/test_costs.py` checks cent precision on a prorated amount and reuses the shared report helpers.
- `tests/test_evidence_cli.py` checks equal offset timestamps and distinct microseconds.
- `tests/test_inputs.py` checks unknown key lines and the explicit YAML diagnostics.
- `tests/test_installed_package.py` checks file-level errors for parser depth limits.
- `tests/test_model.py` checks decoder positions, finite YAML values and file-level errors.
- `tests/test_privacy.py` checks exact diagnostics for private scan text and unrecognised input keys.
- `tests/test_repo_basics.py` checks the deep simulation gate and the README URLs.
- `tests/test_rules.py` isolates the locale cache in the missing-label tests.
- `.planning/quick/261122-rv8-lean2/SUMMARY.md` records the changes and checks.

## User-visible changes

A misspelt input key now produces a sentence such as “Remove the unrecognised field on line 4 of inputs.yaml.” Syntax errors point to the line. YAML values with known fields retain those field names. Scans with more than six fractional timestamp digits receive a field error.

Both regenerated demos changed 39 cost attributes and the status rule checksum in the appendix. The comparison against the previous HTML confirmed that these were the only byte changes. The package description now links directly to GitHub.

## Deviations and open work

JSON duplicate-key and non-finite-number errors identify the file because the standard decoder does not supply positions to its validation hooks. Parser limits also use a file-level diagnostic. No work remains for this task.

## Verification

`uv sync`, both Ruff checks, both language demos, the site check and `uv build` passed. The default suite passed 688 tests in 104.99 seconds. The deep simulation passed 6 tests in 796.68 seconds. The site check covered 18 pages and 635 references. Both demos opened at 360 px in offline Chromium in light and dark mode with both embedded fonts and zero HTTP requests.

## Suggested commits

1. `fix: emit cost attributes at cent precision` (user-visible HTML)
2. `fix: report parser locations from native marks` (user-visible)
3. `fix: locate unknown input keys by line` (user-visible)
4. `refactor: select explicit CLI error messages`
5. `fix: simplify readiness rules and timestamp handling` (user-visible)
6. `ci: run deep simulation once per push`
7. `docs: make README links work on PyPI` (user-visible)
8. `test: consolidate repeated report and parser checks`

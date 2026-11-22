---
quick_id: 261122-rv5
slug: lean
date: 2026-11-22
status: planned
---

# Quick task: release review batch 5, structure and lean code

Fix R-31 and R-32 from `.planning/quick/261122-rev-release-review/FINDINGS.md`. The concrete lists are "What to delete or simplify" in `REVIEW-fable-1.md` (items 1 to 10) and in `REVIEW-astra-1.md`, and finding F-14. Line numbers there refer to `82d9d8f`; batches 1 to 3 have changed the code since, so find each place again.

The goal: an experienced Python developer reading `src/fazit/` sees small modules with one job, short functions, one way to do each thing, and nothing that exists only to look careful. This is a refactor. **No behaviour change**: every test keeps passing unchanged (moving an import in a test is fine), and both demo reports and all three profiles in both languages render byte-identical HTML before and after. Record the SHA-256 of `fazit demo --sample {town,nonprofit} --profile {opendesk,nextcloud,generic} --lang {en,de}` (12 reports) before you start and compare at the end.

## Items

1. **Split `rules.py`** along its jobs: mapping files, licence classification (with the licence privacy filter that sits in `model.py`), status evaluation, evidence precedence (today split between `rules.py` and `inputs.py`). Choose names that read well (`mappings.py`, `licences.py`, `status.py`, `evidence.py` are suggestions, not orders). Build the SKU and plan lookup once and use it for classification, the public JSON and the report. Remove the `TYPE_CHECKING` import cycle between `model.py` and `rules.py`. Rename `rules.Mapping` so nothing needs `Mapping as MappingABC`.
2. **Long functions.** Break up `_evaluate_workload`, `licence_findings`, catalogue `_findings` and any other function over about 40 lines into named steps, where that makes them easier to read, not merely shorter.
3. **One set of validation helpers** instead of four (`model.py`, `inputs.py`, `rules.py`, `catalogue.py`), with each pattern (GUID, identifier, date) defined once, and one idiom for "non-negative integer".
4. **`costs.py` with `fractions.Fraction`.** Replace the Decimal twelfths machinery (`_precision`, `_from_twelfths`, `_currency_group`, the twelfths multipliers, `localcontext`, the `assert`, the matching context in `i18n.py`) with exact fractions, rounding to cents only for display, exactly as today (round half up, as the existing tests and `tests/test_simulation.py` define). Totals must stay byte-identical in every report.
5. **Smaller items.** Timestamp comparison with datetimes at whole seconds if the schema allows it without changing any accepted or rejected input (otherwise leave it and say why); `guid()` as one pattern match; language validated in one place; delete checks that cannot fail (the repeated coverage check in rules, the shared-container tracking in `parsing.py` that JSON and alias-free YAML cannot produce, and its test only if it tests nothing else); `SECTION_ORDER` moves to the tests; one cached locale loader without a deepcopy on every call, as long as callers cannot mutate shared state (make the data immutable or keep the copy and say why); `parsing.py` checks a float without rebuilding a YAML document; a short comment on why `LookupError` and `AttributeError` are caught.
6. **Comments and docstrings.** Remove comments that say what the code does and docstrings that repeat a name. Keep every comment that says why.

## Rules

- Keep `AGENTS.md`: frozen dataclasses, type hints, no inheritance trees, no new abstractions. Fewer lines is the expected result; report the line count of `src/fazit/*.py` before and after.
- Do not change rule YAML, locales, the template's output or any test assertion. If a simplification would change output, skip it and list it.

## Done means

```
uv run ruff check .
uv run ruff format --check .
uv run pytest -q
uv run pytest -q tests/test_simulation.py --hypothesis-profile=deep
uv run fazit demo --lang de
uv run fazit demo --lang en
uv run python site/check_site.py
```

plus the 12 report hashes identical before and after. Suggest one commit per item.

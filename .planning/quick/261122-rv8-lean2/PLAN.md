---
quick_id: 261122-rv8
slug: lean2
date: 2026-11-22
status: complete
---

# Quick task: release review round 2, lean pass and remaining items

Round 2 of the release review found that the byte-identical refactor and the error-position work left the code that reads most like machine output (F2-04 in `.planning/quick/261122-rev-release-review/REVIEW-fable-2.md`), and that source grew by 283 lines and tests by 1,571. This batch removes that, and fixes F2-03, F2-06, F2-07 and the rest of F-19. Read the summaries of `261122-rv5-lean` and `261122-rv7-round2` first; rv7 has just landed.

Unlike batch 5, output may change where an item says so. Every principle keeps its test; never weaken a test to make a simplification pass.

## Items

1. **Costs.** Remove `input_exponent` and the hand-built Decimal context (`costs.py`, `report.py`): `data-amount` attributes carry exact cents (or the value the report shows), not the digits of the input. Update the tests that read them. Regenerate the site demos.
2. **Parsing.** Syntax errors (JSON, YAML) name the line only; delete the second JSON tokenizer and the second YAML event walk that exist only to add a field name to syntax errors. Value errors found on composed YAML nodes (duplicate key, invalid integer spelling, non-finite number, invalid date) keep naming the known field and line, using the node's own marks. Replace the hand-written YAML 1.1 float parser and the check that mimics a quirk of the old code with the smallest correct check. Strict scalar spelling is an explicit parameter, not implied by passing `integer_fields`. Aim for `parsing.py` well under its current 295 lines.
3. **Unknown keys (F2-03, F-19).** A misspelt or unknown key is reported by line ("Remove the unrecognised field on line 4 of inputs.yaml."), never as `$[0]`; no user-facing message contains `$`.
4. **Messages.** `i18n.py` no longer builds message codes by appending `_option`, `_field` or `_document`; each call site names its message.
5. **Small items.** `inputs.py` two consecutive `if` blocks with the same failure become one; `status.py` no longer special-cases one finding id suffix in the generic engine (move the distinction into rule data or the finding's catalogue entry); `catalogue.py` validates labels against locales loaded once per process; `model.py` compares timestamps as `datetime` values: accept at most six fractional digits (microseconds) and reject more with a field error, and drop the sub-microsecond comparison code.
6. **CI (F2-06).** Per push, run the default suite on all four runners. Run the deep simulation once per push on Ubuntu with Python 3.12 only, not on every runner. Update `tests/test_repo_basics.py` so it still requires the deep run somewhere in CI.
7. **README on PyPI (F2-07).** Relative links in `README.md` and `README.de.md` that would be dead on PyPI become absolute GitHub URLs (`https://github.com/rouxdutoit/fazit/blob/main/...`).
8. **Volume.** Look again at what batches 1, 2, 5, 6 and 7 added to `src/` and `tests/`, and delete what an economical developer would not have written: helpers used once, checks that cannot fail, tests that repeat another test. Report line counts of `src/fazit/*.py` and `tests/*.py` before and after.

## Done means

```
uv run ruff check .
uv run ruff format --check .
uv run pytest -q
uv run pytest -q tests/test_simulation.py --hypothesis-profile=deep
uv run fazit demo --lang de
uv run fazit demo --lang en
uv run python site/check_site.py
uv build
```

If the report changes, regenerate `site/demo/en` and `site/demo/de` and say what changed. Suggest one commit per item; mark user-visible changes.

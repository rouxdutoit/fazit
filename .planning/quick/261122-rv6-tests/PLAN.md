---
quick_id: 261122-rv6
slug: tests
date: 2026-11-22
status: planned
---

# Quick task: release review batch 6, a leaner test suite with the same protection

Fix R-33 from `.planning/quick/261122-rev-release-review/FINDINGS.md`. The concrete lists are F-15 and items 12 to 16 of "What to delete or simplify" in `REVIEW-fable-1.md`, and the test item in `REVIEW-astra-1.md`. Line numbers refer to `82d9d8f`.

**Never weaken a test or a principle.** Every promise in `AGENTS.md` ("What this tool must never do", "Report", "Tests") and every principle in `DECISIONS.md` keeps a test that fails when it breaks. Remove a test only when another test already fails for the same defect; say which one in the summary. Before deleting any test, break the code it guards on purpose and show that a remaining test fails (mutation check), then restore the code.

## Coordination

A report redesign (`.planning/report-redesign/UI-SPEC.md`) will rewrite `tests/test_report.py` right after this batch. Change `tests/test_report.py` only to move its shared helpers out and update imports; leave its parametrisation (item 1) to the redesign and note that in the summary. Item 1 still applies to the other test files.

## Items

1. **Run once what is the same everywhere.** The stylesheet is identical in every report: check CSS, escaping and structure on one report per language where the property does not depend on sample or profile; keep the matrix only for checks whose result can differ by sample, profile or language.
2. **The clock matrix** in `tests/test_cli.py` (rendering 26 reports to prove what the AST test proves): keep the AST test and one end-to-end run per command.
3. **Duplicates.** Destination checks exist three times (`tests/test_cli.py`, `tests/test_output.py`): keep one home. `--debug` is tested twice: keep one. `assert "Sie" in text` adds nothing over the locale tests: remove it if so.
4. **Change detectors.** Tests that assert README prose or the exact CI command list fail on the next honest edit. Keep what they protect (README does not overclaim; CI runs every "Done means" command, both Python versions, read-only permissions, SHA-pinned actions) and check that, not exact wording or order.
5. **Shared helpers.** Tests import private helpers from other test modules (`_section`, `_readiness`, `_rebuild`, `_audit_environment`, `_assert_no_private_text` and more). Move shared helpers into one module (`tests/helpers.py` or `conftest.py` fixtures), give them public names, and import them from there.
6. **Names and noise.** Test names say the behaviour they protect; no docstrings that repeat the name; no comments that say what.

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

Report test count, runtime and test line count before and after, and the mutation checks you ran. Suggest one commit per item.

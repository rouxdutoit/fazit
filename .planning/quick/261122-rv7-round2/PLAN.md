---
quick_id: 261122-rv7
slug: round2
date: 2026-11-22
status: planned
---

# Quick task: release review round 2, fixes

Fix the round-2 findings of Codex GPT-6.2-Astra in `.planning/quick/261122-rev-release-review/REVIEW-astra-2.md`. Its reproductions are described there; reproduce each as a failing test first. Read `DECISIONS.md` principles 5 and 8 and the M0 section, and the summaries of `261122-rv1-judgement` and `261122-rv5-lean` (module layout).

A report redesign is being built in parallel by another session and touches `status.py`, `report.py`, the template, the locales, `status.yaml` and `tests/test_report.py`. Keep changes in `status.py` and `report.py` as small as the fix allows, do not touch the template or `tests/test_report.py`, and add locale strings only if a fix needs a new sentence.

## Items

1. **A2-01 (critical).** For the same scope and date, a licensed headcount from the directory above the sum of assigned seats in a complete inventory is a discrepancy: flag it, carry it into licence readiness and into every absence inferred from assignments, keep measured positives, and suggest no pilot that rests on it. Test the nonprofit case (20 licensed, one assigned seat) and the town case (85 licensed, zero-assignment products). Add an independent headcount bound to `tests/tenants.py` and an invariant in `tests/test_simulation.py` so the generator would have found this.
2. **A2-02 (high).** For "any use" findings, a partial negative measurement must not override a confirmed positive answer (town telephony: interview says in use, one of 85 accounts checked shows none). Keep the Blocker. Test both directions of partial boolean evidence.
3. **A2-03 (high).** Apply disputes by finding ID to every rule that uses the disputed finding, in every workload, so a disputed count cannot make another area Ready or a pilot. If this lets you simplify how a dispute travels through `status.py` (the reviewer notes several dictionaries), do so.
4. **A2-04 (high).** A supplied answer that Windows desktops are not required, alongside Windows-only applications without a web version, is a disagreement: show both facts and do not give a definite desktop answer until reconciled. Both product profiles.
5. **A-07 (rest).** When a file name the user gave contains an at sign, error messages name it by its role ("the scan file", "the inputs file") instead of echoing it; otherwise as given. Update `tests/test_cli.py` around line 150, which currently requires the address to be printed.
6. **A-09 (rest).** Compare instants, not spellings, when deciding that two observations share a period (`09:00Z` equals `10:00+01:00`).
7. **A-13 (rest).** Validate source labels in both locales at catalogue load, like workload, finding and unit labels, so a missing label is one localised sentence, not a traceback.
8. **A2-05 (medium).** An invalid calendar date in `inputs.yaml` names its own field and line, not line 1.
9. **A2-07 (medium).** The sdist's own test suite must pass when unpacked: checks that need the git checkout (history, `.github/`, `site/`) skip with a stated reason when those files are absent, and the checks keep running in the repository. Do not drop tests from the sdist.
10. **Lean.** `cli.py` subclasses a Typer command only to drop braces from a usage line. Replace it with something simpler if one exists (check what produces the braces); otherwise keep it and say why.

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

and the unpacked sdist's `pytest -q` passes. If the town or nonprofit report changes, regenerate `site/demo/en` and `site/demo/de` and say what changed visibly. Suggest one commit per item; mark user-visible changes.

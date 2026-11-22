---
quick_id: 261122-rv9
slug: round3
date: 2026-11-22
status: complete
---

# Quick task: release review round 3, fixes

Fix A3-01, A3-02 and A3-03 from `.planning/quick/261122-rev-release-review/REVIEW-astra-3.md` and F3-01 from `REVIEW-fable-3.md`. Reproduce each as a failing test first. Read the summaries of `261122-rv1-judgement`, `261122-rv7-round2` and `261122-rv8-lean2`.

Licence reconciliation has now been fixed case by case three times (A-01, A2-01, A3-01/02). Fix it once, as a rule, not as another special case.

## Items

1. **Licence evidence must reconcile before anything is inferred from it (A3-01 critical, A3-02 high).** Absences inferred from licence assignments (a workload has no assigned licence, so it is not in use) and every pilot that rests on them need a reconciled licence snapshot: a complete inventory and a complete licensed headcount from the directory, for the same instant, that agree. They agree when the licensed headcount is not above the total of assigned seats in user SKUs, and no user SKU has more assigned seats than the licensed headcount. If the headcount is missing, denied, skipped, partial, from another instant, or disagrees, the snapshot is unreconciled: inferred absences stay open with a reason, licence readiness is not Ready, no pilot rests on them, and measured positive assignments still count as evidence of use. Replace the existing special cases with this rule where it covers them. In `tests/tenants.py`, generate directory headcounts independently of assignments, both above and below them, and make the simulation invariant check the rule in both directions.
2. **Partial evidence of telephony use (A3-03 high).** A partial measurement that shows telephony in use, with a supplied "no replacement", keeps the Blocker and the transfer need Yes (town sample, use measured in 1 of 85 accounts, collector partial). Use `accept_partial_true` on the telephony in-use rules in `status.yaml` and make the transfer-need code in `report.py` keep confirmed use. Keep the change in `report.py` to the few lines it needs; a report redesign is about to rewrite that file.
3. **Huge numbers (F3-01 medium).** An integer of about 4,300 digits in `inputs.yaml` (for example `users` or `training_days_per_person`) ends in a Python traceback when a derived figure is formatted. Give every integer and amount that Fazit accepts from `inputs.yaml` and `scan.json` an upper bound that keeps every derived figure printable (counts of people, devices, items and months are far below 10^12; amounts far below 10^15), and reject anything larger with the existing one-sentence field error. Test the boundary through the CLI for both files. No traceback without `--debug`.

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

The sample reports should not change; if they do, regenerate `site/demo/en` and `site/demo/de` and say why. Suggest one commit per item; mark user-visible changes.

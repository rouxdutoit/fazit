---
quick_id: 261122-rv9
status: complete
date: 2026-11-22
---

# Release review round 3

## Results

1. **A3-01 and A3-02.** Licence absences and dependent pilots now require a complete licence inventory and a complete measured directory headcount from the same instant. The headcount must be at least the highest assignment count for a single SKU and at most the sum of assigned seats. Missing, incomplete, mistimed or contradictory data leaves licence readiness incomplete and inferred absences Unknown. The report shows the existing bilingual reason and retains measured positive assignments. The scan uses `assigned` for user seats. [Microsoft Graph SKU definition](https://learn.microsoft.com/en-us/graph/api/resources/subscribedsku?view=graph-rest-1.0)
2. **A3-03.** Telephony use measured in one of 85 accounts yields Blocker when the organisation confirms that it has no replacement, and Needs work when it has one. The transfer need is Yes. Readiness still shows incomplete coverage, and conflicting accounts of use leave the transfer need Unknown.
3. **F3-01.** Counts and training days are capped at 999,999,999,999. Storage is capped at `2**63 - 1` bytes, parallel running at 60 months, and monetary amounts at 15 whole digits and two decimal places. Oversized values in known fields of either input file produce the existing localised sentence naming the file and field, with exit code 2.

## Files changed

- `src/fazit/licences.py` requires comparable directory evidence and reconciles assignment counts in both directions.
- `src/fazit/rules/status.yaml` accepts a measured Yes under partial coverage in both telephony use rules.
- `src/fazit/report.py` preserves confirmed transfer needs under partial coverage and respects disputes about the evidence.
- `src/fazit/validation.py` sets the count and storage limits and enforces the applicable maximum.
- `src/fazit/model.py` applies the storage limit to byte-valued findings and the count limit to other findings, coverage and seats.
- `src/fazit/parsing.py` retains field diagnostics when integer literals exceed Python's conversion limit.
- `src/fazit/inputs.py` caps training days in both whole-number and quoted decimal form.
- `tests/tenants.py` draws directory headcounts independently of assignments and keeps generated inputs within the supported bounds.
- `tests/test_simulation.py` tests both licence mismatches and checks that unreconciled inventories leave assignment absences unresolved.
- `tests/test_evidence_cli.py` covers licence pilot eligibility, incomplete directory evidence and partial telephony measurements through the CLI.
- `tests/test_cli.py` tests the numeric boundaries and oversized literals in the YAML and JSON inputs.
- `tests/test_rules.py` gives licence classification fixtures a headcount consistent with their assignments.
- `site/demo/de/index.html` regenerates the German town openDesk demo.
- `site/demo/en/index.html` regenerates the English town openDesk demo.
- `.planning/quick/261122-rv9-round3/SUMMARY.md` records the results and suggested commits.

## Verification

Regression tests reproduced all four findings before the fixes. `uv sync` and both Ruff checks passed. The full suite passed 705 tests in 104.74 seconds. The deep simulation passed 6 tests in 829.88 seconds. Both language demos passed, and the site checker verified 18 pages and 613 references. Both reports opened in offline Chromium at 360 px in light and dark mode with both embedded fonts and zero HTTP requests.

## Deviations and open work

All 12 demo variants differ from their baselines only in the `status.yaml` checksum in the appendix. The two published demo files were regenerated from the matching language runs. There are no other deviations, conflicts with `AGENTS.md`, or open items in this task.

## Suggested commits

1. `fix: reconcile licence inventory with the directory` (user-visible). Include the licence evidence tests, simulation invariant and independent headcount generation.
2. `fix: preserve confirmed telephony use with partial coverage` (user-visible). Include the telephony regressions and both regenerated demos.
3. `fix: reject oversized numbers in report inputs` (user-visible). Include the CLI boundary tests, simulation input limits and this summary.

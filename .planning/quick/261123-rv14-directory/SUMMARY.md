---
quick_id: 261123-rv14
status: complete
date: 2026-11-23
---

## Plan results

1. Directory reaches Ready when the account list was reviewed and complete internal and guest counts match a complete declared population. Both reviewer cases report Unknown in English and German. The reports explain when the scan cannot confirm that all accounts were checked. A confirmed guest still gives Needs work.
2. The loader refuses a complete count inside a declaration marked partial or with a known shortfall in successful checks. It also refuses a matching count or successful-check figure above the declaration's limit. The 21-failure example is rejected at the finding's coverage field.
3. A matching count can inherit the declared total for validation. The two-account example loads with two successes and zero failures, including when the same instant is written with a different offset. The parsed finding preserves the omitted total.
4. Date-only evidence and period ends can be one day ahead of the scan's UTC calendar date. The period end also observes that limit relative to its collection stamp. A date-only reference supplies its stated day. The loader refuses dates beyond the limit and compares clock times as instants.

## Files changed

- `src/fazit/model.py` validates matching finding coverage against the declaration and applies the calendar allowance.
- `src/fazit/status.py` adds the `requires_directory_population` condition for evidence from a complete declaration.
- `src/fazit/report.py` passes the scan's declaration into readiness evaluation.
- `src/fazit/rules/status.yaml` applies the condition to the internal and guest counts used for Directory Ready.
- `src/fazit/rules/findings.yaml` registers the unverified directory population reason.
- `src/fazit/locales/en.yaml` adds the English explanation and next step.
- `src/fazit/locales/de.yaml` adds the German explanation and next step.
- `DECISIONS.md` records the scope, coverage and date rules in D31.
- `docs/scan-format.md` describes the updated rules for scan producers.
- `tests/test_model.py` covers contradictory coverage, inherited totals and the one-day boundary.
- `tests/test_evidence_cli.py` checks Directory in both languages, distinguishes contradictory from incomplete licence evidence and verifies CLI date handling.
- `tests/test_rules.py` gives the complete-evidence fixtures a matching declaration for the readiness and empty-report assertions.
- `tests/test_simulation.py` generates truthful declared, undeclared and separately filtered lists and checks the date boundary against independently generated time zones.
- `site/demo/de/index.html` was regenerated from the German town demo with openDesk. Its two rule checksums changed.
- `site/demo/en/index.html` was regenerated from the English town demo with openDesk. Its two rule checksums changed.

## Verification

Both Ruff checks and both CLI demo commands passed. The full pytest suite passed 1,034 tests in 212.35 seconds. The deep simulation passed 31 tests in 1,303.40 seconds. The truthful-export property accepted 900 generated scans across the three scopes. The site checker passed 24 pages and 972 references. The alignment check passed all 144 views. Both reports opened offline in Chromium and Firefox with no network requests.

## Deviations and open work

None.

## Suggested commits

- `fix: require verified directory population coverage` for the directory checks, readiness, translations, tests, documentation and demo checksums.
- `fix: allow date-only evidence across time zones` for the date checks, documentation and regressions, including the truthful-export property.
- `docs: record the rv14 directory quick task` for this summary.

## Orchestrator note

Built against `390cd73`, applied onto `f5ccff5` (the founder's polish branch) without conflicts, demos regenerated from the merged template. On the merged code: Ruff, 1,040 tests, both demos and the site check (24 pages, 969 references) pass.

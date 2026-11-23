---
quick_id: 261123-rv16
status: complete
date: 2026-11-23
---

## Files

- `src/fazit/status.py` uses the derived licence inventory to check reconciliation and attaches existing missing-evidence reasons to Directory.
- `src/fazit/model.py` bounds joint account counts by successful census rows and compares date-only references at the end of the UTC−12 day.
- `tests/tenants.py` generates declared censuses with consistent counts and exercises incomplete inventories and collector removal.
- `tests/test_evidence_cli.py` covers incomplete reconciliation and the existing report wording in both languages.
- `tests/test_model.py` extends the roster oracle to unattempted rows and checks the licensed account and date boundaries.
- `tests/test_rules.py` supplies the collectors and inventory required by fixtures that assert Ready.
- `tests/test_simulation.py` tests both steps of the nonprofit regression and tracks Directory status transitions in generated scans.
- `DECISIONS.md` updates D31. `docs/scan-format.md` gives scan producers the corresponding validation and readiness rules.

## Plan results

1. Directory reaches Ready only after the complete census and licence inventory reconcile at the same instant. The former `licences: null` Ready test now expects Unknown. An incomplete check uses the existing reason wording. A confirmed guest still gives Needs work.
2. Generated tenants reached Directory Ready and then Unknown after evidence loss. In the explicit nonprofit case, Directory becomes Unknown when the licence collector is skipped and stays Unknown when the licensed count becomes partial.
3. A single success and an unattempted row cannot establish both a member and a guest. A single successful row with zero members and zero guests cannot establish a licensed account. The exhaustive roster oracle passed, along with all 900 generated truthful directory scans across declared, undeclared and filtered scopes.
4. A date-only reference accepts evidence through 24:00 UTC−12, including the interview at 20:00 UTC−05 on 4 November. The tests cover equality at that boundary and rejection one microsecond later.

## Verification

- `uv sync` and all nine checks in `AGENTS.md` passed. The full suite passed 1,079 tests in 183.51 seconds. The deep profile passed 31 tests in 1,269.72 seconds.
- The site checker passed 24 pages and 969 references. Alignment, spacing and scrollbar checks passed in Chromium and WebKit. Both published reports opened offline.
- Fresh demos for both samples, both languages and all three profiles matched their baseline HTML byte for byte. The fresh German and English town demos also matched the published copies.

## Deviations and open items

None.

## Suggested commits

1. `fix: require licence reconciliation for Directory Ready` with the status change, its rule and CLI tests, the simulation changes and the readiness documentation.
2. `fix: bound directory counts by successful census checks` with the model change, roster tests and census documentation.
3. `fix: validate date-only references through UTC-12 midnight` with the model change, date tests and date documentation.
4. `docs: record quick task 261123-rv16 results` with this summary.

## Orchestrator note

Applied onto `main` at `5157e15` without conflicts. The demos are unchanged. On the merged code: Ruff, 1,079 tests, both demos and the site check (24 pages, 969 references) pass.

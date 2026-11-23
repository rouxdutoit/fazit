---
quick_id: 261123-rv15
status: complete
date: 2026-11-23
---

## Files

- `src/fazit/status.py` feeds licence reconciliation gaps into Directory readiness.
- `src/fazit/model.py` bounds combined census counts and applies the UTC+14 date comparison.
- `tests/test_evidence_cli.py` checks Directory reports in both languages and exercises the date boundary through the CLI.
- `tests/test_model.py` enumerates small censuses against a roster oracle and checks interview dates and reporting periods.
- `DECISIONS.md` amends D31 for all three changes.
- `docs/scan-format.md` documents the revised rules for scan producers.

## Plan results

1. Two assignments on one user SKU against one licensed account make Directory Unknown when it would otherwise be Ready. The Directory card uses the existing licence conflict wording in both languages in place of the Ready statement about guests. A confirmed guest still gives Needs work.
2. A census with one successful check and one failure cannot record both one internal account and one guest. The oracle enumerated censuses of up to four rows and every feasible pair loaded.
3. A 6 November interview is refused at 00:00 UTC on 5 November and accepted from 10:00 UTC. A scan at 20:05 UTC−05:00 accepts an interview dated on its local day. Equivalent instants produce the same result across offsets. Period ends use the same boundary against both the scan and the collection reference.

## Verification

The regression tests reproduced all three issues before the fixes. All nine checks in `AGENTS.md` passed.

- `uv run pytest -q` passed 1,064 tests in 235.58 seconds.
- The deep simulation passed 31 tests in 1,355.64 seconds, including all 900 generated truthful scans across declared, undeclared and filtered scopes.
- Both Ruff checks passed. `site/check_site.py` checked 24 pages and 969 references.
- Regenerated the German and English town demos for openDesk and copied them to the published paths. Both matched the prior files byte for byte and opened offline. Alignment, spacing and scrollbar checks passed in Chromium and WebKit.

## Scope and open items

An explicitly skipped or partial licence collector also leaves a gap when the census supplies a complete licensed count. This extends the conflict case to uphold the skipped-collector principle in `AGENTS.md`. Date-only scan and collection references use the end of their stated UTC day for comparison.

The task has no open items.

## Suggested commits

1. `fix: withhold Directory Ready when licence evidence conflicts` with the status change, its CLI tests and the Directory documentation.
2. `fix: bound combined directory counts by census coverage` with the count check, roster oracle and census documentation.
3. `fix: check date-only evidence at midnight UTC+14` with the date comparison, its tests and date documentation.
4. `docs: record quick task 261123-rv15 verification` with this summary.

## Orchestrator note

Built against `2164567`, applied onto `c2a38f5` without conflicts. The demos are unchanged. On the merged code: Ruff, 1,064 tests, both demos and the site check (24 pages, 969 references) pass.

# Fazit release review 10, final confirmation (reviewer: Claude Fable 5.2)

Commit `b0b213d`.

## Verdict

**One fix first.** The joint-count and date changes hold. The Directory change breaks the rule the project advertises: worse collection now improves a status (F10-01).

Remaining code findings, excluding R-41 and R-42: 0 critical, 1 high, 1 medium, 3 low.

Clean: both Ruff checks, `pytest -q` (1,064 passed), the unpacked sdist (1,058 passed, 6 skipped), deep simulation (31 passed), 12 demos, `site/check_site.py` (24 pages, 969 references), 5,364 malformed files. Public CI is green.

## Round-9 items

- **Directory beside a conflict.** Fixed where the conflict is flagged; made worse otherwise.
- **F10-01 · high · `src/fazit/status.py:270-286`.** The licence check binds Directory only while the licensed count is complete. Bundled nonprofit sample: skip the licence collector and Directory is Unknown; then mark the licensed count partly covered and Directory is Ready. Both are `degraded_tenants()` steps; the pair fails the assertion of `test_worse_collection_never_improves_status`. The round-9 conflict tenant needs one step. Two-step degradations of five tenants give 191 such steps; `25c27a1` gives none. The simulation misses it: its generated tenants never declare a population. It needs an edited scan; nobody is misled today. Tried, then reverted: Ready only after a passed licence check when licence evidence is listed. No such step remains, both samples keep their statuses, one test case changes.
- **Joint counts.** Astra's case is refused. Low: a census of three with one row checked still yields an internal account and a guest.
- **Dates.** Fixed as specified. Low: a scan dated only 4 November still refuses an interview at 20:00−05:00 that day.
- **Unpublished identifiers** (low) and **F5-02** (medium, MODL-05) are unchanged.

2,500 random scans agree with D31; 900 truthful tenants load.

## Founder

R-35: PyPI `fazit` is still unclaimed. R-36: hosting details remain unconfirmed.

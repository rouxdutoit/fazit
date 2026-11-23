# Fazit release review 7, confirmation (reviewer: Claude Fable 5.2)

Commit `5a3bcd0`.

## Verdict

**Release after one fix.** The round-6 fixes hold and every product in Microsoft's reference loads, but public CI on `main` has been red since the redesign merge (F7-02).

Remaining code findings, excluding R-41 and R-42: 0 critical, 1 high, 2 medium, 2 low.

Clean in the checkout: both Ruff checks, `pytest -q` (978 passed), deep simulation (27 passed), 12 demos, `site/check_site.py` (22 pages, 861 references), 5,108 malformed files.

## New findings

- **F7-02 · high · `tests/test_report.py:112,161,184,611`.** Three redesign tests read icons from `site/icons/`, which the sdist omits. CI's step "Test unpacked source distribution" has failed on all three pushes since `69a8ea0`; reproduced locally: 17 failed, 957 passed. Read them from `src/fazit/icons/`, or list the tests in `tests/conftest.py`.
- **F7-01 · medium · `src/fazit/model.py:149,500-502`.** The shared directory population is inferred from matching totals, not declared. No internal accounts in 19 of 20 rows and 19 guests in 19 of 21 rows load with 22 licensed accounts and four pilots. No internal accounts in 20 of 20 rows with guests denied loads with 21. Lists of equal size, 20 internal and 20 guests each fully checked, refuse 25 licensed accounts; with 21 guests they load. Add one coverage per collector to MODL-05.

## Round-6 items

- **A4-01, rest.** Fixed where both counts state one total: Astra's case and mine are refused; 2,000 random scans agree with D31. Rest: F7-01.
- **Partial `MCOPSTN5` inventory.** Fixed. It loads with either identifier missing.
- **Interview dates.** Fixed for undated interviews. Low: dated evidence still gets two answers for one instant (`model.py:430`): a period ending 2 November collected at 00:30+01:00 loads; written as 23:30Z it is refused.
- **SharePoint.** Fixed. No sites with files or storage is refused; truthful empty or partial exports load.
- **F6-01.** Fixed for the reference: all 620 products load. Low: a code or plan name outside the pattern that Microsoft publishes later is still refused.
- **German note.** Fixed.
- **F5-02.** Deferred as MODL-05 (medium). Its examples still load.

900 random truthful tenants load.

## Founder

- **R-35.** `fazit.dev` is registered and live. PyPI `fazit` is still unclaimed.
- **R-36.** The live site serves all 20 pages byte-identical to the repository, with the declared headers; 21 routes load without a console error. Storage location, log retention and the processing agreement are not visible from outside.

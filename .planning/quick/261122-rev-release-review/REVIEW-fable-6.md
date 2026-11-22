# Fazit release review 6, last check (reviewer: Claude Fable 5.2)

Commit `2e4fae1`, 2026-11-22.

## Verdict

**Release as is.** Every round-5 fix does what it says, the changes refuse no truthful tenant, and nothing in the code would embarrass the project in public.

Remaining code findings, excluding R-41, R-42 and the founder's site lines: 0 critical, 0 high, 2 medium, 2 low.

Ran: both Ruff checks, `pytest -q` (740 passed), deep simulation (26 passed), 12 demos, `site/check_site.py`, `uv build`, 5,048 malformed files: no problem. Public CI is green.

## Round-5 items

- **F5-01.** Fixed. 25 assigned of 20 purchased seats loads, with a note. Low: an excess of one reads "Es sind 1 Lizenzplätze".
- **Shared part number.** Fixed. Both `MCOPSTN5` products load; the same GUID twice is refused.
- **A4-01, rest.** Fixed as reported: 20 licensed accounts load, 21 are refused. A neighbour still loads, with five pilots: no internal accounts and 19 guests in the same 19 of 20 rows, 21 licensed. The unchecked row counts twice; add one population per collector to MODL-05.
- **A4-02, rest.** Fixed. Clock times without an offset are refused everywhere.
- **Empty exports.** Fixed for mail, OneDrive and Teams. Low: no SharePoint sites with 32,418 files still loads, with no effect.
- **Future interviews.** Fixed. An undated interview covering December is refused; October loads.
- **F5-02.** Not fixed, recorded as MODL-05 for phase 2. Its examples still load.

## Truthful tenants

900 random truthful tenants built around the changed rules all load. Of 2,000 random directory and licence scans, all 757 impossible under D31 are refused and no possible one is.

- **F6-01 · medium · `src/fazit/model.py:511,520`.** Older than this commit, but against its title: 61 of the 620 products in Microsoft's licence reference are refused as published, because a part number or plan name does not fit the pattern, among them Windows 10/11 Enterprise E3, Microsoft Intune Suite, Microsoft 365 E3 (no Teams) and Office 365 F3 EEA (no Teams). With those names written as null they load. For phase 2: drop such names in the loader instead of refusing the file.

## The question

Phase 2; do not wait. Every registered measured source is a sample source, so any scan with measured evidence, edited or not, yields a report that calls its measurements simulated. MODL-05 closes the gap when the first real collector exists.

Founder: R-35 and R-36 are unchanged.

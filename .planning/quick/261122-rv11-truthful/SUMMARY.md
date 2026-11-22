---
quick_id: 261122-rv11
status: complete
date: 2026-11-22
---

# Truthful scans and licence evidence

## Plan results

1. The CLI accepts assignments above purchased seats. The report shows the excess and explains that it can occur when a subscription is renewed with fewer seats. The assigned seats still establish licence use. Both registered `MCOPSTN5` products loaded through the CLI, and the report shows their GUIDs alongside the shared part number.
2. The CLI rejects future interview dates and times. A period must end by its collection date or, for an undated interview, by the scan date. An invalid date or period produces one localised sentence naming the file and field.
3. Clock times in scan files require `Z` or an explicit UTC offset. CLI tests distinguish the two occurrences of a repeated local hour. Both bundled scans already meet the requirement.
4. A confirmed empty population rules out mail storage and items, OneDrive storage, and Teams channels for the corresponding export and period. The CLI tests also cover a partial count and a different reporting period where positive storage can be valid.
5. With zero internal accounts among 19 successful checks out of 20 and 19 confirmed guests, the CLI accepts 20 licensed accounts and rejects 21. A failed check counts among the rows that could still contain an internal account.
6. The one-violation property covers the new date, offset, empty-export and population checks. A separate property varies seat totals and row order in truthful inventories that have both excess assignments and a shared part number.

## Files

- `DECISIONS.md` updates D31 and records the Microsoft references for the licence rules.
- `src/fazit/catalogue.py` validates population links and registered exceptions for published service plan names.
- `src/fazit/licences.py` uses the same plan-name validation for the service plan catalogue as the scan loader.
- `src/fazit/locales/de.yaml` supplies the German evidence note and field errors.
- `src/fazit/locales/en.yaml` supplies the English evidence note and field errors.
- `src/fazit/model.py` validates dates, offsets, empty populations and checked-row bounds. Product uniqueness uses the normalised GUID.
- `src/fazit/report.py` supplies SKU GUIDs to the licence table when registered products share a part number.
- `src/fazit/rules/findings.yaml` links the affected measurements to their populations and records the published plan-name exception.
- `src/fazit/rules/service_plans.yaml` registers both `MCOPSTN5` product and service plan pairs.
- `src/fazit/templates/report.html.j2` displays the licence notes and GUIDs in the existing table.
- `site/demo/de/index.html` and `site/demo/en/index.html` are regenerated town reports for openDesk. The findings and service plan catalogue checksums are the only changed lines.
- `tests/tenants.py` generates valid aggregates for empty populations.
- `tests/test_evidence_cli.py` exercises both licence states and the field errors through `fazit report`.
- `tests/test_model.py` aligns the duplicate-ID regression with GUID uniqueness in both row orders.
- `tests/test_rules.py` pins the published plan-name exception to its GUID.
- `tests/test_simulation.py` extends the one-violation property and verifies truthful inventory round trips.
- `.planning/quick/261122-rv11-truthful/SUMMARY.md` records the results and commit grouping.

## Verification

Both Ruff checks passed. The full suite passed 740 tests in 112.45 seconds. The deep simulation passed 26 tests in 848.55 seconds. Both languages rendered for the town and nonprofit samples. The site checker passed 18 pages and 610 references and confirmed the published demos match fresh output byte for byte.

Both published demos opened in offline Chromium at 360 px in light and dark mode, with both embedded fonts and zero HTTP requests. The added licence evidence fit its table cells at 360 px and 1280 px.

## Deviations and open work

No plan deviations or conflicts with `AGENTS.md`. The single collection time per collector and source remains scheduled for phase 2 under F5-02.

## Suggested commits

1. `fix: accept excess assignments and shared licence part numbers` (user-visible)
2. `fix: reject interview evidence dated after the scan` (user-visible)
3. `fix: require UTC offsets on scan timestamps` (user-visible)
4. `fix: reject content in exports with empty populations` (user-visible)
5. `fix: bound licensed accounts using checked directory rows` (user-visible)
6. `test: generate scan contradictions and truthful inventories`

Include the replaced licence rejection cases with item 1 and the valid-tenant generator adjustment with item 4. Regenerate both demo copies with each rule-file change.

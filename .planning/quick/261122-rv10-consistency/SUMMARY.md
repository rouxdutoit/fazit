---
quick_id: 261122-rv10
status: complete
date: 2026-11-22
---

# Scan consistency

## Plan results

1. D31 records the relationships between scan fields, the scope of count bounds and the conditions for licence reconciliation.
2. The scan loader rejects impossible coverage, counts, subsets, seat assignments and licence inventories. The CLI exits with code 2 and one localised sentence naming the file and field. Missing, incomplete, mistimed or conflicting directory evidence still withholds inferred licence absences and dependent pilots. Positive assignments remain visible.
3. Measured snapshots and licence inventories require a clock time. Period-based measurements, provided evidence and unknown evidence can still carry a date alone. Different snapshot times leave licence reconciliation unverified.
4. The generator produces scans with valid coverage and population bounds. A property mutates one field in a valid scan and checks the file and field in both languages across ten violations. Six CLI cases reproduced A4-01, A4-02 and A4-03 before the fix and passed afterward.
5. Both publiccode descriptions place the report redesign before import, packaging and phases 1.1 to 1.3. The velocity count in `.planning/STATE.md` is the outstanding edit because the task's write scope reserves `.planning/` changes for this summary. Its front matter already records 11 completed plans.

## Files

- `DECISIONS.md` records D31.
- `publiccode.yml` updates the English and German roadmap descriptions.
- `src/fazit/catalogue.py` validates declarations for aggregate counts and subset populations.
- `src/fazit/rules/findings.yaml` declares the subset populations and the counts that can accumulate multiple units per checked row.
- `src/fazit/model.py` checks scan evidence against successful checks, comparable populations, purchased seats and collection times.
- `src/fazit/licences.py` uses the validated inventory for the existing directory reconciliation.
- `src/fazit/report.py` calls the same inventory coverage check for callers that construct a scan in memory.
- `src/fazit/evidence.py` relies on the value required for measured evidence.
- `src/fazit/status.py` relies on the reason required for unknown evidence.
- `src/fazit/locales/de.yaml` supplies German wording for missing clock times, unsupported measurements and excess assignments, and clarifies the inventory coverage error.
- `src/fazit/locales/en.yaml` supplies the corresponding English wording.
- `tests/tenants.py` generates bounded observations and uses Unknown when an incomplete collection has zero successful checks.
- `tests/test_simulation.py` varies single contradictions and checks the loader's localised field errors.
- `tests/test_evidence_cli.py` reproduces the three review findings through the CLI.
- `tests/test_model.py` gives the fixture a timed licence inventory and uses a count that fits each coverage variant in the acceptance test.
- `tests/fixtures/planted_scan.json` adds the clock time to the licence inventory in the privacy fixture.
- `site/demo/de/index.html` regenerates the German town openDesk report.
- `site/demo/en/index.html` regenerates the English town openDesk report.
- `.planning/quick/261122-rv10-consistency/SUMMARY.md` records the outcome and suggested commits.

## Verification

Both Ruff checks passed. The full suite passed 721 tests in 111.06 seconds. The deep simulation passed 16 tests in 826.39 seconds. The town and nonprofit demos ran in both languages using the bundled scans. The site checker passed 18 pages and 610 references.

The regenerated reports match the published copies byte for byte. The findings catalogue checksum is the only changed line in each published report. Both opened in offline Chromium at 360 px in both themes with the embedded fonts and zero HTTP requests.

## Suggested commits

1. `docs: record scan consistency rules`
2. `fix: reject impossible scan counts and coverage` (user-visible)
3. `fix: require clock times for measured snapshots` (user-visible)
4. `test: exercise one scan contradiction at a time`
5. `docs: align the bilingual public roadmap` (user-visible)

---
quick_id: 261122-rv12
status: complete
date: 2026-11-22
---

## Files changed

- `DECISIONS.md` records the D31 rules for coverage, empty exports, licence identifiers and interview dates.
- `src/fazit/model.py` derives count bounds, checks undated periods against the scan's UTC day and trims padding from licence GUIDs.
- `src/fazit/catalogue.py` validates published identifier spellings against their GUIDs and normalises whitespace for matching.
- `src/fazit/licences.py` accepts incomplete product identities in incomplete inventories and resolves published SKU aliases.
- `src/fazit/report.py` uses the same registered SKU lookup for display and classification.
- `src/fazit/rules/findings.yaml` links SharePoint file and storage totals to the site count and lists published identifier exceptions.
- `src/fazit/locales/de.yaml` adds the singular wording for an excess of one licence seat. `src/fazit/locales/en.yaml` supplies the same key with the existing English wording.
- `src/fazit/templates/report.html.j2` selects the note by the number of excess seats.
- `tests/test_model.py` adds the exhaustive directory oracle and checks time zones, empty SharePoint exports and the full licence reference.
- `tests/test_evidence_cli.py` checks incomplete `MCOPSTN5` rows and the note for one excess seat in both languages.
- `tests/fixtures/microsoft_licence_reference.json` records 620 product GUIDs, 629 product identifier variants and 834 service plan identifier pairs from the published table and its CSV.
- `site/demo/de/index.html` and `site/demo/en/index.html` were regenerated from the matching town and openDesk demos. Their appendix checksum for `findings.yaml` changed.

## Plan results

1. The review cases accept 20 licensed accounts and reject 21 with a field error. The oracle enumerates small directories and possible checked, failed and unchecked rows to verify both sides of the bound.
2. A partial `MCOPSTN5` inventory loads with either identifier absent. The report lists the incomplete row as unregistered and retains the use confirmed by the fully identified row. Conflicting identifier pairs still raise a field error.
3. The same scan instant gives the same result for an undated interview in either offset. An interview ending on 6 November is accepted from midnight UTC on that day.
4. A complete SharePoint export with zero sites rejects positive file counts or storage for the same reporting period. Zero totals and evidence from another period load.
5. All 620 products and their published service plan identifiers load. The fixture uses the CSV values for two GUIDs misprinted in the web table. [Microsoft licence reference](https://learn.microsoft.com/en-us/entra/identity/users/licensing-service-plan-reference)
6. An excess of one now reads “Es ist 1 Lizenzplatz mehr zugewiesen als erworben.” The existing English sentence already agrees with one.

## Verification

Both Ruff checks passed. The standard suite passed 759 tests in 114.88 seconds. The deep simulation passed 26 tests in 866.61 seconds. Both demo commands and the site check passed. The site check verified 18 pages and 610 references. Both reports opened offline at 360 px with embedded fonts in Chromium and Firefox, and Chromium produced A4 PDFs.

## Deviation and open work

The supplied checkout is at `19d877b` and the redesign is still on `report-redesign`. The fixes were implemented on the supplied checkout. Integration with the redesign remains open for the orchestrator.

## Suggested commits

- `fix: enforce the licensed account population bound`
- `fix: accept incomplete licence product identities`
- `fix: compare undated interview periods in UTC`
- `fix: reject SharePoint content when the export has no sites`
- `fix: accept published Microsoft licence identifiers`
- `fix: use singular wording for one excess licence seat`
- `docs: record the round-six follow-up`

Include each regression and its D31 change in the corresponding commit. Regenerate both demos in the SharePoint and published identifier commits because each changes the rule checksum.

## Orchestrator note

Built against `19d877b` while the report redesign was on its own branch, then applied three-way onto the merged redesign (`69a8ea0`). Three conflicts were resolved in favour of the redesign: `catalogue.py` keeps the redesign's label pattern (with `category`) plus this batch's identifier pattern and helper; `de.yaml` keeps the redesign's wording plus the new singular key; the template keeps the redesign's licence layout, with the singular/plural choice applied to its excess note. On the merged code: Ruff, 978 tests, the deep simulation (27 properties), both demos and the site check (22 pages, 861 references) pass.

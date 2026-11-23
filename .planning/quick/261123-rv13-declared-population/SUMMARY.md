---
quick_id: 261123-rv13
status: complete
date: 2026-11-23
---

## Plan results

1. `src/fazit/model.py` reads the optional `directory_population` object in `scan.json` 1.x. It applies the declared total to measured internal, guest and licensed account counts from the declared collector and instant. `src/fazit/demo/town/scan.json` declares its 103-account census. `src/fazit/demo/nonprofit/scan.json` declares its 21-account census.
2. `src/fazit/rules/findings.yaml` removes the unconditional directory subset rule. All 729 truthful filtered-list combinations load. The CLI refuses 11 internal and 10 guest accounts in a declared 20-row census and accepts the same counts with independent scopes. `tests/test_cli.py` adjusts the census in the integer-boundary fixtures so they still test the maximum count and oversized values.
3. `src/fazit/licences.py` requires complete coverage of a declared directory population before confirming licence absences. `tests/test_evidence_cli.py` verifies that the four affected areas stay Unknown in the round-7 cases. Reports use the existing `licence_directory_unverified` reason when the declaration is missing, incomplete or from a different instant. Confirmed assignments stay visible.
4. `src/fazit/catalogue.py` accepts known published identifiers with missing GUIDs in incomplete inventories. `src/fazit/model.py` accepts omitted plan GUIDs in those inventories. `tests/test_model.py` verifies that all 620 reference products keep their seat counts and that missing identifiers leave products or plans unclassified.
5. `src/fazit/model.py` compares dates with timestamps using the UTC calendar day. `tests/test_model.py` verifies identical results for both representations of the 2 November example and covers date-only interview answers.
6. `tests/test_model.py` runs the exhaustive oracle with and without a declaration. `tests/test_simulation.py` generates truthful directory exports independently and verifies that they load and leave licence-dependent readiness Unknown without a declaration.

`DECISIONS.md` updates D31. `docs/scan-format.md` documents the declaration, UTC date rules and incomplete licence identifiers. Both bundled samples render in both languages. The CLI runs regenerated `site/demo/de/index.html` and `site/demo/en/index.html`. The finding catalogue checksum is the only HTML change in each demo.

## Verification

Both Ruff checks, both CLI demos and the site checker passed. Pytest passed all 1,001 tests in 182.33 seconds. The site checker verified 22 pages and 861 references. Chromium and Firefox opened both reports offline without external requests.

## Deviations and open items

None for this quick task.

## Suggested commits

- `fix: compare scan dates using UTC`
- `fix: keep partial licence rows with missing GUIDs`
- `fix: reconcile licences using declared directory scope`
- `docs: record the declared population quick task`

## Orchestrator note

Built against `2cddd2f`, applied onto `489a577` (after the founder's `home-cut` and CI fixes) without conflicts, demos regenerated from the merged template. On the merged code: Ruff, 1,002 tests, the deep simulation (28 properties, run on `f348f4d` plus this batch), both demos and the site check (24 pages, 972 references) pass. The unpacked sdist run gives 996 passed and one failure that is already on `main` without this batch (`test_status_palette_is_shared_by_the_site_and_report` reads `site/style.css`); it was reported to the session that owns it.

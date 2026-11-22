---
quick_id: 261122-rv7
status: complete
date: 2026-11-22
---

# Release review round 2

## Plan results

1. **A2-01.** The nonprofit report with 20 licensed accounts and one assigned seat withholds dependent pilots and shows the positive assignment evidence. The town report with 85 licensed accounts and three zero-assignment products withholds the licence pilot. Losing directory access leaves the affected conclusions open. The simulation checks the seat bound against an independently generated directory count.
2. **A2-02.** An interview confirming telephony use and no replacement still produces a Blocker and a Yes transfer need after a check of one account finds no use. A partial positive observation against a supplied No remains a dispute, with both observations shown.
3. **A2-03.** A disputed integration count leaves Integrations and Small apps Unknown and out of the pilot list when the Small apps rules reference the count. Tests cover both Ready conditions and rules that establish a problem.
4. **A2-04.** In openDesk and Nextcloud, a supplied No for Windows desktops alongside Windows-only applications without a web version makes the desktop transfer need Unknown. The report states both facts and asks the service owner to reconcile them.
5. **A-07.** CLI diagnostics replace input basenames containing an at sign with the scan or inputs file role. The diagnostics retain ordinary basenames, error details, and recognised field names.
6. **A-09.** Population checks compare collection instants. Equal UTC and offset timestamps share the same observation time, and the check distinguishes instants less than a microsecond apart.
7. **A-13.** Catalogue loading validates measured, licence, and provided source labels in both languages. The CLI reports a missing label in a single localised sentence that identifies the locale and source key.
8. **A2-05.** Impossible calendar dates in inputs point to the scalar's field and line, including quoted dates.
9. **A2-07.** The source distribution includes every test file. Four checkout-dependent tests skip with reasons in the unpacked archive and run in the repository. The Linux Python 3.12 CI job builds and tests the unpacked archive.
10. **Lean.** Typer 0.28 adds braces inside `TyperArgument.make_metavar` when it renders a required argument for usage. Setting `metavar` controls the text inside the braces. The existing command override preserves the documented usage line and the required argument.

## Files

- `.github/workflows/ci.yml` runs the archive verification in CI.
- `src/fazit/catalogue.py` checks each registered source code against both locale tables.
- `src/fazit/cli.py` identifies the input role at the read and render error boundaries.
- `src/fazit/evidence.py` distinguishes a partial negative measurement from contradictory evidence of use.
- `src/fazit/i18n.py` applies the localised input role to identifying filenames.
- `src/fazit/inputs.py` declares the calendar field for parsing.
- `src/fazit/licences.py` compares the headcount with the sum of assigned seats and carries reconciliation gaps into readiness.
- `src/fazit/locales/de.yaml` supplies German input-role diagnostics and desktop reconciliation wording, and describes unverified licence assignments.
- `src/fazit/locales/en.yaml` supplies the corresponding English wording.
- `src/fazit/model.py` shares timestamp equivalence between subset and licence checks and retains full fractional precision.
- `src/fazit/parsing.py` validates calendar dates while the YAML scalar's source position is available.
- `src/fazit/report.py` carries a conflict reason into the desktop transfer gap.
- `src/fazit/status.py` indexes disputes once by finding ID and applies them to every referencing rule.
- `tests/conftest.py` marks the four tests that require checkout files when the source archive omits them.
- `tests/tenants.py` draws the licensed headcount independently of the licence inventory, bounded by the directory population.
- `tests/test_cli.py` checks filename privacy and calendar diagnostics in both languages.
- `tests/test_evidence_cli.py` covers licence reconciliation, directory access loss, telephony evidence, timestamp equivalence, and both desktop mappings. Three classification fixtures use headcounts consistent with their test inventories.
- `tests/test_inputs.py` checks the scalar error for an impossible quoted date.
- `tests/test_rules.py` exercises disputed findings in edited cross-workload rules and missing labels in either locale.
- `tests/test_simulation.py` checks that excess licensed headcounts mark licence readiness incomplete and leave inferred assignment absences unknown.
- `.planning/quick/261122-rv7-round2/SUMMARY.md` records the results and suggested commits.

## Verification

`uv sync`, both Ruff checks, both language demos, the site checker, and `uv build` passed. The checkout suite passed 692 tests in 110.96 seconds. The deep simulation passed 6 tests in 857.98 seconds. In the unpacked source distribution, 688 tests passed and 4 skipped in 112.26 seconds.

The town and nonprofit demos matched their baselines byte for byte in all languages and profiles. The site checker matched both checked-in demo pages and checked 18 pages and 599 references. The English and German reports opened at 360 px in offline Chromium with both embedded fonts and zero HTTP requests.

## Deviations and open work

None within this plan.

## Suggested commits

- A-09. `fix: compare observation timestamps by instant` (user-visible).
- A2-01. `fix: reconcile licence assignments with licensed headcounts` (user-visible).
- A2-02. `fix: preserve confirmed telephony use after partial checks` (user-visible).
- A2-03. `fix: apply evidence disputes across workload rules` (user-visible).
- A2-04. `fix: flag conflicting Windows desktop requirements` (user-visible).
- A-07. `fix: hide identifying input filenames in CLI errors` (user-visible).
- A-13. `fix: validate source labels when loading the catalogue` (user-visible).
- A2-05. `fix: point calendar errors to their input field and line` (user-visible).
- A2-07. `test: run the unpacked source distribution suite in CI`.
- Lean. `docs: record round 2 verification and the Typer usage decision`.

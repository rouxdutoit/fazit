---
phase: report-redesign
plan: "01"
subsystem: report
tags: [readiness, licences, catalogue, bilingual-copy]
requires: []
provides:
  - Assessed workloads with validated categories
  - Bilingual rule actions with a kind and finding owner roles
  - Revision 4.1 locale copy and refreshed town demos
affects: [RR-06, RR-07, RR-02, RR-03, RR-04, RR-05, Phase 1.1]
actuals:
  tokens: 68891
  tasks: 3
  commits: 0
tech-stack:
  added: []
  patterns: [Catalogue-driven categories, Bilingual rule text]
key-files:
  created: [.planning/report-redesign/RR-01-SUMMARY.md]
  modified:
    - src/fazit/catalogue.py
    - src/fazit/status.py
    - src/fazit/report.py
    - src/fazit/rules/findings.yaml
    - src/fazit/rules/status.yaml
    - src/fazit/locales/en.yaml
    - src/fazit/locales/de.yaml
    - src/fazit/templates/report.html.j2
key-decisions:
  - Keep Licences in the inventory and evaluate the 14 assessed workloads.
  - Use the same lost-working-time label in the cost group, line and input field.
patterns-established:
  - Catalogue order determines the assessed workload order.
  - The deciding rule carries its action and kind through to the readiness row.
requirements-completed: [RULE-02, RULE-03, I18N-01, I18N-02]
coverage:
  - id: D1
    description: Assessed workloads carry registered categories and licence gaps remain visible.
    requirement: RULE-02
    verification:
      - kind: integration
        ref: tests/test_rules.py#test_demo_rows_show_the_categories_of_assessed_workloads
        status: pass
      - kind: integration
        ref: tests/test_rules.py#test_licence_inventory_shows_its_coverage_gap
        status: pass
      - kind: integration
        ref: tests/test_evidence_cli.py#test_licence_pilots_require_reconciled_directory_headcount
        status: pass
    human_judgment: false
  - id: D2
    description: Licence gaps preserve incomplete evidence and withhold Ready.
    requirement: RULE-03
    verification:
      - kind: e2e
        ref: tests/test_simulation.py#test_incomplete_required_evidence_prevents_ready
        status: pass
    human_judgment: false
  - id: D3
    description: The telephony row renders its deciding action in both languages and escapes markup.
    requirement: I18N-01
    verification:
      - kind: integration
        ref: tests/test_rules.py#test_town_telephony_shows_deciding_next_step
        status: pass
      - kind: integration
        ref: tests/test_rules.py#test_next_step_text_is_autoescaped
        status: pass
    human_judgment: false
  - id: D4
    description: Both locales have matching keys and placeholders and pass the wording checks.
    requirement: I18N-02
    verification:
      - kind: unit
        ref: tests/test_locales.py#test_locale_key_parity
        status: pass
      - kind: unit
        ref: tests/test_locales.py#test_locale_and_status_rule_copy_avoid_verdicts_and_promises
        status: pass
    human_judgment: false
  - id: D5
    description: The site counts match both regenerated demos and D-81 records the Phase 1.1 count.
    verification:
      - kind: integration
        ref: uv run python site/check_site.py
        status: pass
      - kind: other
        ref: RR-01 Task 3 D-81 amendment count and diff check
        status: pass
    human_judgment: false
  - id: D6
    description: Native German wording and the choice of action kinds require review.
    verification: []
    human_judgment: true
    rationale: The maintainer must judge the wording, administrative register and verbs against the evidence and the roles.
duration: 24 min from the first recorded verification timestamp
completed: 2026-11-22
status: complete
---

# RR-01 summary

The report assesses 14 areas with five catalogue categories. The licence inventory continues to supply evidence for those areas, and each deciding rule now shows a bilingual action. Both locales contain the revision 4.1 copy for the remaining redesign.

All three tasks ran in order from `2e4fae1`. The 25 modified files and this summary are in the working tree.

## Changes by task

### Task 1 — Assessed workloads and licence evidence

- `src/fazit/rules/findings.yaml` registers five ordered categories, assigns one to each assessed workload, marks Licences as unassessed, and makes the existing contract-terms answer a headline finding.
- `src/fazit/catalogue.py` validates the assessed flag, category reference, category use, unique category IDs and category labels in both locales. `src/fazit/status.py` loads and evaluates exactly the assessed set. `src/fazit/rules/status.yaml` drops the Licences block. `src/fazit/mappings.py` requires unassessed workloads in `no_function` and rejects functions mapped to them.
- `src/fazit/report.py` and `src/fazit/templates/report.html.j2` carry category IDs and labels into readiness rows and show licence coverage and absent inventory in the recorded evidence. `src/fazit/locales/en.yaml` and `src/fazit/locales/de.yaml` supply the five labels.
- `tests/test_model.py` and `tests/test_rules.py` cover invalid catalogue and mapping data, locale validation, changing a category in a copied catalogue, the readiness rows across both samples and all languages and profiles, and absent or incomplete licence inventories. `tests/test_inputs.py`, `tests/test_evidence_cli.py`, `tests/test_simulation.py` and `tests/test_cli.py` follow the evidence to its inventory location and check the assessed set.
- `README.md`, `README.de.md`, `site/pilots/index.html` and `site/de/pilots/index.html` give the revised area count. The tally and report-card alternative text in `site/index.html` and `site/de/index.html` reflect both regenerated town demos in `site/demo/en/index.html` and `site/demo/de/index.html`. Each demo has 3 Ready, 9 Needs work, 1 Blocker and 1 Unknown.

### Task 2 — Bilingual actions and owners

- `src/fazit/status.py` requires a non-empty English and German `next_step` and its `kind` on problem rules. `src/fazit/rules/status.yaml` supplies the actions for all 30 rules. The report renders the deciding action after its reason using `src/fazit/templates/report.html.j2` and `readiness.next_step` in both locale files.
- `src/fazit/rules/findings.yaml` assigns an owner to every finding. `src/fazit/catalogue.py` validates the six allowed roles and names the finding and field in diagnostics.
- `tests/test_rules.py` and `tests/test_model.py` cover missing and invalid metadata, rule text, the telephony context and rendering, and autoescaping. Both site demos were regenerated.

### Task 3 — Revision 4.1 copy and D-81

- `src/fazit/locales/en.yaml` and `src/fazit/locales/de.yaml` add the summary, filter, navigation, role, cost, next-step and appendix copy. Five evidence fixes describe actions available today. Both locales use the new scenario and lost-working-time wording.
- `tests/test_locales.py` guards the full ban list over locale values and status-rule text, checks every reason fix for import or export language, and covers category and role labels.
- `.planning/phases/01.1-ai-assistants-and-decision-window/01.1-CONTEXT.md` records the D-81 amendment immediately below D-81. Copilot will be first within its status group and category, second in the catalogue and first in the replacements table. Phase 1.1 takes the count from 14 to 15 assessed areas.
- `site/demo/en/index.html` and `site/demo/de/index.html` were regenerated from the final locale data.

## Interfaces

```python
CategoryEntry(id: str, label: str)
WorkloadEntry(id: str, label: str, assessed: bool = True, category: str | None = None)
NextStep(kind: str, text: Mapping[str, str])
StatusRule(
    id: str,
    when: tuple[Condition, ...],
    status: str,
    reason: Mapping[str, str],
    next_step: NextStep,
)
```

`Catalogue.categories` is the ordered `tuple[CategoryEntry, ...]`. `Catalogue.assessed_workload_ids` returns the assessed IDs in catalogue order. `Catalogue.workload_ids` includes all 15 workloads. `FindingEntry.owner` is a role ID.

The template reads `workload_categories` for the ID and `category_labels` for the localised label. The context also supplies `categories` in catalogue order for RR-02. Both `statuses` and `status_by_workload` give access to `row.deciding.next_step.kind` and `row.deciding.next_step.text[lang]`. The inventory uses `product_count` and `licence_plan_list_incomplete`. The reused helpers `readiness_row` and `report_section` are in `tests/helpers.py`, and `flatten_keys` is in `tests/test_locales.py`.

## Where the licence evidence appears

| Evidence or reason code | Location |
| --- | --- |
| No licence inventory, `not_in_scan` | Licence products summary in `found`, with Unknown provenance and a reason and fix |
| `coverage_partial`, `coverage_unknown` | Licence products summary in `found`, where the product count carries no more specific reason |
| `licence_products_missing` | Licence products summary in `found`, with Unknown provenance for an empty inventory without complete coverage |
| `licence_assignments_conflict`, `licence_directory_unverified` | Licence products summary in `found` and the affected assessed rows through the existing reconciliation evidence |
| `licence_plan_list_incomplete` | Licence inventory note in `found` when the derived evidence carries this code, and the assessed rows that use the affected signals |
| `licence_plan_list_missing`, `licence_not_classified` | The relevant product’s service-plan cell in `found`. The existing classification and precedence determine the reason on assessed rows. |
| `assigned_exceeds_purchased` | The assigned-seats cell in `found`, with the excess count. Positive assignments feed the assessed areas. |
| Repeated registered part numbers | The product-code cell in `found` displays each affected SKU GUID. |
| `licences.contract_terms_known` | Headline and full finding record in `found`, with the answer’s provenance |

## Verification

Each task passed its `<automated>` command before work moved to the next task.

| Check | Result |
| --- | --- |
| Baseline licence and reconciliation tests on `2e4fae1` | 91 passed in 11.50 s before editing the licence tests. The old Licences row assertions read `licence_assignments_conflict`, `licence_directory_unverified` and `licence_products_missing`. |
| Task 1 targeted model, rules, evidence CLI, inputs and CLI tests | 576 passed in 37.18 s. |
| Task 1 `<automated>` | 770 passed in 111.55 s. Both Ruff checks, both language demo content checks and the site checker passed. |
| Task 2 red tests | Four expected failures in 1.29 s. Both telephony rows lacked the new paragraph, and the loaders accepted a rule without a next step and a finding without an owner. The JUnit evidence returned `RED_EVIDENCE_OK`. |
| Task 2 focused green tests | Seven passed in 1.68 s, including the two telephony renders, validation and escaped markup. |
| Task 2 `<automated>` | Targeted rules and locale suite 171 passed in 13.65 s. Full suite 785 passed in 127.59 s. Both Ruff checks, the banned target and import term check, German demo and site checker passed. |
| Task 3 locale tests | 15 passed in 0.40 s. The spec comparison matched 65 bilingual keys, the three German coverage labels and both status lists. |
| Task 3 `<automated>` and final checks | `uv run pytest -q` passed **789 tests in 128.22 s**. `uv run ruff check .` passed. `uv run ruff format --check .` reported 151 formatted files. The two `uv run fazit demo` commands exited 0 and the printed paths led to reports with the expected titles. `uv run python site/check_site.py` checked 18 pages and 610 references and printed “No errors.” |
| Published demo copies | Each matched a fresh town openDesk build byte for byte. Both opened in Chromium at 360 px in light and dark modes with scripting disabled, offline contexts and remote requests blocked. Both embedded fonts loaded. There was no page overflow or remote request. |
| rv11 and safeguards | The comparison to `2e4fae1` matched the assessed rule conditions and reasons, `STATUSES`, and all D31 catalogue fields. The D31 decisions, scan model, validator, licence reconciliation, service-plan catalogue, inputs and cost code matched the base. The excess-seat and repeated-part-number regressions passed in the full suite. |

The acceptance counts passed. There is one unassessed entry, zero Licences status blocks, one category registry, 14 workload categories, zero `contracts_costs` entries, one template `data-category`, 30 rules with 30 valid kinds, and 41 finding owners. Both home tallies say 14 and the four specified documentation and pilot files have no old counts. Both locales have all four requested groups, six matching break-even, scope, stay, path and appendix keys, and zero old scenario values. German evidence wording occurs once, `summary.ready_definition` occurs zero times, and the D-81 amendment occurs once.

## Existing test changes

| Test | Basis | Existing assertion updated |
| --- | --- | --- |
| `test_rules.py::test_removing_a_workloads_evidence_never_gives_ready` | C2, UI-SPEC §9 item 10 | Assert the assessed order and remove evidence from every assessed workload. Each still has to become Unknown and name its missing evidence. |
| `test_rules.py::test_shipped_status_rules_define_each_assessed_workload` | C2, §9 item 10 | Check exact status-block coverage against the assessed catalogue order. |
| `test_inputs.py::test_sample_inputs_and_rendered_statuses` | C2 | Remove Licences from the town Ready set and the non-profit Needs work set. Assert both samples’ existing contract answers appear under recorded evidence with Provided provenance. |
| `test_cli.py::test_scan_only_report_explains_readiness_and_missing_evidence` | C2 | Use assessed IDs for readiness order, the bar’s total and the appendix’s ready-evidence count. |
| `test_simulation.py::_statuses` | C2 | Use the assessed catalogue in the order assertion for all generated tenants. |
| `test_simulation.py::test_incomplete_required_evidence_prevents_ready` | C2 | Check for the licence contradiction in the recorded inventory and require Licences to be absent from statuses. The property still checks partial, skipped and disputed evidence on assessed workloads. |
| `test_evidence_cli.py::test_skipping_directory_keeps_unreconciled_licence_absence_unknown` | C2 | Check the inventory reason in each reconciliation case in `found`. Retain the affected areas’ Unknown status, directory reason and measured positive signal assertions. |
| `test_evidence_cli.py::test_empty_licence_inventory_requires_completed_coverage` | C2 | Scope product count, provenance, zero-count coverage and missing reason checks to the licence summary. Telephony still has to report the expected status and carry Unknown evidence when coverage is incomplete. |
| `test_evidence_cli.py::test_licensed_accounts_make_zero_assignments_inconclusive` | C2 | Scope the recorded count and contradiction to `found`. Retain telephony and derived assignment evidence checks. |
| `test_evidence_cli.py::test_licence_pilots_require_reconciled_directory_headcount` | C2 | Check the inventory’s reconciliation reason separately. Require the four affected assessed workloads to lose pilot eligibility and retain their individual gap reasons. |
| `test_evidence_cli.py::test_report_rejects_date_only_snapshots_that_could_restore_licence_pilots` and `test_report_requires_snapshot_offsets_during_the_repeated_hour` | C2 | Read the reconciliation precondition from `found`. The date and offset rejection assertions still name the same fields. |
| `test_evidence_cli.py::test_assigned_product_without_plans_leaves_licence_evidence_unknown` and `test_unclassified_phone_plan_leaves_add_on_assignment_unknown` | C2, §9 item 11 | Narrow the reason searches to `found` while keeping the existing readiness and evidence assertions. |
| `test_rules.py::test_disputed_count_blocks_every_workload_that_uses_it` | §9 item 10 | Add the existing integrations action to the synthetic rule to satisfy the schema. The conflict assertions still apply. |
| `test_locales.py::test_catalogue_labels_and_reason_codes_have_translations` | §9 item 11 and Task 2 owner labels | Extend the coverage check to categories and all six role labels. |

Task 1 also added `found` coverage to the existing incomplete-roster test and an explicit headline assertion to the supplied-finding test. The Task 3 copy required no changes to existing wording assertions under §9 item 9. The existing category, mapping and status failure tests gained cases for the new fields.

## Deviations and implementation choices

- The run used rv11. Its assigned-seat excess is a cell-level note with a count, and its repeated-part-number distinction uses the SKU GUID in the product cell. Both remain in the inventory. The catalogue additions preserve the population links and the plan-name exception from rv11.
- The behaviour list places plan classification gaps on the assessed rows. The Task 1 test instruction also requires them in `found`. The inventory therefore shows `licence_plan_list_incomplete` from the derived evidence alongside the two existing per-product reasons. This uses the current classification and reconciliation logic.
- The draft category validation rejects unused categories as the plan directs under planner’s discretion. The report uses one lost-working-time label for the block, line and input. The additional copy covers `nav.label`, `nav.skip`, `summary.caveat_one`, `costs.inputs_missing_one`, `moves.status_link`, `moves.workload_status` and all six `role.*` labels.
- The checkout initially had no local test environment. Verification used a temporary offline environment pointing at the existing installed dependencies and this checkout’s source. The installed-wheel tests exercised their usual isolated, offline installation. Chromium used offline contexts and request blocking because the sandbox denied an isolated network namespace.
- The requested working-tree handoff takes precedence over the generic workflow’s commits and phase bookkeeping. The TDD red and green checks ran in the working tree.

## Open work

The maintainer’s native German review of the strings and action kinds is open. The subsequent redesign work follows `REV4-CHANGE-MAP.md`, including the Windows-software wording in RR-06 and the home figure strips, report-card screenshots and `publiccode.yml` follow-ups in RR-05.

## Native German review

The German values below are drafts for the maintainer’s review. The locale table uses zero-based indices for individual cost formulas.

### Locale values

| Key | English | German |
| --- | --- | --- |
| `header.title` | What leaving Microsoft 365 would take | Was ein Umstieg von Microsoft 365 erfordert |
| `nav.summary` | Summary | Überblick |
| `nav.next_steps` | Next steps | Nächste Schritte |
| `nav.areas` | Areas | Bereiche |
| `nav.costs` | Costs | Kosten |
| `nav.replacements` | Replacements | Ersatz |
| `nav.closer_look` | Closer look | Prüfbedarf |
| `nav.appendix` | Appendix | Anhang |
| `nav.label` | Report sections | Abschnitte des Berichts |
| `nav.skip` | Skip to content | Zum Inhalt springen |
| `summary.title` | Where the organisation stands | Wo die Organisation steht |
| `summary.of_areas` | Of {n} areas: | Von {n} Bereichen: |
| `summary.blockers` | What blocks this move | Was diesem Umstieg entgegensteht |
| `summary.confirmed` | Confirmed blockers: {shown} of {total} | Bestätigte Hindernisse: {shown} von {total} |
| `summary.all_blockers` | All blockers | Alle Hindernisse |
| `summary.caveat` | {n} areas are Unknown or have incomplete evidence, so a Blocker cannot be ruled out. | {n} Bereiche sind unbekannt oder unvollständig belegt; ein Hindernis lässt sich daher nicht ausschließen. |
| `summary.caveat_one` | {n} area is Unknown or has incomplete evidence, so a Blocker cannot be ruled out. | Bei {n} Bereich ist der Status unbekannt oder die Nachweise sind unvollständig, sodass sich ein Hindernis nicht ausschließen lässt. |
| `summary.unknown` | What is still unknown | Was noch unbekannt ist |
| `summary.not_examined` | All open points | Alle offenen Punkte |
| `summary.define.blocker` | A confirmed obstacle that must be resolved before this move. | Ein bestätigtes Problem, das vor diesem Umstieg gelöst sein muss. |
| `summary.define.needs_work` | The checks found work to do before a move. | Die Prüfungen haben Aufgaben ergeben, die vor einem Umstieg zu erledigen sind. |
| `summary.define.unknown` | Evidence is missing, so this version cannot assess the area. | Es fehlen Nachweise, daher kann diese Version den Bereich nicht bewerten. |
| `summary.define.ready` | The current checks found no blocker and no missing evidence. | Die aktuellen Prüfungen haben kein Hindernis und keine fehlenden Nachweise ergeben. |
| `summary.scope_title` | What {profile} covers | Was {profile} abdeckt |
| `summary.scope_of` | Of the {n} functions Fazit checks for {profile}: | Von den {n} Funktionen, die Fazit für {profile} prüft: |
| `summary.scope_needed` | Outside {profile} and needed here | Nicht in {profile} enthalten und hier benötigt |
| `summary.scope_unknown` | {n} more are outside {profile} and still Unknown here. | Weitere {n} sind nicht in {profile} enthalten; ob sie hier benötigt werden, ist unbekannt. |
| `found.title` | What Fazit recorded | Was Fazit erfasst hat |
| `costs.title` | What staying and moving cost over five years | Was Verbleib und Umstieg in fünf Jahren kosten |
| `costs.partial_exit` | Partial move | Teilweiser Umstieg |
| `costs.full_exit` | Full move | Vollständiger Umstieg |
| `costs.total_label` | {scenario} · five-year total | {scenario} · Summe über fünf Jahre |
| `costs.stay_basis` | Today's yearly costs for five years | Heutige Jahreskosten über fünf Jahre |
| `costs.comparison_unknown` | Comparison unknown | Vergleich unbekannt |
| `costs.stay_assumption` | Staying assumes no price change. | Für den Verbleib ist keine Preisänderung angenommen. |
| `costs.break_even` | {scenario} costs the same as staying if target operations cost {amount} a year (entered: {entered}). | {scenario} kostet gleich viel wie der Verbleib, wenn der Betrieb des Zielsystems {amount} pro Jahr kostet (angegeben: {entered}). |
| `costs.break_even_none` | {scenario} costs more than staying even with no operations cost. | {scenario} kostet auch ohne Betriebskosten mehr als der Verbleib. |
| `costs.vat_note` | Amounts are as entered. The inputs file does not say whether they include VAT. | Beträge wie angegeben. Die Eingabedatei gibt nicht an, ob sie Umsatzsteuer enthalten. |
| `costs.profile_note` | The costs come from the inputs file and are the same for every target profile. | Die Kosten stammen aus der Eingabedatei und sind für jedes Zielprofil gleich. |
| `costs.less` | less than staying | weniger als beim Verbleib |
| `costs.more` | more than staying | mehr als beim Verbleib |
| `costs.same` | the same as staying | gleich viel wie beim Verbleib |
| `costs.sub_cent` | differs by less than one cent | weicht um weniger als einen Cent ab |
| `costs.total_unknown` | Total unknown | Summe unbekannt |
| `costs.known_blocks` | Total of known blocks {amount} | Summe der bekannten Blöcke: {amount} |
| `costs.inputs_missing` | {n} inputs are missing | {n} Angaben fehlen |
| `costs.inputs_missing_one` | {n} input is missing | {n} Angabe fehlt |
| `costs.missing_fix` | Enter the missing amounts in the inputs file and build the report again. | Tragen Sie die fehlenden Beträge in die Eingabedatei ein und erstellen Sie den Bericht erneut. |
| `costs.input_fields.productivity_loss` | Lost working time (internal estimate, not a payment) | Verlorene Arbeitszeit (interne Schätzung, keine Zahlung) |
| `costs.groups.productivity_loss` | Lost working time (internal estimate, not a payment) | Verlorene Arbeitszeit (interne Schätzung, keine Zahlung) |
| `costs.line_items.productivity_loss` | Lost working time (internal estimate, not a payment) | Verlorene Arbeitszeit (interne Schätzung, keine Zahlung) |
| `costs.formulas[1]` | In each move scenario, subtract the months of parallel running from 60. Multiply the annual cost of retained Microsoft licences by the remaining months and divide by 12. | Ziehen Sie bei beiden Umstiegsszenarien die Monate des Parallelbetriebs von 60 ab. Multiplizieren Sie die Jahreskosten der beibehaltenen Microsoft-Lizenzen mit den verbleibenden Monaten und teilen Sie das Ergebnis durch 12. |
| `costs.formulas[4]` | The amount entered for lost working time forms its own cost block. | Für verlorene Arbeitszeit wird der angegebene Betrag angesetzt. |
| `readiness.title` | Where each area stands | Wo jeder Bereich steht |
| `readiness.next_step` | Next step | Nächster Schritt |
| `readiness.evidence_summary` | Evidence · {measured} measured, {provided} provided, {unknown} unknown | Nachweise · {measured} erhoben, {provided} bereitgestellt, {unknown} unbekannt |
| `readiness.all_replacements` | All replacements | Alle Ersatzlösungen |
| `filter.status_legend` | Show areas by status | Bereiche nach Status anzeigen |
| `filter.category_legend` | Show areas by category | Bereiche nach Kategorie anzeigen |
| `filter.all` | All | Alle |
| `filter.all_categories` | All categories | Alle Kategorien |
| `filter.empty` | No area matches this selection. Choose "All" to see every area. | Kein Bereich entspricht dieser Auswahl. Wählen Sie „Alle“, um alle Bereiche anzuzeigen. |
| `filter.search_hint` | Filtered-out areas and, in some browsers, closed sections are not searched. | Ausgeblendete Bereiche und, je nach Browser, geschlossene Abschnitte werden nicht durchsucht. |
| `moves.title` | What replaces what | Was wodurch ersetzt wird |
| `moves.workload_status` | Area status | Status des Bereichs |
| `moves.status_link` | {area}: {status} | {area}: {status} |
| `mapping_coverage.in_suite` | In the suite | In der Suite |
| `mapping_coverage.in_suite_with_limits` | In the suite with limits | In der Suite mit Einschränkungen |
| `mapping_coverage.open_source_community` | Open source community solution | Open-Source-Lösung der Community |
| `attention.title` | What needs a closer look | Was genauer zu prüfen ist |
| `path.title` | What to do next | Was als Nächstes zu tun ist |
| `path.even_if_staying` | Worth doing even if you stay | Sinnvoll, auch wenn Sie bleiben |
| `path.for_move` | Needed for a move | Für einen Umstieg nötig |
| `role.it_team` | IT team | IT-Abteilung |
| `role.licence_management` | Licence management | Lizenzverwaltung |
| `role.service_owner` | Service owner | Fachlich verantwortliche Stelle |
| `role.data_protection` | Data protection officer | Datenschutzbeauftragte |
| `role.information_security` | Information security officer | Informationssicherheitsbeauftragte |
| `role.procurement` | Procurement | Beschaffung |
| `appendix.title` | How this report was made | Wie dieser Bericht entstanden ist |
| `appendix.not_looked` | What Fazit does not look at | Was Fazit nicht betrachtet |
| `appendix.not_looked_text` | File contents, mail, data about individual people, departments, and the settings of the target system. | Dateiinhalte, E-Mails, Daten zu einzelnen Personen, Abteilungen und die Einstellungen des Zielsystems. |
| `reason.not_in_export.fix` | Ask the service owner for the missing information. Enter it in the inputs file if there is a matching field. | Erfragen Sie die fehlende Angabe bei der fachlich verantwortlichen Stelle. Tragen Sie sie in die Eingabedatei ein, sofern dort ein Feld dafür vorgesehen ist. |
| `reason.source_not_supplied.fix` | Find out which source can provide the missing information. It stays Unknown while it is absent from the scan and inputs file. | Klären Sie, aus welcher Quelle die fehlende Angabe stammt. Fehlt sie in der Erhebungsdatei und in der Eingabedatei, bleibt sie unbekannt. |
| `reason.needs_recipient_export.fix` | Ask the mail administrator to check the count separately. It stays Unknown in this report. | Lassen Sie die Zahl gesondert von der für E-Mail zuständigen Stelle ermitteln. Im Bericht bleibt sie unbekannt. |
| `reason.licence_plan_list_incomplete.fix` | Ask licence management to check which service plans belong to the product. | Lassen Sie durch die Lizenzverwaltung prüfen, welche Dienstpläne zum Produkt gehören. |
| `reason.not_recognised.fix` | Check the version of the tool that produced the scan and the reason code in the scan file. | Prüfen Sie die Version des Erhebungsprogramms und den Grundcode in der Erhebungsdatei. |
| `category.communication` | Communication | Kommunikation |
| `category.files` | Files and documents | Dateien und Dokumente |
| `category.identity_devices` | Identity and devices | Identität und Geräte |
| `category.automation_ai` | Automation and AI | Automatisierung und KI |
| `category.security` | Security and compliance | Sicherheit und Compliance |

### Site and documentation values

| Location | English | German |
| --- | --- | --- |
| READMEs | The report assesses fourteen areas. | Der Bericht bewertet vierzehn Bereiche. |
| Pilots pages | It covers dependencies, readiness across 14 areas, open source alternatives and a five-year cost comparison based on figures you supply. | Er zeigt Abhängigkeiten, die Bereitschaft in 14 Bereichen, mögliche Open-Source-Alternativen und einen Kostenvergleich über fünf Jahre auf Grundlage Ihrer Angaben. |
| Home-page tally | All 14 areas in the sample: 3 Ready, 9 Needs work, 1 Blocker, 1 Unknown. | Alle 14 Bereiche im Beispiel: 3 Bereit, 9 Handlungsbedarf, 1 Hindernis, 1 Unbekannt. |
| Report-card image alternative text | Readiness section of the sample report: 3 areas Ready, 9 Needs work, 1 Blocker, 1 Unknown. | Abschnitt zur Bereitschaft aus dem Beispielbericht: 3 Bereiche Bereit, 9 Handlungsbedarf, 1 Hindernis, 1 Unbekannt. |
| D-81 amendment, Phase 1.1 figure tile | 15 areas assessed, from AI agents to mail | 15 Bereiche, von KI-Agenten bis E-Mail |

### Rule next steps

| Rule | Kind | Action verb EN / DE | English | German |
| --- | --- | --- | --- | --- |
| `directory-guests` | `decide` | decides / entscheidet | The service owner decides which guest accounts should retain access. | Die fachlich verantwortliche Stelle entscheidet, welche Gastkonten weiterhin Zugriff erhalten. |
| `directory-accounts-not-reviewed` | `clarify` | checks / prüft | The IT team checks which accounts on the list are still needed. | Die IT-Abteilung prüft, welche der aufgeführten Konten noch benötigt werden. |
| `mail-other-systems` | `replace` | plans / plant | The IT team plans a new way for the affected systems to send mail. | Die IT-Abteilung plant für die betroffenen Systeme einen neuen Versandweg für E-Mails. |
| `onedrive-external-sharing` | `decide` | decides / entscheidet | The service owner decides which external recipients should retain access to shared files. | Die fachlich verantwortliche Stelle entscheidet, welche externen Empfänger weiterhin auf freigegebene Dateien zugreifen sollen. |
| `sharepoint-custom-solutions` | `clarify` | records / erfasst | The service owner records which processes rely on the custom site solutions. | Die fachlich verantwortliche Stelle erfasst, welche Arbeitsabläufe von den individuell angepassten Lösungen abhängen. |
| `teams-guests` | `replace` | plans / plant | The IT team plans how to manage guest access to team workspaces after the move. | Die IT-Abteilung plant, wie der Gastzugriff auf die gemeinsamen Arbeitsbereiche nach dem Umstieg verwaltet wird. |
| `teams-chat-history` | `clarify` | reviews / prüft | The data protection officer reviews which chat records the organisation is required to retain. | Die oder der Datenschutzbeauftragte prüft, welche Chatverläufe die Organisation aufbewahren muss. |
| `teams-audio-conferencing` | `clarify` | checks / prüft | The service owner checks which meetings still need a telephone dial-in. | Die fachlich verantwortliche Stelle prüft, für welche Besprechungen eine telefonische Einwahl benötigt wird. |
| `office-macro` | `clarify` | checks / prüft | The service owner checks which files contain macros that staff still use. | Die fachlich verantwortliche Stelle prüft, welche Dateien Makros enthalten, die die Beschäftigten noch nutzen. |
| `office-access` | `clarify` | records / erfasst | The service owner records the tasks staff carry out with the databases. | Die fachlich verantwortliche Stelle erfasst, für welche Aufgaben die Beschäftigten die Datenbanken nutzen. |
| `office-publisher` | `clarify` | checks / prüft | The service owner checks which layout files staff still need to edit. | Die fachlich verantwortliche Stelle prüft, welche Layoutdateien die Beschäftigten noch bearbeiten müssen. |
| `office-visio` | `clarify` | identifies / ermittelt | The service owner identifies the diagrams that staff need to keep editing. | Die fachlich verantwortliche Stelle ermittelt, welche Diagramme die Beschäftigten weiterhin bearbeiten müssen. |
| `office-onenote` | `replace` | tests / erprobt | The IT team tests a way to transfer the notebooks needed after the move. | Die IT-Abteilung erprobt die Übernahme der Notizbücher, die nach dem Umstieg benötigt werden. |
| `devices-managed` | `replace` | plans / plant | The IT team plans how to enrol the devices in a replacement management service. | Die IT-Abteilung plant, wie sie die Geräte in eine andere Geräteverwaltung aufnimmt. |
| `devices-windows` | `clarify` | checks / prüft | The IT team checks which devices are suitable for a different operating system. | Die IT-Abteilung prüft, welche Geräte sich für ein anderes Betriebssystem eignen. |
| `devices-add-on` | `clarify` | checks / prüft | Licence management checks which device management functions the assigned add-ons cover. | Die Lizenzverwaltung prüft, welche Funktionen der Geräteverwaltung die zugewiesenen Zusatzlizenzen abdecken. |
| `software-no-web-version` | `decide` | decides / entscheidet | The service owner decides which applications without a web version must remain available after the move. | Die fachlich verantwortliche Stelle entscheidet, welche Anwendungen ohne Webversion nach dem Umstieg verfügbar bleiben müssen. |
| `software-present` | `clarify` | records / erfasst | The service owner records which tasks rely on the applications in the inventory. | Die fachlich verantwortliche Stelle erfasst, welche Aufgaben von den Anwendungen in der Bestandsliste abhängen. |
| `power-premium-licences` | `clarify` | identifies / ermittelt | Licence management identifies the applications and workflows that rely on the assigned add-ons. | Die Lizenzverwaltung ermittelt, welche Anwendungen und Abläufe auf die zugewiesenen Zusatzlizenzen angewiesen sind. |
| `power-in-use` | `replace` | plans / plant | The IT team plans a replacement for the applications and workflows needed after the move. | Die IT-Abteilung plant eine Ersatzlösung für die Anwendungen und Abläufe, die nach dem Umstieg weiter benötigt werden. |
| `telephony-no-replacement` | `replace` | plans / plant | The IT team plans a replacement that keeps the required phone services running during the move. | Die IT-Abteilung plant eine Ersatzlösung, mit der die benötigten Telefondienste beim Umstieg weiterlaufen können. |
| `telephony-in-use` | `replace` | tests / erprobt | The IT team tests the available replacement against the organisation's call flows. | Die IT-Abteilung erprobt die verfügbare Ersatzlösung anhand der benötigten Anrufabläufe. |
| `telephony-unused-add-on` | `decide` | decides / entscheidet | Licence management decides whether to retain the assigned telephony licences. | Die Lizenzverwaltung entscheidet, ob die zugewiesenen Telefonielizenzen beibehalten werden. |
| `identity-sso-applications` | `replace` | plans / plant | The IT team plans how to connect the affected applications to a replacement sign-in service. | Die IT-Abteilung plant die Anbindung der betroffenen Anwendungen an einen anderen Dienst für die zentrale Anmeldung. |
| `identity-conditional-access` | `clarify` | records / erfasst | The information security officer records the conditions under which the organisation currently grants access. | Die oder der Informationssicherheitsbeauftragte erfasst, unter welchen Bedingungen die Organisation derzeit Zugriff gewährt. |
| `identity-add-on` | `clarify` | checks / prüft | Licence management checks which access functions the assigned add-ons cover. | Die Lizenzverwaltung prüft, welche Zugriffsfunktionen die zugewiesenen Zusatzlizenzen abdecken. |
| `security-in-use` | `replace` | plans / plant | The information security officer plans how the replacement will meet the protection and retention requirements. | Die oder der Informationssicherheitsbeauftragte plant, wie die Ersatzlösung die Anforderungen an Schutz und Aufbewahrung erfüllt. |
| `security-add-on` | `clarify` | records / erfasst | Licence management records which protection and retention functions depend on the assigned add-ons. | Die Lizenzverwaltung erfasst, für welche Schutz- und Aufbewahrungsfunktionen die zugewiesenen Zusatzlizenzen benötigt werden. |
| `small-apps-in-use` | `decide` | decides / entscheidet | The service owner decides which forms, tasks or bookings need to remain available after the move. | Die fachlich verantwortliche Stelle entscheidet, welche Formulare, Aufgaben oder Buchungen nach dem Umstieg verfügbar bleiben müssen. |
| `integrations-present` | `clarify` | records / erfasst | The IT team records what data each integration transfers and what actions it triggers. | Die IT-Abteilung erfasst, welche Daten jede Schnittstelle überträgt und welche Vorgänge sie auslöst. |

## Finding owners

Admin-centre measurements and the inventory questions assigned to the IT lead use the IT team. The contract review belongs to procurement. Questions about external sharing, custom site solutions, automation and smaller applications go to the departments using them. Chat history retention goes to data protection, and the combined protection and retention question goes to information security.

| Finding | Owner role |
| --- | --- |
| `licences.contract_terms_known` | `procurement` |
| `directory.user_count` | `it_team` |
| `directory.licensed_user_count` | `it_team` |
| `directory.guest_count` | `it_team` |
| `directory.group_count` | `it_team` |
| `directory.account_list_reviewed` | `it_team` |
| `mail.mailbox_count` | `it_team` |
| `mail.shared_mailbox_count` | `it_team` |
| `mail.storage_bytes` | `it_team` |
| `mail.item_count` | `it_team` |
| `mail.other_systems_send_mail` | `it_team` |
| `onedrive.account_count` | `it_team` |
| `onedrive.storage_bytes` | `it_team` |
| `onedrive.external_sharing_in_use` | `service_owner` |
| `sharepoint.site_count` | `it_team` |
| `sharepoint.storage_bytes` | `it_team` |
| `sharepoint.file_count` | `it_team` |
| `sharepoint.custom_solutions_in_use` | `service_owner` |
| `teams.team_count` | `it_team` |
| `teams.channel_count` | `it_team` |
| `teams.teams_with_guests_count` | `it_team` |
| `teams.chat_history_must_be_kept` | `data_protection` |
| `office_files.kind.macro` | `it_team` |
| `office_files.kind.access` | `it_team` |
| `office_files.kind.publisher` | `it_team` |
| `office_files.kind.visio` | `it_team` |
| `office_files.kind.onenote` | `it_team` |
| `device_management.device_count` | `it_team` |
| `device_management.windows_device_count` | `it_team` |
| `device_management.in_use` | `it_team` |
| `device_management.windows_desktops_required` | `it_team` |
| `windows_software.application_count` | `it_team` |
| `windows_software.without_web_version_count` | `it_team` |
| `power_platform.in_use` | `service_owner` |
| `telephony.in_use` | `it_team` |
| `telephony.replacement_available` | `it_team` |
| `identity_access.sso_application_count` | `it_team` |
| `identity_access.conditional_access_in_use` | `it_team` |
| `security_compliance.protection_or_retention_in_use` | `information_security` |
| `small_apps.in_use` | `service_owner` |
| `integrations.application_count` | `it_team` |

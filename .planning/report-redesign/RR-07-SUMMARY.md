---
phase: report-redesign
plan: "07"
subsystem: report
tags: [readiness, target-profiles, mappings, bilingual-copy]
requires:
  - phase: RR-01
    provides: Fourteen assessed areas, bilingual next steps and finding owner roles
  - phase: RR-06
    provides: Explicit Windows desktop need and interview answers for SharePoint workflows and VBA
provides:
  - Profile-aware readiness and shared transfer-gap evidence
  - Three updated mappings with operator-review status
  - Scope statement data and refreshed site demos
affects: [RR-02, RR-03, RR-04, RR-05, RR-08]
actuals:
  tokens: 54189
  tasks: 3
  commits: 0
tech-stack:
  added: []
  patterns: [Data-driven target rules, Shared transfer-gap evidence]
key-files:
  created: [.planning/report-redesign/RR-07-SUMMARY.md]
  modified:
    - DECISIONS.md
    - src/fazit/mappings.py
    - src/fazit/status.py
    - src/fazit/report.py
    - src/fazit/rules/mappings/opendesk.yaml
    - src/fazit/rules/mappings/nextcloud.yaml
    - src/fazit/rules/mappings/generic.yaml
    - src/fazit/rules/status.yaml
    - src/fazit/templates/report.html.j2
    - src/fazit/locales/en.yaml
    - src/fazit/locales/de.yaml
    - tests/test_rules.py
    - tests/test_simulation.py
    - site/index.html
    - site/de/index.html
    - site/demo/en/index.html
    - site/demo/de/index.html
key-decisions:
  - D32 makes readiness depend on the chosen profile's transfer gaps.
  - Both target next steps are replace actions because they concern work for a move.
patterns-established:
  - WorkloadStatus.transfer_gaps supplies the need and reason for the gap list and scope statement.
  - A target rule uses the same reason, condition and next-step interface as a workload rule.
requirements-completed: [RULE-01, RULE-02, RULE-03, RULE-04, I18N-01, I18N-02]
coverage:
  - id: D1
    description: Mapping validation, review notices, gap labels and anchors work in both report languages.
    requirement: RULE-04
    verification:
      - kind: integration
        ref: tests/test_rules.py#test_bad_mapping_names_the_file_and_field
        status: pass
      - kind: integration
        ref: tests/test_rules.py#test_reviewed_mapping_shows_the_date
        status: pass
      - kind: integration
        ref: tests/test_rules.py#test_attention_lists_each_transfer_gap_from_the_profile
        status: pass
    human_judgment: false
  - id: D2
    description: Target needs affect readiness and preserve the evidence and precedence of workload rules.
    requirement: RULE-03
    verification:
      - kind: integration
        ref: tests/test_rules.py#test_target_gaps_reach_readiness_and_appendix
        status: pass
      - kind: unit
        ref: tests/test_rules.py#test_evaluation_applies_profile_gaps_after_workload_rules
        status: pass
      - kind: unit
        ref: tests/test_simulation.py#test_target_gaps_cannot_improve_readiness
        status: pass
    human_judgment: false
  - id: D3
    description: Scope data matches both tables and the checked-in reports match the package.
    requirement: RULE-01
    verification:
      - kind: integration
        ref: tests/test_rules.py#test_scope_statement_matches_the_replacements_and_gap_lists
        status: pass
      - kind: integration
        ref: tests/test_rules.py#test_marking_a_mapping_as_a_transfer_gap_adds_it_to_the_gap_list
        status: pass
      - kind: integration
        ref: uv run python site/check_site.py
        status: pass
    human_judgment: false
  - id: D4
    description: The bilingual mapping claims and target actions await maintainer and operator review.
    requirement: I18N-01
    verification: []
    human_judgment: true
    rationale: Native German usage and coverage of real deployments need human review before release.
duration: 25 min from the first sample baseline to the final automated checks
completed: 2026-11-22
status: complete
---

# RR-07 summary

The chosen profile now affects readiness through the organisation’s documented needs. The same transfer-gap evidence supplies readiness, the gap list and the scope data for RR-03.

All three tasks ran in order from `eafd482`. The implementation and this summary are in the working tree.

## Changes by task

### Task 1 — Mapping sources and review status

- `src/fazit/mappings.py` adds `transfer_undocumented` and `GAP_COVERAGE`. The loader requires a registered need finding for each gap and reads `operator_review` as `None` for `unreviewed` or as a calendar date.
- The three files in `src/fazit/rules/mappings/` mark SharePoint workflows, Teams chat history and VBA macros as direct transfers with no documented method. All three carry `operator_review: unreviewed`. The openDesk file adds XWiki, Notes and CryptPad with diagrams.net, updates two notes and uses the plan’s source references dated 2026-11-22 on all 22 rows.
- `src/fazit/report.py` selects both gap coverages. `src/fazit/templates/report.html.j2` anchors each gap by its function, uses its coverage label as the fallback, and shows the review notice beneath the replacements heading and in the mapping appendix. Both locale files carry the bilingual text.
- `tests/test_rules.py` verifies the shipped coverage data, the three new validation cases, the review notices in both languages, the gap anchors and the fallback labels.

### Task 2 — Target-aware readiness

- `src/fazit/status.py` evaluates each workload first, computes transfer needs from those results, then applies the selected profile’s gaps. A confirmed need can set Needs work or append a note to a decided area. An unresolved need adds missing evidence and withholds Ready. The evaluator keeps incomplete evidence and the deciding workload rule wherever one exists.
- `src/fazit/rules/status.yaml` holds two bilingual Needs work templates. The loader uses the shared rule ID and next-step validation and checks both reason placeholders with `Formatter.parse`. `DECISIONS.md` records D32.
- `src/fazit/report.py` rebuilds the existing gap list from the ordered `TransferGap` objects. `src/fazit/templates/report.html.j2` includes fired target rules and their conditions in the appendix after the workload’s own fired rules.
- `tests/test_rules.py` covers those rules in evaluation and in both report languages, including invalid YAML values, precedence, next steps and conditions. `tests/test_simulation.py` compares every profile with a copy whose gap rows have suite coverage. The existing `tests/test_evidence_cli.py` assertions passed as written.

### Task 3 — Scope data and site reports

- `src/fazit/report.py` exposes a frozen `ScopeStatement` for openDesk and Nextcloud. Its counts come from the replacements mapping, and its needed labels and anchors come from the same transfer gaps as the report. Generic returns `None`. RR-03 owns the display.
- `tests/test_rules.py` compares the data with the rendered coverage labels and gap list for both samples, both languages and both product profiles. A copied mapping tests that a coverage change reaches both the scope data and the table.
- Fresh town openDesk builds replaced `site/demo/en/index.html` and `site/demo/de/index.html`. The openDesk SharePoint and Office-file cells in `site/index.html` and `site/de/index.html` list the new replacements. Both demos retain 3 Ready, 9 Needs work, 1 Blocker and 1 Unknown, so the existing tally and alternative text match the new reports.

## Interfaces

```python
evaluate(
    findings: Mapping[str, Finding],
    rule_set: StatusRuleSet,
    catalogue: Catalogue,
    mapping: TargetMapping,
    *,
    collectors: Mapping[str, Collector] | None = None,
    alternatives: Mapping[str, Finding] | None = None,
) -> tuple[WorkloadStatus, ...]

TransferGap(
    mapping: FunctionMapping, finding: Finding | None, need: str, reasons: tuple[str, ...]
)
TargetGapRule(id: str, status: str, reason: Mapping[str, str], next_step: NextStep)
WorkloadStatus(
    workload: str,
    status: str,
    reason_code: str | None,
    missing: tuple[MissingEvidence, ...],
    deciding: StatusRule | None,
    notes: tuple[StatusRule, ...],
    evidence: tuple[Finding, ...],
    transfer_gaps: tuple[TransferGap, ...] = (),
)
TargetMapping(
    profile: str,
    label: Mapping[str, str],
    description: Mapping[str, str],
    product_profile: bool,
    reviewed_on: date | None,
    no_function: tuple[str, ...],
    functions: tuple[FunctionMapping, ...],
    file_name: str,
)
ScopeStatement(
    profile: str,
    total: int,
    by_coverage: tuple[tuple[str, int], ...],
    needed: tuple[tuple[str, str], ...],
    unknown_need: int,
    reviewed_on: date | None,
)
scope_statement(
    mapping: TargetMapping, statuses: tuple[WorkloadStatus, ...], lang: str
) -> ScopeStatement | None
```

`StatusRuleSet.target_gaps` maps coverage IDs to templates. Fired target rules are `StatusRule` values in `row.deciding` or `row.notes`. `TransferGap.finding` is the selected observation when one exists. `TransferGap.mapping.need_finding` is the catalogue ID even when the answer is missing. The rendered gap list still receives the four-item tuples `(mapping, finding, need, reasons)`.

RR-06’s `sharepoint.workflows_in_use` and `office_files.vba_macros_in_use` drive the workflow and VBA gaps in all three profiles. Both have `owner: service_owner`. Teams chat history uses the existing `teams.chat_history_must_be_kept` finding with `owner: data_protection`.

## Sample comparison with RR-06

The baseline was captured before editing. All six sample and profile pairs preserve their statuses and deciding rules. The non-profit totals are 7 Ready, 5 Needs work, 0 Blockers and 2 Unknown under each profile.

| Sample | Profile | Area | Change from RR-06 and the gap that caused it |
| --- | --- | --- | --- |
| Town | openDesk | Office files | Incomplete after `vba_macros` adds the missing VBA need answer. |
| Town | openDesk | Device management | Incomplete after `desktop_operating_system` adds the missing Windows desktop answer. The `device_management` gap adds a note after `devices-windows`. |
| Town | openDesk | Windows-only software | `windows_applications` adds a note after `software-present`. |
| Town | openDesk | Power Platform | `automation_and_low_code` adds a note after `power-in-use`. |
| Town | openDesk | Telephony | `telephony` adds a note to the existing Blocker. |
| Town | Nextcloud Hub | Office files | Incomplete after `vba_macros` adds the missing VBA need answer. |
| Town | Nextcloud Hub | Device management | Incomplete after `desktop_operating_system` adds the missing Windows desktop answer. The `device_management` gap adds a note after `devices-windows`. |
| Town | Nextcloud Hub | Windows-only software | `windows_applications` adds a note after `software-present`. |
| Town | Generic | Office files | Incomplete after `vba_macros` adds the missing VBA need answer. |
| Town | Generic | Windows-only software | `windows_applications` adds a note after `software-present`. |
| Non-profit | openDesk | Device management | Incomplete after `desktop_operating_system` adds the missing Windows desktop answer. |
| Non-profit | Nextcloud Hub | Device management | Incomplete after `desktop_operating_system` adds the missing Windows desktop answer. |
| Non-profit | Generic | — | No changed rows. |

The town’s SharePoint workflow answer was already listed under missing evidence and appears once on its area row. The constructed comparison shows Telephony as Needs work and incomplete on openDesk and Unknown on Nextcloud and generic. With complete underlying device checks and an unanswered Windows desktop need, Device management is Unknown on openDesk and Nextcloud and Ready on generic. Confirmed Teams chat history need keeps `teams-chat-history` as the deciding rule on all three profiles and adds a target note.

## Scope statements

The profile labels and totals apply to both samples. Counts are in ladder order. `reviewed_on` is `None` for all eight scope statements.

| Profile label in both languages | Total | English coverage labels and counts | German coverage labels and counts |
| --- | ---: | --- | --- |
| openDesk | 22 | In the suite 6, In the suite with limits 8, Direct transfer undocumented 3, Not available 5 | In der Suite 6, In der Suite mit Einschränkungen 8, Direkte Übernahme nicht dokumentiert 3, Nicht verfügbar 5 |
| Nextcloud Hub | 19 | In the suite 3, In the suite with limits 9, Open source community solution 1, Direct transfer undocumented 3, Not available 3 | In der Suite 3, In der Suite mit Einschränkungen 9, Open-Source-Lösung der Community 1, Direkte Übernahme nicht dokumentiert 3, Nicht verfügbar 3 |

| Sample | Profile | Needed functions in order, in both languages | Unknown need |
| --- | --- | --- | ---: |
| Town | openDesk | Device management, Windows applications, Power Platform, telephony | 3 |
| Town | Nextcloud Hub | Device management, Windows applications | 3 |
| Non-profit | openDesk | Empty | 1 |
| Non-profit | Nextcloud Hub | Empty | 1 |

| Gap anchor ID | English function label | German function label |
| --- | --- | --- |
| `transfer-gap-device_management` | Device management with Microsoft Intune | Geräteverwaltung mit Microsoft Intune |
| `transfer-gap-windows_applications` | Running Windows-only applications | Betrieb reiner Windows-Anwendungen |
| `transfer-gap-automation_and_low_code` | Power Platform automation and low-code applications | Automatisierung und Low-Code-Anwendungen mit Power Platform |
| `transfer-gap-telephony` | Teams Phone and public telephone calling | Teams Phone und Anrufe ins öffentliche Telefonnetz |

The three Unknown needs for both town scope statements are SharePoint workflows, VBA macros and the Windows desktop operating system. The non-profit’s Unknown need in both profiles is the Windows desktop operating system. The generic scope value is `None` for both samples and languages.

## Verification

Each task’s `<automated>` chain exited successfully before the next task began.

| Check | Result |
| --- | --- |
| Task 1 regression before implementation | 9 expected failures in 2.11 s. Missing review metadata and gaps without need findings were accepted, the invalid review date named the wrong field, and the six reports lacked the notice. JUnit evidence returned `RED_EVIDENCE_OK`. |
| Task 1 focused and automated runs | Focused suite 41 passed in 4.96 s. The final Task 1 chain passed 187 rule tests in 17.48 s and 828 full-suite tests in 141.24 s. Both Ruff checks, the loader checks and the German report label, notice and anchor checks passed. The first chain reached Ruff after 828 passing tests and flagged three long test lines. The rerun passed after wrapping the strings. |
| Task 1 mapping acceptance | Row counts 22, 19 and 19. Need binding counts 8, 6 and 5. Three transfer-only rows and one unreviewed marker per profile. All 22 openDesk dates and source references match the plan. The generic file has zero mentions of XWiki, Notes or CryptPad. |
| Task 2 regression before implementation | 6 expected failures in 2.08 s. The openDesk phone case was Unknown, the Nextcloud device case was Ready and the generic Teams appendix lacked the target rule. JUnit evidence returned `RED_EVIDENCE_OK`. |
| Task 2 focused and automated runs | Focused tests 81 passed in 14.17 s. The full evidence CLI file passed 138 tests in 21.55 s. Task 2’s chain passed 236 rule and simulation tests in 81.16 s and 851 full-suite tests in 151.18 s. Both Ruff checks, the template-loader assertion, and the openDesk and Nextcloud English demo assertions passed. |
| Task 2 baseline acceptance | 32 workload rules and one Blocker rule. That YAML block, `STATUSES` and `_evaluate_workload` match RR-06. `evaluate` takes `mapping` before the keyword-only arguments, and report code reads the rows’ gaps. The D31 entry, scan loader, validator, findings catalogue, service plan catalogue, licence reconciliation and cost model match RR-06. The rv11 excess-seat and repeated-part-number regressions pass. |
| Task 3 regression before implementation | 9 expected failures in 1.94 s because the context lacked `scope_statement`. JUnit evidence returned `RED_EVIDENCE_OK`. The pre-update site check reported the four expected cell mismatches and the two stale demos. |
| Task 3 focused and automated runs | 11 scope and copied-mapping tests passed in 2.52 s. The final `uv run pytest -q` passed **860 tests in 156.09 s**. `uv run ruff check .` passed and `uv run ruff format --check .` reported 155 formatted files. The scope import and both fresh demo commands exited 0, and both printed paths resolved to report files. `uv run python site/check_site.py` checked 18 pages and 616 references and printed “No errors.” |
| Final report and site checks | The site checker verified byte-for-byte matches to fresh town openDesk builds. The home-page comparison found exactly two changed cells per language. The report template retains the original CSS and CSP, including both embedded fonts. The licence inventory and cost sections match the baseline template. The scope context exists and the template has zero scope references. `git diff --check` passed. |
| Offline browser and print | Chromium opened both checked-in demos with scripting disabled and network access blocked. At 360 px in light and dark modes, both fonts loaded, the review notices and all eight anchors appeared, and there were zero HTTP requests or horizontal overflow. The A4 PDF text in both languages includes the review notice. |

## Existing test edits

| Test in `tests/test_rules.py` | Basis | Assertion or fixture adjustment |
| --- | --- | --- |
| `test_shipped_mapping_covers_every_workload` | C5 | Check the 19 shared functions in order, the three extra openDesk positions and coverage, the exact three transfer-only rows, review state, need bindings and citation dates. Keep the duplicate, workload coverage and generic restrictions. |
| `test_generic_mapping_names_no_target_products` | C5 | Extend the product list with XWiki, Notes and CryptPad. |
| `test_bad_mapping_names_the_file_and_field` | C5 | Add cases for missing review, invalid review date and missing gap need. Keep the previous cases and diagnostic assertion. |
| `test_attention_lists_each_unavailable_function_from_the_profile` | C5 | Rename to `test_attention_lists_each_transfer_gap_from_the_profile`, select both gap codes and assert the named function’s anchor. Keep the mapping order, note, source and date checks. |
| `test_gap_need_uses_only_its_declared_complete_answer` | C5 | Read the renamed Teams coverage and require a need finding for every gap. Keep the four need and provenance cases. |
| `test_marking_a_mapping_unavailable_adds_it_to_the_gap_list` | C5 and criterion 24 | Rename to `test_marking_a_mapping_as_a_transfer_gap_adds_it_to_the_gap_list`. Give the changed row a valid need finding and leave the answer absent. Assert Unknown and the fallback label for both gap codes. Task 3 also compares the before and after scope and table counts. |
| `test_telephony_needs_replacement_or_explicit_non_use` | C1 | With confirmed use and no replacement answer, require incomplete Needs work and the target rule for openDesk. Keep the missing replacement and licence evidence checks and all other cases. A new case verifies Unknown under the other profiles. |
| `test_worst_rule_wins_and_ties_keep_file_order` | C1 | Require the Windows application target note after the existing `software-present` note and assert its positive-count condition. The synthetic Blocker still decides. |
| `test_skipped_collector_cannot_make_a_workload_ready` and `_status` | C1 | Supply the required openDesk mapping argument. The existing assertions stay in force. |
| `test_removing_a_workloads_evidence_never_gives_ready` | C1 | Run the original order, Ready and evidence-removal assertions under all three profiles. Complete evidence also reports No for every gap. |
| `test_shipped_status_rules_define_each_assessed_workload` | C1 | Expect the additional `target_gaps` block and require the exact 32 workload rules separately. |
| `test_bad_status_rule_names_the_file_and_field` | C1 | Extend the existing file and field checks to target templates, including allowed coverage and status, IDs, placeholders and next-step kind. |
| `test_all_problem_rules_have_bilingual_product_neutral_next_steps` | C1 | Apply the existing language, sentence and banned-word assertions to both templates. Check allowed kinds and the shipped `replace` kinds. |
| `test_only_blocker_rules_can_describe_a_blocker` | C1 | Apply the existing wording check to both target templates. |

## Deviations and implementation choices

- Task 1 changes the gap selector in `report.py`, where RR-06 computed the gap list. This makes the two gap coverage codes work in Task 1 before Task 2 moves the calculation into `status.py`.
- The copied-mapping test uses the report renderer with an explicitly unanswered registered finding. The old fixture lacked the need field now required by Task 1. Using the report context in Task 3 lets the test compare scope data with HTML from the same render.
- The run uses the current RR-06 and rv11 sources and the coordinator’s home-page amendment. The updated coverage cells preserve their existing badge, wording pattern and markup. The actual sample comparison includes Nextcloud and generic target notes in addition to the openDesk examples in the plan.
- The working-tree handoff follows the user’s instruction in place of the generic GSD workflow’s commit and phase bookkeeping. The red and green runs used the existing environment under `UV_OFFLINE=1` and `UV_NO_SYNC=1`.

## Native German review

| Location | English | German |
| --- | --- | --- |
| `opendesk.intranet_pages.microsoft` | SharePoint pages and intranet sites | SharePoint-Seiten und Intranet-Websites |
| `opendesk.intranet_pages.replacement` | XWiki | XWiki |
| `opendesk.intranet_pages.note` | The knowledge module documents wiki pages, subpages, further wikis and access rights per page. It names no way to carry over existing SharePoint pages or site structure. | Das Modul Wissen beschreibt Wikiseiten, Unterseiten, weitere Wikis und Zugriffsrechte für einzelne Seiten. Eine Übernahme vorhandener SharePoint-Seiten oder Website-Strukturen ist dort nicht beschrieben. |
| `opendesk.notes.microsoft` | OneNote notebooks | OneNote-Notizbücher |
| `opendesk.notes.replacement` | Notes | Notes |
| `opendesk.notes.note` | The component list includes Notes for collaborative notes. Its guide is only available inside the installed application, and no public documentation describes carrying over OneNote notebooks. | Die Komponentenübersicht nennt Notes für gemeinsame Notizen. Die Anleitung ist nur in der installierten Anwendung verfügbar, und eine Übernahme von OneNote-Notizbüchern ist öffentlich nicht dokumentiert. |
| `opendesk.diagrams.microsoft` | Visio diagrams | Visio-Diagramme |
| `opendesk.diagrams.replacement` | CryptPad with diagrams.net | CryptPad mit diagrams.net |
| `opendesk.diagrams.note` | The architecture names CryptPad for editing diagrams.net documents. It does not say whether existing Visio files can be opened or converted. | Laut Architekturdokumentation dient CryptPad zur Bearbeitung von diagrams.net-Dokumenten. Ob vorhandene Visio-Dateien geöffnet oder konvertiert werden können, geht daraus nicht hervor. |
| `opendesk.security_and_compliance.note` | The architecture documents malware scanning of uploaded files and mail attachments. It does not document organisation-wide retention or legal holds. | Die Architekturdokumentation beschreibt die Prüfung hochgeladener Dateien und E-Mail-Anhänge auf Schadsoftware. Organisationsweite Aufbewahrung und Sperren für Rechtsverfahren sind dort nicht beschrieben. |
| `opendesk.forms_tasks_bookings.note` | The task guide covers tasks with reminders, status and members. It describes no general forms or public appointment booking. | Die Anleitung zu Aufgaben beschreibt Aufgaben mit Erinnerungen, Status und Beteiligten. Allgemeine Formulare und eine öffentliche Terminbuchung sind dort nicht beschrieben. |
| `mapping_coverage.transfer_undocumented` | Direct transfer undocumented | Direkte Übernahme nicht dokumentiert |
| `moves.unreviewed` | This mapping has not yet been reviewed by someone who operates the target system. | Diese Zuordnung wurde noch nicht von einer Person geprüft, die das Zielsystem betreibt. |
| `moves.reviewed` | This mapping was reviewed on {date} by someone who operates the target system. | Diese Zuordnung wurde am {date} von einer Person geprüft, die das Zielsystem betreibt. |
| Home coverage cell, SharePoint / openDesk | With limits: Shared folders in Nextcloud Files · Separate redesign of workflows · XWiki | Mit Einschränkungen: Gemeinsame Ordner in Nextcloud Files · Gesonderte Neugestaltung der Arbeitsabläufe · XWiki |
| Home coverage cell, Office files / openDesk | With limits: Collabora Online · Separate conversion or redevelopment · Notes · CryptPad with diagrams.net | Mit Einschränkungen: Collabora Online · Gesonderte Konvertierung oder Neuentwicklung · Notes · CryptPad mit diagrams.net |

| Rule field | Kind and verb | English | German |
| --- | --- | --- | --- |
| `target-transfer-undocumented.reason` | — | The {profile} target profile documents no direct transfer for {function}, which this organisation needs. | Für „{function}“ dokumentiert das Zielprofil „{profile}“ keine direkte Übernahme, und die Organisation benötigt diese Funktion. |
| `target-transfer-undocumented.next_step` | `replace` · plan and test / planen und erproben | The service owner and the IT team plan how the existing content is carried over or rebuilt, and test that method before a move. | Die fachlich verantwortliche Stelle und die IT-Abteilung planen, wie die bestehenden Inhalte übernommen oder neu aufgebaut werden, und erproben dieses Vorgehen vor einem Umstieg. |
| `target-not-available.reason` | — | The {profile} target profile lists no solution for {function}, which this organisation needs. | Das Zielprofil „{profile}“ nennt für „{function}“ keine Lösung, und die Organisation benötigt diese Funktion. |
| `target-not-available.next_step` | `replace` · decide / entscheiden | The service owner and the IT team decide how this function is provided after a move. | Die fachlich verantwortliche Stelle und die IT-Abteilung entscheiden, wie diese Funktion nach einem Umstieg bereitgestellt wird. |

Planning and testing a way to carry content over serves the move. Deciding how to provide a function after the move likewise addresses replacement, which is why both actions use `replace`.

## Open reviews and handoff

Native German review of the table and action kinds remains open. The operator review of all three mapping files and the target-gap templates is the founder’s gate before the redesigned report ships. The review record can identify the operator. The mapping records only the review date.

| Review item | Profiles | Question for the operator review |
| --- | --- | --- |
| SharePoint pages and wiki content | Nextcloud Hub, generic | Which coverage class fits Collectives given its CollectiveCloud maintenance? Which generic solution type and transfer limitations can the mapping substantiate? |
| OneNote notebooks | Nextcloud Hub, generic | Which notes capability can the profile name, and what can be carried over from existing notebooks? |
| Visio diagrams | Nextcloud Hub, generic | Is a diagram editor part of the supported Nextcloud deployment? Which generic solution type and transfer limits can be documented? |
| XWiki applications and `automation_and_low_code` | openDesk | What does the shipped XWiki applications feature cover, and which Power Platform use cases still need separate redevelopment? |
| `device_management` | openDesk, Nextcloud Hub | Is enrolment and device policy enforcement supplied by the profile or by a separately operated service? |
| `desktop_operating_system` | openDesk, Nextcloud Hub | Which parts of managing a workstation operating system require separate provision, and which device, peripheral and application needs remain for the operator to check? |
| `windows_applications` | openDesk, Nextcloud Hub, generic | Which Windows application hosting or replacement options can the operator substantiate, and what dependencies need checking per application? |
| `telephony` | openDesk | What covers office extensions, number routing and public calls beyond meeting dial-in, and what requires a separate telephone service? |
| Transfer-only rows and rule actions | All three | What can be evidenced for SharePoint workflows, Teams chat history and VBA, and do the two Needs work actions reflect what operators would need to arrange? |

RR-02 can read `row.transfer_gaps` in mapping order and put a needed gap first. RR-03 has the scope object, matching gap anchors and review date for the summary. RR-04 can use the ordinary `StatusRule.next_step` interface and the existing gap list. RR-05 records the operator gate.

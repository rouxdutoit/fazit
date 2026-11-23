---
phase: report-redesign
plan: "06"
subsystem: report
tags: [readiness, mappings, validation, bilingual-copy]
requires:
  - phase: RR-01
    provides: Fourteen assessed areas, bilingual next steps with a kind, and finding owner roles
provides:
  - Explicit Windows desktop need and catalogue-driven validation of supplied subsets
  - Teams and SharePoint readiness evidence and interview-controlled workflow and VBA transfer needs
  - Simulated provenance labels, a fictional inventory heading, and a tested scan format reference
affects: [RR-07, RR-02, RR-03, RR-04]
actuals:
  tokens: 35587
  tasks: 3
  commits: 0
tech-stack:
  added: []
  patterns: [Catalogue-driven input validation, Scan-level provenance wording]
key-files:
  created: [docs/scan-format.md, .planning/report-redesign/RR-06-SUMMARY.md]
  modified:
    - src/fazit/mappings.py
    - src/fazit/inputs.py
    - src/fazit/report.py
    - src/fazit/rules/findings.yaml
    - src/fazit/rules/status.yaml
    - src/fazit/templates/report.html.j2
key-decisions:
  - Use the declared need finding for each transfer gap.
  - Compare an answer count with its catalogue populations when one inputs file supplies all of them.
  - Use the VBA answer for transfer need and assess Office files from the file counts.
patterns-established:
  - The sample scan determines the displayed provenance word for every measured observation.
  - The scan reference example is loaded and rendered in the test suite.
requirements-completed: [RULE-02, RULE-03, RULE-05, COST-01, COST-06, MODL-01, MODL-03, MODL-04]
coverage:
  - id: D1
    description: The Windows desktop gap follows its own answer and only Blocker rules may use blocker language.
    requirement: RULE-05
    verification:
      - kind: integration
        ref: tests/test_evidence_cli.py#test_desktop_gap_keeps_a_no_answer_with_windows_only_software
        status: pass
      - kind: unit
        ref: tests/test_rules.py#test_only_blocker_rules_can_describe_a_blocker
        status: pass
    human_judgment: false
  - id: D2
    description: Contradictory subset counts in one inputs file fail with a field-specific error.
    requirement: MODL-03
    verification:
      - kind: integration
        ref: tests/test_inputs.py#test_report_refuses_contradictory_input_counts
        status: pass
    human_judgment: false
  - id: D3
    description: Teams and SharePoint require the new answers for Ready, and the workflow and VBA gaps use their own answers in every profile.
    requirement: RULE-02
    verification:
      - kind: unit
        ref: tests/test_rules.py#test_sharepoint_and_teams_require_the_new_answers_for_ready
        status: pass
      - kind: integration
        ref: tests/test_rules.py#test_workflow_and_vba_gaps_follow_their_own_answers
        status: pass
      - kind: unit
        ref: tests/test_rules.py#test_shipped_risky_extensions
        status: pass
    human_judgment: false
  - id: D4
    description: Both sample languages label their measured evidence and fictional inventory.
    requirement: MODL-04
    verification:
      - kind: integration
        ref: tests/test_cli.py#test_sample_reports_label_simulated_measurements_and_fictional_inventory
        status: pass
    human_judgment: false
  - id: D5
    description: The scan format names the loader fields and codes and includes a working non-sample example.
    requirement: MODL-01
    verification:
      - kind: integration
        ref: tests/test_model.py#test_scan_format_document_matches_the_loader
        status: pass
    human_judgment: false
  - id: D6
    description: The German copy, next-step kinds and scan format reference are ready for maintainer review.
    verification: []
    human_judgment: true
    rationale: The review covers administrative register, action wording, and the accuracy and tone of the reference.
duration: 22 min from the first recorded baseline to final verification
completed: 2026-11-22
status: complete
---

# RR-06 summary

The desktop transfer gap follows the organisation’s explicit answer. Teams and SharePoint need answers about apps and workflows before they can be Ready. Sample reports label their simulated evidence, and the scan format has a working example.

All three tasks ran in order from `9cb7e91`, which includes rv11 from `2e4fae1`. The 29 implementation files and this summary are in the working tree.

## Changes by task

### Task 1 — Windows evidence and supplied counts

- `src/fazit/mappings.py`, `src/fazit/report.py` and the `opendesk.yaml`, `nextcloud.yaml` and `generic.yaml` files in `src/fazit/rules/mappings/` remove the inference from applications without web versions to Windows desktop need. Both locales drop the obsolete desktop conflict reason.
- `src/fazit/rules/status.yaml` distinguishes running an application on Windows from using Windows on staff workstations. `software-no-web-version` retains its condition and Needs work status and uses a bilingual `clarify` step.
- `src/fazit/inputs.py` validates related counts supplied in one file. `DECISIONS.md` records the inputs rule at the end of D31. `tests/tenants.py` bounds generated subset counts by the sum of their supplied parents.
- `tests/test_evidence_cli.py`, `tests/test_rules.py` and `tests/test_inputs.py` cover absent, positive and negative answers, software count conflicts, localised count errors, valid partial inputs and refusal of the retired mapping field.

### Task 2 — Teams, SharePoint and legacy Office formats

- `src/fazit/rules/findings.yaml` and both locales add the three boolean interview findings. `src/fazit/rules/status.yaml` adds the SharePoint workflow and Teams app checks and their bilingual `clarify` actions. A different confirmed problem can still decide the area while the missing answer remains visible.
- All three mappings bind `sharepoint_workflows` and `vba_macros` to the corresponding interview findings. Nine legacy Office extensions bring the list of formats that may contain macros to 20 in `src/fazit/rules/risky_file_types.yaml`.
- `inputs.example.yaml` and `docs/interview-checklist.md` and `docs/interview-checklist.de.md` include the three questions. The checklist macro questions follow the catalogue's extension order. Both samples' `scan.json` and `inputs.yaml` files carry the new fields with the planned example values.
- `tests/test_rules.py` exercises false, true and missing answers, incomplete decided areas, both transfer needs on all profiles and the town's gap tally. `tests/test_inputs.py` verifies the interview and mapping contract. `tests/test_evidence_cli.py` supplies the new Teams answer in the existing licence-classification fixture.

| Finding | Owner role |
| --- | --- |
| `sharepoint.workflows_in_use` | `service_owner` |
| `teams.apps_in_use` | `it_team` |
| `office_files.vba_macros_in_use` | `service_owner` |

The other 41 assignments are recorded in the previous summary. [RR-01 finding owners](RR-01-SUMMARY.md#finding-owners)

### Task 3 — Simulated measurements and scan format

- `src/fazit/templates/report.html.j2` and both locales label sample measurements and identify the sample inventory as fictional. The measurement hooks carry `measured`, and the rule appendix names the required provenance.
- `docs/scan-format.md` documents the accepted fields, evidence rules and code values, with one non-sample example. `tests/test_model.py` checks the document against the loader and runs its example through `fazit report`. `tests/test_cli.py` checks the sample and regular headings and provenance labels in both languages.

After each task, the matching town openDesk outputs replaced `site/demo/en/index.html` and `site/demo/de/index.html`.

## Interfaces for RR-07

The frozen `FunctionMapping` dataclass has these fields.

```python
@dataclass(frozen=True)
class FunctionMapping:
    function: str
    workload: str
    microsoft: Mapping[str, str]
    replacement: Mapping[str, str]
    coverage: str
    reference_url: str | None
    checked_on: date | None
    note: Mapping[str, str] | None
    need_finding: str | None = None
```

Every mapping that still supplies `need_if_positive` fails validation at its `functions[index]` field. The desktop mapping reads `device_management.windows_desktops_required`. The workflow and VBA mappings read `sharepoint.workflows_in_use` and `office_files.vba_macros_in_use`. An Unknown need uses its evidence reason when one exists. The fallback is `answer_not_provided` for a row with a need finding and `not_established` when the row has none.

`_mapping_gaps` currently selects rows with `coverage: not_available`. The new coverage code for “Direct transfer undocumented” in RR-07 needs to keep the affected rows in that gap list. The VBA answer serves the mapping. The Office files status still comes from the file counts.

`load_inputs_text` passes a map from answer-count IDs to their catalogue `subset_of` parents into `_read_inputs`. The map covers subsets whose parents are also answer counts. Once their values have been parsed, the reader compares the subset with the sum of its parents when every value is supplied in the same file. An excessive subset raises `subset_count_exceeds_population` at `provided_counts.<subset id>`. Missing and `null` counts are accepted.

## Sample results

The status of each area matched RR-01 for both samples across all three profiles and both languages. The town's SharePoint row pairs Needs work with the missing workflow answer.

| Status | Town | Non-profit |
| --- | --- | --- |
| Ready | 3 · OneDrive, Teams, smaller applications | 7 · Directory, mail, Windows software, Power Platform, telephony, identity and access, security and compliance |
| Needs work | 9 · Directory, mail, SharePoint, Office files, device management, Windows software, Power Platform, identity and access, integrations | 5 · OneDrive, Teams, Office files, device management, smaller applications |
| Blocker | 1 · Telephony | 0 |
| Unknown | 1 · Security and compliance | 2 · SharePoint, integrations |

| Sample | Profile | Yes | No | Unknown |
| --- | --- | ---: | ---: | ---: |
| Town | openDesk | 4 | 1 | 3 |
| Town | Nextcloud | 2 | 1 | 3 |
| Town | Generic | 1 | 1 | 2 |
| Non-profit | openDesk | 0 | 7 | 1 |
| Non-profit | Nextcloud | 0 | 5 | 1 |
| Non-profit | Generic | 0 | 4 | 0 |

For the town under openDesk, the four Yes gaps are device management, Windows applications, automation and low-code, and telephony. Teams chat history is No. The SharePoint workflow, VBA and Windows desktop gaps are Unknown. The non-profit's VBA gap is No in each profile.

## Verification

| Check | Result |
| --- | --- |
| Task 1 regression run before implementation | 12 expected failures and 15 passes in 3.47 s. The old code inferred desktop need, propagated the software conflict, accepted the obsolete mapping key and contradictory counts, and used blocker language in a Needs work rule. |
| Task 1 focused run after implementation | 30 passed in 3.41 s, including rv11's excess-seat and repeated-part-number regressions. |
| Task 1 `<automated>` | 799 passed in 128.60 s. Both Ruff checks, the generated demo checks, the CLI rejection and site checker passed. The two retired source identifiers and the forbidden wording count reached zero. The inputs error code occurs once in the loader. |
| Task 2 regression run before implementation | 14 expected failures and 2 passes in 2.11 s. The Ready checks, transfer mappings, extensions and town SharePoint evidence showed the previous behaviour. |
| Task 2 focused run after implementation | 29 passed in 3.72 s, including catalogue and interview agreement, both sample status sets and the licence-classification safeguard. |
| Task 2 `<automated>` | 811 passed in 133.63 s. Both Ruff checks, the town and non-profit demo checks and the site checker passed. Acceptance counts confirmed three new findings, 32 problem rules and kinds, one Blocker, two new need bindings per mapping and 20 macro extensions. |
| Task 3 regression run before implementation | Five expected failures in 1.07 s. Both reports used unqualified measurement labels and the scan format document was absent. |
| Task 3 focused run after implementation | 13 passed in 2.26 s, including the German provenance test as written, locale parity and the rv11 regressions. |
| Task 3 `<automated>` and final checks | `uv run pytest -q` passed **816 tests in 136.38 s**. `uv run ruff check .` and `uv run ruff format --check .` passed for Task 3 and again at close-out. Both `uv run fazit demo --lang de` and `uv run fazit demo --lang en` exited 0 with fresh reports and the expected labels. The documented scan rendered without sample labels. `uv run python site/check_site.py` checked 18 pages and 610 references and printed “No errors.” The two locale keys per language, five macro occurrences and single JSON fence passed their counts. |
| Published demos and offline browser | The site copies matched fresh builds byte for byte. Chromium opened both at 360 px in light and dark modes with scripting disabled and HTTP requests blocked. Both fonts loaded, the inventory headings and licence labels rendered, and the four views had zero HTTP requests and no horizontal page overflow. |
| Baseline comparison | The scan model, validator, licence code, service plans and cost code match rv11. D31 differs by the new inputs bullet. The original catalogue records, `STATUSES`, `SECTION_ORDER`, CSP and home tallies match the RR-01 baseline. `telephony-no-replacement` is the sole Blocker. `git diff --check` passed. |

## Existing test edits

| Test or fixture | Basis | Change |
| --- | --- | --- |
| `tests/test_evidence_cli.py::test_windows_dependency_is_scoped_to_the_desktop_move` | C6, A7 | Require Unknown and `answer_not_provided` without a desktop finding for every tested software list. Keep the software status, application need and partial-count assertions with the updated reason. |
| `tests/test_evidence_cli.py::test_desktop_gap_shows_disputed_software_count_from_another_workload` | C6 | Renamed to `test_desktop_gap_keeps_its_answer_when_software_counts_disagree`. Require the provided No on the desktop gap and keep the dispute assertion on the software area. |
| `tests/test_evidence_cli.py::test_desktop_gap_shows_disagreement_between_confirmation_and_software_list` | C6 | Renamed to `test_desktop_gap_keeps_a_no_answer_with_windows_only_software`. Require No without a conflict in the desktop gap, Yes for Windows applications, and retain the supplied No and two-application evidence. |
| `tests/test_rules.py::test_bad_mapping_names_the_file_and_field` | C6 | Add a formerly valid inference key and require rejection at `functions[0]`. |
| `tests/test_rules.py::test_attention_shows_provided_counts_and_zero_explicitly` | C6 | Check the application gap as Provided Yes and the desktop gap as Unknown with its reason. Preserve the explicit figure and zero checks. |
| `tests/tenants.py::_inputs` | C3 | Bound each generated subset when its parents are supplied so the property tests exercise valid inputs. |
| `tests/test_rules.py::test_shipped_risky_extensions` | C4 | Add the nine legacy extensions to the expected macro order and overall set. |
| `tests/test_inputs.py::test_checklist_matches_inputs_and_catalogue` | C4 | Require the checklist extensions in catalogue order. |
| `tests/test_inputs.py::test_every_provided_finding_is_used_by_the_report` | C5 | Verify both mapping-only answers and their exact functions in every profile. |
| `tests/test_evidence_cli.py::test_unlisted_plan_prevents_an_absence_conclusion_but_preserves_known_assignments` | C2 | Supply the new Teams answer so the existing Ready and licence-classification assertions still isolate the licence evidence. |

## Deviations and implementation choices

- The current scan loader validates subset relationships in `_ScanReader.check_populations`. RR-06 used that behaviour as its reference. The implementation keeps those scan checks and extends validation to one inputs file.
- The English and German checklist questions for SharePoint and Teams ask about workflows that run or start there and apps that are attached to teams. Using the narrower draft questions could give a false No when staff do not rely on an existing workflow or attachment. The German rule sentences use the administrative wording in the review table.
- The current template prints a separate provenance word on every licence product row. The count and those rows share the macro result. A populated inventory count always has measured provenance, including partial inventories. The four macro call sites are the evidence summary, headline list, licence count and transfer-gap evidence. The rule-evidence list uses the evidence summary through `evidence_pair`.
- The English scan format reference follows the plan's D18 convention. The document test also checks `tool` subfields and coverage `kind` because the loader accepts them.
- The working-tree handoff follows the requested scope in place of the generic workflow's commit and phase bookkeeping. Verification used the existing environment with `UV_OFFLINE=1` and `UV_NO_SYNC=1`. Chromium's offline mode and request blocking provided the browser check when the sandbox denied a separate network namespace.
- Planning commit `68ee6be` arrived during close-out. Its change map assigns the readiness-bar removal to RR-02, and the homepage example is in RR-05.
- The first supplemental Task 3 shell check over-escaped the Markdown fence. The plan's exact fence count passed on the corrected run. The Task 3 `<automated>` command had already passed.

## Native German review

| Task | Location | Kind | English | German |
| --- | --- | --- | --- | --- |
| 1 | `software-no-web-version.reason` | — | At least one Windows-only application has no web version and needs Windows to run, either on staff workstations or on a separate Windows system. For the move away from Microsoft 365, plan how staff will keep using it or arrange a replacement. | Mindestens eine reine Windows-Anwendung hat keine Webversion und benötigt Windows, entweder auf den Arbeitsplatzrechnern der Beschäftigten oder auf einem gesonderten Windows-System. Planen Sie für den Umstieg von Microsoft 365 den Weiterbetrieb der Anwendung oder eine Ersatzlösung. |
| 1 | `software-no-web-version.next_step` | `clarify` (asks / klärt) | The IT team asks the service owner of each such application whether staff need it on their own workstations or can use it on a separate Windows system. | Die IT-Abteilung klärt für jede betroffene Anwendung mit der fachlich verantwortlichen Stelle, ob die Beschäftigten sie auf ihren Arbeitsplatzrechnern benötigen oder auf einem gesonderten Windows-System nutzen können. |
| 2 | `finding.sharepoint.workflows_in_use` | — | Workflows on SharePoint sites, lists or libraries in use | Workflows auf SharePoint-Websites, in Listen oder Bibliotheken im Einsatz |
| 2 | `finding.teams.apps_in_use` | — | Apps, tabs, bots or connectors added to teams | In Teams eingebundene Apps, Registerkarten, Bots oder Konnektoren |
| 2 | `finding.office_files.vba_macros_in_use` | — | VBA macros that staff rely on | VBA-Makros, auf die die Beschäftigten angewiesen sind |
| 2 | `sharepoint.ready.reason` | — | The SharePoint sites have been counted, and the organisation reports neither custom solutions nor workflows on them. | Die SharePoint-Websites sind erfasst. Nach Angaben der Organisation werden dort weder individuell angepasste Lösungen noch Workflows genutzt. |
| 2 | `sharepoint-workflows.reason` | — | Workflows on SharePoint sites, lists or libraries need to be rebuilt or replaced before the sites move. | Workflows auf SharePoint-Websites, in Listen oder Bibliotheken müssen vor dem Umstieg neu eingerichtet oder ersetzt werden. |
| 2 | `sharepoint-workflows.next_step` | `clarify` (lists / erfasst) | The service owner of each affected site lists the workflows and approvals that staff still rely on. | Die fachlich verantwortliche Stelle jeder betroffenen Website erfasst die Workflows und Genehmigungen, auf die die Beschäftigten noch angewiesen sind. |
| 2 | `teams.ready.reason` | — | The teams have no guests and no added apps, tabs, bots or connectors, and the chat history does not need to be kept. | In den Teams gibt es keine Gäste und keine eingebundenen Apps, Registerkarten, Bots oder Konnektoren. Der Chatverlauf muss nicht aufbewahrt werden. |
| 2 | `teams-apps.reason` | — | Apps, tabs, bots or connectors added to teams need a replacement after the move. | Für in Teams eingebundene Apps, Registerkarten, Bots oder Konnektoren ist nach dem Umstieg Ersatz nötig. |
| 2 | `teams-apps.next_step` | `clarify` (lists, asks / erfasst, klärt) | The IT team lists the apps, tabs, bots and connectors added to teams and asks each service owner which of them staff still use. | Die IT-Abteilung erfasst die in Teams eingebundenen Apps, Registerkarten, Bots und Konnektoren und klärt mit den fachlich verantwortlichen Stellen, welche davon die Beschäftigten noch nutzen. |
| 2 | Inputs example comment for `sharepoint.workflows_in_use` | — | Confirm whether workflows or automated approvals run on SharePoint sites, lists or libraries. | Geben Sie an, ob auf SharePoint-Websites, in Listen oder Bibliotheken Workflows oder automatisierte Genehmigungen laufen. |
| 2 | Inputs example comment for `teams.apps_in_use` | — | Confirm whether apps, tabs, bots or connectors are added to teams. | Geben Sie an, ob in Teams Apps, Registerkarten, Bots oder Konnektoren eingebunden sind. |
| 2 | Inputs example comment for `office_files.vba_macros_in_use` | — | Confirm whether staff rely on VBA macros in Office files. | Geben Sie an, ob die Beschäftigten auf VBA-Makros in Office-Dateien angewiesen sind. |
| 2 | Interview question for `sharepoint.workflows_in_use` | — | Do workflows or automated approvals run on SharePoint sites, lists or libraries, or start from them (`sharepoint.workflows_in_use`)? | Gibt es Workflows oder automatisierte Genehmigungen, die auf SharePoint-Websites, in Listen oder Bibliotheken laufen oder von dort aus gestartet werden (`sharepoint.workflows_in_use`)? |
| 2 | Interview question for `teams.apps_in_use` | — | Are apps, tabs, bots or connectors added to teams (`teams.apps_in_use`)? | Sind in Teams Apps, Registerkarten, Bots oder Konnektoren eingebunden (`teams.apps_in_use`)? |
| 2 | Interview question for `office_files.vba_macros_in_use` | — | Do staff rely on VBA macros in Office files for their work (`office_files.vba_macros_in_use`)? | Sind die Beschäftigten bei ihrer Arbeit auf VBA-Makros in Office-Dateien angewiesen (`office_files.vba_macros_in_use`)? |
| 2 | Interview question for `office_files.kind.macro` | — | How many files with extensions that allow macros has the IT lead counted (`.xlsm`, `.xltm`, `.xlam`, `.xlsb`, `.docm`, `.dotm`, `.pptm`, `.potm`, `.ppam`, `.ppsm`, `.sldm`, `.xls`, `.xlt`, `.xla`, `.doc`, `.dot`, `.ppt`, `.pot`, `.pps`, `.ppa`) (`office_files.kind.macro`)? | Wie viele Dateien hat die IT-Stelle mit Endungen erfasst, die Makros zulassen (`.xlsm`, `.xltm`, `.xlam`, `.xlsb`, `.docm`, `.dotm`, `.pptm`, `.potm`, `.ppam`, `.ppsm`, `.sldm`, `.xls`, `.xlt`, `.xla`, `.doc`, `.dot`, `.ppt`, `.pot`, `.pps`, `.ppa`) (`office_files.kind.macro`)? |
| 3 | `provenance.measured_sample` | — | Measured (simulated) | Erhoben (simuliert) |
| 3 | `found.title_sample` | — | What Fazit recorded for a fictional organisation | Was Fazit für eine fiktive Organisation erfasst hat |

## Open work

Maintainer review remains for the German strings and next-step kinds, and for the scan format's accuracy and tone. The README link and the DOCS-04 filename reference belong to the coordinator. RR-07 owns the target-aware readiness and mapping review.

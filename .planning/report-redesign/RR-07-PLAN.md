---
phase: report-redesign
plan: 07
type: execute
wave: 3
depends_on: ["RR-01", "RR-06"]
files_modified:
  - src/fazit/mappings.py
  - src/fazit/rules/mappings/opendesk.yaml
  - src/fazit/rules/mappings/nextcloud.yaml
  - src/fazit/rules/mappings/generic.yaml
  - src/fazit/rules/status.yaml
  - src/fazit/status.py
  - src/fazit/report.py
  - src/fazit/templates/report.html.j2
  - src/fazit/locales/en.yaml
  - src/fazit/locales/de.yaml
  - tests/test_rules.py
  - tests/test_evidence_cli.py
  - tests/test_simulation.py
  - DECISIONS.md
  - site/index.html
  - site/de/index.html
  - site/demo/en/index.html
  - site/demo/de/index.html
autonomous: true
requirements: [RULE-01, RULE-02, RULE-03, RULE-04, I18N-01, I18N-02]

estimate:
  tokens: 160000
  raw_tokens: 160000
  tasks: 3
  confidence: medium

must_haves:
  truths:
    - "The status evaluator receives the chosen profile's mapping; the same scan and inputs can give an area a different status under openDesk, Nextcloud and the generic profile, and only through the gap rows of that profile (launch critique C1)"
    - "A function the profile leaves out (coverage `not_available` or `transfer_undocumented`) whose need is Yes makes its area at least Needs work, with a reason that names the profile and the function; the rule is data in `status.yaml`, and the loader refuses any status other than Needs work for it, so a target gap alone never makes a Blocker"
    - "A gap whose need is Unknown never improves a status: it adds the need finding to the area's missing evidence, so a Ready area becomes Unknown and a decided area becomes incomplete; a gap whose need is No changes nothing"
    - "openDesk maps SharePoint pages to XWiki, OneNote to Notes and Visio to CryptPad with diagrams.net, each citing the page checked on 2026-11-22; every openDesk row cites the page or page section that supports it, and no row cites the bare architecture overview"
    - "SharePoint workflows, Teams chat history and VBA macros read \"Direct transfer undocumented\" / \"Direkte Übernahme nicht dokumentiert\" (`transfer_undocumented`) in all three profiles; functions the target does not include keep \"Not available\""
    - "Every mapping file carries `operator_review: unreviewed`; the report says in the replacements section and the appendix that the mapping has not yet been reviewed by someone who operates the target system"
    - "The report context carries `scope_statement` per REV4-CHANGE-MAP: `None` for the generic profile; otherwise profile, total, counts per coverage id in ladder order, needed functions with the id of their gap element, and the Unknown-need count, all equal to the replacements table and the gap list"
    - "No score, verdict, percentage or supplier recommendation is added; `STATUSES` and the cost model are unchanged"
  artifacts:
    - path: "src/fazit/rules/status.yaml"
      provides: "The two target-gap rule templates, Needs work only, with reason and next step in both languages"
      contains: "target_gaps:"
    - path: "src/fazit/rules/mappings/opendesk.yaml"
      provides: "22 rows with specific citations, three new functions, three transfer rows, the review marker"
      contains: "operator_review: unreviewed"
    - path: "src/fazit/status.py"
      provides: "evaluate(..., mapping) applies the target gaps after the status rules"
      contains: "transfer_gaps"
    - path: "src/fazit/report.py"
      provides: "scope_statement for RR-03"
      contains: "scope_statement"
  key_links:
    - from: "src/fazit/rules/mappings/*.yaml"
      to: "src/fazit/status.py"
      via: "gap rows with their need finding become target rules or missing evidence on their area"
      pattern: "need_finding"
    - from: "src/fazit/status.py"
      to: "src/fazit/report.py"
      via: "WorkloadStatus.transfer_gaps feeds mapping_gaps and scope_statement, so the gap list, the cards and the summary use one need per function"
      pattern: "transfer_gaps"
---

# Plan RR-07: target-aware readiness, the mapping review and the scope-statement data

## Goal

Make a status mean something for the target the reader chose (launch critique C1), make the mapping files say only what their sources say (C5), and give RR-03 the data for "What {profile} covers" (UI-SPEC 1.2, scope statement; usefulness A6).

<objective>
Today `evaluate` receives no profile: Codex GPT-6.2-Astra and Claude Fable 5.2 both found all fifteen statuses identical under openDesk, Nextcloud and generic for both samples, while only the transfer-gap list changed (8, 6 and 4 rows). This plan feeds the profile's gap rows into evaluation as data-driven rules, reviews the openDesk mapping against the current openDesk documentation, relabels transfer-only gaps, marks every mapping file unreviewed, and builds the scope statement with tests that its counts equal the replacements table.

Purpose: readiness, the gap list, the cards (RR-02) and the summary (RR-03) all rest on one need per function and one coverage per row.
Output: mapping loader and three mapping files, a `target_gaps` block in `status.yaml`, the evaluator and its tests, `scope_statement` in the report context, a few lines of template and locale copy, a decision entry, regenerated site reports.

Run order of the plan set: RR-01, RR-06, RR-07, RR-02, RR-03, RR-04, RR-05. This plan relies on RR-01 (`next_step` with `kind`; `assessed` workloads) and RR-06 (Windows desktop need stays Unknown unless answered; interview answers for SharePoint workflows and VBA).
</objective>

<execution_context>
Read these two files before starting. They are plain paths, not includes.
- $HOME/.claude/gsd-core/workflows/execute-plan.md
- $HOME/.claude/gsd-core/templates/summary.md
</execution_context>

<context>
Read these files first. They are plain paths from the repository root.
- AGENTS.md
- DESIGN.md (binding design and copy rules; "Copy" applies to every string in this plan)
- DECISIONS.md (Principles; D1, D20; the M0 bullet on mappings: "The need remains unknown without a specific complete answer")
- .planning/REQUIREMENTS.md (RULE-01 to RULE-04)
- .planning/report-redesign/REV4-CHANGE-MAP.md (binding: rules for every plan, owners, the scope-statement interface)
- .planning/report-redesign/UI-SPEC.md (revision 4.1: section 1.2 scope statement, 2.3 target line, 8, 9 "Honesty", 11 criterion 24)
- .planning/research/launch-critique/SYNTHESIS.md (C1, C5, D), with CRITIC-astra.md (comments 3 and 8) and CRITIC-fable.md (comment 10)
- .planning/research/report-usefulness/SYNTHESIS.md (A6, A8, C4), CROSS-fable.md and CROSS-astra.md (scope statement guards)
- .planning/report-redesign/RR-01-PLAN.md and the RR-01 and RR-06 SUMMARY files (what landed, final names)

Base: current `main` (172f278 or later) with RR-01 and RR-06 applied. Facts checked by the planner on df36196 (re-check each with grep before relying on it):
- `evaluate(findings, rule_set, catalogue, *, collectors=None, alternatives=None)` in `src/fazit/status.py` has one production caller, `_evidence_context` in `src/fazit/report.py`, and three test callers in `tests/test_rules.py` (`_status`, and two direct calls near `test_removing_a_workloads_evidence_never_gives_ready`).
- `_mapping_gaps(mapping, by_id, statuses)` in `src/fazit/report.py` derives each gap's need after evaluation, from the need finding and the missing reasons of the evaluated rows; it skips every row whose coverage is not `not_available`. RR-06 deletes its `need_if_positive` branch and the field everywhere, and makes the default reason of an Unknown need `answer_not_provided` when the row has a need finding; move the function as RR-06 left it.
- RR-06 (per its plan) adds the boolean answers `sharepoint.workflows_in_use` and `office_files.vba_macros_in_use` and sets them as `need_finding` of the `sharepoint_workflows` and `vba_macros` rows in all three mapping files; adds the rule `sharepoint-workflows` (Needs work) and puts `sharepoint.workflows_in_use == false` into SharePoint's ready evidence; `office_files.vba_macros_in_use` feeds no status rule. The town answers neither (both needs Unknown), the non-profit answers both `false`. Status rules after RR-06: 32. Confirm each name with grep; if RR-06 landed differently, follow what landed and record it.
- After RR-06 every gap row in every profile already has a `need_finding` (openDesk 8, Nextcloud 6, generic 5 `need_finding` lines, counting the generic desktop row, which is not a gap there). This plan relabels three of those rows `transfer_undocumented`; they must stay in the gap list, in the target evaluation and in the scope statement's "outside the profile" counts, which is why gap rows are selected by `GAP_COVERAGE` everywhere, never by `not_available`.
- `COVERAGE_LADDER` in `src/fazit/mappings.py` has eight ids, `not_available` last; the generic profile may use `COVERAGE_LADDER[4:]`. `_MAPPING_REFERENCE` accepts a `#` fragment.
- The gap list in the template is `li[data-gap][data-need]` inside `div[data-subsection="cannot-be-moved"]`; tests match `<li data-gap="…" data-need="…">` with the closing `>`, so no attribute may be added to that `li`.
- The appendix lists the deciding and noted rules of each area by iterating `status_rules.workloads[row.workload].rules`; synthesised rules would not appear there without a template change.
- Shipped rows: 19 per profile; gap rows 8 (openDesk), 6 (Nextcloud), 4 (generic); `need_finding` lines 6, 4, 3; ten openDesk rows cite exactly `https://docs.opendesk.eu/operations/architecture/`.
- Town under openDesk on df36196 (before RR-06): sharepoint_workflows Unknown, teams_chat_history No, vba_macros Unknown, device_management Yes, desktop_operating_system Yes, windows_applications Yes, automation_and_low_code Yes, telephony Yes. After RR-06 removes the desktop inference, desktop_operating_system is Unknown: 4 needed, 1 not needed, 3 Unknown (CROSS-fable).
- On df36196 every gap whose need is Yes in the two samples sits on an area already Needs work or Blocker; the visible change on the samples is notes and incomplete markers. Expected after RR-06 and this plan (verify, then record): town under openDesk gains target notes on device management, Windows software, Power Platform and telephony; Office files becomes incomplete (VBA need Unknown, no rule asks for it) under all three profiles; device management becomes incomplete under openDesk and Nextcloud (desktop need Unknown) but not under generic, where the desktop row is not a gap; SharePoint is already incomplete through its own ready evidence, so nothing is added twice. The status differences between profiles are proved with constructed evidence in Task 2.

Environment:
- The executor cannot commit. Leave every change in the working tree; the orchestrator reviews and commits.
- Run every command from the repository root through `uv`; if the shell does not find it, run `export PATH="$HOME/.local/bin:$PATH"` first. Install nothing and add no dependency. Add no module. No network: every fact you need is in this plan.
- Locate every symbol with grep at execution time, never by line number. Re-read every file immediately before you edit it; never revert or reformat changes you did not make.
- Never weaken a test or a principle. Existing tests change only where C1 or C5 changes the behaviour they assert (UI-SPEC 9 says rule evaluation changes only through RR-06 and RR-07); list each edited assertion with its item in the SUMMARY. Principle tests may only get stricter.
- Every report command builds into a fresh temporary output directory and checks exit code, file existence and content separately. Every new user-facing string goes into both locales; every new German string is a draft for the native-review table of the SUMMARY. No "z. B."-style abbreviations; formal "Sie"; status names exactly Bereit, Handlungsbedarf, Hindernis, Unbekannt.
- No person names anywhere in the shipped files or the report. The operator review is recorded as a date; who reviewed goes into the review record, not the mapping file.

## Sources for the mapping review (checked by the planner on 2026-11-22)

All pages fetched on 2026-11-22. Use these and nothing else; if a statement below is not listed, leave it out of the mapping files.

| # | URL | What it establishes |
|---|-----|---------------------|
| S1 | https://docs.opendesk.eu/operations/introduction/#overview | The table "functional main components": Chat & collaboration, Element ft. Nordeck widgets 1.12.29; **Collaborative notes, Notes (aka Docs), MIT, 5.6.1**, documentation "available in installed application"; **Diagram editor, CryptPad ft. diagrams.net, 2026.5.1**; File management, Nextcloud 33.0.9; Groupware, OX App Suite 8.53; **Knowledge management, XWiki 18.4.7**; Portal & IAM, Nubus 1.23.2; Project management, OpenProject 17.9.4; Videoconferencing, Jitsi 2.0.11248; Weboffice, Collabora 26.04.4. No device management, workstation operating system, environment for Windows applications or low-code platform is listed. |
| S2 | https://docs.opendesk.eu/operations/architecture/#nubus-identity-and-access-management--portal | "Nubus provides the management required for users, groups and other IAM objects, as well as the portal, the Identity provider for Single Sign-On". |
| S3 | https://docs.opendesk.eu/operations/architecture/#keycloak | Keycloak "serves as the OIDC provider, handling user authentication". |
| S4 | https://docs.opendesk.eu/operations/architecture/#ox-app-suite-groupware-with-ox-dovecot-mail-backend | OX App Suite is used "for email, calendar, address book and personal task management"; mail attachments are scanned for malware via ICAP. |
| S5 | https://docs.opendesk.eu/operations/architecture/#nextcloud-files | Nextcloud is "a file storage and sync platform" with desktop, mobile and web interfaces; uploaded files are scanned for malware via ICAP. |
| S6 | https://docs.opendesk.eu/operations/architecture/#elementsynapse-chat--call | Element "is used for chat and direct audio & video calling". |
| S7 | https://docs.opendesk.eu/operations/architecture/#jitsi-video-conferencing | Jitsi is used for video conferencing; Jigasi "allows joining the meeting via phone call if an external SIP server and SIP trunk are provided". |
| S8 | https://docs.opendesk.eu/operations/architecture/#collabora-weboffice | Collabora is used "for editing Office documents such as rich texts, spreadsheets and presentations". |
| S9 | https://docs.opendesk.eu/operations/architecture/#cryptpad-online-diagrams | "In openDesk, CryptPad is for editing diagrams.net documents." Nothing about Visio files, and no other CryptPad application (no forms) in openDesk. |
| S10 | https://docs.opendesk.eu/operations/architecture/#component-integration | Functional integrations between the openDesk applications (silent login, central contacts, central navigation, file picker, newsfeed, OpenProject file store); details in upstream documentation. |
| S11 | https://docs.opendesk.eu/user/applications/wissen/ | The "Wissen" module: pages with subpages, further wikis ("Subwikis"), "Zugriffsrechte für die Seite ändern", templates, version history, export as HTML, PDF, ODT or RTF; a help topic "Importieren/Exportieren" without detail. It names neither SharePoint nor any way to carry over SharePoint pages. The page does not name XWiki; S1 and the architecture section `#xwiki-knowledge-management` ("XWiki is an open-source wiki platform for knowledge management") do. |
| S12 | https://docs.opendesk.eu/user/applications/dateien/ | Internal and external sharing of files and folders, public links with expiry. No workflow, trigger or approval feature. (Already cited; still true.) |
| S13 | https://docs.opendesk.eu/user/applications/chat/ | Chat and collaboration guide; no mention of Teams and no import of past conversations (the only import is of whiteboard files). (Already cited; still true.) |
| S14 | https://docs.opendesk.eu/user/applications/office/ | Create and edit documents, spreadsheets, presentations and diagrams in the file store; "Dateien importiert"; no mention of macros, VBA or Visio. (Already cited; still true.) |
| S15 | https://docs.opendesk.eu/user/applications/aufgaben/ | Tasks in task folders with reminders, status, priority and members; no forms for others and no appointment booking. |

Not confirmed, therefore left out: an openDesk user guide for Notes or for the diagram editor (none on docs.opendesk.eu; S1 says the Notes guide is inside the installed application); any import of OneNote notebooks into Notes; Visio support in CryptPad as shipped in openDesk; forms in openDesk's CryptPad; a dedicated openDesk security or antivirus page (`/operations/antivirus/` and `/operations/security/` returned 404 on 2026-11-22). Nextcloud and generic rows for wiki pages, notes and diagrams are not added: the Nextcloud 35 user manual documents Collectives (https://docs.nextcloud.com/server/stable/user_manual/en/collectives/index.html), but the app is published by the CollectiveCloud team, and no Nextcloud page establishes a diagram editor; record both as questions for the operator review in the SUMMARY. XWiki's "Anwendungen" (applications) in S11 may bear on the openDesk low-code row; leave that row as it is and list it for the operator review.
</context>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: Mapping review: specific citations, XWiki, Notes and CryptPad for openDesk, "Direct transfer undocumented", need answers on every gap, and the unreviewed marker</name>
  <files>src/fazit/mappings.py, src/fazit/rules/mappings/opendesk.yaml, src/fazit/rules/mappings/nextcloud.yaml, src/fazit/rules/mappings/generic.yaml, src/fazit/templates/report.html.j2, src/fazit/locales/en.yaml, src/fazit/locales/de.yaml, tests/test_rules.py</files>
  <read_first>AGENTS.md, DESIGN.md ("Copy"), the "Sources for the mapping review" table in this plan, .planning/research/launch-critique/CRITIC-astra.md (comment 8), .planning/research/launch-critique/CRITIC-fable.md (comment 10), src/fazit/mappings.py (grep `COVERAGE_LADDER`, `class FunctionMapping`, `class TargetMapping`, `def _need_conditions`, `def _function_mapping`, `def load_mapping`), src/fazit/validation.py (grep `def calendar_date`, `def choice`, `def fail`), all three files in src/fazit/rules/mappings/, src/fazit/rules/findings.yaml (grep `sharepoint.workflows_in_use`, `office_files.vba_macros_in_use`, added by RR-06), .planning/report-redesign/RR-06-SUMMARY.md, src/fazit/templates/report.html.j2 (`data-section="moves"`, `data-subsection="cannot-be-moved"`, the appendix mapping part with `data-mapping-details`), src/fazit/locales/en.yaml and de.yaml (`moves`, `mapping_coverage`, `attention`), tests/test_rules.py (grep `FUNCTION_IDS`, `def test_shipped_mapping_covers_every_workload`, `def test_bad_mapping_names_the_file_and_field`, `def test_attention_lists_each_unavailable_function_from_the_profile`, `def test_gap_need_uses_only_its_declared_complete_answer`, `def test_marking_a_mapping_unavailable_adds_it_to_the_gap_list`)</read_first>
  <behavior>
    - `COVERAGE_LADDER` gains `transfer_undocumented` directly before `not_available`; a new constant `GAP_COVERAGE = ("transfer_undocumented", "not_available")` names the coverages that make a row a transfer gap; the generic profile still accepts `COVERAGE_LADDER[4:]`, which now includes it
    - Every mapping file has a top-level `operator_review`; the loader accepts `unreviewed` or a calendar date and exposes it as `TargetMapping.reviewed_on` (`None` when unreviewed); a missing or other value is refused with the field `operator_review`, naming the file
    - Every row with a gap coverage, in every profile, has a `need_finding`; one without is refused with `functions[<index>].need_finding`
    - openDesk has 22 rows; every `checked_on` is "2026-11-22"; no `reference_url` equals the bare `https://docs.opendesk.eu/operations/architecture/`; the rows and citations are exactly those of the action below
    - In all three profiles `sharepoint_workflows`, `teams_chat_history` and `vba_macros` have coverage `transfer_undocumented` and a `need_finding`; the other gap rows keep `not_available`
    - The replacements table shows "Direct transfer undocumented" / "Direkte Übernahme nicht dokumentiert" for those rows; the gap list lists every gap-coverage row in mapping order and its fallback text is the row's coverage label
    - Each gap item contains an element with `id="transfer-gap-<function>"` (on the `strong` that names the function; the `li` keeps exactly `data-gap` then `data-need`)
    - The replacements section and the appendix mapping part each show one sentence about the review: unreviewed, or the review date, with `data-mapping-review="unreviewed"` or `data-mapping-review="<date>"`
  </behavior>
  <action>
    Loader (`mappings.py`). Insert `transfer_undocumented` before `not_available` in `COVERAGE_LADDER` and add `GAP_COVERAGE`. Add `operator_review` to the required root fields of `load_mapping`: the literal `unreviewed` gives `reviewed_on=None`; otherwise `reader.calendar_date(value, "operator_review")`; add `reviewed_on: date | None` to `TargetMapping`. In `_function_mapping`, after `_need_conditions`, fail `f"{field}.need_finding"` when the coverage is in `GAP_COVERAGE` and there is no need finding (after RR-06 every shipped gap row passes; this guards new rows).

    openDesk (`opendesk.yaml`). Add `operator_review: unreviewed` after `product_profile`. Set every `checked_on` to "2026-11-22" and every `reference_url` as follows (S-numbers from the sources table): identity_management S2; mail_and_calendar S4; personal_files S5; team_files S12; sharepoint_workflows S12; chat S6; video_meetings S7; teams_chat_history S13; office_editing S8; vba_macros S14; device_management S1; desktop_operating_system S1; windows_applications S1; automation_and_low_code S1; telephony S7; single_sign_on S3; security_and_compliance S5; forms_tasks_bookings S15; application_integrations S10. Keep each row's `microsoft`, `replacement` and `need_finding`; change the notes only where a note below says so. Set `sharepoint_workflows`, `teams_chat_history` and `vba_macros` to `transfer_undocumented`, keeping the `need_finding` lines RR-06 put on them (`sharepoint.workflows_in_use`, `teams.chat_history_must_be_kept`, `office_files.vba_macros_in_use`); if RR-06's lines are missing, stop and report: do not invent a finding. New and changed notes, English and German (German drafts):
    - security_and_compliance: "The architecture documents malware scanning of uploaded files and mail attachments. It does not document organisation-wide retention or legal holds." / "Die Architekturdokumentation beschreibt die Prüfung hochgeladener Dateien und E-Mail-Anhänge auf Schadsoftware. Organisationsweite Aufbewahrung und Sperren für Rechtsverfahren sind dort nicht beschrieben."
    - forms_tasks_bookings: "The task guide covers tasks with reminders, status and members. It describes no general forms or public appointment booking." / "Die Anleitung zu Aufgaben beschreibt Aufgaben mit Erinnerungen, Status und Beteiligten. Allgemeine Formulare und eine öffentliche Terminbuchung sind dort nicht beschrieben."
    - telephony: keep the current note (it matches S7).
    Add three rows (function ids, positions, texts; all `in_suite_with_limits`, `checked_on: "2026-11-22"`, no need finding):
    - `intranet_pages`, directly after `sharepoint_workflows`; workload `sharepoint`; microsoft "SharePoint pages and intranet sites" / "SharePoint-Seiten und Intranet-Websites"; replacement "XWiki" / "XWiki"; reference S11; note "The knowledge module documents wiki pages, subpages, further wikis and access rights per page. It names no way to carry over existing SharePoint pages or site structure." / "Das Modul Wissen beschreibt Wikiseiten, Unterseiten, weitere Wikis und Zugriffsrechte für einzelne Seiten. Eine Übernahme vorhandener SharePoint-Seiten oder Website-Strukturen ist dort nicht beschrieben."
    - `notes`, directly after `vba_macros`; workload `office_files`; microsoft "OneNote notebooks" / "OneNote-Notizbücher"; replacement "Notes" / "Notes"; reference S1; note "The component list includes Notes for collaborative notes. Its guide is only available inside the installed application, and no public documentation describes carrying over OneNote notebooks." / "Die Komponentenübersicht nennt Notes für gemeinsame Notizen. Die Anleitung ist nur in der installierten Anwendung verfügbar, und eine Übernahme von OneNote-Notizbüchern ist öffentlich nicht dokumentiert."
    - `diagrams`, directly after `notes`; workload `office_files`; microsoft "Visio diagrams" / "Visio-Diagramme"; replacement "CryptPad with diagrams.net" / "CryptPad mit diagrams.net"; reference S9; note "The architecture names CryptPad for editing diagrams.net documents. It does not say whether existing Visio files can be opened or converted." / "Laut Architekturdokumentation dient CryptPad zur Bearbeitung von diagrams.net-Dokumenten. Ob vorhandene Visio-Dateien geöffnet oder konvertiert werden können, geht daraus nicht hervor."

    Nextcloud and generic. Add `operator_review: unreviewed`; set the same three rows to `transfer_undocumented`, keeping RR-06's need findings; change nothing else (their facts were checked on 2026-11-21 and go to the operator review). Generic keeps no URLs or dates and names no product.

    Copy and template. Add `mapping_coverage.transfer_undocumented` ("Direct transfer undocumented" / "Direkte Übernahme nicht dokumentiert"), `moves.unreviewed` ("This mapping has not yet been reviewed by someone who operates the target system." / "Diese Zuordnung wurde noch nicht von einer Person geprüft, die das Zielsystem betreibt.") and `moves.reviewed` ("This mapping was reviewed on {date} by someone who operates the target system." / "Diese Zuordnung wurde am {date} von einer Person geprüft, die das Zielsystem betreibt."). In the template: render the review sentence as `p[data-mapping-review]` (no class: RR-02 and RR-04 run later and restyle these sections) directly under the replacements heading and after the appendix's mapping description, the date through `format.date`; select gap rows by `GAP_COVERAGE` (pass it in the context or filter on the two ids) instead of `not_available`; use `strings.mapping_coverage[item.coverage]` as the gap note fallback; put `id="transfer-gap-{{ item.function }}"` on the `strong` that opens each gap item. Add no CSS.

    Tests (C5 edits, list each in the SUMMARY). In `tests/test_rules.py`: `FUNCTION_IDS` stays the 19 shared functions, and the shipped-mapping test asserts them in order as a subsequence of every profile, plus exactly `intranet_pages`, `notes`, `diagrams` for openDesk at the positions above; the three transfer rows have `transfer_undocumented` in every profile; every openDesk row is checked on 2026-11-22 and none cites the bare architecture URL; every gap row has a need finding; `reviewed_on is None` for all three shipped files. Add to the parametrised bad-mapping test: `missing_review` (`operator_review` deleted, field `operator_review`), `bad_review` (value "2026-02-30", field `operator_review`), `gap_without_need` (first row set to `not_available` without a need finding, field `functions[0].need_finding`). Update the gap-list tests to select gap rows by `GAP_COVERAGE`. A copied opendesk file with `operator_review: "2026-12-01"` renders `data-mapping-review="2026-12-01"` and the dated sentence; the shipped files render `data-mapping-review="unreviewed"` in both sections and both languages.
  </action>
  <verify>
    <automated>uv run pytest tests/test_rules.py -q && uv run pytest -q && uv run ruff check . && uv run ruff format --check . && uv run python -c 'from fazit.catalogue import load_catalogue; from fazit.mappings import GAP_COVERAGE, load_mapping; c = load_catalogue(); m = load_mapping("opendesk", c); assert len(m.functions) == 22 and m.reviewed_on is None; assert all(r.reference_url != "https://docs.opendesk.eu/operations/architecture/" and r.checked_on.isoformat() == "2026-11-22" for r in m.functions); assert all(r.need_finding for p in ("opendesk", "nextcloud", "generic") for r in load_mapping(p, c).functions if r.coverage in GAP_COVERAGE)' && out="$(mktemp -d)" && log="$(mktemp)" && uv run fazit demo --lang de --out "$out" > "$log" && report="$(tail -n 1 "$log")" && test -f "$report" && grep -q "Direkte Übernahme nicht dokumentiert" "$report" && grep -q 'data-mapping-review="unreviewed"' "$report" && grep -q 'id="transfer-gap-telephony"' "$report"</automated>
    <human-check>Native-German review of the new notes, coverage label and review sentences (SUMMARY table).</human-check>
  </verify>
  <acceptance_criteria>
    - `grep -c "^  - function:" src/fazit/rules/mappings/opendesk.yaml` [HEAD=19 EXPECT==22]; nextcloud and generic stay 19
    - `grep -c "reference_url: https://docs.opendesk.eu/operations/architecture/$" src/fazit/rules/mappings/opendesk.yaml` [HEAD=10 EXPECT==0]
    - `grep -c 'checked_on: "2026-11-22"' src/fazit/rules/mappings/opendesk.yaml` [HEAD=0 EXPECT==22]
    - `grep -c "coverage: transfer_undocumented" src/fazit/rules/mappings/<each>.yaml` [HEAD=0 EXPECT==3] for each of the three files
    - `grep -c "^operator_review: unreviewed" src/fazit/rules/mappings/<each>.yaml` [HEAD=0 EXPECT==1] for each
    - `grep -c "need_finding:" src/fazit/rules/mappings/opendesk.yaml` [df36196=6, after RR-06=8, EXPECT==8], nextcloud [4, 6, EXPECT==6], generic [3, 5, EXPECT==5]: this plan adds or removes none
    - Every row RR-06 linked keeps its link: `sharepoint_workflows` and `vba_macros` read `need_finding: sharepoint.workflows_in_use` and `need_finding: office_files.vba_macros_in_use` in all three files
    - `grep -ci "cryptpad\|xwiki\|notes" src/fazit/rules/mappings/generic.yaml` prints 0
    - Follows DESIGN.md ("Copy"; no colour or symbol added)
  </acceptance_criteria>
  <done>The mapping files say only what dated, specific sources say, transfer-only gaps are labelled as such, every gap can be answered, and every report says the mappings await an operator's review.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: The evaluator takes the profile: a needed gap makes the area Needs work through a data rule, an Unknown need blocks Ready, never a Blocker</name>
  <files>src/fazit/rules/status.yaml, src/fazit/status.py, src/fazit/report.py, src/fazit/templates/report.html.j2, tests/test_rules.py, tests/test_evidence_cli.py, tests/test_simulation.py, DECISIONS.md</files>
  <read_first>AGENTS.md, DESIGN.md ("Copy"), DECISIONS.md (Principles, D1, D20, the M0 bullets on status rules and mappings), .planning/REQUIREMENTS.md (RULE-03: Unknown unless a confirmed problem gives a worse status), .planning/research/launch-critique/CRITIC-astra.md (comment 3), .planning/research/report-usefulness/CROSS-fable.md (statuses identical across profiles), .planning/report-redesign/RR-01-PLAN.md (Task 2: the next-step dataclass, `STEP_KINDS`, owner roles, drafting rules), src/fazit/status.py (grep `class StatusRule`, the next-step dataclass RR-01 added, `class WorkloadStatus`, `class StatusRuleSet`, `def load_status_rules`, `def _evaluate_workload`, `def _unknown_code`, `def evaluate`), src/fazit/report.py (grep `def _mapping_gaps`, `def _evidence_context`, `def _prepare_report`), src/fazit/mappings.py (`GAP_COVERAGE` from Task 1), src/fazit/rules/status.yaml (the `next_step` shape RR-01 gave every rule), src/fazit/templates/report.html.j2 (`macro status_reason`, the readiness notes list, the appendix `rule-details` loop), tests/test_rules.py (grep `def _status`, `def test_removing_a_workloads_evidence_never_gives_ready`, `def test_bad_status_rule_names_the_file_and_field`), tests/test_evidence_cli.py (grep `data-gap="telephony"`, `desktop_operating_system`), tests/test_simulation.py (grep `def test_worse_collection_never_improves_status`, `def _render`, `def _statuses`), tests/tenants.py (grep `def tenants`), tests/test_rules.py (grep `def complete_evidence`; there is no `tests/conftest.py` fixture of that name)</read_first>
  <behavior>
    - `status.yaml` has a top-level `target_gaps` with exactly the keys `transfer_undocumented` and `not_available`, each with `id`, `status`, `reason` and `next_step` (RR-01 shape, with `kind`); the loader refuses a missing key, a status other than `needs_work` (field `target_gaps.<coverage>.status`), and a reason whose English or German text lacks `{profile}` or `{function}` or has another placeholder (field `target_gaps.<coverage>.reason.<lang>`); ids follow `RULE_ID` and are unique among all rule ids
    - `evaluate(findings, rule_set, catalogue, mapping, *, collectors=None, alternatives=None)`: `mapping` is required; rows keep catalogue order over the assessed workloads
    - Each row carries `transfer_gaps`: the profile's gap rows on that workload in mapping order, each with the mapping row, the need finding (or `None`), `need` (`yes`, `no`, `unknown`) and its reason codes, computed by today's `_mapping_gaps` logic moved into `status.py`
    - Need Yes: a rule built from the template for the row's coverage, id `<template id>-<function with _ as ->`, `when` one condition on the need finding (`==` true, or `>` 0 for a count), reason with `{profile}` = the profile label and `{function}` = the row's `microsoft` text in each language, `next_step` from the template. If the area was Ready or Unknown it becomes Needs work with this rule deciding (missing evidence kept, so an incomplete area stays marked incomplete); if it was Needs work or Blocker the rule is added to its notes after the area's own fired rules
    - Need Unknown: the need finding joins the row's missing evidence with the gap's first reason code (and its collector when the finding is measured), unless the row already lists that finding; a Ready area becomes Unknown with the reason code from the existing unknown-code precedence; decided and Unknown areas keep their status
    - Need No: nothing changes. A target rule never sets Blocker; no area is Ready while any of its gaps has need Yes or Unknown
    - The report's `mapping_gaps` comes from the rows' `transfer_gaps` in mapping order (template unchanged apart from Task 1); a fired target rule appears in the readiness reason or notes and in the appendix rule details with `data-rule="<id>"` and its condition
    - Constructed evidence proves the target matters: with telephony in use and the replacement answer missing, telephony is Needs work and incomplete under openDesk (gap `not_available`, need Yes) and Unknown under Nextcloud (no gap); with a complete Ready device-management area but no answer on whether Windows desktops are required, device management is Unknown under openDesk and Nextcloud and Ready under generic; with Teams chat history needed, Teams is Needs work under every profile, decided by `teams-chat-history` with the target note
  </behavior>
  <action>
    Rule data (`status.yaml`). Add after `workloads`:
    ```yaml
    target_gaps:
      transfer_undocumented:
        id: target-transfer-undocumented
        status: needs_work
        reason:
          en: The {profile} target profile documents no direct transfer for {function}, which this organisation needs.
          de: Für „{function}“ dokumentiert das Zielprofil „{profile}“ keine direkte Übernahme, und die Organisation benötigt diese Funktion.
        next_step:
          kind: replace
          en: The service owner and the IT team plan how the existing content is carried over or rebuilt, and test that method before a move.
          de: Die fachlich verantwortliche Stelle und die IT-Abteilung planen, wie die bestehenden Inhalte übernommen oder neu aufgebaut werden, und erproben dieses Vorgehen vor einem Umstieg.
      not_available:
        id: target-not-available
        status: needs_work
        reason:
          en: The {profile} target profile lists no solution for {function}, which this organisation needs.
          de: Das Zielprofil „{profile}“ nennt für „{function}“ keine Lösung, und die Organisation benötigt diese Funktion.
        next_step:
          kind: replace
          en: The service owner and the IT team decide how this function is provided after a move.
          de: Die fachlich verantwortliche Stelle und die IT-Abteilung entscheiden, wie diese Funktion nach einem Umstieg bereitgestellt wird.
    ```
    Both kinds are `replace`: each step only makes sense for a move (RR-01's definition), although the second names a decision; record that reasoning in the SUMMARY's review table. The next steps name no product and no import or export (RR-01's check must still pass). The templates live outside `workloads`, so the 32 workload rules RR-06 leaves (and every test that counts them) are unchanged; RR-01's next-step test must also cover the two templates (extend it, do not count them as workload rules).

    Loader. Add a frozen `TargetGapRule` (`id`, `status`, `reason`, `next_step`) and a `target_gaps` mapping (coverage id to rule) on `StatusRuleSet`; read the block in `load_status_rules` with the shared validator and the refusals of the behaviour list, reusing RR-01's next-step reader. Check placeholders with `string.Formatter().parse`, not a regular expression.

    Evaluation. Keep `_evaluate_workload` as it is and add three steps in `evaluate`: (1) evaluate every assessed workload as today; (2) compute the transfer gaps from the rows: move `_mapping_gaps` from `report.py` into `status.py` unchanged in its need logic, select rows by `GAP_COVERAGE`, and return a small frozen `TransferGap` per row; (3) apply each row's gaps as the behaviour list says, building rows with `dataclasses.replace`. Add `transfer_gaps: tuple[TransferGap, ...] = ()` as the last field of `WorkloadStatus`. Import from `mappings.py` only (`mappings.py` must not import `status.py`). Comments say why the target rules come after the area's own rules (the area's own reason stays the deciding one) and why an Unknown need adds missing evidence (Unknown never improves a status).

    Report. In `_evidence_context`, pass `mapping` to `evaluate`; build `mapping_gaps` as the same four-item tuples as today from the rows' `transfer_gaps` in mapping order, so the template's gap loop is unchanged. In the appendix rule details, after the workload's own deciding and noted rules, render any fired target rule with the same markup (`data-rule`, id, status label, reason, `conditions_list(rule.when)`). The readiness reason, notes and RR-01's next step need no change, because a target rule is a `StatusRule`.

    Tests (C1; list each edited assertion in the SUMMARY). Pass `load_mapping("opendesk", catalogue)` to the existing direct `evaluate` calls; `complete_evidence` stays all Ready under all three profiles (assert it). Add to the bad-status-rule test: `target_gaps` missing (field `target_gaps`), `target_gaps.not_available.status: blocker` (field `target_gaps.not_available.status`), a German reason without `{function}` (field `target_gaps.transfer_undocumented.reason.de`). Add the three constructed cases of the behaviour list with `evaluate` and with rendered reports in both languages (the telephony reason names "openDesk" and "Teams Phone and public telephone calling"; the appendix shows `data-rule="target-not-available-telephony"`). In `tests/test_simulation.py`, add a property over `tenants()` and every profile: no row is Ready while one of its `transfer_gaps` has need Yes or Unknown; every row decided by a target rule is Needs work; no Blocker is decided by a target rule; and against the same tenant evaluated with that profile's gap rows set to `in_suite` (build the copy with `dataclasses.replace`, do not edit files), Ready may become Needs work or Unknown, Unknown may become Needs work, Needs work and Blocker keep their status, and an incomplete row stays incomplete. Re-check the existing gap and desktop assertions in `tests/test_evidence_cli.py`; they should hold unchanged, and any that changes is a finding to report, not to silence.

    Decision. Add the next free `D` number to `DECISIONS.md` (grep the highest first) under today's date: "Readiness depends on the target profile." One short paragraph: the evaluator reads the chosen profile's gap rows; a needed function the profile leaves out or cannot carry over makes the area at least Needs work, never a Blocker on its own; an Unknown need keeps the area from Ready; the rule lives in `status.yaml`; new Blocker rules wait for the operator review (usefulness decision C8).
  </action>
  <verify>
    <automated>uv run pytest tests/test_rules.py tests/test_simulation.py -q && uv run pytest -q && uv run ruff check . && uv run ruff format --check . && uv run python -c 'from fazit.catalogue import load_catalogue; from fazit.status import load_status_rules; r = load_status_rules(load_catalogue()); assert set(r.target_gaps) == {"transfer_undocumented", "not_available"} and {g.status for g in r.target_gaps.values()} == {"needs_work"}' && out="$(mktemp -d)" && log="$(mktemp)" && uv run fazit demo --lang en --out "$out" > "$log" && report="$(tail -n 1 "$log")" && test -f "$report" && grep -q 'data-rule="target-not-available-telephony"' "$report" && outnc="$(mktemp -d)" && lognc="$(mktemp)" && uv run fazit demo --lang en --profile nextcloud --out "$outnc" > "$lognc" && test -f "$(tail -n 1 "$lognc")" && ! grep -q 'data-rule="target-not-available-telephony"' "$(tail -n 1 "$lognc")"</automated>
    <human-check>Native-German review of the two target reasons and next steps, with their kind (SUMMARY table).</human-check>
  </verify>
  <acceptance_criteria>
    - `grep -c "^target_gaps:" src/fazit/rules/status.yaml` [HEAD=0 EXPECT==1]; `grep -c "status: blocker" src/fazit/rules/status.yaml` is unchanged by this task
    - `grep -c "def _mapping_gaps" src/fazit/report.py` [HEAD=1 EXPECT==0]
    - `grep -n "def evaluate" -A3 src/fazit/status.py` shows a `mapping` parameter before the `*`
    - The SUMMARY lists, for the town and non-profit samples under each profile, every row whose status, incomplete marker or notes changed against RR-06's output, with the gap that changed it
    - Follows DESIGN.md ("Copy")
  </acceptance_criteria>
  <done>The same evidence gives target-specific statuses through one data rule, a target gap can never create a Blocker or let an unanswered need through to Ready, and the gap list, readiness and appendix agree on every need.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 3: Scope-statement data for RR-03, equal to the replacements table, and regenerated site reports</name>
  <files>src/fazit/report.py, tests/test_rules.py, site/index.html, site/de/index.html, site/demo/en/index.html, site/demo/de/index.html</files>
  <read_first>AGENTS.md ("Done means"), DESIGN.md, .planning/report-redesign/REV4-CHANGE-MAP.md ("Interfaces between plans": scope statement), .planning/report-redesign/UI-SPEC.md (1.2 scope statement, 8 `summary.scope_*`, 9 "Honesty", 11 criterion 24), .planning/research/report-usefulness/CROSS-astra.md (keep each profile's own coverage labels; never a fraction), src/fazit/report.py (grep `def _evidence_context`, `def _prepare_report`, `mapping_gaps`), src/fazit/mappings.py (`COVERAGE_LADDER`, `GAP_COVERAGE`, `TargetMapping.reviewed_on`), tests/test_rules.py (grep `def report_section` usage and the gap tests), site/check_site.py (grep `def check_tally`, `def check_demo_reports`)</read_first>
  <behavior>
    - The report context has `scope_statement`; for the generic profile (`product_profile` false) it is `None`
    - Otherwise it is a frozen `ScopeStatement` with `profile` (the profile label in the report's language), `total` (number of mapping rows), `by_coverage` (tuple of coverage id and count, only ids present, in `COVERAGE_LADDER` order), `needed` (tuple of the gap row's `microsoft` text in the report's language and `"transfer-gap-<function>"`, need Yes, in mapping order), `unknown_need` (number of gap rows with need Unknown); "outside the profile" means a row whose coverage is in `GAP_COVERAGE`, so the three `transfer_undocumented` rows count exactly as the `not_available` rows do and `reviewed_on` (the mapping's review date or `None`, an addition RR-03 may show)
    - The counts in `by_coverage` sum to `total` and equal the rows of the replacements table per coverage label; `needed` and `unknown_need` equal the gap list's `data-need="yes"` and `data-need="unknown"` items, and every `needed` id exists in the rendered report
    - Nextcloud keeps `open_source_community` as its own entry; coverage ids are never merged
    - No template renders it yet (RR-03 does); no fraction, percentage or bar is derived anywhere
  </behavior>
  <action>
    Data. In `report.py` add a frozen `ScopeStatement` and a function `scope_statement(mapping, statuses, lang)` that builds it from the mapping and the rows' `transfer_gaps` (one source with `mapping_gaps`), returning `None` when `mapping.product_profile` is false; call it from the context builder as `scope_statement=…`. The interface is REV4-CHANGE-MAP's, plus `reviewed_on`; name nothing else.

    Tests (UI-SPEC 11 criterion 24). In `tests/test_rules.py`, parametrised over both samples, both languages and the two product profiles: `scope_statement(...)` equals what the rendered report shows (count of `tr[data-function]` in `moves` per coverage label text, `li[data-gap]` by `data-need` in `attention`, each `needed` id present as `id="…"`); `sum(count) == total`; ids in ladder order; generic gives `None`; with RR-06 and this plan the town under openDesk gives `total` 22, `by_coverage` in_suite 6, in_suite_with_limits 8, transfer_undocumented 3, not_available 5, `needed` names the device-management, Windows-applications, Power Platform and telephony rows, and `unknown_need` is 3 (SharePoint workflows, VBA macros, desktop operating system), matching RR-06's 4 Yes, 1 No, 3 Unknown; the non-profit under openDesk has an empty `needed`. A copied opendesk mapping with one `in_suite` row changed to `not_available` changes `by_coverage` and the replacements table together.

    Site. Regenerate both site demo reports (`uv run fazit demo --lang <lang> --sample town --profile opendesk --out <fresh temporary directory>`, copy the printed report over `site/demo/<lang>/index.html`). If the town's status counts changed, update only the tally sentence and the report-card alt-text counts on both home pages in their existing wording, as RR-01 Task 1 did. Also update the coverage table cells on both home pages (`site/index.html`, `site/de/index.html`) that `site/check_site.py` compares with the mapping files, so they match Task 1's openDesk additions (XWiki, Notes, CryptPad), in the table's existing wording and markup; this is the only other home page edit (founder-approved amendment, 2026-11-22; RR-08 later moves the table to its own page). Otherwise leave the home pages untouched.
  </action>
  <verify>
    <automated>uv run pytest -q && uv run ruff check . && uv run ruff format --check . && uv run python -c 'from fazit.report import scope_statement; print(scope_statement)' && outen="$(mktemp -d)" && logen="$(mktemp)" && uv run fazit demo --lang en --out "$outen" > "$logen" && test -f "$(tail -n 1 "$logen")" && outde="$(mktemp -d)" && logde="$(mktemp)" && uv run fazit demo --lang de --out "$outde" > "$logde" && test -f "$(tail -n 1 "$logde")" && uv run python site/check_site.py</automated>
  </verify>
  <acceptance_criteria>
    - `uv run pytest -q` exits 0 and `uv run python site/check_site.py` prints "No errors."
    - `grep -c "scope_statement" src/fazit/report.py` [HEAD=0 EXPECT>=2]
    - `grep -c "scope_statement" src/fazit/templates/report.html.j2` [HEAD=0 EXPECT==0] (RR-03 renders it)
    - The SUMMARY records the town and non-profit scope statements under openDesk and Nextcloud in both languages
    - Follows DESIGN.md
  </acceptance_criteria>
  <done>RR-03 has tested scope-statement data that cannot disagree with the replacements table or the gap list, and the site reports match the package.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| mapping and rule YAML → status | Consultants and the maintainer edit these files; a gap row now changes readiness |
| public documentation → mapping claim → council decision | A coverage label or note can overstate or understate what a supplier documents |

## STRIDE Threat Register

Security level: ASVS 1. Blocking threshold: high.

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-RR-70 | Tampering | `status.yaml` `target_gaps`: a consultant sets a target gap to Blocker | medium | mitigate | The loader accepts only `needs_work` (Task 2); a Blocker on a gap needs a new reviewed rule (usefulness C8) |
| T-RR-71 | Repudiation | A target gap or Unknown need makes an area look better than its evidence | high | mitigate | Need Unknown only adds missing evidence; need Yes only raises Ready or Unknown to Needs work and keeps the incomplete marker (RULE-03: a confirmed problem may give a worse status than Unknown); property test against the gap-free evaluation (Task 2) |
| T-RR-72 | Repudiation | A mapping row claims coverage its source does not support, or names a supplier as a recommendation | medium | mitigate | Every openDesk row cites the specific source of this plan, checked 2026-11-22; unconfirmed facts are left out; every file says it is unreviewed until the operator review; no recommendation wording |
| T-RR-73 | Repudiation | The gap list, the cards and the summary disagree on a function's need | medium | mitigate | One computation in `status.py`; `mapping_gaps` and `scope_statement` read the rows' `transfer_gaps`; tests compare the context with the rendered tables (Tasks 2 and 3) |
| T-RR-74 | Information disclosure | A reviewer's name enters the mapping file and the report | low | mitigate | `operator_review` holds only `unreviewed` or a date |
| T-RR-01 | Tampering | Markup in a target reason or a mapping note | low | mitigate | Autoescape covers every expression; the existing escaping test applies |
| T-RR-SC | Tampering | package installs | high | mitigate | This plan installs nothing and adds no dependency |
</threat_model>

<verification>
Before declaring the plan complete:
- [ ] `uv run ruff check .` and `uv run ruff format --check .` exit 0
- [ ] `uv run pytest -q` exits 0
- [ ] `uv run fazit demo --lang de` and `uv run fazit demo --lang en`, each into a fresh temporary directory, exit 0 and the printed path exists
- [ ] `uv run python site/check_site.py` prints "No errors."
- [ ] `STATUSES` and the cost model are unchanged; no `status: blocker` was added
</verification>

<success_criteria>
- Statuses depend on the chosen profile through data, never towards Ready on Unknown evidence and never to Blocker on a gap alone
- The openDesk mapping cites a specific, dated page per row and includes XWiki, Notes and CryptPad; transfer-only gaps say so; all three files are marked unreviewed
- `scope_statement` exists, equals the replacements table and the gap list, and is absent for the generic profile
- Every new German string is listed for the maintainer's native review
</success_criteria>

<output>
Create `.planning/report-redesign/RR-07-SUMMARY.md` when done. Record: the final signatures of `evaluate`, `TransferGap`, `TargetGapRule`, `WorkloadStatus`, `TargetMapping` and `ScopeStatement`; the RR-06 need findings used for SharePoint workflows and VBA; every status, incomplete or note change on the two samples under each profile; the scope statements of Task 3; the native-review table (every new German string: mapping notes, the coverage label, the review sentences, the two target reasons and next steps with their kind and the verb behind it); every edited existing assertion with its item (C1 or C5); the questions for the operator review (Nextcloud Collectives, a Nextcloud diagram editor, XWiki applications and the openDesk low-code row, Nextcloud and generic rows for wiki pages, notes and diagrams, every `not_available` row); the test count and runtime of `uv run pytest -q`.

Notes for the following plans:
- RR-02: each card can read `row.transfer_gaps` (need Yes first) for the target line; a target rule is an ordinary `StatusRule`, so the card's reason, notes and next step need no special case.
- RR-03: render `scope_statement` with RR-01's `summary.scope_*` keys and `mapping_coverage.<id>` labels; link each needed function to `#<id>`; `reviewed_on` is available if the summary should say the mapping is unreviewed (founder decision C4 makes the operator review a gate before the redesign ships). The town has 22 openDesk functions, not 19.
- RR-04: the target next steps have kind `replace`; the gap list keeps its markup; the `strong` inside each gap item carries the anchor id.
- RR-05: the operator review of the three mapping files and of `target_gaps` is the founder's gate before ship; list it.
</output>

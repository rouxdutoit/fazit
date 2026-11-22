---
phase: report-redesign
plan: 06
type: execute
wave: 2
depends_on: ["RR-01"]
files_modified:
  - src/fazit/report.py
  - src/fazit/mappings.py
  - src/fazit/inputs.py
  - src/fazit/rules/findings.yaml
  - src/fazit/rules/status.yaml
  - src/fazit/rules/risky_file_types.yaml
  - src/fazit/rules/mappings/opendesk.yaml
  - src/fazit/rules/mappings/nextcloud.yaml
  - src/fazit/rules/mappings/generic.yaml
  - src/fazit/templates/report.html.j2
  - src/fazit/locales/en.yaml
  - src/fazit/locales/de.yaml
  - src/fazit/demo/town/scan.json
  - src/fazit/demo/town/inputs.yaml
  - src/fazit/demo/nonprofit/scan.json
  - src/fazit/demo/nonprofit/inputs.yaml
  - inputs.example.yaml
  - docs/interview-checklist.md
  - docs/interview-checklist.de.md
  - docs/scan-format.md
  - DECISIONS.md
  - tests/test_evidence_cli.py
  - tests/test_rules.py
  - tests/test_inputs.py
  - tests/test_model.py
  - tests/test_cli.py
  - tests/tenants.py
  - site/demo/en/index.html
  - site/demo/de/index.html
autonomous: true
requirements: [RULE-02, RULE-03, RULE-05, COST-01, COST-06, MODL-01, MODL-03, MODL-04]

estimate:
  tokens: 150000
  raw_tokens: 150000
  tasks: 3
  confidence: medium

must_haves:
  truths:
    - "The need for Windows desktops comes only from the answer `device_management.windows_desktops_required`: Windows-only applications without a web version never turn it into Yes and never make a No answer Unknown; unanswered, the desktop gap reads Unknown with `answer_not_provided` (launch critique C6)"
    - "No reason or next step of a rule whose status is not Blocker, and no Ready reason, says that something blocks a move, in either language; a test over the loaded status rules checks it (usefulness A7, UI-SPEC 9 item 11)"
    - "An inputs file that gives a subset count above its population count (for example 20 Windows devices of 10 devices) is refused at load time, naming `inputs.yaml` and `provided_counts.<subset id>` (C3; D31 covers `scan.json` only)"
    - "Teams is Ready only when no apps, tabs, bots or connectors are added to teams, as well as today's conditions; SharePoint is Ready only when no workflows run on its sites, as well as today's conditions; an unanswered new question keeps the area from Ready (C2). No new Blocker rule (founder decision C8)"
    - "The interview, `inputs.example.yaml` and the catalogue carry yes/no answers for SharePoint workflows and VBA macros, and each is the need finding of its function in all three mappings (C5 answers)"
    - "`.xls` and the other legacy Office formats that can hold VBA are listed under \"May contain macros\" (C4)"
    - "In a sample run every measured figure reads \"Measured (simulated)\" / \"Erhoben (simuliert)\" and the inventory heading names a fictional organisation; a report from a non-sample scan shows neither (A3, report side)"
    - "`docs/scan-format.md` documents every field the scan loader accepts and carries one minimal example that a test loads and renders (C9)"
    - "Every rule this plan adds or rewords carries `next_step` with `kind` and both texts; every new or changed German string is in the SUMMARY's native-review table"
  artifacts:
    - path: "src/fazit/rules/status.yaml"
      provides: "Reworded Windows-software rule; `sharepoint-workflows` and `teams-apps` rules; deeper Ready blocks for SharePoint and Teams"
      contains: "id: teams-apps"
    - path: "src/fazit/rules/findings.yaml"
      provides: "Three new answer findings"
      contains: "office_files.vba_macros_in_use"
    - path: "src/fazit/inputs.py"
      provides: "Subset check for counts supplied together in one inputs file"
      contains: "subset_count_exceeds_population"
    - path: "docs/scan-format.md"
      provides: "The scan.json 1.x format with one minimal example"
      contains: "schema_version"
  key_links:
    - from: "src/fazit/rules/mappings/*.yaml"
      to: "src/fazit/report.py"
      via: "`_mapping_gaps` reads the need only from `need_finding`; `need_if_positive` is gone from the loader, the dataclass and the files"
      pattern: "need_finding"
    - from: "src/fazit/rules/findings.yaml"
      to: "inputs.example.yaml and docs/interview-checklist*.md"
      via: "`test_inputs_example_covers_the_contract` and `test_checklist_matches_inputs_and_catalogue` require every answer finding in both"
      pattern: "workflows_in_use"
    - from: "docs/scan-format.md"
      to: "src/fazit/model.py"
      via: "a test loads the example with `load_scan_text` and checks that every loader field name appears in the document"
      pattern: "load_scan_text"
---

# Plan RR-06: rule and validation fixes from the launch critique and the usefulness review

## Goal

The rules say only what the evidence supports. Windows applications no longer decide on their own that the organisation needs Windows desktops; no Needs work reason says "blocks"; contradictory device counts in an inputs file are refused; Teams and SharePoint need more than a count to be Ready; legacy macro formats are listed; the interview records the answers the SharePoint workflow and VBA mappings were missing; sample runs say their measurements are simulated; and the scan format is documented.

<objective>
Apply the rule and validation items of the launch critique (`.planning/research/launch-critique/SYNTHESIS.md` C2, C3, C4, C5 answers, C6, C9, A3 report side) and of the usefulness review (A6's dependency on the desktop inference, A7's "blocks" wording), as `REV4-CHANGE-MAP.md` assigns them to RR-06. Rules stay data; the cost model, `STATUSES` and the section order stay as they are.

Purpose: RR-07 builds the scope statement and target-aware readiness on these rules, and RR-02 builds the cards on them; both need the final rules first.
Output: rule and catalogue data, three small code changes (`report.py`, `mappings.py`, `inputs.py`), template and locale lines for the simulated label, sample data, interview documents, `docs/scan-format.md`, one D31 bullet, tests, regenerated site demo reports.

Run order of the plan set: RR-01, RR-06, RR-07, RR-02, RR-03, RR-04, RR-05. No RR-08: the simulated label and the scan format fit Task 3.
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
- DECISIONS.md (Principles, D31, the M0 entry "2026-11-21 — M0 complete")
- .planning/report-redesign/REV4-CHANGE-MAP.md (binding: rules for every plan, who owns what)
- .planning/report-redesign/RR-01-PLAN.md and, once it exists, `.planning/report-redesign/RR-01-SUMMARY.md` (the `next_step` layout with `kind`, the owner roles, the drafting rules, the renamed `found.title`)
- .planning/research/launch-critique/SYNTHESIS.md (C2 to C6, C9, A3), with CRITIC-astra.md (comments 2, 5, 7, 8 and the "Published sample report" table) and CRITIC-fable.md (comments 4 and 11) in the same folder
- .planning/research/report-usefulness/SYNTHESIS.md (A6, A7, and decision 8 in section C)
- .planning/report-redesign/UI-SPEC.md (revision 4: section 2.3 "Reason" and "Next step", section 2.4, section 9 "Honesty" and item 11)
- docs/interview-checklist.md and docs/interview-checklist.de.md

Base: current `main` (df36196 or later) with RR-01 applied. RR-01 removes Licences from assessment (14 assessed areas, 30 status rules), gives every rule `next_step` with `kind` (`clarify`, `decide`, `replace`) and both texts, and changes `found.title` to "What Fazit recorded" / "Was Fazit erfasst hat". If `.planning/quick/261122-rv11-truthful` has landed, D31 and the scan loader have more checks; nothing here depends on them.

Facts checked on df36196 (re-check with grep before relying on them):
- The desktop inference: `FunctionMapping.need_if_positive` and `_need_conditions` in `src/fazit/mappings.py`; the `need_if_positive` branch in `_mapping_gaps` in `src/fazit/report.py`, which sets need Yes from `windows_software.without_web_version_count` when the desktop answer is missing, and turns an answer No into Unknown with `desktop_requirements_conflict`; `need_if_positive: windows_software.without_web_version_count` on the `desktop_operating_system` row of all three mapping files. `grep -rn "need_if_positive" src/fazit | wc -l` prints 16; `grep -rn "desktop_requirements_conflict" src tests | wc -l` prints 4 (both locales, `report.py`, one test). The reason code is not in `findings.yaml`'s `codes.reasons`; it exists only in the report and the locales.
- The town demo (opendesk) lists eight transfer gaps: needed (Yes) device_management, desktop_operating_system, windows_applications, automation_and_low_code, telephony; not needed teams_chat_history; Unknown sharepoint_workflows, vba_macros. After Task 1 the desktop gap is Unknown: 4 Yes, 1 No, 3 Unknown, which RR-07's scope statement expects (usefulness A6).
- The only status text that says "blocks" is `software-no-web-version` ("blocks a move away from Windows desktops", "verhindert die Ablösung").
- C3: `_population_bounds` and `check_subsets` in `src/fazit/model.py` check `subset_of` only inside `scan.json`, and only for observations with the same source and period or instant. `load_inputs_text` in `src/fazit/inputs.py` checks no relationship between counts. Reproduced: the town scan with an inputs file giving `device_management.device_count: 10` and `device_management.windows_device_count: 20` renders and exits 0. The only catalogue pair both supplied as answers is `device_management.windows_device_count` (`subset_of: [device_management.device_count]`). The error code `subset_count_exceeds_population` and its sentence exist in both locales.
- A rule condition that is not answered already counts as missing evidence and keeps an area from Ready (`_matching_rules` in `src/fazit/status.py`), so Teams' audio-conferencing licence condition already does; no Ready condition is added for it.
- `src/fazit/rules/risky_file_types.yaml` lists 11 macro extensions, none of them legacy binary formats. `tests/test_rules.py::test_shipped_risky_extensions` lists them, and `test_checklist_matches_inputs_and_catalogue` requires the checklist's macro question to list exactly the same extensions.
- `test_every_provided_finding_is_used_by_the_report` (`tests/test_inputs.py`) asserts that the only answer finding no status rule reads is `device_management.windows_desktops_required`, and that it is the desktop row's need finding in every profile.
- Every sample scan lists every catalogue finding (`test_catalogue_and_town_sample_agree` checks the town's order; `test_sample_has_all_findings_and_explicit_gaps` checks both samples).
- The Hypothesis tenant generator (`_inputs` in `tests/tenants.py`) draws every answer count independently, so it can draw more Windows devices than devices.
- Provenance words are printed by `strings.provenance[...]` at five places in `src/fazit/templates/report.html.j2`: in `evidence_summary`, the headline list, the licence product count, the rule-evidence list, and once for a rule condition's required provenance. `sample_scan` (from `Scan.is_sample`) is in the template context. `test_german_visible_text_uses_only_german_provenance_words` (`tests/test_cli.py`) requires every German provenance value to appear in the German town report and no English one.
- A scan with `source_kind: import`, no collectors, `licences: null`, one unknown finding (`directory.user_count`, `not_collected_in_this_version`) and one provided finding (`telephony.in_use`, source `interview`) loads and renders today; it is not a sample scan.
- `.planning/REQUIREMENTS.md` DOCS-04 names `docs/schema.md`; the launch critique and the change map name `docs/scan-format.md`. This plan writes `docs/scan-format.md` and leaves REQUIREMENTS.md to the coordinator.

Scope precedence: the founder's launch-critique and usefulness decisions win over UI-SPEC where they differ (UI-SPEC 9 says rule evaluation changes only through RR-06 and RR-07). Not in this plan: target-aware readiness, coverage labels, citations and the unreviewed marker of the mapping files (RR-07); the empty inventory for the own-answers walkthrough (README is the coordinator's, the blank interview starter is OUTP-04); new Blocker rules (decision C8: only with the operator review).

Size: three tasks, one executor run. Task 2 touches the most files but each change is a line or a block; do it in the order its action lists.

Environment:
- The executor cannot commit. Leave every change in the working tree; the orchestrator reviews and commits.
- Run every command from the repository root. Every Python command goes through `uv`; if the shell does not find it, run `export PATH="$HOME/.local/bin:$PATH"` first. Install nothing and add no dependency. Add no module.
- Locate every Python symbol with grep at execution time, never by line number. Re-read every file immediately before you edit it; never revert, reformat or rewrite changes you did not make. Other plans and the site may carry uncommitted edits: change only what this plan names.
- Never weaken a test or a principle. Existing tests change only where a launch-critique item changes the behaviour they assert (C2, C3, C4, C5, C6, A3), or as UI-SPEC section 9 item 10 permits (fixtures gain fields); list each edited assertion with its item in the SUMMARY. Principle tests (unknown is never Ready, a skipped collector never improves a status, no invented numbers) may only get stricter.
- Every report command builds into a fresh temporary output directory and checks exit code, file existence and content separately (D-56). No network.
- Every user-facing string goes into both locale files. English is British; German is native administrative German with the formal "Sie", no abbreviations such as "z. B.", status names exactly Bereit, Handlungsbedarf, Hindernis, Unbekannt, and "Umstieg" for the move. The German below is a draft: use it, improve it only if it breaks a rule here, and list every German string you add or change in the SUMMARY's native-review table with its English counterpart.
- New next steps follow RR-01 Task 2's drafting rules exactly: one sentence, one owner role from RR-01's set, no target product, none of the words import or export (not even inside another word), no "element", kind from the action the sentence names.
- If report output changes, regenerate both site demo reports (`uv run fazit demo --lang <lang> --sample town --profile opendesk --out <fresh temporary directory>`, then copy the printed report over `site/demo/<lang>/index.html`). The readiness tally of the town must not change in this plan (Task 2 keeps Teams Ready and SharePoint Needs work in the town); if `site/check_site.py` reports a tally mismatch, stop and report it instead of editing the home pages.
</context>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: Desktop need only from its answer, no "blocks" outside Blocker rules, and contradictory counts in an inputs file refused</name>
  <files>src/fazit/report.py, src/fazit/mappings.py, src/fazit/inputs.py, src/fazit/rules/status.yaml, src/fazit/rules/mappings/opendesk.yaml, src/fazit/rules/mappings/nextcloud.yaml, src/fazit/rules/mappings/generic.yaml, src/fazit/locales/en.yaml, src/fazit/locales/de.yaml, DECISIONS.md, tests/test_evidence_cli.py, tests/test_rules.py, tests/test_inputs.py, tests/tenants.py, site/demo/en/index.html, site/demo/de/index.html</files>
  <read_first>AGENTS.md, DESIGN.md ("Copy"), DECISIONS.md (D31, M0 entry: "The need remains unknown without a specific complete answer"), .planning/research/launch-critique/CRITIC-astra.md (comments 5 and 8, and the row "blocks a move away from Windows desktops" of the sample-report table), .planning/research/report-usefulness/SYNTHESIS.md (A6, A7), .planning/report-redesign/UI-SPEC.md (2.3 "Reason"), .planning/report-redesign/RR-01-SUMMARY.md (next-step layout and roles), src/fazit/mappings.py (grep `class FunctionMapping`, `def _need_conditions`, `def _function_mapping`), src/fazit/report.py (grep `def _mapping_gaps`), src/fazit/rules/mappings/*.yaml (grep `desktop_operating_system`), src/fazit/rules/status.yaml (the `windows_software` block), src/fazit/inputs.py (grep `def load_inputs_text`, `def _read_inputs`), src/fazit/model.py (grep `def check_subsets` for the rule being mirrored), src/fazit/catalogue.py (grep `subset_of`), tests/test_evidence_cli.py (grep `def test_windows_dependency_is_scoped_to_the_desktop_move`, `def test_desktop_gap_accepts_a_specific_confirmed_requirement`, `def test_desktop_gap_shows_disputed_software_count_from_another_workload`, `def test_desktop_gap_shows_disagreement_between_confirmation_and_software_list`), tests/test_rules.py (grep `def test_attention_shows_provided_counts_and_zero_explicitly`), tests/test_inputs.py (grep `def test_inputs_module_has_no_catalogue_ids`), tests/tenants.py (grep `def _inputs`)</read_first>
  <behavior>
    - Town (opendesk, both languages): the gap `desktop_operating_system` has `data-need="unknown"` with `data-reason="answer_not_provided"`; `windows_applications` stays `data-need="yes"`; the Windows-software row stays Needs work
    - With the desktop answer `false` and two applications without a web version, the desktop gap reads `data-need="no"` and nothing in the report carries `desktop_requirements_conflict`; with the answer `true` it reads Yes; with no answer it reads Unknown whatever the software list says
    - `need_if_positive` exists nowhere in `src/`, and a mapping row that carries it is refused naming `functions[<index>]` (unknown key)
    - The reworded `software-no-web-version` rule keeps two sentences: the first says the application needs Windows to run, on workstations or on a separate Windows system; the second is about the move away from Microsoft 365; neither says "blocks", "verhindert" or "Hindernis"
    - For every rule whose status is not `blocker`, and for every Ready reason, no English text contains "block" and no German text contains "hindernis", "verhinder" or "blockier" (case-insensitive), in the reason and in the next step
    - An inputs file with `device_management.device_count: 10` and `device_management.windows_device_count: 20` is refused: `load_inputs_text` raises with field `provided_counts.device_management.windows_device_count` and code `subset_count_exceeds_population`; `fazit report` exits 2 with one stderr line naming `inputs.yaml` and that field, and writes nothing; 10 of 10, either count alone, or a `null` population loads
  </behavior>
  <action>
    Remove the desktop inference (C6). In `src/fazit/mappings.py`, delete `need_if_positive` from `FunctionMapping`, from `_need_conditions` (which then returns the need finding only) and from the optional keys of `_function_mapping`, so a row that still carries it is refused as an unknown key. Delete the `need_if_positive:` line from the `desktop_operating_system` row of all three mapping files and change nothing else in those files (RR-07 owns them next). In `_mapping_gaps` in `src/fazit/report.py`, delete the `need_if_positive` branch; the need comes only from the row's `need_finding` as for every other row. For the default reason of an Unknown need, use `answer_not_provided` when the row has a `need_finding` and `not_established` when it has none, so the unanswered desktop gap keeps today's reason. Delete `reason.desktop_requirements_conflict` from both locales.

    Reword the Windows-software rule (C6, A7). In `rules/status.yaml`, rule `software-no-web-version`, replace the reason and next step with:
    - reason en: "At least one Windows-only application has no web version and needs Windows to run, either on staff workstations or on a separate Windows system. For the move away from Microsoft 365, plan how staff will keep using it or arrange a replacement."
    - reason de: "Mindestens eine reine Windows-Anwendung hat keine Webversion und benötigt Windows, entweder auf den Arbeitsplatzrechnern der Beschäftigten oder auf einem gesonderten Windows-System. Planen Sie für den Umstieg von Microsoft 365, wie die Beschäftigten sie weiter nutzen, oder sorgen Sie für einen Ersatz."
    - next_step, kind `clarify`, en: "The IT team asks the service owner of each such application whether staff need it on their own workstations or can use it on a separate Windows system."
    - next_step de: "Die IT-Abteilung klärt mit der fachlich verantwortlichen Stelle jeder solchen Anwendung, ob die Beschäftigten sie auf dem eigenen Arbeitsplatzrechner benötigen oder über ein gesondertes Windows-System nutzen können."
    Keep the rule's id, condition and status. If RR-01 drafted a next step for it, replace that one.

    Subset check for inputs (C3). In `src/fazit/inputs.py`, after the counts are read, refuse any supplied count whose catalogue entry has `subset_of` when every parent is also supplied (not `null`) in the same `provided_counts` and the count exceeds their sum: `validator.fail(f"provided_counts.{finding_id}", "subset_count_exceeds_population")`. Build the subset map from the catalogue in `load_inputs_text` (answer counts with `subset_of` whose parents are answer counts) and pass it to `_read_inputs`; name no catalogue id in `inputs.py` (`test_inputs_module_has_no_catalogue_ids`). Counts from different files are not compared, as D31 compares only observations from one source and instant. In `DECISIONS.md`, add one bullet at the end of D31's list: "Counts supplied together in one `inputs.yaml` follow the same subset rule: a subset count fits within its population when both are given." Change nothing else in D31. In `tests/tenants.py`, make `_inputs` keep every drawn subset count within its drawn parents (for example clamp it after drawing), so generated tenants stay valid; this makes the generator stricter, not the tests weaker.

    Tests (C6, A7, C3).
    - In `tests/test_evidence_cli.py`, rewrite the four desktop tests to the new behaviour, keeping their names unless a name states the old behaviour (then rename and list it): `test_windows_dependency_is_scoped_to_the_desktop_move` expects `desktop_need` "unknown" in the last case and the reworded reason (assert a phrase of the new first sentence and "move away from Microsoft 365" instead of "blocks a move away from Windows desktops" and "Microsoft 365 exit"); `test_desktop_gap_shows_disputed_software_count_from_another_workload` expects the desktop gap to read the answer (`data-need="no"`) and the dispute to stay on the Windows-software row; `test_desktop_gap_shows_disagreement_between_confirmation_and_software_list` expects `data-need="no"`, no `desktop_requirements_conflict` anywhere, and the software row with "2 applications". Keep `test_desktop_gap_accepts_a_specific_confirmed_requirement` as is.
    - In `tests/test_rules.py`, `test_attention_shows_provided_counts_and_zero_explicitly`: the software list makes `windows_applications` Yes and leaves `desktop_operating_system` Unknown. Add "no Needs work reason says it blocks a move" (UI-SPEC 9 item 11) over the loaded rule set with the checks of the behaviour list, and add `need_if_positive` as a refused case in `test_bad_mapping_names_the_file_and_field`.
    - In `tests/test_inputs.py`, add the subset refusal and the four accepted cases through `load_inputs_text`, and the CLI case with the town scan (exit 2, one stderr line naming the file and field, no output directory).
    Regenerate both site demo reports.
  </action>
  <verify>
    <automated>uv run pytest -q && uv run ruff check . && uv run ruff format --check . && test "$(grep -rn "need_if_positive\|desktop_requirements_conflict" src | wc -l)" -eq 0 && out="$(mktemp -d)" && log="$(mktemp)" && uv run fazit demo --lang en --out "$out" > "$log" && report="$(tail -n 1 "$log")" && test -f "$report" && grep -q 'data-gap="desktop_operating_system" data-need="unknown"' "$report" && grep -q 'data-gap="windows_applications" data-need="yes"' "$report" && ! grep -qi "blocks a move" "$report" && dir="$(mktemp -d)" && printf 'provided_counts:\n  device_management.device_count: 10\n  device_management.windows_device_count: 20\n' > "$dir/inputs.yaml" && { uv run fazit report src/fazit/demo/town/scan.json --inputs "$dir/inputs.yaml" --out "$dir/out" > /dev/null 2> "$dir/err"; test "$?" -eq 2; } && grep -q "provided_counts.device_management.windows_device_count" "$dir/err" && test ! -e "$dir/out" && uv run python site/check_site.py</automated>
    <human-check>Native-German review of the reworded Windows-software reason and its next step, with the other drafts of this plan.</human-check>
  </verify>
  <acceptance_criteria>
    - `uv run pytest -q` exits 0 and `uv run python site/check_site.py` prints "No errors."
    - `grep -rn "need_if_positive" src/fazit | wc -l` [HEAD=16 EXPECT==0]
    - `grep -rn "desktop_requirements_conflict" src tests | wc -l` [HEAD=4 EXPECT==0]
    - `grep -i "block\|verhindert\|hindernis" src/fazit/rules/status.yaml | grep -vc "status: blocker"` [HEAD=2 EXPECT==0] (no Blocker rule text uses these words today; if RR-01 gave the Blocker rule's next step one of them, it may stay and the count equals those lines)
    - `grep -c "subset_count_exceeds_population" src/fazit/inputs.py` [HEAD=0 EXPECT==1]
    - The SUMMARY lists every edited existing assertion with its item (C6, A7 or C3) and the reworded texts for review
    - Follows DESIGN.md ("Copy")
  </acceptance_criteria>
  <done>The desktop need is Unknown until someone answers it, no Needs work text says "blocks", contradictory device counts in one inputs file are refused with the field named, and the demo reports match.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: Deeper Ready rules for Teams and SharePoint, interview answers for SharePoint workflows and VBA, and legacy macro formats</name>
  <files>src/fazit/rules/findings.yaml, src/fazit/rules/status.yaml, src/fazit/rules/risky_file_types.yaml, src/fazit/rules/mappings/opendesk.yaml, src/fazit/rules/mappings/nextcloud.yaml, src/fazit/rules/mappings/generic.yaml, src/fazit/locales/en.yaml, src/fazit/locales/de.yaml, src/fazit/demo/town/scan.json, src/fazit/demo/town/inputs.yaml, src/fazit/demo/nonprofit/scan.json, src/fazit/demo/nonprofit/inputs.yaml, inputs.example.yaml, docs/interview-checklist.md, docs/interview-checklist.de.md, tests/test_rules.py, tests/test_inputs.py, tests/test_evidence_cli.py, site/demo/en/index.html, site/demo/de/index.html</files>
  <read_first>AGENTS.md ("Data, not code, holds judgement"), DESIGN.md ("Copy"), .planning/research/launch-critique/SYNTHESIS.md (C2, C4, C5), .planning/research/launch-critique/CRITIC-fable.md (comment 4), .planning/research/launch-critique/CRITIC-astra.md (comments 7 and 8), .planning/research/report-usefulness/SYNTHESIS.md (A6; section C decision 8), .planning/report-redesign/RR-01-SUMMARY.md (next-step layout, owner roles), src/fazit/rules/findings.yaml (the `sharepoint`, `teams` and `office_files` findings), src/fazit/rules/status.yaml (the `sharepoint`, `teams` and `office_files` blocks), src/fazit/rules/risky_file_types.yaml, src/fazit/rules/mappings/*.yaml (grep `function: sharepoint_workflows`, `function: vba_macros`), src/fazit/risky_files.py (grep `_RISKY_FINDING_PREFIX`), src/fazit/locales/en.yaml and de.yaml (the `finding` group), src/fazit/demo/town/inputs.yaml, src/fazit/demo/nonprofit/inputs.yaml, inputs.example.yaml (the `confirmations` block and its `# EN:`/`# DE:` comment pairs), docs/interview-checklist.md and .de.md (sections SharePoint, Teams, Office files), tests/test_inputs.py (grep `def test_inputs_example_covers_the_contract`, `def test_checklist_matches_inputs_and_catalogue`, `def test_every_provided_finding_is_used_by_the_report`, `def test_sample_inputs_and_rendered_statuses`), tests/test_rules.py (grep `def test_shipped_risky_extensions`, `def test_gap_need_uses_only_its_declared_complete_answer`, `def complete_evidence`), tests/test_evidence_cli.py (grep `def test_unlisted_plan_prevents_an_absence_conclusion_but_preserves_known_assignments`, `def test_header_shows_both_file_dates_when_samples_are_mixed`), tests/test_model.py (grep `def test_catalogue_and_town_sample_agree`)</read_first>
  <behavior>
    - The catalogue has three new boolean answer findings, each `unit: null`, `provided: answer`, `headline: false`: `sharepoint.workflows_in_use` (after `sharepoint.custom_solutions_in_use`), `teams.apps_in_use` (after `teams.chat_history_must_be_kept`) and `office_files.vba_macros_in_use` (after `office_files.kind.onenote`)
    - Each new finding carries `owner` (RR-01 requires it): `sharepoint.workflows_in_use` and `office_files.vba_macros_in_use` → `service_owner`, `teams.apps_in_use` → `it_team`; record them in the SUMMARY with RR-01's owner table
    - SharePoint is Ready only with today's conditions and `sharepoint.workflows_in_use == false`; rule `sharepoint-workflows` (Needs work) fires when it is true. Teams is Ready only with today's conditions and `teams.apps_in_use == false`; rule `teams-apps` (Needs work) fires when it is true. An unanswered new question leaves the area Unknown or, when another rule decides it, incomplete with the question listed as missing evidence. No new rule has status `blocker`
    - The rows `sharepoint_workflows` and `vba_macros` carry `need_finding: sharepoint.workflows_in_use` and `need_finding: office_files.vba_macros_in_use` in all three mapping files; an answer `true` makes the need Yes, `false` No, no answer Unknown
    - The macro kind lists, after today's eleven extensions, `xls`, `xlt`, `xla`, `doc`, `dot`, `ppt`, `pot`, `pps`, `ppa`; the interview's macro question in both languages lists the same twenty
    - Town statuses are unchanged (after RR-01: Ready onedrive, teams, small_apps; Blocker telephony; Unknown security_compliance; the rest Needs work); the town's SharePoint row is now marked incomplete; the town's gaps read 4 Yes, 1 No, 3 Unknown (`sharepoint_workflows`, `vba_macros`, `desktop_operating_system`). Nonprofit statuses are unchanged, and its `vba_macros` gap reads No
    - Both locales carry the three finding labels; `inputs.example.yaml` carries the three keys with their `# EN:`/`# DE:` comments; each checklist has one question per new key
  </behavior>
  <action>
    Catalogue and labels. Add the three findings to `rules/findings.yaml` in the places the behaviour gives. Labels (`finding.<id>`), English / German draft:
    - `sharepoint.workflows_in_use`: "Workflows on SharePoint sites, lists or libraries in use" / "Workflows auf SharePoint-Websites, in Listen oder Bibliotheken im Einsatz"
    - `teams.apps_in_use`: "Apps, tabs, bots or connectors added to teams" / "In Teams eingebundene Apps, Registerkarten, Bots oder Konnektoren"
    - `office_files.vba_macros_in_use`: "VBA macros that staff rely on" / "VBA-Makros, auf die die Beschäftigten angewiesen sind"
    The VBA answer must not start with `office_files.kind.` (that prefix is the risky-file list's).

    Status rules (C2; decision C8: Needs work only). In `rules/status.yaml`:
    - SharePoint ready evidence gains `{finding: sharepoint.workflows_in_use, op: '==', value: false}`; ready reason: "The SharePoint sites have been counted, and the organisation reports neither custom solutions nor workflows on them." / "Die SharePoint-Websites sind erfasst, und die Organisation meldet dort weder individuell angepasste Lösungen noch Workflows."
    - New rule `sharepoint-workflows` after `sharepoint-custom-solutions`: when `sharepoint.workflows_in_use == true`, status `needs_work`; reason "Workflows on SharePoint sites, lists or libraries need to be rebuilt or replaced before the sites move." / "Workflows auf SharePoint-Websites, in Listen oder Bibliotheken müssen neu erstellt oder ersetzt werden, bevor die Websites umziehen."; next_step kind `clarify`: "The service owner of each affected site lists the workflows and approvals that staff still rely on." / "Die fachlich verantwortliche Stelle jeder betroffenen Website erfasst die Workflows und Genehmigungen, auf die die Beschäftigten noch angewiesen sind."
    - Teams ready evidence gains `{finding: teams.apps_in_use, op: '==', value: false}`; ready reason (says what was answered, not only that teams were counted, CRITIC-fable comment 4): "The teams have no guests and no added apps, tabs, bots or connectors, and the chat history does not need to be kept." / "Die Teams haben keine Gäste und keine eingebundenen Apps, Registerkarten, Bots oder Konnektoren, und der Chatverlauf muss nicht erhalten bleiben."
    - New rule `teams-apps` after `teams-chat-history`: when `teams.apps_in_use == true`, status `needs_work`; reason "Apps, tabs, bots or connectors added to teams need a replacement after the move." / "In Teams eingebundene Apps, Registerkarten, Bots oder Konnektoren benötigen nach dem Umstieg einen Ersatz."; next_step kind `clarify`: "The IT team lists the apps, tabs, bots and connectors added to teams and asks each service owner which of them staff still use." / "Die IT-Abteilung erfasst die in Teams eingebundenen Apps, Registerkarten, Bots und Konnektoren und klärt mit der fachlich verantwortlichen Stelle, welche davon die Beschäftigten noch nutzen."
    - `office_files.vba_macros_in_use` feeds no status rule: the macro count already decides Office files, and the answer says whether a transfer gap matters (planner's discretion; record it).
    Use RR-01's `next_step` layout (`kind`, `en`, `de`). Status names, owners and words follow RR-01 Task 2.

    Mappings (C5 answers). Add `need_finding: sharepoint.workflows_in_use` to the `sharepoint_workflows` row and `need_finding: office_files.vba_macros_in_use` to the `vba_macros` row of all three mapping files, directly after `workload:` as the desktop row does. Change nothing else in the mapping files.

    Risky file types (C4). Append `xls, xlt, xla, doc, dot, ppt, pot, pps, ppa` to the macro kind's extensions; keep its label and note. Update the macro question of both checklists to list all twenty extensions in the same order.

    Inputs and interview. In `inputs.example.yaml`, add the three keys with `null` to `confirmations` in catalogue order, each after a comment pair:
    - "# EN: Confirm whether workflows or automated approvals run on SharePoint sites, lists or libraries." / "# DE: Geben Sie an, ob auf SharePoint-Websites, in Listen oder Bibliotheken Workflows oder automatisierte Genehmigungen laufen."
    - "# EN: Confirm whether apps, tabs, bots or connectors are added to teams." / "# DE: Geben Sie an, ob in Teams Apps, Registerkarten, Bots oder Konnektoren eingebunden sind."
    - "# EN: Confirm whether staff rely on VBA macros in Office files." / "# DE: Geben Sie an, ob die Beschäftigten auf VBA-Makros in Office-Dateien angewiesen sind."
    In the checklists, add one question each under SharePoint, Teams and Office files, in the existing form "- question (`id`)?" and without "confirm", "knows whether" or "bestätigt":
    - "Do staff rely on workflows or automated approvals that run on SharePoint sites, lists or libraries, including flows started from them (`sharepoint.workflows_in_use`)?" / "Sind die Beschäftigten auf Workflows oder automatisierte Genehmigungen angewiesen, die auf SharePoint-Websites, in Listen oder Bibliotheken laufen, auch auf dort gestartete Flows (`sharepoint.workflows_in_use`)?"
    - "Are apps, tabs, bots or connectors added to teams that staff use (`teams.apps_in_use`)?" / "Sind in Teams Apps, Registerkarten, Bots oder Konnektoren eingebunden, die die Beschäftigten nutzen (`teams.apps_in_use`)?"
    - "Do staff rely on VBA macros in Office files for their work (`office_files.vba_macros_in_use`)?" / "Sind die Beschäftigten bei ihrer Arbeit auf VBA-Makros in Office-Dateien angewiesen (`office_files.vba_macros_in_use`)?"

    Sample data. In both sample `scan.json` files, add one entry per new finding at its catalogue position, shaped like the existing `device_management.windows_desktops_required` entry (unknown, `answer_not_provided`). Sample answers (they are labelled sample answers): town `teams.apps_in_use: false`, `sharepoint.workflows_in_use: null`, `office_files.vba_macros_in_use: null` (the town keeps its Teams status, and its SharePoint workflow and VBA needs stay Unknown for RR-07's scope statement); nonprofit `teams.apps_in_use: false`, `sharepoint.workflows_in_use: false`, `office_files.vba_macros_in_use: false`. Add them in catalogue order inside `confirmations`.

    Tests (C2, C4, C5).
    - `tests/test_rules.py`: `test_shipped_risky_extensions` lists the twenty macro extensions (C4); new tests: SharePoint and Teams are Ready with every answer `false` (`complete_evidence`), Needs work through `sharepoint-workflows` and `teams-apps` with `true`, and not Ready with the new answer removed; each new rule's `next_step` has kind `clarify` and both texts; `sharepoint_workflows` and `vba_macros` read Yes, No and Unknown from their answers in every profile.
    - `tests/test_inputs.py`: `test_every_provided_finding_is_used_by_the_report` expects the mapping-only answers `{device_management.windows_desktops_required, office_files.vba_macros_in_use}`, each the need finding of its row (`desktop_operating_system`, `vba_macros`) in every profile (C5). `test_sample_inputs_and_rendered_statuses` must pass without edits.
    - `tests/test_evidence_cli.py`: in `test_unlisted_plan_prevents_an_absence_conclusion_but_preserves_known_assignments`, add `teams.apps_in_use: false` to the answers (C2, the fixture answers the new Ready question).
    - The town's gap counts of the behaviour (4 Yes, 1 No, 3 Unknown under opendesk) as one assertion in `tests/test_rules.py`, so RR-07 inherits it.
    Regenerate both site demo reports.
  </action>
  <verify>
    <automated>uv run pytest -q && uv run ruff check . && uv run ruff format --check . && uv run python -c 'from fazit.catalogue import load_catalogue; from fazit.status import load_status_rules; from fazit.mappings import load_mapping, PROFILES; from fazit.risky_files import load_risky_file_types; c = load_catalogue(); rules = {r.id: r for b in load_status_rules(c).workloads.values() for r in b.rules}; assert rules["teams-apps"].status == rules["sharepoint-workflows"].status == "needs_work"; assert all(r.status != "blocker" or r.id == "telephony-no-replacement" for r in rules.values()); macro = next(k for k in load_risky_file_types(c) if k.id == "macro"); assert {"xls", "doc", "ppt"} <= set(macro.extensions) and len(macro.extensions) == 20; needs = {p: {f.function: f.need_finding for f in load_mapping(p, c).functions} for p in PROFILES}; assert all(n["sharepoint_workflows"] == "sharepoint.workflows_in_use" and n["vba_macros"] == "office_files.vba_macros_in_use" for n in needs.values()), needs' && out="$(mktemp -d)" && log="$(mktemp)" && uv run fazit demo --lang en --out "$out" > "$log" && report="$(tail -n 1 "$log")" && test -f "$report" && grep -q 'data-gap="sharepoint_workflows" data-need="unknown"' "$report" && grep -q 'data-gap="vba_macros" data-need="unknown"' "$report" && grep -q '<code>.xls</code>' "$report" && grep -q 'data-workload="teams" data-status="ready"' "$report" && np="$(mktemp -d)" && nplog="$(mktemp)" && uv run fazit demo --sample nonprofit --lang de --out "$np" > "$nplog" && test -f "$(tail -n 1 "$nplog")" && grep -q 'data-gap="vba_macros" data-need="no"' "$(tail -n 1 "$nplog")" && uv run python site/check_site.py</automated>
    <human-check>Native-German review of the labels, rule texts, next steps, example comments and checklist questions of this task.</human-check>
  </verify>
  <acceptance_criteria>
    - `uv run pytest -q` exits 0 and `uv run python site/check_site.py` prints "No errors."
    - `grep -cE "^  - id: (sharepoint\.workflows_in_use|teams\.apps_in_use|office_files\.vba_macros_in_use)$" src/fazit/rules/findings.yaml` [HEAD=0 EXPECT==3]
    - `grep -c "^      - id:" src/fazit/rules/status.yaml` [HEAD=30 after RR-01, EXPECT==32]
    - `grep -cE "^          kind: (clarify|decide|replace)$" src/fazit/rules/status.yaml` [HEAD=30 after RR-01, EXPECT==32] (adjust the indentation to RR-01's layout and record it)
    - `grep -c "status: blocker" src/fazit/rules/status.yaml` [HEAD=1 EXPECT==1]
    - `grep -c "need_finding: sharepoint.workflows_in_use\|need_finding: office_files.vba_macros_in_use" src/fazit/rules/mappings/opendesk.yaml` [HEAD=0 EXPECT==2], and the same for `nextcloud.yaml` and `generic.yaml`
    - `grep -cw "xls" src/fazit/rules/risky_file_types.yaml` [HEAD=0 EXPECT==1]
    - The SUMMARY lists every edited existing assertion with its item, the town and nonprofit gap counts, and the German drafts
    - Follows DESIGN.md ("Copy")
  </acceptance_criteria>
  <done>Teams and SharePoint need an answer about apps and workflows before they can be Ready, the SharePoint workflow and VBA gaps can be answered, legacy macro formats are listed, the samples keep their statuses, and the interview documents match the catalogue.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 3: "Measured (simulated)" and a fictional-inventory heading in sample runs, and the scan format with one minimal example</name>
  <files>src/fazit/templates/report.html.j2, src/fazit/locales/en.yaml, src/fazit/locales/de.yaml, docs/scan-format.md, tests/test_cli.py, tests/test_model.py, site/demo/en/index.html, site/demo/de/index.html</files>
  <read_first>AGENTS.md ("Report", "Words"), DESIGN.md ("Copy", "Structure"), DECISIONS.md (D31, M0 entry, Principle 5), .planning/research/launch-critique/SYNTHESIS.md (A3, C9), .planning/research/launch-critique/CRITIC-astra.md (comment 2 and the sample-report rows "Microsoft 365 inventory" / "Measured"), .planning/research/launch-critique/CRITIC-fable.md (comment 11 and the "Measured" row of the overreach table), .planning/report-redesign/UI-SPEC.md (2.4; 9 "Honesty"), src/fazit/templates/report.html.j2 (grep `strings.provenance[`, `strings.found.title`, `sample_scan`, `macro evidence_summary`), src/fazit/locales/en.yaml and de.yaml (groups `provenance`, `found`, `header`), src/fazit/model.py (grep `_SCAN_FIELDS`, `_FINDING_FIELDS`, `_COLLECTOR_REQUIRED`, `_COLLECTOR_OPTIONAL`, `_COVERAGE_COUNTS`, `_LICENCE_FIELDS`, `_PRODUCT_REQUIRED`, `_PRODUCT_OPTIONAL`, `_SERVICE_PLAN_FIELDS`, `SOURCE_KINDS`, `COLLECTOR_STATUSES`, `PROVENANCES`, `COVERAGE_KINDS`, `def is_sample`, `def check_evidence`, `def check_finding_source`, `def load_scan_text`), src/fazit/rules/findings.yaml (`codes`), tests/test_cli.py (grep `def test_german_visible_text_uses_only_german_provenance_words`, `def test_sample_measurement_labels_and_directory_note`), docs/interview-checklist.md (tone of a user document)</read_first>
  <behavior>
    - In a sample scan (`sample_scan` true), every printed provenance word for measured evidence is `provenance.measured_sample`: "Measured (simulated)" / "Erhoben (simuliert)"; `data-provenance="measured"` and every other hook keep their values; `<span class="prov">Measured</span>` never appears in a sample report, in either language
    - In a sample scan the inventory section's `h2` reads `found.title_sample`: "What Fazit recorded for a fictional organisation" / "Was Fazit für eine fiktive Organisation erfasst hat"; otherwise `found.title`
    - The rule-condition line that names a required provenance (for telephony, "Provided") is unchanged
    - `docs/scan-format.md` names, in backticks, every field the loader accepts (the nine field tuples of the read-first list) and every value of the four code tuples; explains the provenance rules as `check_evidence` and `check_finding_source` apply them; points to `src/fazit/rules/findings.yaml` for finding ids, units, collectors, sources and reason codes and to D31 for the consistency checks, without copying them; says that no import or live collection exists yet and that answers and costs belong in `inputs.yaml`; and contains exactly one fenced `json` block
    - The example loads with `load_scan_text`, is not a sample scan, and `fazit report` builds a report from it with exit 0; that report shows neither "(simulated)" nor the fictional heading
  </behavior>
  <action>
    Simulated label (A3). Add `provenance.measured_sample` and `found.title_sample` to both locales with the texts of the behaviour. In `report.html.j2`, add one macro `provenance_word(provenance)` that returns `strings.provenance.measured_sample` when `sample_scan` and `provenance == 'measured'`, otherwise `strings.provenance[provenance]`, and use it at the four places that print the provenance of evidence (`evidence_summary`, the headline list, the licence product count, the rule-evidence list); leave the rule-condition line as it is. Change the inventory `h2` to `found.title_sample` when `sample_scan`. Add no CSS and no attribute. The decision is per scan, not per finding: `Scan.is_sample` is true for every scan that holds evidence from a sample source (D31), so every measured figure in it is simulated. Provided answers keep "Provided", because their source already names the sample ("Sample interview answer").

    Scan format (C9). Write `docs/scan-format.md` in English (developer reference, like command help under D18; record this): title "Scan file format"; what the file is and who writes it today (`fazit demo`, with simulated data; no import or live collection yet); that answers, costs and Windows-only applications belong in `inputs.yaml`; the top-level fields; collectors; findings and the rules per provenance (measured, provided, unknown: which fields are required and which must be empty); coverage; licences, products and service plans; what the loader does with unknown keys (drops and counts them without showing them) and that the format holds no free text or person names (Principle 5); `schema_version` major 1 and that another major is refused; one minimal example; and one line on `source_kind`: `sample` for fictional data, `import` for evidence brought in from outside Fazit, `live` for live collection (not built). Use this example, which loads today:

    ```json
    {
      "schema_version": "1.0",
      "tool": {"name": "fazit", "version": "0.1.0"},
      "generated_at": "2026-11-02T09:00:00Z",
      "source_kind": "import",
      "collectors": [],
      "findings": [
        {"id": "directory.user_count", "workload": "directory", "value": null, "unit": "users", "provenance": "unknown", "collector": null, "source": null, "collected_at": null, "period": null, "coverage": null, "missing_reason": "not_collected_in_this_version"},
        {"id": "telephony.in_use", "workload": "telephony", "value": true, "unit": null, "provenance": "provided", "collector": null, "source": "interview", "collected_at": "2026-11-02", "period": null, "coverage": null, "missing_reason": null}
      ],
      "licences": null
    }
    ```

    Format it readably in the document (one key per line is fine). Write plain sentences in the register of the interview checklist; no marketing words; say what exists today. Do not edit README.md (the coordinator links it).

    Tests (A3, C9).
    - `tests/test_cli.py`, next to `test_sample_measurement_labels_and_directory_note`: for the town in both languages, `<span class="prov">` + the plain measured word + `</span>` does not occur, the simulated word occurs, and the found `h2` is the sample title; for the scan-format example, neither occurs and the `h2` is `found.title`. `test_german_visible_text_uses_only_german_provenance_words` must pass unchanged (the new value is German and appears in the German town report).
    - `tests/test_model.py`: `test_scan_format_document_matches_the_loader`: read `docs/scan-format.md`; exactly one fenced `json` block; it loads with `load_scan_text` and the shipped catalogue, `is_sample` is false; every name of the nine field tuples and every value of the four code tuples appears in backticks in the document; the document mentions D31 and `findings.yaml`; `fazit report` on the example in a temporary directory exits 0 and writes the report.
    Regenerate both site demo reports.
  </action>
  <verify>
    <automated>uv run pytest -q && uv run ruff check . && uv run ruff format --check . && out="$(mktemp -d)" && log="$(mktemp)" && uv run fazit demo --lang en --out "$out" > "$log" && report="$(tail -n 1 "$log")" && test -f "$report" && grep -q "Measured (simulated)" "$report" && grep -q "What Fazit recorded for a fictional organisation" "$report" && ! grep -q '<span class="prov">Measured</span>' "$report" && outde="$(mktemp -d)" && logde="$(mktemp)" && uv run fazit demo --lang de --out "$outde" > "$logde" && test -f "$(tail -n 1 "$logde")" && grep -q "Erhoben (simuliert)" "$(tail -n 1 "$logde")" && doc="$(mktemp -d)" && uv run python -c 'import re, sys; text = open("docs/scan-format.md", encoding="utf-8").read(); blocks = re.findall(r"```json\n(.*?)```", text, re.S); assert len(blocks) == 1; open(sys.argv[1], "w", encoding="utf-8").write(blocks[0])' "$doc/scan.json" && dlog="$(mktemp)" && uv run fazit report "$doc/scan.json" --out "$doc/out" > "$dlog" && test -f "$(tail -n 1 "$dlog")" && ! grep -q "(simulated)" "$(tail -n 1 "$dlog")" && uv run python site/check_site.py</automated>
    <human-check>Native-German review of `provenance.measured_sample` and `found.title_sample`. A read of `docs/scan-format.md` by the maintainer for accuracy and tone.</human-check>
  </verify>
  <acceptance_criteria>
    - `uv run pytest -q` exits 0 and `uv run python site/check_site.py` prints "No errors."
    - `grep -c "measured_sample\|title_sample" src/fazit/locales/en.yaml` [HEAD=0 EXPECT==2], and the same for `de.yaml`
    - `grep -c "provenance_word(" src/fazit/templates/report.html.j2` [HEAD=0 EXPECT==5] (one definition, four uses)
    - `test -f docs/scan-format.md` and `grep -c '^```json' docs/scan-format.md` [HEAD=absent EXPECT==1]
    - `grep -c "Measured (simulated)" site/demo/en/index.html` [HEAD=0 EXPECT>=1]
    - Follows DESIGN.md ("Copy"; the label is a word in the provenance position, no pill)
  </acceptance_criteria>
  <done>A cropped sample report can no longer pass simulated figures off as measured or the fictional inventory as the reader's own, and anyone can read and check the scan format against a working example.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| inputs.yaml → report | The operator types counts and answers; contradictions must not reach the report as fact |
| rule and mapping YAML → report | Consultants edit these files; their text is printed into the report |
| sample data → reader | A screenshot or excerpt of a sample report can travel without its header |
| docs/scan-format.md → third-party producers | A wrong document leads others to write files the loader refuses or misreads |

## STRIDE Threat Register

Security level: ASVS 1. Blocking threshold: high.

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-RR6-01 | Repudiation | Removing the desktop inference hides a real Windows dependency | medium | mitigate | The Windows-software row stays Needs work with a reason that names the Windows need; `windows_applications` stays Yes; the desktop gap shows Unknown with `answer_not_provided`, never No without an answer (Task 1 tests) |
| T-RR6-02 | Tampering | Contradictory counts in one inputs file | medium | mitigate | Load-time subset check naming file and field; generic over the catalogue's `subset_of` (Task 1) |
| T-RR6-03 | Repudiation | New answers make Ready easier to reach | medium | mitigate | New questions only add Ready conditions; unanswered keeps the area from Ready; tests with the answer removed (Task 2); no new Blocker rule |
| T-RR6-04 | Spoofing | A sample figure read as a real measurement | medium | mitigate | "Measured (simulated)" at every evidence provenance and the fictional heading in sample runs; tests in both languages (Task 3) |
| T-RR6-05 | Tampering | `docs/scan-format.md` drifts from the loader | low | mitigate | A test loads and renders the example and checks every loader field name (Task 3) |
| T-RR6-06 | Tampering | Markup in new rule texts or labels | low | mitigate | Autoescape covers every expression; RR-01's rule-markup test covers the new rules |
| T-RR-SC | Tampering | package installs | high | mitigate | This plan installs nothing and adds no dependency |
</threat_model>

<verification>
Before declaring the plan complete:
- [ ] `uv run ruff check .` and `uv run ruff format --check .` exit 0
- [ ] `uv run pytest -q` exits 0
- [ ] `uv run fazit demo --lang de` and `uv run fazit demo --lang en`, each into a fresh temporary directory, exit 0 and the printed path exists
- [ ] `uv run python site/check_site.py` prints "No errors."
- [ ] `STATUSES`, the cost model and `SECTION_ORDER` are unchanged; the town's readiness tally is unchanged
- [ ] Only `telephony-no-replacement` has status `blocker`
</verification>

<success_criteria>
- The report states a Windows desktop need only when someone has answered it, and no Needs work reason says "blocks"
- Contradictory device counts in one inputs file are refused
- Teams and SharePoint need answers about apps and workflows to be Ready; the SharePoint workflow and VBA gaps can be answered; legacy macro formats are listed
- Sample runs label simulated figures and the fictional inventory as such; the scan format is documented with a tested example
- Every new or reworded rule has a next step with its kind; every German draft is listed for review
</success_criteria>

<output>
Create `.planning/report-redesign/RR-06-SUMMARY.md` when done. Record: the final shape of `FunctionMapping` and of the inputs subset check; the town and nonprofit statuses and gap counts per profile after the plan; the native-review table (every German string added or changed, with its English counterpart, key or rule id, and kind for next steps); every edited existing assertion with its item; the planner's-discretion items (VBA answer feeds no status rule; scan format in English only; the default reason of an Unknown need); anything RR-07 must know about the mapping rows it reviews next (`need_if_positive` gone; `need_finding` added on `sharepoint_workflows` and `vba_macros`; `_mapping_gaps` lists only `not_available` rows today, so a new coverage id for "Direct transfer undocumented" must keep these rows in the gap list); the test count and runtime of `uv run pytest -q`.
</output>

## Source coverage

| Source | Item | Where | Status |
|--------|------|-------|--------|
| CRITIQUE C6 | Windows desktop need stays Unknown unless answered | Task 1 | COVERED |
| USEFULNESS A7 / spec 2.3, 9 item 11 | No Needs work reason says "blocks"; test over all rules | Task 1 | COVERED |
| CRITIQUE C3 | Windows subtotal larger than the device total | Task 1 (inputs.yaml); `scan.json` already refused by D31 (`check_subsets`, acf9be9) for comparable observations | COVERED |
| CRITIQUE C2 | Deeper Ready rules for Teams and SharePoint | Task 2 | COVERED |
| CRITIQUE C5 (answers) | Interview fields for SharePoint workflows and VBA, connected to the mappings | Task 2 (mappings otherwise: RR-07) | COVERED |
| CRITIQUE C4 | `.xls` and legacy macro formats | Task 2 | COVERED |
| CRITIQUE A3 (report side) | "Simulated" label and fictional inventory heading | Task 3 | COVERED; empty inventory for the own-answers walkthrough: README (coordinator) and OUTP-04 |
| CRITIQUE C9 | `docs/scan-format.md` with one minimal example | Task 3 | COVERED; REQUIREMENTS DOCS-04 names `docs/schema.md` (coordinator) |
| USEFULNESS A6 | Town gaps 4 Yes, 1 No, 3 Unknown for RR-07 | Tasks 1 and 2 | COVERED |
| Decision C8 | No new Blocker rule before the operator review | Task 2 | COVERED |

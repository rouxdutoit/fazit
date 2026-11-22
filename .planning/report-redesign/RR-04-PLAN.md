---
phase: report-redesign
plan: 04
type: execute
wave: 6
depends_on: ["RR-01", "RR-06", "RR-07", "RR-02", "RR-03"]
files_modified:
  - src/fazit/report.py
  - src/fazit/templates/report.html.j2
  - src/fazit/icons/circle.svg
  - src/fazit/icons/contrast.svg
  - src/fazit/icons/code.svg
  - src/fazit/icons/cancel.svg
  - site/icons/circle.svg
  - site/style.css
  - src/fazit/locales/en.yaml
  - src/fazit/locales/de.yaml
  - tests/test_report.py
  - tests/test_rules.py
  - tests/test_cli.py
  - tests/test_evidence_cli.py
  - site/demo/en/index.html
  - site/demo/de/index.html
autonomous: true
requirements: [REPT-01, REPT-03, REPT-04, REPT-05, OUTP-03, OUTP-04]

estimate:
  tokens: 210000
  raw_tokens: 210000
  tasks: 3
  confidence: low

must_haves:
  truths:
    - "\"What to do next\" follows the summary and has two groups: \"Worth doing even if you stay\" lists the `clarify` and `decide` next steps of Blocker and Needs work areas first, then, under the subheading \"Evidence still needed\" (`readiness.missing`, carrying `id=\"not-examined\"`), every open point once, grouped by the evidence requested, with its areas linked, the fix that names who acts, and the `inputs.yaml` key where one closes it; \"Needed for a move\" lists the `replace` steps (UI-SPEC 4.1, criterion 22)"
    - "No status timeline, pilot sentence, stock step list or proposed decision remains in the report"
    - "A skip link, a sticky bar with the wordmark and seven links in section order (Summary, Next steps, Areas, Costs, Replacements, Closer look, Appendix) and `main#main` let a reader reach every section; every in-page link resolves; the bar scrolls sideways at 360 px with visible continuation and unclipped focus (UI-SPEC 5, 6.2 exception 3)"
    - "Header, replacements, closer look, recorded inventory and appendix use the site's components as UI-SPEC section 4 decides, with every existing hook kept; the appendix has an open part \"What Fazit does not look at\""
    - "Coverage symbols are inline paths from the shared icon set, drawn in `--fg` (cancel in `--fg-2`), never in a status colour and never a status symbol: `in_suite` is the new `circle`, in the report and on the website's coverage table (UI-SPEC 6.2, criterion 12)"
    - "Print starts `path`, costs and appendix on new pages, so page one is header and summary; print shows every card and every disclosure's content, no bar or filters, unsplit card heads and repeated table headers, and is the same with any filter active (UI-SPEC 7)"
    - "At 360 px the summary's status list and blockers come before any secondary figure, there is no sideways page scroll, a seven-digit tile amount stays on one line, long German cost cells are not clipped, and targets are at least 44 px (UI-SPEC 7, criterion 13)"
    - "No CSS rule and no locale key remains that nothing uses"
  artifacts:
    - path: "src/fazit/report.py"
      provides: "Open points grouped by the evidence requested, and next steps split by kind, in the report context"
      contains: "data-open-point"
    - path: "src/fazit/templates/report.html.j2"
      provides: "What to do next, navigation, restyled sections, print and phone rules"
      contains: "class=\"bar\""
    - path: "src/fazit/icons/circle.svg"
      provides: "Coverage symbol for in the suite, byte-identical to site/icons/circle.svg"
    - path: ".shots/report-redesign/check.mjs"
      provides: "Browser check parts layout and print (ignored by git)"
  key_links:
    - from: "src/fazit/report.py"
      to: "src/fazit/templates/report.html.j2"
      via: "the report context carries the open points and the steps by kind; the template renders them in `path`"
      pattern: "data-step-kind"
    - from: "src/fazit/templates/report.html.j2"
      to: "src/fazit/icons/circle.svg"
      via: "the report's icon list registers circle, contrast, code and cancel and inlines their paths"
      pattern: "circle"
    - from: "src/fazit/templates/report.html.j2"
      to: "tests/test_report.py"
      via: "every href in the report names an id that exists exactly once"
      pattern: "href=\"#"
---

# Plan RR-04: what to do next, navigation, remaining sections, print and phone

## Goal

The report puts the findings first: what a move would take, what stops it, what is still open and what it costs. It shows every area as a card the reader can filter, draws the costs, and looks like the website, without changing what is measured, provided or unknown (`.planning/report-redesign/UI-SPEC.md`, revision 4.1, section 0). There is no score, recommendation or proposed resolution.

<objective>
Replace the old suggested path with "What to do next", built only from findings; add the navigation; bring the remaining sections onto the site's components with a coverage symbol that no status uses; and make the report print with header and summary as page one and read well at 360 px.

Purpose: UI-SPEC sections 1.1, 4, 4.1, 5, 6.2 and 7, and the usefulness review (`.planning/research/report-usefulness/SYNTHESIS.md`, A4, A5, A11, A14; founder decisions C2 and C13). The IT lead and the integrator get one working list of open evidence and next steps; the council gets a page one that prints alone.
Output: report context and template, the `circle` symbol in `site/icons/` and `src/fazit/icons/`, the permitted test edits 7, 8, 9 and 12, new item 11 tests, the browser check parts `layout` and `print`, regenerated site demo reports.

This is plan 6 of 7 in the run order RR-01, RR-06, RR-07, RR-02, RR-03, RR-04, RR-05. RR-05 (design checks, real-PDF page-one check, screenshots, decisions) follows.
</objective>

<execution_context>
Read these two files before starting. They are plain paths, not includes.
- $HOME/.claude/gsd-core/workflows/execute-plan.md
- $HOME/.claude/gsd-core/templates/summary.md
</execution_context>

<context>
Read these files first. They are plain paths from the repository root.
- AGENTS.md
- DESIGN.md (binding: structure, tiles, no borders on cards on screen, symbols, links, copy, accessibility, lean)
- DECISIONS.md (Principles)
- .planning/report-redesign/UI-SPEC.md (revision 4.1; sections 1.1, 2.4, 4, 4.1, 5, 6, 7, 8, 9 and 11)
- .planning/report-redesign/REV4-CHANGE-MAP.md (who owns what; the interfaces "Next-step kind" and "Open points")
- .planning/research/report-usefulness/SYNTHESIS.md (sections A and C)
- .planning/report-redesign/RR-01-SUMMARY.md, RR-02-SUMMARY.md and RR-03-SUMMARY.md (what they delivered and where)
- .planning/phases/01-demo-and-report/01-CONTEXT.md (D-27, D-29, D-44, D-61, D-64, D-72, D-80)

What earlier plans deliver and this plan relies on, without implementing it:
- RR-01: Licences has no status, card or category; every problem rule's `next_step` carries `kind` (`clarify`, `decide` or `replace`), required by the rule loader and read in the template as `row.deciding.next_step.kind` (for a fired note, `rule.next_step.kind`; RR-01 adds no data attribute); the owner roles as the locale group `role.*`; every reason `fix` names what a person can do today (C7); RR-01 drops the old `path.unknown` and `path.needs_work` keys; all copy of UI-SPEC section 8, including `path.even_if_staying`, `path.for_move`, `appendix.not_looked`, `appendix.not_looked_text`, the `nav.*` labels, `nav.label`, `nav.skip`, `moves.status_link` and the new `moves.workload_status` value. None of `kind`, `next_step`, `role.*` or these keys exists on `main` today: find them with grep in `src/fazit/status.py`, `src/fazit/report.py` and the locales at execution time.
- RR-02: the site frame (`div.sec.grid`, `h2.sec-label`), tokens and site aliases, area cards `article.finding#readiness-W` in status groups `h3#status-S`, the `details` component, and `.shots/report-redesign/check.mjs` with the part `filters`. RR-02 leaves today's `div[data-subsection="not-examined"]` markup at the end of `readiness` untouched; this plan moves it.
- RR-03: `id="not-examined"` on today's not-examined block at the end of `readiness`, so the summary's link resolves until this plan moves it; `SECTION_ORDER` = header, summary, path, readiness, costs, moves, attention, found, appendix, footer, with `path` still holding today's content; the summary with `h2#summary-title`, the status list, blockers, unknowns (linking to `#not-examined`), the tiles, and `div#costs-missing`; the cost chart and break-even; an all-Unknown test fixture.
- RR-06 and RR-07: final rules and readiness; nothing here depends on their details.

Precondition: RR-03 is complete on `main` and `tests/helpers.py` exists. Import shared test helpers from `tests/helpers.py` (`ReportDocument`, `report_section`, `readiness_row`).

Environment:
- The executor cannot commit. Leave every change in the working tree; the orchestrator reviews and commits.
- Run every command from the repository root through `uv`; if the shell does not find it, run `export PATH="$HOME/.local/bin:$PATH"` first. Install nothing; add no dependency and no module. `node`, `pdftotext`, `pdfinfo` and `pdftoppm` are used only by the browser check in `.shots/`, never added to the repository.
- Base: current `main` (df36196 or later). Code moved since the plans were first written (D31 load-time checks in `model.py`, special cases removed from `status.py`). Locate every Python symbol with grep at execution time (for example `grep -n "_ICONS" src/fazit/report.py`, `grep -n "def _evidence_context" src/fazit/report.py`, `grep -n "class WorkloadStatus\|class MissingEvidence" src/fazit/status.py`), never by line number. Re-read every file before editing; never revert changes you did not make. `site/style.css` may carry unrelated edits: change only the declaration this plan names.
- Never weaken a test or a principle. Existing tests change only as UI-SPEC section 9 permits; this plan uses items 7, 8, 9 and 12 and adds item 11 tests. Any other failing test means the code is wrong; if the spec makes it impossible, stop and report.
- Hooks: every `data-*` attribute keeps its name, values, order and host element unless UI-SPEC 9 lists it; ids `readiness-title`, `readiness-{workload}`, `software-title`, `licences-title`, `not-examined` and RR-07's `transfer-gap-{function}` stay unique; `<section data-section="…">` tags stay literal. The CSP meta line is never touched.
- CSS follows DESIGN.md and UI-SPEC 6: tokens only, seven type sizes, the spacing scale; copy site rules declaration for declaration apart from the six exceptions of UI-SPEC 6.2. The bar's mask is written as UI-SPEC 6.2 exception 3 gives it; RR-05 owns its colour value, so this plan does not change it.
- Copy belongs to RR-01. Use its keys. If a key this plan needs is missing, add it in both locales with the text of UI-SPEC section 8 and list the German in the SUMMARY's native-review table as a draft. Add no other copy; never "verdict", "recommendation", "Urteil", "Empfehlung" or "empfohlen".
- Every report command builds into a fresh temporary output directory and checks exit code, file existence and content separately (D-56). No network. Do not publish the site from this plan.
</context>

<tasks>

<task type="tracer">
  <name>Task 1: End-to-end "What to do next": open points grouped by the evidence requested and next steps split by kind, from report context to rendered path, with every test that read the old path — one path only</name>
  <files>src/fazit/report.py, src/fazit/templates/report.html.j2, src/fazit/locales/en.yaml, src/fazit/locales/de.yaml, tests/test_report.py, tests/test_rules.py, tests/test_cli.py, tests/test_evidence_cli.py, site/demo/en/index.html, site/demo/de/index.html</files>
  <read_first>DESIGN.md ("Structure", "Copy"), .planning/report-redesign/UI-SPEC.md (sections 2.4 last paragraph, 4 row "Suggested path", 4.1 in full, 8 rows `path.*` and `readiness.missing`, 9 items 11 and 12, 11 criterion 22), .planning/report-redesign/REV4-CHANGE-MAP.md ("Interfaces between plans": next-step kind, open points), src/fazit/status.py (grep `class MissingEvidence`, `class WorkloadStatus`, `class StatusRule`, `next_step`, `kind`), src/fazit/catalogue.py (grep `provided`, `measured_by`, `owner`, `ROLES`), src/fazit/inputs.py (grep `def load_inputs_text`: `provided_counts` for answer counts, `confirmations` for answer booleans, `windows_only_software`), src/fazit/report.py (grep `def _evidence_context`, `unknown_findings=`, `skipped_collectors=`), src/fazit/templates/report.html.j2 (the `path` section; `div[data-subsection="not-examined"]` at the end of `readiness`; macros `reason_detail`, `status_label`), site/style.css (`.rows`, `.subsection`), tests/test_rules.py (grep `def test_suggested_path_lists_only_the_designated_workload_statuses`, `def test_suggested_path_explains_empty_lists`, `def test_complete_counts_must_agree_but_a_partial_count_can_be_consistent`, `def test_disputed_count_blocks_every_workload_that_uses_it`), tests/test_evidence_cli.py (grep `data-path-status`), tests/test_cli.py (grep `def test_scan_only_report_explains_readiness_and_missing_evidence`), tests/test_report.py (grep `def test_report_document_structure`)</read_first>
  <behavior>
    - `section[data-section="path"]` holds `h2.sec-label#path-title` (`path.title`) and, in order: `h3` `path.even_if_staying`; the steps of kind `clarify` and `decide` as `dl.rows` (only when there is one); `div[data-subsection="not-examined"]` (no id) holding `h4#not-examined` with `readiness.missing` ("Evidence still needed") and the open points as `dl.rows`, or `p` with `path.empty.unknown` when nothing is open; then, only when a step of kind `replace` exists, `h3` `path.for_move` and those steps as `dl.rows`. With no open point and no step of any kind, the section also ends with `p` `path.empty.blocker`, as today
    - A step row is `div > dt + dd[data-step-kind="{kind}"]`: `dt` is the area name linking to `#readiness-W`; `dd` is the rule's `next_step` in the report language. Steps come from Blocker and Needs work areas in display order (Blocker, then Needs work; catalogue order inside), the deciding rule first, then the other fired rules (`notes`), each rule once
    - Open points cover every Unknown area, every `row.missing` gap of every area (decided or Unknown), every unknown finding and every skipped collector, and each appears exactly once. Grouping key, the evidence requested: an answer finding's `inputs.yaml` path (`provided_counts.{id}` for a count, `confirmations.{id}` for a boolean); `windows_only_software` for both software-list findings; otherwise `collector.{id}` when the gap or finding names a collector; otherwise `finding.{id}`; an Unknown area with no gap is `area.{id}`; a skipped collector is `collector.{id}`. One missing export or answer is one row
    - An open-point row is `div > dt[data-open-point="{key}"] + dd`: `dt` names what is open (the collector's label for a collector row, otherwise the figure's or area's label); `dd` holds `ul.open-items` with one `li` per figure, collector or gapless Unknown area in the row, then one `p` with the owner role from RR-01's `role.*` group, the key in `code` when the row has an `inputs.yaml` key, and each distinct `reason.*.fix` of the row once
    - Item hooks keep their names: a figure's `li` carries `data-unexamined-finding="{id}"` when its observation is Unknown and `data-unexamined-gap="{id}"` when any area has a gap on it (both, in that order, when both hold), then the figure label and one link per affected area to `#readiness-W`; a skipped collector's `li` carries `data-unexamined-collector="{id}"` with the collector label and the reason label; every link to an Unknown area carries `data-unexamined-workload="{workload}"`, and no link to a decided area does
    - Rows are in catalogue order of the first figure or area they name; rows that name only a collector come last, in scan order. Output is deterministic
    - No `ul[data-path-status]`, `li[data-path-workload]`, `ol`, timeline, pilot sentence, stock step or proposed decision remains; `readiness` no longer holds the not-examined index
  </behavior>
  <action>
    Report context (`report.py`, UI-SPEC 4.1; map interface "Open points"). Add two small functions, each fitting on a screen, called from the evidence context (grep `def _evidence_context`): one builds the open points from the statuses, the merged findings, the catalogue entries and the scan's collectors, using the grouping key of the behaviour list, and returns them as a tuple of frozen dataclasses (key, what is open, items, affected areas per item, the `inputs.yaml` key or `None`, the distinct reason codes); the other splits the next steps into `clarify`/`decide` and `replace` lists in the behaviour's order, reading `kind` from `row.deciding.next_step.kind` and each note's `next_step.kind`. Each open point also carries its owner role id, read from the `owner` field RR-01 Task 2 puts on every catalogue finding entry (one of the six ids of `ROLES`, labelled by the `role.*` locale group), derived as RR-01 says: a figure's row from that finding's owner, a collector's row from its findings' owner, an Unknown area's row from its first missing finding (grep `owner` in `src/fazit/catalogue.py` and `role` in the locales; use the names RR-01-SUMMARY records); if a row's findings name different owners, the row shows every distinct owner in `ROLES` order, joined by " · "; a row with no finding to take an owner from (an Unknown area decided only by its reason code) takes the owner of that area's first finding in catalogue order, and `it_team` if the area has none. Record every such row in the SUMMARY. Expose both in the context. Remove `unknown_findings` and `skipped_collectors` from the context if nothing else reads them. Never change `STATUSES`, the evaluator or a status.

    Template. Rewrite the `path` section as the behaviour says, inside the frame RR-02 built, and move `div[data-subsection="not-examined"]` out of `readiness` into it with its new content, taking RR-03's `id="not-examined"` off the `div` and putting it on the `h4`, so exactly one element in the report has that id; give `h2` the id `path-title`. Every visible text comes from a locale key or catalogue label; use the existing `reason_detail` macro or the `reason` group for labels and fixes. Copy the site's `.rows` and `.subsection` rules if RR-02 or RR-03 have not already; style `ul.open-items` as plain rows with tokens only. Delete the old path markup and its CSS (`.path-workloads`, the `ol` rules, the not-examined list rules nothing else uses).

    Locales. Use `path.title`, `path.even_if_staying`, `path.for_move`, `path.empty.unknown`, `path.empty.blocker` and `readiness.missing` as RR-01 left them. Leave the now unused keys (`path.blocker`, `path.ready`, `path.empty.ready`, `path.pilot_evidence`, `path.pilot_choice`, `path.sequence`, `path.steps`, `readiness.not_examined` and any other `path.*` key nothing reads) for Task 3's clean-up, so the template-uses-locale and parity tests stay green in between.

    Test edits, permitted item 12, and no others. In `tests/test_rules.py`: rewrite `test_suggested_path_lists_only_the_designated_workload_statuses` (rename allowed) to assert, for its fixture: the deciding rule of telephony (Blocker) appears as `dd[data-step-kind]` with its kind and next step from the loaded rules, never from literals; every `clarify`/`decide` step precedes `id="not-examined"` and every `replace` step follows it; mail's gap appears as an open point linking to `#readiness-mail`; no link in `path` targets a Ready card; no `ol`, pilot or stock-step text and no "%". Rewrite `test_suggested_path_explains_empty_lists` for the case with nothing open and no step (the `complete_evidence` fixture, every area Ready; adjust values only if an area is not Ready): `path.empty.unknown` and `path.empty.blocker` appear and no `data-open-point` or `data-step-kind`. In `test_complete_counts_must_agree_but_a_partial_count_can_be_consistent` and `test_disputed_count_blocks_every_workload_that_uses_it`, and in `tests/test_evidence_cli.py` in `test_supplied_zero_preserves_a_skipped_observation`, `test_incomplete_bound_collector_is_reported_without_a_scan_finding`, `test_licensed_accounts_make_zero_assignments_inconclusive`, `test_licence_pilots_require_reconciled_directory_headcount`, `test_measured_positive_count_cannot_be_overridden_by_zero` and `test_disagreeing_provided_answers_remain_visible_and_undecided`, replace each "not among the Ready path items" assertion with "the area's card is not Ready" (`readiness_row` and its `data-status`) and, where the scenario leaves the area Unknown or incomplete, "an open point links to `#readiness-W`"; a baseline assertion that an area was in the Ready path list becomes "its card is Ready". In `tests/test_cli.py` `test_scan_only_report_explains_readiness_and_missing_evidence`, the not-examined assertions slice `path` instead of `readiness`; everything else in the test stays as RR-02 left it. `test_report_document_structure` keeps its `data-subsection` order unchanged (not-examined, cannot-be-moved, run-details): add no `data-subsection` anywhere.

    New item 11 tests in `tests/test_report.py` ("open points grouped by the evidence requested", "every next step has a kind", criterion 22), over town and non-profit in both languages and RR-03's all-Unknown fixture: `data-open-point` values are unique; every `row.missing` gap of every area is a link to its card inside the `li` of its figure, gaps inside decided areas included; every unknown finding has exactly one `li[data-unexamined-finding]`, every skipped collector exactly one `li[data-unexamined-collector]`, every Unknown area at least one link with `data-unexamined-workload`; in the town sample the skipped `exchange_recipients` collector and `mail.shared_mailbox_count` share one row keyed `collector.exchange_recipients`, and in the scan-only town report both software-list findings share the row `windows_only_software`; a row with an answer finding shows its `inputs.yaml` path in `code`; every row shows exactly one owner role text from the `role` group; `id="not-examined"` occurs exactly once, on an `h4` inside `path`; every `dd[data-step-kind]` value is `clarify`, `decide` or `replace` and equals its rule's `kind`; `h4#not-examined` follows every `clarify`/`decide` step and precedes every `replace` step; the path contains no `<ol`, no `data-path-status` and no `data-path-workload`.

    Regenerate both site demo reports from `uv run fazit demo --lang <lang> --sample town --profile opendesk --out <fresh temporary directory>`.
  </action>
  <verify>
    <automated>uv run pytest tests/test_report.py tests/test_rules.py tests/test_cli.py tests/test_evidence_cli.py -q && uv run pytest -q && uv run ruff check . && uv run ruff format --check . && out="$(mktemp -d)" && log="$(mktemp)" && uv run fazit demo --lang en --out "$out" > "$log" && report="$(tail -n 1 "$log")" && test -f "$report" && uv run python -c 'import re, sys; html = open(sys.argv[1], encoding="utf-8").read(); path = re.search(r"<section data-section=\"path\">.*?</section>", html, re.S)[0]; ready = html.split("<section data-section=\"readiness\">", 1)[1].split("</section>", 1)[0]; keys = re.findall(r"data-open-point=\"([^\"]+)\"", path); assert keys and len(keys) == len(set(keys)), keys; assert "collector.exchange_recipients" in keys; assert "<ol" not in path and "data-path-status" not in html and "not-examined" not in ready; assert path.count("id=\"not-examined\"") == 1 and re.search(r"<h4 id=\"not-examined\"", path); kinds = [(m.start(), m[1]) for m in re.finditer(r"data-step-kind=\"([^\"]+)\"", path)]; anchor = path.index("id=\"not-examined\""); assert all((pos < anchor) == (kind != "replace") for pos, kind in kinds), kinds' "$report" && uv run python site/check_site.py</automated>
  </verify>
  <acceptance_criteria>
    - `uv run pytest -q` exits 0 and `uv run python site/check_site.py` prints "No errors."
    - `grep -c "path.steps\|pilot_evidence\|pilot_choice\|data-path-status" src/fazit/templates/report.html.j2` [HEAD=3 EXPECT==0]
    - `grep -rc "data-path-status\|data-path-workload" tests` sums to 0 [HEAD=17 (test_rules.py 7, test_evidence_cli.py 10) EXPECT==0]
    - `grep -c 'data-subsection="not-examined"' src/fazit/templates/report.html.j2` stays 1, and it now sits inside the `path` section
    - Guard: `git diff -U0 -- src/fazit/status.py src/fazit/costs.py` is empty (no status or cost change)
    - The SUMMARY lists every edited existing assertion with its UI-SPEC section 9 item, the open-point rows of the English town report (key, items, areas), and the owner role each row shows
    - Follows DESIGN.md (one idea per row; facts only; no proposed decision; status names exact)
  </acceptance_criteria>
  <done>Directly after the summary, the reader finds what is worth doing whether or not the organisation moves, every piece of missing evidence once with who acts and what closes it, and what only a move needs; the stock steps and the status timeline are gone.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: Navigation, header, coverage symbol `circle`, replacements, closer look, recorded inventory and appendix on the site's components</name>
  <files>src/fazit/report.py, src/fazit/templates/report.html.j2, src/fazit/icons/circle.svg, src/fazit/icons/contrast.svg, src/fazit/icons/code.svg, src/fazit/icons/cancel.svg, site/icons/circle.svg, site/style.css, src/fazit/locales/en.yaml, src/fazit/locales/de.yaml, tests/test_report.py, tests/test_cli.py, tests/test_evidence_cli.py, site/demo/en/index.html, site/demo/de/index.html</files>
  <read_first>DESIGN.md ("Structure", "Symbols", "Links and buttons", "Accessibility and weight"), .planning/report-redesign/UI-SPEC.md (sections 1.1, 4 in full, 5, 6.2 with its exceptions and the coverage symbol list, 8 rows `nav.*`, `moves.*`, `appendix.not_looked*`, `found.title`, 9 items 7, 8 and 9, 11 criteria 1, 12, 15), .planning/report-redesign/REV4-CHANGE-MAP.md (the row "Coverage symbol `circle`" with the exact path), site/style.css (`.sr-only`, `.skip`, `.bar`, `.bar-in`, `.wordmark`, `.bar-links`, `.bar-links-in`, `.bar-links a`, `a`, `a:hover`, `html`, `.page-intro`, `.eyebrow`, `.note`, `.coverage` and its 600 px layout, `.cov-cell`, `.cov`, `.cov-full::before`, `.rows`, `.tiles`, `.tile-label`, `.figure-num`), site/index.html (the skip link, the bar, the coverage table rows), site/icons/check-circle.svg, site/icons/contrast.svg, site/icons/code.svg, site/icons/cancel.svg, site/icons/LICENSE, src/fazit/icons/LICENSE, src/fazit/report.py (grep `_ICONS`, `def _assets`, `project_name=`), src/fazit/templates/report.html.j2 (the `body` start, `header`, `main`, every `h2`, the moves, attention, found and appendix sections; macros `column`, `icon`, `mapping_date`, `workload_status`, `attention_evidence`; the `a:hover` rules), tests/test_report.py (grep `def test_report_cannot_fetch_resources`, `def test_report_styles_work_in_light_dark_narrow_and_print`), tests/test_evidence_cli.py (grep `def test_headline_qualifies_zero_without_complete_coverage`), tests/test_cli.py (grep `header\[key\]`), site/check_site.py (grep `def check_coverage`, `def check_reference`)</read_first>
  <behavior>
    - `body` starts with `a.skip[href="#main"]` (`nav.skip`), then `div.bar > div.bar-in > a.wordmark[href="#main"]` with `project_name` (lowercase "fazit", the wordmark), then `nav.bar-links[aria-label]` (`nav.label`) `> div.bar-links-in` with seven links in section order: Summary `#summary-title`, Next steps `#path-title`, Areas `#readiness-title`, Costs `#costs-title`, Replacements `#moves-title`, Closer look `#attention-title`, Appendix `#appendix-title`; `h2` of costs, attention and appendix gain those ids; `main` has `id="main"`; `html { scroll-padding-block-start: calc(var(--bar-h) + 16px) }`
    - The bar is `div.bar`, not a second `header`; sticky; below 820 px `.bar-in` stays a flex row and `.bar-links` scrolls sideways (`min-width: 0; overflow-x: auto; scrollbar-width: none; padding: 4px`) with the edge fade of exception 3; links `inline-flex` with `min-height: var(--hit)`; `a:hover { color: var(--accent-hover); }` unchanged; the dark glow uses `var(--link-glow)`
    - Header (`.page-intro`): organisation (or the unnamed-organisation words) as `p.eyebrow`, `h1`, `dl.report-meta` as one wrapping row at `--fs-footnote` (`display: flex; flex-wrap: wrap; gap: 4px 24px; margin-top: 16px`) with scan date, inputs date, tool version and target profile and their `data-input-role` hooks, then the sample note as `.note` (`margin-top: 24px`); the local and offline sentences move to run details
    - Coverage symbols: `in_suite` circle; `in_suite_with_limits` contrast; `open_source_community` and `open_source_third_party` code; `announced`, `component_vendor_solution`, `proprietary_third_party` and `not_available` cancel; drawn in `--fg`, cancel in `--fg-2`, never a status colour, never a status symbol. `circle.svg` is new in `site/icons/` and `src/fazit/icons/`, byte-identical, in the existing file layout: `<svg xmlns="http://www.w3.org/2000/svg" height="24" viewBox="0 -960 960 960" width="24"><path d="M480-80q-83 0-156-31.5T197-197q-54-54-85.5-127T80-480q0-83 31.5-156T197-763q54-54 127-85.5T480-880q83 0 156 31.5T763-763q54 54 85.5 127T880-480q0 83-31.5 156T763-197q-54 54-127 85.5T480-80Z"/></svg>` with no trailing newline (Material Symbols Rounded, filled; Apache-2.0 under the existing `LICENSE` files, no new licence file); `contrast.svg`, `code.svg` and `cancel.svg` are byte-identical copies of `site/icons/`; all four are registered in `_ICONS`. The website's coverage table uses `circle` too, and this plan owns that change (RR-05 need not make it): in `site/style.css` only the `url()` of `.cov-full::before` changes, from `icons/check-circle.svg` to `icons/circle.svg`; `site/icons/check-circle.svg` stays as the shared source of the report's Ready symbol
    - Replacements: a `.coverage` table with columns Microsoft function, Replacement (`.cov-cell`: inline coverage symbol, the coverage label at weight 600 on line one, the replacement on line two), Checked on (`mapping_date`), Area status (`workload_status` with its incomplete marker inside a link to `#readiness-W`, underlined, `aria-label` from `moves.status_link`); `tr[data-function][data-workload][data-status]` unchanged; no-function lines kept
    - Closer look: file types as `.coverage` (`tr[data-kind]`), software counts as `dl.rows` (each `dt`/`dd[data-software-count]` pair in a `div`), the Windows-only software table as `.coverage` (`tr[data-software-entry]`, region labelled by `software-title`), transfer gaps unchanged as `ul.mapping-gaps > li[data-gap][data-need]`, styled as rows, each keeping RR-07's `id="transfer-gap-{function}"` on its `strong` (the summary's scope statement links there) and RR-07's `p[data-mapping-review]` sentence under the replacements heading
    - Recorded inventory (`found`, after `attention` per RR-03's order; title `found.title`, or RR-06's `found.title_sample` in a sample run; provenance words through RR-06's `provenance_word` macro): `ul.tiles.tiles-2` of headline figures, each `li[data-provenance]` holding `strong.tile-label`, then `span.figure-num` with today's `value_text` (and its "at least" wording), then provenance and detail; then the licence products in a closed `details` whose `summary` (`id="licences-title"`) gives the product count with its provenance, or Unknown, and whose body holds today's `p[data-provenance]` line and the licence table (class `coverage`, hooks unchanged); no nav link
    - Appendix: Collection methods, Readiness rules, Function mapping and the cost formulas each in a closed `details` whose `summary` is today's heading text; then two open parts: `div.subsection` with `h3` `appendix.not_looked` and `p` `appendix.not_looked_text` (no `data-subsection`), and `div[data-subsection="run-details"]` with its `h3`, now starting with the local and offline sentences
    - In every report, every `href` starts with `#` and names an id that exists exactly once
  </behavior>
  <action>
    Navigation (UI-SPEC 5, 6.2 exceptions 3 and 4). Add the skip link and the bar at the start of `body`, before `header`; texts from RR-01's `nav` group, the wordmark from `project_name`, the `aria-label` one expression, so the template holds no literal text. Add the ids and `id="main"`. Copy the site's `.sr-only`, `.skip`, `.bar`, `.bar-in`, `.wordmark`, `.bar-links`, `.bar-links-in`, `.bar-links a` and hover rules, minus anything that depends on the site's script (menu button, menu states, call-to-action button), apply exception 3, keep the report's `a:hover` rule text, change the dark glow's raw colour to `var(--link-glow)`, add the scroll padding.

    Header (UI-SPEC 1.1). Restyle as the behaviour says, copying `.page-intro`, `.eyebrow` and `.note`. Move `header.local` and `header.offline` to the start of run details. Permitted edit 8: a test that looks for those two sentences in the header slice looks in run details instead; leave assertions on other header content where they are (`tests/test_cli.py` today checks them in the whole document, which needs no edit).

    Symbols and replacements (UI-SPEC 4, 6.2). Write `site/icons/circle.svg` with exactly the bytes of the behaviour, copy it and the three other files into `src/fazit/icons/` unchanged, and add the four names to `_ICONS`. Change the one `url()` in `site/style.css`. Map coverage codes to symbols in the template (or a small mapping in `report.py`), render each with the existing `icon` macro inside `.cov-cell`, and copy the site's `.coverage`, `.cov-cell` and `.cov` layout rules without the icon masks (exception 1). Header cells through the `column` macro: `moves.microsoft`, `moves.replacement`, `appendix.mapping_date`, `moves.workload_status`. The status link wraps `workload_status(row)` and carries the `aria-label` from `moves.status_link` and an underline.

    Closer look, recorded inventory, appendix. Build each as the behaviour says, copying the site's `.rows`, `.tiles` and `.figure-num` rules (the tile label is a `strong` so the headline test's structure holds; style it with the site's tile-label declarations). Keep every hook and id, including `h3#software-title` and the attention region labels tests split on. Add no `data-provenance` element before the Windows-only software table (a test counts them there). Every `details` uses RR-02's component rules.

    Tests. Item 7: in `test_headline_qualifies_zero_without_complete_coverage`, `span class="figure"` becomes `span class="figure-num"`; the qualified-zero wording stays. Item 9: expectations that still hold old title, scenario or coverage wording follow the locale. New item 11 tests in `tests/test_report.py`, over the four sample and language pairs: "nav links resolve" (every `href` starts with `#` and its id occurs exactly once; the bar's links are the seven of the behaviour list in that order; the first element in `body` is the skip link; `main` has `id="main"`); every replacements row has exactly one coverage symbol whose path is the registered icon for its code, the `in_suite` path is not the path of any `span.status` symbol, and no element in the replacements table carries a status class outside `workload_status`; `site/icons/circle.svg` and `src/fazit/icons/circle.svg` are byte-identical; the appendix contains `appendix.not_looked` and `appendix.not_looked_text`. Keep `test_report_cannot_fetch_resources` unchanged.

    Regenerate both site demo reports as in Task 1.
  </action>
  <verify>
    <automated>uv run pytest -q && uv run ruff check . && uv run ruff format --check . && for name in circle contrast code cancel; do cmp -s "site/icons/$name.svg" "src/fazit/icons/$name.svg" || exit 1; done && grep -q 'cov-full::before { --icon: url("icons/circle.svg")' site/style.css && out="$(mktemp -d)" && log="$(mktemp)" && uv run fazit demo --lang en --out "$out" > "$log" && report="$(tail -n 1 "$log")" && test -f "$report" && uv run python -c 'import re, sys; html = open(sys.argv[1], encoding="utf-8").read(); ids = re.findall(r" id=\"([^\"]+)\"", html); refs = re.findall(r"href=\"([^\"]*)\"", html); assert all(ref.startswith("#") and ids.count(ref[1:]) == 1 for ref in refs), [r for r in refs if ids.count(r[1:]) != 1]; assert re.search(r"<body>\s*<a class=\"skip\" href=\"#main\"", html); nav = re.findall(r"href=\"#([^\"]+)\"", html.split("class=\"bar-links-in\"", 1)[1].split("</nav>", 1)[0]); assert nav == ["summary-title", "path-title", "readiness-title", "costs-title", "moves-title", "attention-title", "appendix-title"], nav; header = html.split("</header>", 1)[0]; run = html.split("data-subsection=\"run-details\"", 1)[1]; assert "contacted no host" not in header and "contacted no host" in run' "$report" && uv run python site/check_site.py</automated>
  </verify>
  <acceptance_criteria>
    - `uv run pytest -q` exits 0 and `uv run python site/check_site.py` prints "No errors."
    - `grep -c 'class="bar"' src/fazit/templates/report.html.j2` [HEAD=0 EXPECT==1]
    - Guard: `grep -c "<header" src/fazit/templates/report.html.j2` still prints 1, and `grep -c 'a:hover { color: var(--accent-hover); }' src/fazit/templates/report.html.j2` still prints 1
    - Guard: `git diff -U0 -- src/fazit/templates/report.html.j2 > "$tmp"` succeeds and `grep -c "http-equiv" "$tmp"` prints 0
    - `ls src/fazit/icons/*.svg | wc -l` [HEAD=5 EXPECT==9, assuming RR-01 to RR-03 added no icon; otherwise their count plus 4], `ls site/icons/*.svg | wc -l` [HEAD=31 EXPECT==32], and `cmp` finds the four files identical
    - `grep -c "check-circle" site/style.css` [HEAD=1 EXPECT==0]; `git diff -- site/style.css` shows only that line from this plan
    - `grep -c "status-ready\|status-blocker\|status-needs-work" src/fazit/templates/report.html.j2` stays at its RR-03 value (no new status colour use)
    - The SUMMARY lists every edited existing assertion with its UI-SPEC section 9 item
    - Follows DESIGN.md (the bar holds the page links; every control works by keyboard; sections with a label left and content right; tiles with one anchor; symbols from the shared set and no status symbol reused)
  </acceptance_criteria>
  <done>A reader can skip to the content and reach every section in order from a sticky bar; every section uses the site's components; coverage reads as a symbol no status uses, in the report and on the website; the appendix says what Fazit does not look at; all hooks survive.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 3: Print with header and summary as page one, phone order, lean clean-up, and the browser check parts layout and print</name>
  <files>src/fazit/templates/report.html.j2, src/fazit/locales/en.yaml, src/fazit/locales/de.yaml, tests/test_report.py, site/demo/en/index.html, site/demo/de/index.html</files>
  <precondition>Node and Playwright with Chromium are installed (`/home/roux/.local/share/playwright-1.62.1/node_modules/playwright` exists, `node --version` succeeds), and `pdftotext`, `pdfinfo` and `pdftoppm` are on the path. If not, do everything else, record what did not run in the SUMMARY, and hand back.</precondition>
  <read_first>DESIGN.md ("Accessibility and weight", "Lean"), AGENTS.md ("No dead code"), .planning/report-redesign/UI-SPEC.md (section 1.2 "Page one", section 7 in full, section 9 "Hooks kept" for the CSS a test matches, section 11 criteria 2, 9, 13, 14, 16), .planning/research/report-usefulness/SYNTHESIS.md (A2), tests/test_report.py (grep `def test_report_styles_work_in_light_dark_narrow_and_print`), tests/test_locales.py (grep `def test_locale_key_parity`, `def test_template_uses_locale_for_visible_text`), src/fazit/templates/report.html.j2 (the style block in full), src/fazit/locales/en.yaml and src/fazit/locales/de.yaml, .shots/report-redesign/check.mjs (the part `filters` from RR-02)</read_first>
  <behavior>
    - Print: `.bar`, `.skip`, `.filters` and `.areas-empty` hidden; light palette; every `details` open through `details::details-content { content-visibility: visible; display: block; block-size: auto }` with chevrons hidden; type in pt (display 24, title 18, headline 14, lead 12, body 10, subhead 9, footnote 8); card padding 12pt, section padding 16pt; one column with tiles in two; card head (area, status, reason, next step) kept together without a new wrapper element; evidence may break between rows; `thead { display: table-header-group }`; `.table-scroll { overflow: visible }`; `break-inside: avoid` on tiles, rows, cost rows and `tr`; `break-before: page` on `[data-section="path"]`, `[data-section="costs"]` and `[data-section="appendix"]` and nowhere in header or summary, so header and summary are page one; `print-color-adjust: exact`; 0.5pt `--rule` borders on cards, tiles, rows, notes and bar segments; links in `--fg`; `@page { margin: 15mm }`
    - Phone (360 px): one column with a 16 px gutter; the summary keeps source order (no `order`, grid placement or `flex-direction: *-reverse` in it), so the status list and blockers come before the tiles and any secondary figure; meta row, legends and filter tracks wrap; cost headings wrap and block values sit one per line; cost table rows stack; no sideways page scroll
    - The CSS the style test matches still exists: a `(max-width: 40rem)` query, `content: attr(data-label)`, `@page { margin: … }`, `@media print`, `break-inside: avoid`, `print-color-adjust: exact`, the print `::details-content` rule
    - No CSS rule matches nothing the template can render, and no locale key is left that the template, the code, the tests and `site/check_site.py` never read (keys read through a dynamic group such as `costs[result.id]`, `status[...]`, `mapping_coverage[...]`, `reason[...]` or `code_label` stay)
    - Browser check part `layout`: at 1280 by 800 the title, the summary's status list (counts with definitions) and the first blocker row, or the zero-blocker sentence and its caveat, are inside the first screen, in both languages and both samples, and the summary contains no `.readiness-bar` or other part-of-whole element; at 360 px, light and dark: the status list and the blockers part sit above the first cost tile; no sideways scroll; every tile `.figure-num` on one line; no clipped cost-table cell; the bar's links scroll with a mask and a focused link's ring is not clipped; filter tracks wrap; filter segments, bar links and `summary` elements at least 44 px high; the skip link visible with a ring when focused; the unknown cost marker's dashed outline visible
    - Browser check part `print`: A4 PDFs of the town reports in both languages with backgrounds on and off, with and without a status filter selected by keyboard; `pdftotext` shows the summary title on page one and no text of `path` there; the titles of `path`, costs and appendix each open a page; the text contains evidence from a Ready card's disclosure, a licence product code, every appendix part (including "What Fazit does not look at") and the run details; it shows neither the search hint nor the filter legends; the text with a filter equals the text without
  </behavior>
  <action>
    Print and phone (UI-SPEC 7). Rewrite the print block and the narrow rules as the behaviour says. Set the pt sizes by overriding the seven type tokens inside the print block, after the token blocks, so the colour token blocks and their order stay untouched. Keep the card head together with `break-after: avoid` and `break-inside: avoid` on its parts. Use the site's 600 px `.coverage` stacked layout for tables other than the cost table, and RR-03's 40rem cost-table stacking. Then delete the old `table:not(.cost-table)` card-stack rules, which RR-03 left in place because the tables Task 2 restyles still used them (UI-SPEC 3.2); keep the `content: attr(data-label)` declaration of the cost table. Whether page one fits A4 for every sample is RR-05's real-PDF check; record here the page count of header and summary per report and language from the `print` part.

    Lean clean-up (DESIGN.md "Lean", AGENTS.md "No dead code"). Delete every CSS rule whose selector matches nothing the template can render (for example the old headline, figure, readiness table, path, not-examined list, moves, licences and sample-note rules), and every locale key nothing reads, in both locales with the same keys: grep the dotted key and its leaf in `src/fazit`, `tests` and `site/check_site.py` before deleting, and keep any key reached through a dynamic group. Expected among them: the old `path.*` keys listed in Task 1 and `readiness.not_examined`. List each deleted rule and key in the SUMMARY. The locale parity test must still pass.

    Tests. Keep `test_report_styles_work_in_light_dark_narrow_and_print` passing unchanged (RR-05 restructures it). Add item 11 assertions in `tests/test_report.py` for print rules that have no test yet: print hides `.bar` and `.filters`, opens every `details`, and sets `break-before: page` on `path`, costs and appendix and on no other section.

    Browser check. Extend `.shots/report-redesign/check.mjs` with the parts `layout` and `print`, keeping its argument contract (`--only <part>`) and its one-line-per-failure output. Both parts read only the four sample report folders (`town-en`, `town-de`, `nonprofit-en`, `nonprofit-de`) of the directory argument. For print, use Chromium's `page.pdf` with A4 format, write the PDFs and `pdftoppm` previews at 50 dpi to `.shots/report-redesign/out/`, read text with `pdftotext -layout`, split pages on form feeds, and read the expected texts from the DOM of the same report (section titles, the first `li[data-evidence]` label inside a Ready card, the first `tr[data-product]` header cell, the appendix part headings), never from literals in the script. Check the page size with `pdfinfo`.

    Regenerate both site demo reports as in Task 1.
  </action>
  <verify>
    <automated>uv run pytest -q && uv run ruff check . && uv run ruff format --check . && d="$(mktemp -d)" && for s in town nonprofit; do for l in en de; do uv run fazit demo --lang "$l" --sample "$s" --out "$d/$s-$l" > "$d/$s-$l.log" && test -f "$(tail -n 1 "$d/$s-$l.log")" || exit 1; done; done && node .shots/report-redesign/check.mjs "$d" && uv run python site/check_site.py</automated>
    <human-check>At the end of the redesign, open the PDF previews in `.shots/report-redesign/out/`: page one holds only header and summary, card heads are not split, table headers repeat, and amounts and borders stay legible with backgrounds off.</human-check>
  </verify>
  <acceptance_criteria>
    - `uv run pytest -q` exits 0 and `uv run python site/check_site.py` prints "No errors."
    - `node .shots/report-redesign/check.mjs <dir>` (parts `filters`, `layout`, `print`) exits 0 for the four reports
    - `uv run pytest tests/test_locales.py -q` exits 0 after the key clean-up
    - `grep -c "table:not(.cost-table)" src/fazit/templates/report.html.j2` [HEAD=at least 1 after RR-03, EXPECT==0]
    - `grep -c "break-before: page" src/fazit/templates/report.html.j2` is at least 1, and the selectors carrying it name exactly `path`, `costs` and `appendix`
    - The SUMMARY lists every deleted CSS rule and locale key, and the page count of header and summary per report and language
    - Follows DESIGN.md (every page works at 360 px without sideways scrolling; lean; nothing moves under reduced motion)
  </acceptance_criteria>
  <done>The report prints with header and summary as page one and the working sections after it, complete whatever the screen state; at 360 px the council's facts come first without sideways scrolling; no unused CSS or strings remain; a browser check proves both.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| report file → reader's browser and printer | Opened offline and printed by people who did not build it |
| printed PDF → filed record | A council may file the printout as the record of the assessment |

## STRIDE Threat Register

Security level: ASVS 1. Blocking threshold: high.

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-RR-09 | Repudiation | open points: grouping drops a gap, an unknown finding or a skipped collector, so missing evidence looks complete | high | mitigate | Task 1 tests that every gap of every area, every unknown finding, every skipped collector and every Unknown area appears, and that no key repeats, over both samples, both languages and the all-Unknown fixture |
| T-RR-13 | Tampering | "What to do next" reads as a proposed resolution or effort estimate | medium | mitigate | Steps come only from rule `next_step` sentences and reason fixes owned by RR-01; no new copy; no stock steps, timeline or proposed decision (Task 1 tests); RR-01's ban-list test covers the locales |
| T-RR-10 | Tampering | navigation: a link to an external target or a broken fragment | medium | mitigate | Every `href` starts with `#` and resolves exactly once (Task 2 test); the existing resource test and `check_site.py` reference checks still run |
| T-RR-11 | Repudiation | print drops closed evidence or reflects a screen filter | medium | mitigate | `::details-content` opens every disclosure in print; filters are screen-only; the `print` check compares PDF text with and without a filter and looks for Ready evidence, licences and every appendix part (Task 3) |
| T-RR-12 | Tampering | new icon files differ from the shared, licensed set | low | mitigate | Byte-identical copies checked with `cmp` and a test; RR-05 adds a test that every packaged icon matches the site's |
| T-RR-SC | Tampering | package installs | high | mitigate | Nothing is installed |
</threat_model>

<verification>
Before declaring the plan complete:
- [ ] `uv run ruff check .` and `uv run ruff format --check .` exit 0
- [ ] `uv run pytest -q` exits 0
- [ ] `uv run fazit demo --lang de` and `uv run fazit demo --lang en`, each into a fresh temporary directory, exit 0 and the printed path exists
- [ ] `uv run python site/check_site.py` prints "No errors."
- [ ] `node .shots/report-redesign/check.mjs <dir>` exits 0
- [ ] The CSP meta line is unchanged; `src/fazit/status.py` and `src/fazit/costs.py` are unchanged by this plan
</verification>

<success_criteria>
- "What to do next" meets UI-SPEC 4.1 and criterion 22, built only from findings, with every open point once
- Every section is on the site's components, with navigation in section order, and every hook survives
- Coverage uses `circle` for `in_suite` in the report and on the website; no status symbol is reused
- Print and phone meet UI-SPEC section 7, proved in a browser and on real PDFs
- No unused CSS or locale key remains
</success_criteria>

<output>
Create `.planning/report-redesign/RR-04-SUMMARY.md` when done. Record: the final markup of the bar, one step row, one open-point row and one replacements row from the English town report; the open-point rows of that report (key, items, areas); every edited existing assertion with its UI-SPEC section 9 item; every deleted CSS rule and locale key; the owner role of each open-point row; the result of each `layout` and `print` check per report, width and scheme, and the page count of header and summary; helpers found moved; a native-review table of every German string this plan added or changed (expected: none; any key added because RR-01 lacked it is a draft); the test count and runtime of `uv run pytest -q`.
</output>

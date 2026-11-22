---
phase: report-redesign
plan: 03
type: execute
wave: 5
depends_on: ["RR-01", "RR-06", "RR-07", "RR-02"]
files_modified:
  - src/fazit/report.py
  - src/fazit/i18n.py
  - src/fazit/templates/report.html.j2
  - tests/report_expectations.py
  - tests/helpers.py
  - tests/fixtures/all_unknown_scan.json
  - tests/test_report.py
  - tests/test_rules.py
  - tests/test_costs.py
  - site/demo/en/index.html
  - site/demo/de/index.html
autonomous: true
requirements: [REPT-02, REPT-04, REPT-05, COST-03, OUTP-03]

estimate:
  tokens: 230000
  raw_tokens: 230000
  tasks: 3
  confidence: medium

must_haves:
  truths:
    - "The report has ten sections in the order header, summary, path, readiness, costs, moves, attention, found, appendix, footer (UI-SPEC 1)"
    - "The summary shows, in order: one `dl.status-summary` introduced by \"Of {n} areas:\" (n from the catalogue's assessed areas), one row per status in display order with symbol, name, count and definition, zero counts kept; what blocks this move (at most 3 rows; \"Confirmed blockers: {shown} of {total}\" only when rows are cut off; \"All blockers\" only when total is at least 1; otherwise the no-blocker sentence with its caveat); what is still unknown (at most 4 deduplicated rows, \"All open points\" and the missing-input link); the scope statement from RR-07 when present; three cost tiles; the Stay assumption and break-even lines (UI-SPEC 1.2, revision 4.1)"
    - "The summary holds no readiness bar, `data-segment`, percentage or other part-of-whole picture, and counts appear only in the status list (UI-SPEC 1.2 item 1, 11 criteria 2 and 3)"
    - "Three tiles, Stay, Partial move, Full move, show the five-year total in whole currency units with its origin; a move tile's main line gives the absolute difference in whole units with less, more, the same or less than one cent; an unknown total shows the Unknown label, the known blocks and the missing-input count; a known move total with Stay unknown shows \"Comparison unknown\" (UI-SPEC 1.2 item 5, 11 criterion 10)"
    - "Break-even: one line per move scenario whose comparison is known, giving the yearly target operations cost at which that scenario's five-year total equals staying and the entered value, both in whole units, computed exactly from the unchanged cost model; `costs.break_even_none` when even zero operations leaves the move dearer; absent when the comparison or the operations input is unknown. Town full move: EUR 39,130 a year, entered EUR 12,000 (UI-SPEC 3.3, 11 criterion 11)"
    - "The cost chart draws only rows with a known total, on one scale built from known totals; a row with an unknown block shows only the dashed Unknown marker, \"Total unknown\", the known blocks and every unknown block named; it is absent when the cost inputs are absent or entirely null (UI-SPEC 3.1)"
    - "The cost section reads: intro line, profile note, chart, Stay assumption and break-even lines, results table, rounding note, VAT note, missing inputs under `id=\"costs-missing\"` with the fix, cost inputs disclosure; `data-block` appears exactly four times (UI-SPEC 3, 9)"
    - "A test fixture with every area Unknown exists for summary tests and RR-05's page-one check"
    - "No score, percentage, verdict, proposed resolution or recommendation appears; a difference is less or more, never a saving"
  artifacts:
    - path: "src/fazit/templates/report.html.j2"
      provides: "Summary section, cost tiles, Stay assumption and break-even lines, cost chart, reordered costs section"
      contains: "data-section=\"summary\""
    - path: "src/fazit/report.py"
      provides: "Summary rows, comparison per move scenario, break-even helper, chart rows on one scale"
      contains: "break_even"
    - path: "tests/report_expectations.py"
      provides: "Ten-section SECTION_ORDER with path third"
      contains: "\"summary\""
    - path: "tests/fixtures/all_unknown_scan.json"
      provides: "A scan with no findings, no licences and every collector skipped"
      contains: "\"findings\": []"
  key_links:
    - from: "src/fazit/report.py"
      to: "src/fazit/templates/report.html.j2"
      via: "one comparison helper and one break-even helper feed both the summary tiles and the cost section"
      pattern: "data-break-even"
    - from: "src/fazit/templates/report.html.j2"
      to: "tests/test_costs.py"
      via: "chart values carry data-chart-value and must equal the table subtotals"
      pattern: "data-chart-value"
---

# Plan RR-03: summary, cost tiles, break-even and cost chart

## Goal

The report puts the findings first and says, with facts and open questions only, what a move would take, what stops it, what is still open and what it costs; it draws the costs and looks like the website, without changing what is measured, provided or unknown (`.planning/report-redesign/UI-SPEC.md`, revision 4.1, section 0). It never proposes what the council should decide.

<objective>
Add the summary that is page one's body, put the sections in their new order with `path` third, and present the costs: three totals as tiles in the summary, the Stay assumption and a break-even line, and a chart on one scale in the cost section.

Purpose: UI-SPEC sections 1, 1.2 and 3 (revision 4.1). A council member reading page one sees what each status means and how many areas have it, what blocks this move, what is still open, what the target covers, and the three totals, with every unknown still visible as unknown.
Output: report context, template and CSS for the summary and the cost section; one whole-unit option on the money formatter; the all-Unknown fixture; permitted test edit 1; new item 11 tests; regenerated site demo reports.

This is plan 5 of 7 in the run order RR-01, RR-06, RR-07, RR-02, RR-03, RR-04, RR-05. It relies on, and does not implement: RR-01's copy (every key of UI-SPEC 8 revision 4.1, including `summary.define.*`, `summary.scope_*`, `costs.total_label`, `costs.stay_basis`, `costs.comparison_unknown`, `costs.stay_assumption`, `costs.break_even`, `costs.break_even_none`, `costs.vat_note`, `costs.profile_note` and the productivity-loss labels) and its `assessed` catalogue flag; RR-07's `scope_statement` context value; RR-02's cards, group headings `h3#status-{status}`, `status_counts` in display order, `area_count` (assessed areas from the catalogue), and the readiness bar with its `data-segment` hooks in `readiness` (permitted edit 4); RR-02 removes `ul.status-legend` from `readiness`. RR-03 does not move the readiness bar. Its only change inside `readiness` is adding `id="not-examined"` to today's `div[data-subsection="not-examined"]`, which RR-02 leaves without an id, so the summary's "All open points" link resolves; RR-04 then moves that block to `path`. RR-04 (what to do next, navigation, appendix, print, phone) and RR-05 (design checks, PDF page-one check, decisions) follow. The decision-window tiles of UI-SPEC 1.2 item 6 ship with Phase 1.1 and are not built here.
</objective>

<execution_context>
Read these two files before starting. They are plain paths, not includes.
- $HOME/.claude/gsd-core/workflows/execute-plan.md
- $HOME/.claude/gsd-core/templates/summary.md
</execution_context>

<context>
Read these files first. They are plain paths from the repository root.
- AGENTS.md
- DESIGN.md (binding: hierarchy, tiles with one anchor, tokens only, copy, standalone links end in a chevron, never reuse a status symbol)
- DECISIONS.md (Principles; the "M0 complete" cost formulas)
- .planning/report-redesign/UI-SPEC.md (revision 4.1; sections 0, 1, 1.2, 3, 3.1, 3.2, 3.3, 6, 8, 9, 10 and 11 criteria 2, 3, 10, 11, 13, 16)
- .planning/report-redesign/REV4-CHANGE-MAP.md (rules for every plan; who owns what; interfaces "Scope statement" and "Break-even"; the revision 4.1 table)
- .planning/research/report-usefulness/SYNTHESIS.md (sections A and C)
- The SUMMARY files of RR-01, RR-06, RR-07 and RR-02 in `.planning/report-redesign/` (key names, the `scope_statement` shape, the display-order helper, the group heading ids)

Precondition: RR-01, RR-06, RR-07 and RR-02 are complete on the working branch. Check before starting: `grep -n "define\|scope_\|break_even\|stay_basis\|comparison_unknown\|vat_note\|profile_note" src/fazit/locales/en.yaml` finds RR-01's keys; `grep -n "scope_statement" src/fazit/report.py` finds RR-07's value; `grep -n "status-group\|status-{{" src/fazit/templates/report.html.j2` finds RR-02's groups; `grep -n "area_count" src/fazit/report.py` finds RR-02's count. If any is missing, stop and report; do not build it here.

Facts checked on `main` at 784e33b (2026-11-22), after 0ae2be2, 6e36d71 and acf9be9. Re-check each with grep; the earlier plans change some of them.
- `src/fazit/costs.py` computes with `Fraction`: `compute_scenarios(inputs) -> tuple[ScenarioResult, ...]`, `ScenarioResult(id, running, blocks, total, missing_inputs, difference_to_stay)`, `CostGroup(id, lines, total, missing)`, `YEARS = 5`, `SCENARIOS`, `BLOCKS`. The operations input is `ScenarioInputs.operations_per_year` (`src/fazit/inputs.py`); the spec's `annual_operations` means this field. Its cost line is `operations_per_year × YEARS` with no other factor, so a scenario's total is linear in it. Stay's three change blocks are `CostGroup`s with no lines and total 0.
- `src/fazit/i18n.py`: `_money_parts` rounds half away from zero to cents; `plain_amount`; `Formatter.money(amount, currency)` always prints two decimals; `reason_text(strings, code)` returns label and fix. `report.py` imports `plain_amount` from `i18n` (there is no `_plain_amount`).
- `src/fazit/report.py`: `_prepare_report`, `_evidence_context` (builds `statuses`, `status_counts` — in `STATUSES` order today, in display order after RR-02 — and `status_by_workload`; RR-02 adds `area_count`), `_cost_context(inputs)` (no formatter; returns `scenarios`, `cost_blocks`, `current_costs`, `target_costs`, `cost_currency`, `plain_amount`), `_cost_table_blocks`, `_formatting_context` (exposes `format`, `strings`, `reason_text`, `workload_labels`).
- `src/fazit/status.py`: `WorkloadStatus(workload, status, reason_code, missing, deciding, notes, evidence)` with property `incomplete`; `MissingEvidence(finding_id, reason_code, collector)`.
- Template macros: `status_label`, `workload_status`, `status_reason`, `cost_heading` (origin `calculated_with_examples` when `prices_invented`, else `calculated`), `cost_amount`, `cost_caption`, `cost_input_row`. Today the cost section reads: `h2`, `costs.provide_inputs` when `inputs is none`, the cost inputs disclosure, the results table, `costs.rounding`, then one `h3` and `ul > li[data-missing-cost]` per scenario with missing inputs.
- Tests: `SECTION_ORDER` lives in `tests/report_expectations.py` and is used by `tests/test_cli.py`, `tests/test_report.py`, `tests/test_rules.py` and `tests/test_installed_package.py`; no test lists the sections by hand. `tests/helpers.py` has `ROOT`, `PLANTED_SCAN`, `report_section`, `rebuild_report`, `sample_scan_path`, `sample_inputs_path`. `tests/test_costs.py` has `worked_example` (the town amounts), `test_zero_overlap_without_current_licence_cost` (partial total 507,800), `test_demo_cost_comparison`, `test_empty_inputs_render_unknown_costs`, `test_sample_measurements_do_not_label_real_prices_invented`, `test_money_format`, `_cost_section`, `_rendered_totals`. `tests/test_rules.py` has the `complete_evidence` fixture and `test_suggested_path_explains_empty_lists`. `tests/test_report.py::test_checksums_use_the_five_rule_reads` shows how to run on a copied rules directory (`copytree` of `rules.rules_dir()` and `monkeypatch.setattr(rules, "rules_dir", ...)`).
- Cost figures (exact, from `compute_scenarios` on the sample inputs): town Stay 600,000, Partial 527,800 (difference -72,200), Full 464,350 (difference -135,650); non-profit Stay 22,000, Partial 29,870 (difference +7,870), Full unknown (missing `target_costs.full_exit.productivity_loss`; known blocks 28,300 + 10,700 + 1,600 = 40,600).
- Break-even (operations per year at which the move costs the same as staying = entered − difference ÷ `YEARS`): town Full 39,130 (entered 12,000), town Partial 20,440 (entered 6,000), non-profit Partial 26 (entered 1,600), non-profit Full absent. Verified: setting the town full move's `operations_per_year` to 39130 gives `difference_to_stay == 0`.
- Chart shares (row total ÷ largest known total, four decimals): town 1.0000, 0.8797, 0.7739; non-profit Stay 0.7365, Partial 1.0000, Full no bar.
- A scan with `"findings": []`, `"licences": null`, `"source_kind": "import"` and every collector `"status": "skipped", "reason": "source_not_supplied"` passes today's load-time checks and `fazit report` renders every area Unknown.

Environment:
- The executor cannot commit. Leave every change in the working tree; the orchestrator reviews and commits.
- Run every command from the repository root through `uv`; if the shell does not find it, run `export PATH="$HOME/.local/bin:$PATH"` first. Install nothing; add no dependency and no module.
- Locate every Python symbol with grep at execution time, never by line number. Re-read every file before editing; never revert changes you did not make. Do not change the cost model: `git diff -- src/fazit/costs.py src/fazit/status.py` stays empty.
- Copy belongs to RR-01. Use its keys and read their placeholders from the locale files. Add no copy, with one exception: if a singular form RR-03 needs (`summary.caveat_one`, `costs.inputs_missing_one`) is missing, add it in both locales following the `units`/`unit_one` precedent, and list every such string in the SUMMARY's native-review table with the German marked as a draft (formal "Sie", no abbreviations such as "z. B.", status names exactly Bereit, Handlungsbedarf, Hindernis, Unbekannt).
- Never weaken a test or a principle. Existing tests change only as UI-SPEC section 9 permits; this plan uses item 1 and adds item 11 tests. Any other failing test means the template or code is wrong; if the spec makes it impossible, stop and report.
- Hooks: every existing `data-*` attribute keeps its name, values, order and host. New hooks only: `data-summary`, `data-cost-tile`, `data-comparison`, `data-break-even`, `data-chart-scenario`, `data-chart-block`, `data-chart-value`. Never reuse `data-subsection` (a test pins its order), `data-segment`, `data-scenario` with `data-total`, `data-block`, `data-amount` or `data-missing-cost` outside their current places (tests count them). The summary adds no `data-workload`, `data-status`, `data-reason`, `data-evidence`, `data-missing` or `data-input-role` hook.
- CSS follows DESIGN.md and UI-SPEC 6: tokens only, seven type sizes, the spacing scale; copy site rules declaration for declaration apart from the six exceptions in UI-SPEC 6.2.
- Every report command builds into a fresh temporary output directory and checks exit code, file existence and content separately (D-56). No network. Do not publish the site from this plan.
</context>

<tasks>

<task type="tracer">
  <name>Task 1: Section order and the summary's findings: status list, blockers, unknowns, scope statement; the all-Unknown fixture (size: large)</name>
  <files>src/fazit/report.py, src/fazit/templates/report.html.j2, tests/report_expectations.py, tests/helpers.py, tests/fixtures/all_unknown_scan.json, tests/test_report.py, tests/test_rules.py, site/demo/en/index.html, site/demo/de/index.html</files>
  <read_first>DESIGN.md, .planning/report-redesign/UI-SPEC.md (sections 1, 1.2 items 1 to 4, 8 rows `summary.*` and `path.empty.*`, 9 item 1, 10, 11 criteria 2, 3 and 16), .planning/report-redesign/REV4-CHANGE-MAP.md ("Scope statement" interface; revision 4.1 table), site/style.css (`.rows`, `.rows > div`, `.rows dt`, `.rows dd`, `.subsection`, `.sec-label`, `.sec-body`, `.note-text`), src/fazit/report.py (grep `def _evidence_context`, `status_counts`, `area_count`, `scope_statement`), src/fazit/i18n.py (grep `def reason_text`), src/fazit/templates/report.html.j2 (the `status_label`, `status_reason` macros; RR-02's readiness section frame and `h3#status-` headings; `data-subsection="not-examined"`; the order of the `section` elements; the missing-inputs block of the costs section), tests/report_expectations.py, tests/helpers.py (grep `PLANTED_SCAN`, `def report_section`), tests/test_report.py (grep `def test_checksums_use_the_five_rule_reads`, `SECTION_ORDER`), tests/test_rules.py (grep `def test_suggested_path_explains_empty_lists`, `def complete_evidence`), src/fazit/demo/town/scan.json (top-level keys and collectors)</read_first>
  <behavior>
    - `SECTION_ORDER` in `tests/report_expectations.py` is header, summary, path, readiness, costs, moves, attention, found, appendix, footer, and every report renders its sections in that order; `path` keeps today's content (RR-04 rewrites it)
    - `section[data-section="summary"]` uses the same site frame as RR-02's readiness section, with `h2.sec-label#summary-title` ("Where the organisation stands") and, in order: the status list; the blockers part; the unknowns part; the scope statement when present; then (Task 2) the tiles
    - `div[data-subsection="not-examined"]` in `readiness` gains `id="not-examined"` after its `data-subsection` attribute; nothing else in `readiness` changes
    - Status list: `p` "Of {n} areas:" in `--fg-2` (n = RR-02's `area_count`, never a literal), then `dl.status-summary` with four `div` rows in display order (blocker, needs_work, unknown, ready), zero counts kept; each `dt` holds `status_label(status)` and the count at `--fs-lead`, each `dd` the definition `summary.define.{status}` at `--fs-footnote` in `--fg-2`; `dt` and `dd` share a row from 640 px and the `dd` wraps under the `dt` below 640 px; the four counts sum to n. No other count, no bar, no `data-segment`, no `%` in the summary
    - Blockers part (`div.subsection[data-summary="blockers"]`, `h3` `summary.blockers`, then `dl.rows`): at most 3 rows, catalogue order, each `dt` the area name linking to `#readiness-{workload}` with the "Evidence incomplete" marker when incomplete, each `dd` the deciding reason in full (`status_reason`); `summary.confirmed` ("Confirmed blockers: {shown} of {total}") only when total is greater than shown; a standalone link `summary.all_blockers` to `#status-blocker` only when total is at least 1; with no blocker, `path.empty.blocker` and, when any area is Unknown or incomplete, `summary.caveat` with that number (the singular key for 1)
    - Unknowns part (`div.subsection[data-summary="unknown"]`, `h3` `summary.unknown`): at most 4 rows, the areas that are Unknown or incomplete, each once, in catalogue order, each `dd` the fix of `row.reason_code` for an Unknown area or of the first missing item for an incomplete decided area; then the standalone link `summary.not_examined` ("All open points") to `#not-examined` and, when any scenario misses inputs, `costs.inputs_missing` with the number of distinct missing input paths across all scenarios (singular key for 1) linking to `#costs-missing`, followed by `costs.missing_fix`; with no such area, `path.empty.unknown` and the links. Never omitted
    - Scope statement (`div.subsection[data-summary="scope"]`), only when `scope_statement` is not `None`: `h3` `summary.scope_title` with the profile; one line `summary.scope_of` with n and the profile, then each coverage id of `by_coverage` as its `mapping_coverage` label and count, as text in `--fg`; then, when `needed` is not empty, `dl.rows` with one row whose `dt` is `summary.scope_needed` and whose `dd` lists each needed function as a link to `#{its gap element id}`; then, when `unknown_need` is at least 1, `summary.scope_unknown` with that number. No fraction, percentage or bar
    - When `scope_statement.reviewed_on` is `None`, the scope statement ends with RR-07's mapping-review sentence for an unreviewed mapping (the same locale key RR-07 uses in the replacements section), so page one never presents unreviewed coverage counts without saying so; with a date, no sentence
    - The costs section has `div#costs-missing` around today's missing-input headings and lists, with `p` `costs.missing_fix`, whenever any scenario misses inputs; `li[data-missing-cost]` markup is unchanged
    - `tests/fixtures/all_unknown_scan.json` renders a report in which every card is Unknown; `tests/helpers.py` exposes it as `ALL_UNKNOWN_SCAN`
  </behavior>
  <action>
    Order (UI-SPEC 1, permitted edit 1). Set `SECTION_ORDER` in `tests/report_expectations.py` to the ten sections with `path` third. In the template, add the summary section after the header, move `path` directly after it, and move `found` after `attention`; keep every section's content. Readiness stays where RR-02 left it, with its bar; do not move the bar. Add `id="not-examined"` to today's not-examined block (after `data-subsection`) and change nothing else there; RR-04 moves it.

    Fixture. Write `tests/fixtures/all_unknown_scan.json` from the keys of `src/fazit/demo/town/scan.json`: same `schema_version`, `tool` and `generated_at`, `source_kind` "import", `findings` empty, `licences` null, every collector of the town scan with status "skipped", reason "source_not_supplied" and empty `permissions_used`. Add `ALL_UNKNOWN_SCAN` next to `PLANTED_SCAN` in `tests/helpers.py`. RR-05 uses it for the PDF page-one check; keep the name.

    Context (UI-SPEC 1.2). In `report.py`, add small functions that return lists and counts (the template applies the caps of 3 and 4, so a test sees both cap and total): the status rows from RR-02's `status_counts` (display order) with `area_count` as n (`STATUSES` untouched; if `status_counts` is not in display order or `area_count` is missing, stop and report: RR-02 owns both); the blocker rows in catalogue order with their total; the open rows (Unknown or incomplete, each area once, catalogue order) with the fix text chosen as the behaviour says, through the existing `reason_text`; the number of open areas for the caveat; the distinct missing input paths across all scenarios.

    Template and CSS. Build the status list as the behaviour says; `.status-summary` rows are a two-column grid from 640 px (`dt` content width, `dd` the rest, 4 px row gap and the scale's column gap) and one column below; copy the site's `.rows` rules for `dl.rows` (`h3 + .rows { margin-top: 12px }`), each row a `div` holding `dt` and `dd`. Standalone links end in an inline chevron symbol in the link colour (DESIGN.md "Links"). Choose the singular keys when the number is 1. Render the scope statement from `scope_statement` exactly as RR-07 shaped it (read RR-07's SUMMARY; field names per the map: `profile`, `total`, `by_coverage`, `needed`, `unknown_need`, plus RR-07's `reviewed_on`, which UI-SPEC 1.2 item 4 does not show, so this plan does not render it). Wrap the cost section's missing-input headings and lists in `div` with `id="costs-missing"` and add `p` with `costs.missing_fix`, only when a scenario misses inputs, so every link to it resolves.

    Tests (item 11) in `tests/test_report.py`: (a) summary caps and deduplication on a copied rules directory in which every `needs_work` rule becomes `blocker` (patch it as `test_checksums_use_the_five_rule_reads` does), so the town report has more than three blockers: the summary shows the first three in catalogue order, "Confirmed blockers: 3 of N" with N the number of blocker cards, and "All blockers" to `#status-blocker`; (b) on the town and non-profit demos, both languages: no `summary.confirmed` text when total is at most 3, "All blockers" present exactly when a card is a blocker, the status list has four rows in display order whose counts equal the number of cards per status and sum to the "Of {n}" number, which equals the number of cards; the summary has no `data-segment`, `readiness-bar` or `%`; every `href="#…"` in the summary resolves to an id in the same report (`#not-examined`, `#status-blocker` when present, `#costs-missing` when present, each card and gap link); (c) on `ALL_UNKNOWN_SCAN` without inputs, both languages: every card Unknown, the status list reads n Unknown and 0 for the others, the caveat with n, exactly four unknown rows matching the first four cards, "All open points" and the missing-input link present, no "All blockers"; (d) scope statement: for the town with `opendesk` the summary's scope counts and names equal `scope_statement` and the replacements table's coverage counts; with `generic` there is no `data-summary="scope"`. In `tests/test_rules.py`, next to `test_suggested_path_explains_empty_lists`: render the `complete_evidence` scan and assert the no-blocker sentence without the caveat and `path.empty.unknown` in the unknowns part.

    Regenerate both site demo reports from `uv run fazit demo --lang <lang> --sample town --profile opendesk --out <fresh temporary directory>`.
  </action>
  <verify>
    <automated>uv run pytest -q && uv run ruff check . && uv run ruff format --check . && out="$(mktemp -d)" && log="$(mktemp)" && uv run fazit demo --lang en --out "$out" > "$log" && report="$(tail -n 1 "$log")" && test -f "$report" && uv run python -c 'import re, sys; html = open(sys.argv[1], encoding="utf-8").read(); sections = re.findall(r"data-section=\"([a-z]+)\"", html); assert sections == ["header", "summary", "path", "readiness", "costs", "moves", "attention", "found", "appendix", "footer"], sections; summary = html.split("data-section=\"summary\"", 1)[1].split("</section>", 1)[0]; assert "data-segment" not in summary and "readiness-bar" not in summary and "%" not in summary; assert summary.count("<dt") >= 4 and "status-summary" in summary' "$report" && grep -q "Where the organisation stands" "$report" && out2="$(mktemp -d)" && uv run fazit report tests/fixtures/all_unknown_scan.json --lang de --out "$out2" > "$log" && test -f "$(tail -n 1 "$log")" && uv run python site/check_site.py</automated>
  </verify>
  <acceptance_criteria>
    - `uv run pytest -q` exits 0 and `uv run python site/check_site.py` prints "No errors."
    - `grep -c '"summary"' tests/report_expectations.py` [HEAD=0 at 784e33b, EXPECT==1]
    - `grep -c 'data-section="summary"' src/fazit/templates/report.html.j2` [HEAD=0, EXPECT==1]
    - `grep -c 'status-summary' src/fazit/templates/report.html.j2` [HEAD=0, EXPECT>=1]
    - `grep -c 'id="costs-missing"' src/fazit/templates/report.html.j2` [HEAD=0, EXPECT==1]
    - `grep -c 'id="not-examined"' src/fazit/templates/report.html.j2` [HEAD=0 at 784e33b, EXPECT==1]
    - `test -f tests/fixtures/all_unknown_scan.json` and `grep -c "ALL_UNKNOWN_SCAN" tests/helpers.py` [HEAD=0, EXPECT==1]
    - The SUMMARY lists every edited existing assertion with its UI-SPEC section 9 item
    - Follows DESIGN.md (findings first; facts as rows; standalone links end in a chevron; tokens only; status always symbol and word)
  </acceptance_criteria>
  <done>The report opens with a summary in the new section order: each status once with its count and meaning, scoped blockers and open questions capped and honestly qualified, and the scope statement when RR-07 supplies it; an all-Unknown fixture exists.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: Three cost tiles, the comparison, the break-even helper and the Stay assumption in the summary (size: medium)</name>
  <files>src/fazit/report.py, src/fazit/i18n.py, src/fazit/templates/report.html.j2, tests/test_costs.py, site/demo/en/index.html, site/demo/de/index.html</files>
  <read_first>DESIGN.md ("Lists of facts are tiles"), .planning/report-redesign/UI-SPEC.md (section 1.2 item 5, 3.3, section 8 rows `costs.*`, section 11 criteria 10, 11 and 13), .planning/report-redesign/REV4-CHANGE-MAP.md ("Break-even" interface), DECISIONS.md ("M0 complete" cost formulas), site/style.css (`.tiles`, `.tiles-3`, `.tiles li`, `.tiles p`, `.tiles .tile-label`, `.tiles .tile-title`, `.figure-num`, `.note-text`), src/fazit/costs.py (grep `class ScenarioResult`, `class CostGroup`, `YEARS`, `operations_per_year`), src/fazit/inputs.py (grep `operations_per_year`), src/fazit/i18n.py (grep `def _money_parts`, `def money`), src/fazit/report.py (grep `def _cost_context`, `plain_amount`), src/fazit/templates/report.html.j2 (the `cost_heading` macro and its origin logic, the summary from Task 1), tests/test_costs.py (grep `def test_money_format`, `def test_zero_overlap_without_current_licence_cost`, `def test_demo_cost_comparison`, `worked_example`)</read_first>
  <behavior>
    - `Formatter.money(amount, currency, *, whole=False)`: with `whole=True` it rounds half away from zero to whole units, as `_money_parts` does for cents, and prints no decimal separator; existing calls are unchanged
    - A pure comparison function takes a move scenario's difference from staying and returns its absolute amount and one of `less`, `more`, `same`, `sub_cent` or `unknown`: negative is less, positive is more, exactly zero is same, non-zero but formatted with cents like zero is sub_cent. The amount is shown in whole units; when it is non-zero but rounds to zero whole units it is shown with cents, so the number and the words never contradict each other; sub_cent and same show no amount
    - One break-even helper per move scenario (UI-SPEC 3.3) returns `None` (absent) when the scenario's or Stay's total is unknown or its `operations_per_year` is `None`; otherwise the exact amount `operations_per_year − difference_to_stay ÷ YEARS` as a `Fraction`, with the entered value, and a flag `none` when that amount is below zero. No float, no change to `costs.py`
    - The summary holds, after the scope statement (or the unknowns part), `ul.tiles.tiles-3` with one `li[data-cost-tile]` per scenario in the order stay, partial_exit, full_exit: `p.tile-label` `costs.total_label` with the scenario name; the anchor `.figure-num` at `--fs-headline` with `white-space: nowrap`, the total in whole units in the input currency; the main line `p.tile-title` (Stay: `costs.stay_basis`; a move: the difference and `costs.less`/`more`/`same`/`sub_cent`, with `data-comparison` set to the comparison value); the detail `p[data-cost-origin]` with the origin word from the cost headings' logic
    - Unknown total: the anchor is `status_label('unknown')`, never a number or dash; the main line is `costs.known_blocks` with the sum of the blocks that have a known total and at least one cost line, when any; otherwise `costs.stay_basis` for Stay and `costs.comparison_unknown` for a move; the detail is `costs.inputs_missing` (singular for 1) with the distinct missing input paths of that scenario, linking to `#costs-missing`. Unknown comparison (move total known, Stay unknown): the move tile shows its total and the main line `costs.comparison_unknown` followed by the missing-input count of Stay linking to `#costs-missing`; `data-comparison="unknown"`
    - Under the tiles, `div` of `p.note-text`: `costs.stay_assumption`, then per move scenario with a break-even result one `p.note-text[data-break-even="{scenario}"]`: `costs.break_even` with the scenario name, the amount and the entered value, both in whole units, or `costs.break_even_none` with the scenario name. Built by one macro that Task 3 reuses
    - Town, English: tiles "EUR 600,000", "EUR 527,800", "EUR 464,350"; main lines "EUR 72,200" with "less than staying" and "EUR 135,650" with "less than staying"; break-even lines with "EUR 20,440" (entered "EUR 6,000") and "EUR 39,130" (entered "EUR 12,000")
  </behavior>
  <action>
    Formatter (whole units). Add the keyword to `Formatter.money` in `i18n.py` and a whole-unit case to `test_money_format` in both languages (for example 1234.50 → "EUR 1,235" and "1.235 EUR", -0.50 → "-EUR 1"/"-1 EUR" only if that is what half away from zero and the existing sign rule give; derive expectations from the rule, not by guessing).

    Comparison and break-even (UI-SPEC 1.2 item 5, 3.3). In `report.py`, next to `_cost_context`, add the comparison function, the break-even helper and a function that returns, per scenario, the tile data: total, comparison, known-block sum (blocks with a known total and at least one line, so Stay's line-less change blocks never make a "known" sum), distinct missing paths, break-even. Read `operations_per_year` from the inputs; with no inputs every result is unknown and there is no break-even. Compute with the cost model's own `Fraction` and `YEARS`; the spec's "exact Decimal" means exact arithmetic, never float. The map calls this "one helper in the cost code"; it lives in the report's cost context so `src/fazit/costs.py` stays byte-identical. The costs section in Task 3 uses the same helper.

    Tiles. Render the tiles as the behaviour says, after the scope statement and before where the decision window will go. Copy the site's `.tiles` and `.tiles-3` rules; the money anchor uses `--fs-headline` and `white-space: nowrap` (UI-SPEC 6.1). One anchor per tile, then the main line, then one line of detail (DESIGN.md); no symbol on the money tiles except the Unknown status label, which is the anchor itself. Use the existing origin logic of `cost_heading` for `data-cost-origin`. Write the Stay assumption and break-even macro.

    Tests in `tests/test_costs.py` (item 11): the comparison function on less, more, same, sub-cent and unknown, with exact `Fraction` amounts; the break-even helper on the worked example (full 39130, partial 20440; and replacing the full move's `operations_per_year` with `Decimal("39130")` in `compute_scenarios` gives `difference_to_stay == 0`), the none case (worked example's partial move with `one_time_migration` raised until `difference_to_stay ÷ 5` exceeds `operations_per_year`), and the absent cases (operations `None`; Stay unknown); the town tiles in both languages, with expected text built through the formatter rather than literal German formats; the three tiles in whole units (no decimal separator in any `.figure-num` of the summary); the non-profit: Partial break-even "EUR 26" with entered "EUR 1,600", no break-even line for the full move, the full tile shows Unknown, "Total of known blocks" with 40,600 in whole units and the singular missing-input text linking to `#costs-missing`; the unknown comparison with a known total, built from a copy of the town inputs with `microsoft_licences_per_year: null` and the partial move's `parallel_running_months: 0` (the 507,800 case): the Stay tile shows Unknown and `costs.stay_basis`, the partial tile shows 507,800 in whole units and `costs.comparison_unknown` with the singular missing-input count, the full tile shows Unknown with its known blocks, no break-even line, and the costs section has `id="costs-missing"`; a seven-digit amount (raise the partial move's `one_time_migration` in a copied inputs file by 1,100,000) appears as one text in one `.figure-num`, and the stylesheet gives that element `white-space: nowrap`. RR-04's browser check proves the one line at 360 px.

    Regenerate both site demo reports as in Task 1.
  </action>
  <verify>
    <automated>uv run pytest tests/test_costs.py -q && uv run pytest -q && uv run ruff check . && uv run ruff format --check . && out="$(mktemp -d)" && log="$(mktemp)" && uv run fazit demo --lang en --out "$out" > "$log" && report="$(tail -n 1 "$log")" && test -f "$report" && uv run python -c 'import sys; html = open(sys.argv[1], encoding="utf-8").read(); summary = html.split("data-section=\"summary\"", 1)[1].split("</section>", 1)[0]; assert summary.count("data-cost-tile=") == 3, summary.count("data-cost-tile="); assert "EUR 600,000" in summary and "EUR 527,800" in summary and "EUR 464,350" in summary; assert "EUR 72,200" in summary and "EUR 135,650" in summary and "less than staying" in summary; assert "EUR 39,130" in summary and "EUR 12,000" in summary and "data-break-even=\"full_exit\"" in summary' "$report" && uv run python site/check_site.py && git diff --exit-code -- src/fazit/costs.py</automated>
  </verify>
  <acceptance_criteria>
    - `uv run pytest tests/test_costs.py -q` exits 0 and the new tests are among them
    - `grep -c "data-cost-tile" src/fazit/templates/report.html.j2` [HEAD=0, EXPECT>=1]
    - `grep -c "tiles-3" src/fazit/templates/report.html.j2` [HEAD=0, EXPECT>=1]
    - `grep -c "break_even" src/fazit/report.py` [HEAD=0, EXPECT>=1]
    - `git diff -- src/fazit/costs.py` is empty
    - Guard: `grep -ci "saving\|ersparnis" src/fazit/locales/en.yaml src/fazit/locales/de.yaml` still prints 0 for both files
    - Follows DESIGN.md (tiles: one anchor, a main line, one line of detail)
  </acceptance_criteria>
  <done>Page one shows the three five-year totals in whole units with origin and difference, an unknown total or comparison says so and counts the missing inputs, and the Stay assumption and break-even lines state the one varied input exactly.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 3: The cost section in its new order: intro, chart on one scale, notes, table layout (size: large)</name>
  <files>src/fazit/report.py, src/fazit/templates/report.html.j2, tests/test_costs.py, site/demo/en/index.html, site/demo/de/index.html</files>
  <read_first>DESIGN.md ("Colour", "Symbols", "Accessibility and weight"), .planning/report-redesign/UI-SPEC.md (sections 3, 3.1, 3.2, 3.3, 6.2 "New" components, 9 "Hooks kept", 11 criteria 10, 11 and 13), site/style.css (`.legend`, `.coverage`, `.coverage thead th`, its 600 px stacked layout, `.sec-intro`), src/fazit/costs.py (grep `BLOCKS`, `class CostGroup`, `class ScenarioResult`), src/fazit/report.py (grep `def _cost_table_blocks`, `def _cost_context`, the comparison and break-even helpers from Task 2), src/fazit/templates/report.html.j2 (the header's `dl.report-meta`, the cost section, the `cost_*` macros, the Stay assumption and break-even macro from Task 2, the 40rem query), src/fazit/locales/en.yaml (`costs.groups`, `costs.line_items`, `costs.origins`), tests/test_costs.py (grep `def test_demo_cost_comparison`, `def test_empty_inputs_render_unknown_costs`, `def test_sample_measurements_do_not_label_real_prices_invented`, `def _cost_section`, `_rendered_totals`)</read_first>
  <behavior>
    - Cost section order: `h2`; the intro line; `p` `costs.profile_note`; `div.cost-bars` (or, when the cost inputs are absent or entirely null, `p.note` with `costs.provide_inputs` and no chart); the Stay assumption and break-even lines (Task 2's macro); the results heading and table (structure and hooks unchanged, always visible); `costs.rounding`; `p` `costs.vat_note`; `div#costs-missing`; the cost inputs disclosure
    - Intro line (`p.sec-intro`, no `data-*` hook): the organisation name (or `header.unnamed_organisation`), `header.scan_date` with the scan date, `header.inputs_date` with `inputs.as_of` (or `common.date_not_supplied`, or `costs.not_provided` without inputs), and the price origin word (`costs.origins.invented` when amounts are invented, else `costs.origins.provided`, or `costs.not_provided` without inputs), separated by middle dots; existing keys only
    - The chart has a wrapping `.legend` naming the four blocks with the `costs.groups` labels (so productivity loss carries RR-01's internal-estimate label) and one row per scenario (`[data-chart-scenario]`): a heading line (scenario left; total, difference and origin right), the bar or the Unknown marker, the block values in text
    - Scale: `--share` of a row with a known total is that total divided by the largest known total of the three rows, written in the bar's inline style as `--share: <number>` with four decimals (numbers only); a zero denominator draws no fill. Town: 1.0000, 0.8797, 0.7739; non-profit: 0.7365, 1.0000, and no bar for the full move
    - Known row: `div.cost-bar[aria-hidden="true"]` (flex, 24 px, radius 999 px, gap 2 px) with a filled part `calc(var(--share) * (100% - 56px))` wide holding `span.cost-segment[data-chart-block]` per non-zero block (`flex-grow` the plain amount, `min-width: 2px`) in table order, tinted running `--fg`, direct project `--fg-2`, productivity loss `color-mix(in srgb, var(--fg-2) 55%, var(--bg))`, parallel running `color-mix(in srgb, var(--fg-2) 25%, var(--bg))`; no status colour, no pattern
    - Values line: every block with its amount in table order (`[data-chart-value]`), equal to the table's subtotal text; an explicit zero reads like "EUR 0.00" and has no segment
    - Row with any unknown block: no `.cost-bar` fill and no `--share`; only `span.cost-segment.is-unknown` (48 px, transparent, 1 px dashed `--fg-2`, help symbol); heading `costs.total_unknown`; values line `costs.known_blocks` with the known blocks' sum (blocks with a known total and at least one line), then every unknown block named with `status_label('unknown')`; no difference; with no known block, the marker and the Unknown label alone
    - A move row with a known total shows the difference and direction from Task 2's comparison function (with cents, as in the table); when Stay is unknown it shows `costs.difference` with the Unknown label instead
    - `data-block` appears exactly four times; the results table, both `caption[data-invented-amounts]`, `data-scenario`/`data-total`, `data-amount`, `data-cost-line`, `data-cost-input` and `li[data-missing-cost]` are unchanged
    - The old card-stack rules for other tables (`table:not(.cost-table)`) still serve the tables of moves, attention, found and the appendix, so they stay until RR-04 moves those tables to `.coverage` and deletes them (UI-SPEC 3.2); `.cost-table` takes the site's `.coverage` cell padding and header style, and in the `(max-width: 40rem)` query each `.cost-table` row stacks: heading, then one line per scenario with `content: attr(data-label)` left and the amount right
  </behavior>
  <action>
    Chart data (UI-SPEC 3.1). In `report.py`, add one function that builds the three chart rows from the scenario results: for each, the blocks in table order (running cost and the three change blocks) with their totals, whether the row's total is known, the known-block sum, the unknown block ids, and the share string. Compute the share exactly as a `Fraction` and format it with four decimals so output stays byte-identical across runs. Decide "chart shown" from the inputs: absent, or every cost input null, means no chart; an explicit zero is an input and keeps the chart.

    Template. Reorder the cost section as the behaviour says; move the cost inputs disclosure to the end and keep `costs.provide_inputs` (today's sentence) for the no-chart case. Build the chart markup of the behaviour list; values use `Formatter.money` with the input currency through the existing `cost_amount` macro; unknown blocks are named with `status_label('unknown')`, so status is always symbol plus word. Put the origin (`small[data-cost-origin]`, existing logic of `cost_heading`) beside each known total. Call Task 2's Stay assumption and break-even macro under the chart. Never write `data-block`, `data-amount`, `data-scenario` or `data-total` in the chart.

    CSS (UI-SPEC 3.1, 3.2, 6.2). Chart rules as the behaviour says; the heading line wraps on narrow screens and the block values go one per line at 360 px. Leave the old `table:not(.cost-table)` card-stack rules for the other tables in place: the moves, attention, found and appendix tables still use them until RR-04 moves them to the site's `.coverage` layout and deletes the rules (UI-SPEC 3.2); split a rule that also names `.cost-table` if the cost table needs its own declarations. Give `.cost-table` the site's `.coverage` cell padding and header style, and in the `(max-width: 40rem)` query stack each row as the behaviour says, so long German amounts never clip. Keep the `content: attr(data-label)` declaration (a style test matches it).

    Tests in `tests/test_costs.py` (item 11): one chart scale (the largest share is 1.0000 unless every known total is 0; each share equals its row's total over the largest known total, to four decimals, with totals taken from `compute_scenarios`; town and non-profit values as in the behaviour); no bar on a row with an unknown total (in the non-profit report the full move's row has the `is-unknown` marker, no `--share`, no `data-chart-block`, "Total unknown", the known-block sum and the Unknown label for productivity loss, and no difference); no chart for a report without inputs or with `inputs.example.yaml`; chart text equals table amounts (for every scenario and block, the `data-chart-value` amount equals the subtotal cell of that block's table body in that scenario's column); Stay's three change blocks read as formatted zero with no segment; the section order of the behaviour list, by the index of each part's first marker; the intro line contains the organisation name and both dates, and `costs.profile_note` and `costs.vat_note` appear once each; the Stay assumption and the same break-even lines appear in the costs section as in the summary. The existing cost tests must pass unchanged.

    Regenerate both site demo reports as in Task 1.
  </action>
  <verify>
    <automated>uv run pytest tests/test_costs.py tests/test_report.py -q && uv run pytest -q && uv run ruff check . && uv run ruff format --check . && out="$(mktemp -d)" && log="$(mktemp)" && uv run fazit demo --lang en --sample nonprofit --out "$out" > "$log" && report="$(tail -n 1 "$log")" && test -f "$report" && grep -q "cost-segment is-unknown" "$report" && grep -q "Total unknown" "$report" && uv run python -c 'import re, sys; html = open(sys.argv[1], encoding="utf-8").read(); costs = html.split("data-section=\"costs\"", 1)[1].split("</section>", 1)[0]; assert len(re.findall(r"data-block=\"", costs)) == 4; shares = re.findall(r"--share: ([0-9.]+)", costs); assert shares == ["0.7365", "1.0000"], shares' "$report" && out2="$(mktemp -d)" && uv run fazit demo --lang de --out "$out2" > "$log" && test -f "$(tail -n 1 "$log")" && uv run python site/check_site.py && git diff --exit-code -- src/fazit/costs.py src/fazit/status.py</automated>
  </verify>
  <acceptance_criteria>
    - `uv run pytest -q` exits 0 and `uv run python site/check_site.py` prints "No errors."
    - `grep -c "data-chart-block" src/fazit/templates/report.html.j2` [HEAD=0, EXPECT>=1]
    - `grep -c "table:not(.cost-table)" src/fazit/templates/report.html.j2` [HEAD=6 at 784e33b, EXPECT>=1] (RR-04 deletes them once no table uses them)
    - `grep -c "vat_note\|profile_note" src/fazit/templates/report.html.j2` [HEAD=0, EXPECT>=2]
    - Guard: `grep -c 'data-block="' src/fazit/templates/report.html.j2` still prints 1 (the results table's only `data-block` line)
    - Follows DESIGN.md (no status colour in the chart; pattern means only Unknown; tokens only)
  </acceptance_criteria>
  <done>The cost section prints as a unit with its intro and notes, draws only known totals on one scale with every amount in text, marks unknown totals with the marker alone and never as zero, and keeps the table and its hooks exactly.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| cost inputs → summary and chart | Figures a person typed become the most prominent numbers in the report |
| summary → the council's decision | A shortened list can hide a blocker or an unknown; a single number can read as advice |

## STRIDE Threat Register

Security level: ASVS 1. Blocking threshold: high.

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-RR-07 | Repudiation | summary caps hide blockers or unknowns | medium | mitigate | "{shown} of {total}" whenever rows are cut off, "All blockers" and "All open points" links, caveat whenever evidence is incomplete; tests for caps, deduplication, caveat and the all-Unknown report (Task 1) |
| T-RR-08 | Tampering | an unknown cost drawn or read as zero | high | mitigate | Unknown totals draw no bar, show the dashed marker and the Unknown label, never a number or dash; tests in Tasks 2 and 3 |
| T-RR-09 | Repudiation | chart, tiles and table disagree | medium | mitigate | All read the same results; tiles round only for display; a test compares every chart value with the table |
| T-RR-10 | Repudiation | break-even read as a recommendation or computed wrongly | medium | mitigate | One named input varied, entered value beside it, exact arithmetic from the unchanged model, tested against `compute_scenarios` (town full move 39,130); no line when the comparison is unknown |
| T-RR-SC | Tampering | package installs | high | mitigate | Nothing is installed |
</threat_model>

<verification>
Before declaring the plan complete:
- [ ] `uv run ruff check .` and `uv run ruff format --check .` exit 0
- [ ] `uv run pytest -q` exits 0
- [ ] `uv run fazit demo --lang de` and `uv run fazit demo --lang en`, each into a fresh temporary directory, exit 0 and the printed path exists
- [ ] `uv run python site/check_site.py` prints "No errors."
- [ ] If RR-02 created `.shots/report-redesign/check.mjs`: `node .shots/report-redesign/check.mjs <dir> --only filters` still exits 0
- [ ] The cost model, `STATUSES` and the CSP line are unchanged (`git diff -- src/fazit/costs.py src/fazit/status.py` is empty)
- [ ] The summary contains no `data-segment`, bar, `%`, "verdict", "recommend", "Urteil", "Empfehlung" or "empfohlen"
</verification>

<success_criteria>
- The summary says what a move would take, what stops it, what is still open and what it costs, in that order, with facts and open questions only and unknowns qualified
- The tiles, break-even lines and chart never show an unknown as a number, a dash or zero, and the break-even equals the cost model's result
- Only permitted test edits; the new tests of item 11 for this plan exist; the all-Unknown fixture is in place for RR-05
</success_criteria>

<output>
Create `.planning/report-redesign/RR-03-SUMMARY.md` when done. Record: the signatures of the summary, comparison, break-even, tile and chart functions and of `Formatter.money`; the summary and costs markup of the English town report and the non-profit full-move tile and chart row; the break-even figures rendered for both samples; every edited existing assertion with its UI-SPEC section 9 item; the native-review table of any German string added (drafts); helpers found moved; the test count and runtime of `uv run pytest -q`.
</output>

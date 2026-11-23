---
phase: report-redesign
plan: 02
type: execute
wave: 4
depends_on: ["RR-01", "RR-06", "RR-07"]
files_modified:
  - src/fazit/report.py
  - src/fazit/templates/report.html.j2
  - src/fazit/locales/en.yaml
  - src/fazit/locales/de.yaml
  - tests/report_expectations.py
  - tests/helpers.py
  - tests/test_report.py
  - tests/test_cli.py
  - tests/test_evidence_cli.py
  - tests/test_inputs.py
  - tests/test_simulation.py
  - site/check_site.py
  - site/demo/en/index.html
  - site/demo/de/index.html
autonomous: true
requirements: [REPT-02, REPT-04, REPT-05, RULE-03]

estimate:
  tokens: 200000
  raw_tokens: 200000
  tasks: 3
  confidence: medium

must_haves:
  truths:
    - "The readiness section shows exactly one `article.finding` per assessed area (Licences has none), in status groups ordered Blocker, Needs work, Unknown, Ready, with catalogue order inside each group; `STATUSES` is unchanged (UI-SPEC 1, 2.1)"
    - "Every card takes the area name as its anchor (`.finding-area` at `--fs-headline`) and shows its status, symbol and word, at `--fs-body` on the line under it; it has its category, its reason, a next step unless it is Ready, every evidence gap, a closed evidence disclosure when it has evidence, and a target line (UI-SPEC 2.1, 2.3, revision 4.1)"
    - "Ready cards are compact and never hidden; nothing on a card is collapsed except the evidence disclosure (UI-SPEC 2.1)"
    - "The report has no readiness bar: `.readiness-bar`, its segments and every `data-segment` hook are removed (founder's decision 2026-11-22: no readiness bar anywhere; the status filter's counts carry the distribution)"
    - "A card's target line puts a function with a transfer gap the organisation needs (need Yes) before the two-function cap, then the rest in mapping order (UI-SPEC 2.3, criterion 23)"
    - "Two radio groups filter the cards by status and category with CSS only; they combine, the two All options reset them, the status All option reads \"All · {n}\" with n the number of assessed areas in the catalogue, a combination without a match shows the empty state, a status with count 0 is disabled, and a link to a filtered-out card reveals it (UI-SPEC 2.2)"
    - "The filters work by keyboard with scripting disabled, and print ignores them"
    - "Every `data-*` hook of today's readiness rows survives on the card with the same name, value and order; only the tag changes (UI-SPEC 9)"
    - "Today's not-examined index stays the last element of `readiness`, its markup untouched; RR-04 moves and extends it"
  artifacts:
    - path: "src/fazit/templates/report.html.j2"
      provides: "Section frame, area cards, status groups, evidence disclosures, target lines, filters and their generated CSS rules"
      contains: "<article data-workload="
    - path: "src/fazit/report.py"
      provides: "Report-only display order, status groups, assessed area count, evidence counts, target lines"
      contains: "needs_work"
    - path: "tests/report_expectations.py"
      provides: "DISPLAY_ORDER expectation next to SECTION_ORDER"
      contains: "DISPLAY_ORDER"
    - path: "site/check_site.py"
      provides: "Status tally counted from readiness cards"
      contains: "article"
  key_links:
    - from: "src/fazit/templates/report.html.j2"
      to: "src/fazit/report.py"
      via: "status groups in display order built from a copy of the evaluated rows"
      pattern: "status-group"
    - from: "site/check_site.py"
      to: "site/demo/en/index.html"
      via: "the home page tally is compared with the cards' data-status values"
      pattern: "readiness-"
---

# Plan RR-02: section frame, area cards and filters

## Goal

The report puts the findings first, shows every assessed area as a card the reader can filter by status and category, and looks like the website, without changing what is measured, provided or unknown (`.planning/report-redesign/UI-SPEC.md`, revision 4.1, sections 0 and 2). It says what a move would take, what stops it and what is still open; it gives no score, recommendation or proposed resolution.

<objective>
Replace the readiness table with one card per assessed area inside the site's section frame, grouped by status in display order, move each area's evidence into its card, put a needed transfer gap first on the card's target line, and add the status and category filters that work with HTML and CSS only, with the readiness bar above them as their visual.

Purpose: UI-SPEC sections 2 and 6. The IT lead and the integrator see each area's status, reason and next step at once and can narrow the list without any script.
Output: template, report context, CSS, the permitted test edits that the tag change and the bar order need, new tests, the permitted `check_site.py` edit, a Playwright filter check outside the repository, regenerated site demo reports.

Run order of the plan set: RR-01, RR-06, RR-07, RR-02, RR-03, RR-04, RR-05. This plan relies on, and does not implement: Licences without status, card or category, the `assessed` flag and categories in the catalogue (RR-01); `next_step` with `kind` on every problem rule and all copy keys of UI-SPEC section 8 (RR-01); the desktop inference removed and the Windows-software reason reworded (RR-06); target-aware readiness, the mapping review and the `scope_statement` context (RR-07). RR-03 builds the summary and cost tiles and chart, RR-04 the navigation, "What to do next" (which takes over the not-examined index), the remaining sections, print and phone, and RR-05 the design checks, screenshots and decisions.
</objective>

<execution_context>
Read these two files before starting. They are plain paths, not includes.
- $HOME/.claude/gsd-core/workflows/execute-plan.md
- $HOME/.claude/gsd-core/templates/summary.md
</execution_context>

<context>
Read these files first. They are plain paths from the repository root.
- AGENTS.md
- DESIGN.md (binding: tokens only, type sizes, spacing scale, no borders on cards, labels not pills except filters, symbols, links, motion, accessibility)
- DECISIONS.md (Principles)
- .planning/report-redesign/UI-SPEC.md (revision 4.1, the source of truth; sections 0, 1, 2, 4, 6, 7, 9 and 11 for this plan)
- .planning/report-redesign/REV4-CHANGE-MAP.md (who owns what; this plan owns only its rows)
- .planning/research/report-usefulness/SYNTHESIS.md (sections A and C: findings, not a verdict; no readiness bar at all (founder, after the Apple-lens review); a needed gap before the cap)
- .planning/report-redesign/RR-01-SUMMARY.md, RR-06-SUMMARY.md and RR-07-SUMMARY.md (the context names for categories, the assessed workloads, `next_step` and its `kind`, the transfer-gap data; use the names these record, never guess)
- .planning/phases/01-demo-and-report/01-CONTEXT.md (D-19, D-28, D-43, D-56, D-58, D-66, D-80)
- .planning/phases/01.1-ai-assistants-and-decision-window/01.1-CONTEXT.md (D-81 and its amendment)

Precondition for the whole plan: RR-01, RR-06 and RR-07 are complete and committed, and their SUMMARY files exist. If one is missing, do not start; report back. Shared test helpers (`report_section`, `readiness_row`, `rebuild_report`, `sample_scan_path` and similar) live in `tests/helpers.py`; import from there, never from another test module.

Environment:
- The executor cannot commit. Leave every change in the working tree; the orchestrator reviews and commits.
- Run every command from the repository root. Every Python command goes through `uv`; if the shell does not find it, run `export PATH="$HOME/.local/bin:$PATH"` first. Install nothing; add no dependency and no module. The one exception to `uv` is `node` for the Playwright check in Task 3, which runs from `.shots/` and is never added to the repository.
- The base is current `main`, which since the first draft of this plan gained D31 load-time scan checks in `model.py`, one licence reconciliation rule, value bounds, and the removal of special cases from `status.py`, and then RR-01, RR-06 and RR-07. Locate every Python symbol, test and template block with grep at execution time, never by line number. Re-read every file immediately before editing; never revert, reformat or rewrite changes you did not make.
- Never weaken a test or a principle. Existing tests change only as UI-SPEC section 9 permits; this plan uses items 2, 3, 4, 5 and 6 and adds item 11 tests. If an existing test fails for any other reason, fix the template or code, not the test; if the spec makes that impossible, stop and report the assertion.
- Every `data-*` attribute of today's template keeps its name, values, attribute order and host element unless UI-SPEC section 9 lists the change. Each `<section data-section="…">` tag stays literal, with no class or id. `SECTION_ORDER` is RR-03's; do not touch it.
- Copy. All copy this plan shows exists as keys from RR-01 (`readiness.next_step`, `readiness.evidence_summary`, `readiness.all_replacements`, `filter.*`, `category.*`) or already in the locales; use those keys and add no wording. If a string the cards or filters need has no key, add it to both locales, mark the German value as a draft and list it with its English text in the SUMMARY's native-review table; formal "Sie", no abbreviations with full stops, status names exactly Bereit, Handlungsbedarf, Hindernis, Unbekannt. No "verdict", "score", "recommended", "Urteil", "Empfehlung" or "empfohlen" anywhere.
- CSS follows DESIGN.md: colours, fonts and radii only as tokens; sizes only from the seven type tokens; spacing from the scale (exceptions: the 20 px gutter, 2 px bar and track gaps). Copy site rules from `site/style.css` declaration for declaration, apart from UI-SPEC 6.2's six exceptions. No site rule that depends on the site's script, no icon masks, no `url()` other than the two embedded fonts.
- Every report command builds into a fresh temporary output directory and checks exit code, file existence and content separately (D-56). No network.
- Do not publish the site from this plan; RR-05 brings the home pages and screenshots in line.
</context>

<tasks>

<task type="tracer">
  <name>Task 1 (large): End-to-end area cards: display order and status groups in the report context, site frame and tokens, one card per assessed area, the bar in display order, and every test that reads readiness rows or segments</name>
  <files>src/fazit/report.py, src/fazit/templates/report.html.j2, src/fazit/locales/en.yaml, src/fazit/locales/de.yaml, tests/report_expectations.py, tests/helpers.py, tests/test_report.py, tests/test_cli.py, tests/test_evidence_cli.py, tests/test_inputs.py, tests/test_simulation.py, site/check_site.py, site/demo/en/index.html, site/demo/de/index.html</files>
  <read_first>AGENTS.md, DESIGN.md, .planning/report-redesign/UI-SPEC.md (sections 1, 2, 2.1, 2.3, 6.1, 6.2, 9), .planning/report-redesign/REV4-CHANGE-MAP.md, site/style.css (`:root` and its 600 px override, `body`, `h1, h2, h3, p`, `.grid`, `.sec`, `.sec-label`, `.sec-body`, `.sec-intro`, `.subsection`, `.page-intro`, `.finding`, `.finding-area`, `.finding-status`, `.finding-reason`, `.finding-target`, `.note-text`, `:focus-visible`), site/index.html (a `section.sec.grid` and the `article.finding` under "One finding in full"), src/fazit/report.py (grep `def _evidence_context`, `status_counts`, `status_by_workload`, `def _formatting_context`, and the category and assessed names RR-01 added), src/fazit/status.py (grep `STATUSES`, `class WorkloadStatus`, `class StatusRule`, `next_step`), src/fazit/catalogue.py (grep `assessed`, `categories`), src/fazit/templates/report.html.j2 (the `status_label`, `workload_status`, `status_reason` and `reason_detail` macros; the token blocks; the readiness section with `.readiness-bar`, `ul.status-legend`, the table and `div[data-subsection="not-examined"]`), tests/report_expectations.py, tests/helpers.py (grep `def readiness_row`, `def report_section`), tests/test_cli.py (grep `def test_scan_only_report_explains_readiness_and_missing_evidence`, `data-segment`), tests/test_simulation.py (grep `def _statuses`), and every test that reads readiness rows: run `grep -rn "data-workload=\|readiness_row\|data-segment" tests site/check_site.py`</read_first>
  <behavior>
    - The readiness section body holds, in order: `div.areas` and today's `div[data-subsection="not-examined"]` as the last element (Task 3 inserts the filters before `div.areas`, and the empty state after the last group)
    - No readiness bar remains anywhere in the report: `.readiness-bar`, its segments, their `data-segment` and `data-count` hooks and its CSS are deleted (founder's decision 2026-11-22: no readiness bar anywhere; the status filter's counts carry the distribution); no bar or legend is added anywhere else
    - `ul.status-legend` is gone from the readiness section (the status filter carries the counts; RR-03 builds the summary's `dl.status-summary`)
    - `div.areas` holds one `div.status-group[data-status-group]` per status that has areas, in the order blocker, needs_work, unknown, ready; each starts with `h3#status-<status>` showing `status_label(status)`; each holds its areas' cards in catalogue order
    - Each card opens `<article data-workload="W" data-status="S"`, then ` data-incomplete` when the area is incomplete, then `data-category`, `class="finding"`, `id="readiness-W"`, `aria-labelledby="area-W"`; exactly one card per assessed catalogue area; no Licences card; no readiness table remains
    - Card parts in order: `h4.finding-area#area-W` (area label, then `span.finding-category` with a middle dot and the category label); `p.finding-status` (today's `workload_status`); `div.finding-reason` (the deciding rule's reason; for Unknown the label of `row.reason_code` in a `span` with `data-reason`; for Ready the ready reason; then the notes of other fired rules as a list); `p.finding-next` for every non-Ready card ("Next step", then the deciding rule's `next_step` text, or for Unknown the fix of `row.reason_code`); `div.finding-missing` with today's "Evidence still needed" list and `li[data-missing]` items; for now, the rule evidence list with `li[data-evidence]` items as today (Task 2 moves it into the disclosure)
    - Inside `.areas`, `.finding-area` is the anchor at `--fs-headline` and `.finding-status` sits on the line under it at `--fs-body`, on every card (UI-SPEC 2.3, revision 4.1)
    - `STATUSES` keeps its value and order; the display order exists only as a report-side copy and in `tests/report_expectations.py` as `DISPLAY_ORDER`; `status_counts` follows display order
    - Every section's content sits in `div.sec.grid` with `h2.sec-label` and `div.sec-body`; the `section` tags are unchanged
    - The lines of the not-examined block are unchanged apart from indentation
    - `site/check_site.py` counts readiness cards for the home-page tally and passes
  </behavior>
  <action>
    Report context (UI-SPEC 1, 2.1). In `report.py`, add a report-only display order (blocker, needs_work, unknown, ready) and a `status_groups` context value: for each status in display order that has rows, the status and its rows, taken from a copy of the evaluated rows, which already come in catalogue order and cover only the assessed areas after RR-01. Switch `status_counts` to the same display order (a report-side list; `STATUSES` is untouched). Add `area_count`, the number of assessed workloads in the catalogue, read from the catalogue through RR-01's assessed flag (not from the evaluated rows and never a literal); if RR-01-SUMMARY records a context value with that meaning, use it instead and add none. Do not touch `STATUSES`, rule evaluation, the cost model or `scope_statement`. Add `DISPLAY_ORDER` with the same four values to `tests/report_expectations.py`, so tests state the expectation instead of importing it from the code under test.

    Tokens and frame (UI-SPEC 6.1, 6.2; DESIGN.md "Tokens", "Structure"). Keep the report's first light `:root` block and its dark block exactly as they are and first in the stylesheet (a test parses the first of each). After them add a second rule that gives the site's names: `--fg`, `--fg-2`, `--rule`, `--fill`, `--link`, `--link-hover` as aliases of the report's tokens; `--solid-bg`, `--solid-fg`, `--link-glow` with the site's light and dark values (the dark values in a second dark `@media` block after the first); `--sans`, `--mono`, `--ease`, `--gutter` (with the site's 600 px override to 16 px), `--max: 1120px`, `--bar-h: 52px`, `--hit: 44px`, `--radius: 8px`, `--radius-pill: 999px`. Write `--sans` and `--mono` with Figtree and "Geist Mono" followed only by generic families (`ui-sans-serif`, `system-ui`, `sans-serif`; `ui-monospace`, `monospace`): DESIGN.md allows no other font family. Change the body and `code` font declarations to use `--sans` and `--mono`. Add the margin reset `h1, h2, h3, h4, p { margin: 0 }`. Copy the site's `body`, `.grid`, `.sec`, `.sec::before`, `.sec-label`, `.sec-body`, `.sec-intro`, `.subsection` and `.page-intro` rules. In every `section`, wrap the content in `div.sec.grid`: the existing `h2` gains class `sec-label` and keeps its id; everything after it goes into `div.sec-body`. Give the header's content a wrapper with class `page-intro`, without changing its content (RR-04 restyles the header). Replace the report's old body width and padding rules with the frame.

    Bar (UI-SPEC 2, 9 item 4). Delete the readiness bar, its segments and its CSS (founder's decision 2026-11-22: no readiness bar anywhere; the status filter's counts carry the distribution). Delete `ul.status-legend` and its CSS from the readiness section; leave the `readiness.counts` key in the locales for RR-03 to reuse or remove.

    Cards (UI-SPEC 2.1, 2.3). At the top of the readiness section body render `div.areas` with the groups and cards of the behaviour list. Move today's row content onto the card: the category span and the `p.finding-next` paragraph that RR-01 added move unchanged (the card shows the `next_step` text in the report's language, never its `kind`); `workload_status`, `status_reason` and the hooks inside them stay as they are, and the "Evidence incomplete" marker keeps its `small` element and gains class `note-text`. Where today's template skips the reason because the Unknown code also appears in the missing list, the card instead always shows the label in the reason and the fix as the next step, as UI-SPEC 2.3 says. Delete the readiness table and its CSS. Leave `div[data-subsection="not-examined"]` as the last element of the section body with its lines unchanged: add no id, no item and no class to it (RR-04 moves it to `path`, adds `id="not-examined"` and the gap items).

    Card CSS. Copy the site's `.finding`, `.finding-area`, `.finding-status`, `.finding-reason`, `.finding-target` and `.note-text` rules. Inside `.areas` (UI-SPEC 6.2 exception 6, widened in revision 4.1): `.finding-area` is the anchor at `--fs-headline` in `--fg`; `.finding-status` at `--fs-body` on the line under it; the site rules outside `.areas` stay as they are. `.finding-next` gets `max-width: 36em; margin-top: 12px`; `.finding-missing` gets `margin-top: 16px; font-size: var(--fs-subhead)`. Status groups are spaced from the scale. All cards share one surface; only the symbol colour and the words differ: no coloured border or tint (UI-SPEC 6.2 new components).

    Locales. Delete the keys only the deleted table read (expected: `readiness.workload`, `readiness.evidence`; confirm each with `grep -rn` over `src` and `tests` first) from both locales, and list them in the SUMMARY. Add no key.

    Tests (UI-SPEC 9). Item 2: change the tag in every regex that reads readiness rows from the table row to `article`, in `readiness_row` in `tests/helpers.py` and wherever a test has its own regex (the grep in read_first lists them); change nothing else in those assertions. Item 3: where a test asserts that readiness rows follow catalogue order (the scan-only readiness test in `tests/test_cli.py` and `_statuses` in `tests/test_simulation.py`), assert instead that the groups follow `DISPLAY_ORDER` (statuses without areas absent), that cards inside each group follow catalogue order, and that there is exactly one card per assessed catalogue area; put that check in one helper in `tests/helpers.py` and use it from both. Item 4: the `data-segment` assertion in the same `tests/test_cli.py` test goes with the bar; in its place, assert from `readiness` that the number of cards per status, in `DISPLAY_ORDER`, equals the counts the test expected from the segments; nothing else in it changes. Item 6: where a test collects values from a whole readiness row and now finds an observation twice because a card shows it in two lists (for example `test_measured_positive_count_cannot_be_overridden_by_zero` in `tests/test_evidence_cli.py`, which bites once Task 2 adds the finding table), scope the assertion to one evidence record (`li[data-evidence="<finding id>"]`). In `site/check_site.py` (item 2), count elements of tag `article` whose id starts with `readiness-` for the tally, instead of table rows (grep `startswith("readiness-")`). Add one item 11 test to `tests/test_report.py`, over the four sample and language pairs: one card per assessed area and none for Licences, group order, catalogue order inside groups, every non-Ready card with a non-empty reason and next step, every card with its localised category label, and no `readiness-bar` or `data-segment` anywhere in the report.

    Amended permitted edits (coordinator, 2026-11-22, after the first run stopped on these conflicts; see the first RR-02-SUMMARY in git history):
    - `tests/test_cli.py` inventory heading assertions (the two literal `<h2>` checks for the fictional and the regular inventory heading): accept the heading with `class="sec-label"`; change only the tag match.
    - `tests/test_cli.py` scan-only readiness test, the `<caption data-sample>` assertion: in Task 1, assert the sample caption where it now renders (the report or the `found` section); in Task 2, when the finding tables move into the cards, restore the assertion to the readiness section.
    - `tests/test_rules.py` RR-01 category integration test (global catalogue order of rendered areas): migrate it like the CLI and simulation order tests, to status groups in `DISPLAY_ORDER` with catalogue order inside each group, using the same helper.

    Site demo. For each of `en` and `de`, run `uv run fazit demo --lang <lang> --sample town --profile opendesk --out <fresh temporary directory>` and copy the printed report over `site/demo/<lang>/index.html`.
  </action>
  <verify>
    <automated>uv run pytest -q && uv run ruff check . && uv run ruff format --check . && out="$(mktemp -d)" && log="$(mktemp)" && uv run fazit demo --lang en --out "$out" > "$log" && report="$(tail -n 1 "$log")" && test -f "$report" && uv run python -c 'import re, sys; from fazit.catalogue import load_catalogue; html = open(sys.argv[1], encoding="utf-8").read(); cards = re.findall(r"<article data-workload=\"([a-z_]+)\" data-status=\"([a-z_]+)\"", html); ids = [w.id for w in load_catalogue().workloads if w.assessed]; assert sorted(w for w, _ in cards) == sorted(ids) and "licences" not in ids, cards; order = ("blocker", "needs_work", "unknown", "ready"); statuses = [s for _, s in cards]; assert statuses == sorted(statuses, key=order.index), statuses; assert all([w for w, s in cards if s == st] == [w for w in ids if w in {x for x, y in cards if y == st}] for st in order); readiness = html.split("data-section=\"readiness\"", 1)[1].split("</section>", 1)[0]; assert "data-segment" not in html and "readiness-bar" not in html, "bar left"' "$report" && outde="$(mktemp -d)" && logde="$(mktemp)" && uv run fazit demo --lang de --out "$outde" > "$logde" && test -f "$(tail -n 1 "$logde")" && uv run python site/check_site.py</automated>
  </verify>
  <acceptance_criteria>
    - `uv run pytest -q` exits 0 and `uv run python site/check_site.py` prints "No errors."
    - `grep -c "<article data-workload=" src/fazit/templates/report.html.j2` [HEAD=0 EXPECT==1]
    - `grep -c 'table class="readiness"' src/fazit/templates/report.html.j2` [HEAD=1 EXPECT==0]
    - `grep -c 'class="status-legend"' src/fazit/templates/report.html.j2` [HEAD=1 EXPECT==0]
    - `grep -c 'readiness-bar' src/fazit/templates/report.html.j2` [HEAD=2 EXPECT==0] and `grep -c "data-segment=" src/fazit/templates/report.html.j2` [HEAD=1 EXPECT==0]
    - `grep -c 'class="sec grid"' src/fazit/templates/report.html.j2` [HEAD=0 EXPECT>=7]
    - `grep -c "DISPLAY_ORDER" tests/report_expectations.py` [HEAD=0 EXPECT==1]
    - Guard: `git diff -w -U0 -- src/fazit/templates/report.html.j2 | grep -c "unexamined\|not-examined\|not_examined"` prints 0 (the not-examined index is untouched apart from indentation)
    - `git diff -- src/fazit/status.py src/fazit/costs.py` is empty (no change to `STATUSES`, evaluation or the cost model)
    - Every test edit in `git diff -- tests` is one of UI-SPEC section 9 items 2, 3, 4 or 6, or a new item 11 test; the SUMMARY lists each edited assertion with its item number
    - Follows DESIGN.md (tokens only, type and spacing scales, no borders or tints on cards)
  </acceptance_criteria>
  <done>Every assessed area is one card in its status group, with its name as the anchor, inside the site's frame and tokens; the readiness bar is gone; all tests that read readiness rows read cards, and the site tally counts cards.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2 (medium): Evidence on the card: closed disclosure with counts, the finding table, provenance as a sentence, the target line with a needed gap first, and compact Ready cards</name>
  <files>src/fazit/report.py, src/fazit/templates/report.html.j2, src/fazit/locales/en.yaml, src/fazit/locales/de.yaml, tests/test_report.py, tests/test_cli.py, tests/test_evidence_cli.py, site/demo/en/index.html, site/demo/de/index.html</files>
  <read_first>DESIGN.md ("Links and buttons", "Symbols", "Motion"), .planning/report-redesign/UI-SPEC.md (sections 2.1, 2.3 "Evidence disclosure" and "Target line", 2.4, 4 "Evidence behind the figures" and "Licence products", 6.2 "details", 9 items 5 and 6, 11 criterion 23), .planning/report-redesign/RR-07-SUMMARY.md (how the transfer-gap need is now computed and exposed), site/style.css (`.evidence`, `.evidence-meta`, `.coverage` and its 600 px layout, `.table-note`, standalone links with a chevron), src/fazit/report.py (grep `groups=`, `alternatives`, `mapping_gaps=`, `def _evidence_context`; RR-07 moved `_mapping_gaps` out of this file), src/fazit/status.py (grep `class TransferGap`, `transfer_gaps`), src/fazit/templates/report.html.j2 (grep `macro provenance_word`, RR-06's sample-run provenance word), src/fazit/mappings.py (grep `class FunctionMapping`, `class TargetMapping`, `no_function`), src/fazit/rules/mappings/opendesk.yaml (the three Teams functions), src/fazit/templates/report.html.j2 (the macros `evidence_summary`, `alternative_evidence`, `evidence_pair`, `mapping_date`; the "Evidence behind the figures" block of the found section, grep `strings.found.evidence`; the replacements table and `ul.mapping-gaps`), src/fazit/demo/town/inputs.yaml (grep `teams.chat_history_must_be_kept`), tests/test_cli.py (grep `def test_sample_measurement_labels_and_directory_note`), tests/test_report.py (grep `def test_workload_evidence_stays_in_the_document_with_localised_reasons`)</read_first>
  <behavior>
    - A card has a closed `details.workload-evidence[data-evidence-workload]` whenever its area has catalogue observations or rule evidence; its `summary` keeps `id="evidence-W"` and reads `readiness.evidence_summary` ("Evidence · {measured} measured, {provided} provided, {unknown} unknown"), counting each observation once across both lists by provenance, including a competing observation that is shown
    - Inside: first the rule evidence (`ul.rule-evidence` with today's `li[data-evidence]`), then today's per-area finding table as `table.coverage` with `caption[data-sample]`, `tr[data-finding]` and the sample note row, both through `evidence_pair`
    - The old narrow-screen card-stack rules `table:not(.cost-table)` stay until RR-04 deletes them, but must not apply inside `.finding`: scope them off the card's evidence tables (for example `:not(.finding *)`) and check the card tables at 360 px
    - The found section no longer has the "Evidence behind the figures" heading or any assessed area's disclosure; the disclosure of each workload without a card (today only Licences) stays in `found` after the licence products block, unchanged apart from the table class; every scan finding id still appears in a `tr[data-finding]`
    - Provenance reads as one sentence in `.evidence-meta`: the provenance word first (weight 600, `--fg`), then source, date, period and coverage separated by middle dots, for example "Measured (simulated) · Sample licence inventory · 2 November 2026 · Complete, 3 of 3 scanned" in a sample run (the word comes from RR-06's `provenance_word` macro, so a sample run never prints the plain measured word); `.prov` and `data-provenance` stay on their elements; `.prov` has no border, background or radius
    - `p.finding-target` shows at most two of the area's mapped functions, each in `span[data-target-function="<function id>"]` with replacement, coverage label (text, no symbol) and check date or the no-project-check wording; functions whose transfer gap has need Yes come first, then the rest in mapping order, so the cap never hides a needed gap; then a standalone link "All replacements" to `#moves-title`; an area in `mapping.no_function` shows `moves.no_function`
    - Ready cards show no next step and no missing list, with `padding: 16px 24px`; like every card, area name as anchor and status at `--fs-body`
  </behavior>
  <action>
    Counts (UI-SPEC 2.3). In `report.py`, add one small function that, for an area, takes the distinct finding ids of its rule evidence and its catalogue observations, counts the shown observation of each id by provenance, adds the competing observation of that id when one is shown, and returns the three counts. Pass the counts per area through the context.

    Disclosure (UI-SPEC 2.3, 6.2). Move each assessed area's `details` block from the found section onto its card, after the missing list: keep the `details` and `summary` attributes, put the chevron symbol and the count sentence in the summary, and put the rule evidence list (as `ul.rule-evidence`, laid out with the site's `.evidence` grid values: one column, three from 640 px, gaps 24 and 32 px) and then the finding table (class `coverage` instead of `evidence`, the site's `.coverage` rules and 600 px stacked layout) inside. Delete the "Evidence behind the figures" heading from the found section; keep the loop only for workloads without a card (Licences, per UI-SPEC 2: its evidence stays in `found`), placed after the licence products block. Delete the locale key `found.evidence` if nothing else reads it (grep). `details` component: summary in `--link`, minimum height `var(--hit)`, the chevron rotates 90 degrees with `--ease` and does not move under reduced motion, the site's focus ring on `summary:focus-visible`.

    Provenance sentence (UI-SPEC 2.4). Rewrite the meta part of `evidence_summary` so the line starts with the `.prov` word, printed through RR-06's `provenance_word` macro as today, and continues with the present parts in the order source, date, period, coverage, joined by " · ", without the field labels. Keep the value text first in the `data-provenance` element, so tests that read the value after the element's opening tag still match. Keep the compact form and `alternative_evidence` working. If a field-label locale key is then unread anywhere (grep), delete it from both locales and list it in the SUMMARY.

    Target line (UI-SPEC 2.3, criterion 23). In `report.py`, add one small function that returns, per area, its functions from the chosen profile's mapping in mapping order, with the functions whose entry in the row's `transfer_gaps` (RR-07: one `TransferGap` per gap row of that workload) has need `yes` moved to the front (stable), cut to two. Take the need from `row.transfer_gaps` as RR-07 leaves it, the same data `mapping_gaps` is built from (use the names RR-07-SUMMARY records); compute nothing new and change no need. Render the line as the behaviour says; the link ends in an inline chevron symbol in the link colour (DESIGN.md "Links").

    Ready cards. Style compact Ready cards as the behaviour says; a Ready card keeps its reason, disclosure and target line.

    Tests. Item 5: the directory-note test in `tests/test_cli.py` reads the note from the readiness section instead of the found section. Item 6: scope any conflict or value assertion that now finds an observation twice in a card to one `li[data-evidence]` record. New item 11 tests in `tests/test_report.py`: disclosures closed and present exactly when the area has evidence; summary counts equal the distinct observations by provenance; the found section holds the Licences disclosure and no other; Ready cards have no `p.finding-next` and no `div.finding-missing`; each target line has at most two `data-target-function` items and one link to `#moves-title`; criterion 23: with a copy of the town inputs in which `teams.chat_history_must_be_kept` is `true`, the Teams card's first `data-target-function` is `teams_chat_history`, and in every sample report each function with need Yes in its row's `transfer_gaps` appears on its area's target line. If `test_workload_evidence_stays_in_the_document_with_localised_reasons` fails because an area gains a disclosure from derived licence evidence alone, stop and report: that is a spec-versus-test question for the maintainer (on today's samples no area does).

    Regenerate both site demo reports as in Task 1.
  </action>
  <verify>
    <automated>uv run pytest -q && uv run ruff check . && uv run ruff format --check . && out="$(mktemp -d)" && log="$(mktemp)" && uv run fazit demo --lang en --out "$out" > "$log" && report="$(tail -n 1 "$log")" && test -f "$report" && grep -q '<ul class="rule-evidence"' "$report" && grep -q 'data-target-function="' "$report" && ! grep -q 'data-unexamined-gap' "$report" && uv run python -c 'import re, sys; html = open(sys.argv[1], encoding="utf-8").read(); found = html.split("data-section=\"found\"", 1)[1].split("</section>", 1)[0]; assert re.findall(r"data-evidence-workload=\"([a-z_]+)\"", found) == ["licences"]; readiness = html.split("data-section=\"readiness\"", 1)[1].split("</section>", 1)[0]; tags = re.findall(r"<details class=\"workload-evidence\"[^>]*>", readiness); assert tags and all(" open" not in tag for tag in tags); assert all(len(re.findall(r"data-target-function=", line)) <= 2 for line in re.findall(r"<p class=\"finding-target\".*?</p>", readiness, re.S))' "$report" && uv run python site/check_site.py</automated>
  </verify>
  <acceptance_criteria>
    - `uv run pytest -q` exits 0 and `uv run python site/check_site.py` prints "No errors."
    - `grep -c "strings.found.evidence" src/fazit/templates/report.html.j2` [HEAD=1 EXPECT==0]
    - `grep -c "data-target-function" src/fazit/templates/report.html.j2` [HEAD=0 EXPECT>=1]
    - Guard: `grep -c "data-unexamined-gap" src/fazit/templates/report.html.j2` still prints 0 (RR-04 adds the gap items)
    - Guard: `git diff -w -U0 -- src/fazit/templates/report.html.j2 | grep -c "unexamined\|not-examined\|not_examined"` still prints 0
    - The SUMMARY lists every edited existing assertion with its UI-SPEC section 9 item
    - Follows DESIGN.md (provenance is a word, not a pill; a standalone link ends in a chevron; tokens only; nothing moves under reduced motion)
  </acceptance_criteria>
  <done>Each card carries its own evidence in a closed disclosure with honest counts, provenance reads as a sentence, a needed transfer gap is never cut from the target line, Ready cards are compact, and Licences' evidence stays in the recorded inventory.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 3 (medium): Status and category filters with radio inputs and CSS only, proved by keyboard with scripting disabled</name>
  <files>src/fazit/report.py, src/fazit/templates/report.html.j2, tests/test_report.py, site/demo/en/index.html, site/demo/de/index.html</files>
  <precondition>Node and Playwright with its Chromium are installed: `/home/roux/.local/share/playwright-1.62.1/node_modules/playwright` exists and `node --version` succeeds. If not, write and run every other part of this task, record in the SUMMARY that the browser check did not run, and hand back.</precondition>
  <read_first>DESIGN.md ("Accessibility and weight", "Links and buttons", "Motion"), .planning/report-redesign/UI-SPEC.md (section 2.2 in full, section 7 "Print", section 11 criteria 5 to 9 and 20), site/style.css (`.sr-only`, `:focus-visible`, `.note`, `.note-text`), src/fazit/templates/report.html.j2 (the readiness section from Tasks 1 and 2, `status_label`, the style block, the CSP `meta`), src/fazit/report.py (`area_count`, `status_counts`, and the category context from RR-01), tests/test_report.py (grep `def test_report_cannot_fetch_resources`, `def test_report_styles_work_in_light_dark_narrow_and_print`), .planning/phases/01.1-ai-assistants-and-decision-window/01.1-04-PLAN.md (Task 3, how Playwright is loaded through `createRequire`)</read_first>
  <behavior>
    - The readiness section body reads: `div.filters`, then `div.areas`, then `p.areas-empty.note`, then the untouched not-examined index
    - `div.filters` holds `fieldset.segmented[data-filter="status"]` and `fieldset.segmented[data-filter="category"]`, each with a `legend.sr-only` from `filter.status_legend` and `filter.category_legend`, then `p.note-text` with `filter.search_hint`; no `form` element
    - Status radios: `name="f-status"`, ids `f-status-all` (checked, label `filter.all` + " · " + `area_count` formatted, "All · 14" today) and `f-status-<status>` in display order, each label with the status symbol, the exact status name and its count; a status with count 0 is `disabled`
    - Category radios: `name="f-category"`, ids `f-category-all` (checked, `filter.all_categories`) and `f-category-<id>` in catalogue category order, label text only
    - `p.areas-empty.note` with `filter.empty`, hidden by default
    - Generated rules inside `@media screen` and `@supports selector(:has(*))`: a checked status hides other groups; a checked category hides other cards and groups left without a card of it; a checked pair with no matching card shows the empty state; a card that is the target of a link, and its group, always show
    - Without `:has()`, `.filters` is hidden and every card shows; in print `.filters` and `.areas-empty` are hidden and every card shows whatever is checked
    - By keyboard with scripting disabled, at 1280 and 360 px in light and dark: Tab reaches each radio group once, arrow keys move and select, the focus ring is visible on the segment, filters combine, All restores, the empty state appears for a pair with no match with no group heading visible, and a link to a filtered-out card reveals it
  </behavior>
  <action>
    Markup (UI-SPEC 2.2). Render the filter block at the top of the readiness section body, before `div.areas`, with the markup of the spec's example: each `label` wraps its `input type="radio"` and its text; status labels use `status_label` followed by " · " and the formatted count; counts come from `status_counts`, the same evaluated rows as the cards, so they can never disagree; the All label's n is `area_count` from the catalogue. Category radios loop over the catalogue's categories, so adding or moving an area needs no template edit (criterion 20). Render `p.areas-empty.note` after `div.areas`.

    CSS (UI-SPEC 2.2 "Look"). Inputs use the `.sr-only` rules, never `display: none`. Track: `display: inline-flex; padding: 2px; gap: 2px; border-radius: var(--radius-pill); background: var(--fill)`; below 40rem it wraps and takes `--radius-card`. Segment (`label`): `min-height: var(--hit); padding: 0 16px; border-radius: var(--radius-pill); font: 600 var(--fs-subhead) / 1 var(--sans)`, colour `--fg-2`, centred content; selected (`label:has(:checked)`): `background: var(--bg); color: var(--fg); box-shadow: 0 1px 3px rgb(0 0 0 / 12%)`; hover `--fg`; disabled 40 % opacity; `label:has(:focus-visible)` takes the site's focus ring; background transition 0.2 s with `--ease`, none under reduced motion. `fieldset` has no border, margin or padding; 12 px between tracks and before the hint; the bar sits directly above the first track, spaced from the scale. The empty state is centred, `--fg-2`, with no symbol.

    Generated rules (UI-SPEC 2.2 rules 1 to 5). With `R` standing for `[data-section="readiness"]`, generate rules 1 to 4 in a Jinja loop over the display-order statuses and the catalogue's category ids (all of them, whatever the counts, so the stylesheet is the same for every sample and profile), inside `@media screen { @supports selector(:has(*)) { … } }`. Rule 5 must win over rules 1 to 3; prefer specificity to `!important`. Add `@supports not selector(:has(*)) { .filters { display: none } }` and, in the print block, hide `.filters` and `.areas-empty`. Filters touch only `.status-group`, `.finding` and `.areas-empty`; nothing else in the report changes when a radio is checked, the bar included.

    Tests (item 11) in `tests/test_report.py`, over the four sample and language pairs: exactly two radio groups with those names; exactly one checked input per group, the All option; the status All label carries the number of assessed areas in the catalogue; a status radio is disabled exactly when no card has that status; every card's `data-category` has a category radio and every category radio has a card; every CSS rule that contains `:checked` lies inside an `@media screen` block (find the block spans by brace matching, not by a fixed line); the `@supports not selector(:has(*))` fallback hides `.filters`; there is no `form` element.

    Browser check (outside the repository). Create `.shots/report-redesign/check.mjs` (`.shots/` is ignored by git; never add the script to the repository). It loads Playwright through `createRequire("/home/roux/.local/share/playwright-1.62.1/node_modules/")`, takes one argument, a directory whose subdirectories `town-en`, `town-de`, `nonprofit-en` and `nonprofit-de` each hold one report, accepts `--only <part>` to run one part, prints one line per failed check and exits 1 if any failed. Later plans add the parts `layout`, `print` and `site`; this task writes the part `filters`. For each report, at 1280 by 800 and 360 by 800, in light and dark, in a context with `javaScriptEnabled: false` and every request other than the report file and `data:` URLs aborted and counted as a failure: check that the CSP meta content is exactly the string in today's template; press Tab from the top and record the focused elements, and check that focus enters each radio group exactly once; with arrow keys select each enabled status and check that only cards of that status, and only that group's heading, are visible; then select categories and check the combination; find a status and category pair with no card from the DOM and check that the empty state is visible and no `.status-group` is; select both All options and check that every card is visible; check that the focused segment's computed outline is not `none`; with a status filter active, follow a link to a card of another status and check that the card is visible; emulate print media with a filter active and check that every card is visible and `.filters` is not. Read state with Playwright locator queries; if the installed version cannot query a page with scripting disabled, run the same key sequence with scripting enabled, record that in the SUMMARY, and rely on the existing test that the report contains no script. Use role queries to check that each fieldset is a group named by its legend and each radio is named by its label text, including the status count.

    Regenerate both site demo reports as in Task 1.
  </action>
  <verify>
    <automated>uv run pytest tests/test_report.py -q && uv run pytest -q && uv run ruff check . && uv run ruff format --check . && d="$(mktemp -d)" && for s in town nonprofit; do for l in en de; do uv run fazit demo --lang "$l" --sample "$s" --out "$d/$s-$l" > "$d/$s-$l.log" && test -f "$(tail -n 1 "$d/$s-$l.log")" || exit 1; done; done && node .shots/report-redesign/check.mjs "$d" --only filters && uv run python site/check_site.py</automated>
  </verify>
  <acceptance_criteria>
    - `uv run pytest -q` exits 0 and `uv run python site/check_site.py` prints "No errors."
    - `node .shots/report-redesign/check.mjs <dir> --only filters` exits 0 for the four reports
    - `grep -c 'name="f-status"' src/fazit/templates/report.html.j2` [HEAD=0 EXPECT>=1] and `grep -c 'name="f-category"' src/fazit/templates/report.html.j2` [HEAD=0 EXPECT>=1]
    - Guard: `grep -c "<form" src/fazit/templates/report.html.j2` still prints 0
    - Guard: `git diff -U0 -- src/fazit/templates/report.html.j2 > "$tmp"` succeeds and `grep -c "http-equiv" "$tmp"` prints 0 (the CSP line is untouched)
    - Guard: `git diff -w -U0 -- src/fazit/templates/report.html.j2 | grep -c "unexamined\|not-examined\|not_examined"` still prints 0
    - `git status --short .shots` prints nothing (the script is ignored)
    - Follows DESIGN.md (pills only for these controls; every control works by keyboard; nothing moves under reduced motion)
  </acceptance_criteria>
  <done>The reader can filter cards by status and category with keyboard or mouse and no script; the filters change nothing else, never reach print, and a browser check proves it.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| report file → reader's browser | The report is opened offline by people who did not build it; it must load nothing and run nothing |
| filters → the reader's picture | A filter must not change a count, a status, the summary or the printed report |
| target line → the reader's picture | The two-function cap must not hide a function the organisation needs and the target lacks |

## STRIDE Threat Register

Security level: ASVS 1. Blocking threshold: high.

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-RR-04 | Tampering | filter markup: a `form`, script or event handler slips in | high | mitigate | Radios without a `form`; the existing resource test rejects `form`, `script`, `use` and `on*`; the browser check aborts and fails on any request |
| T-RR-05 | Repudiation | filters hide a Blocker or Unknown from print or from the summary | medium | mitigate | Rules live only under `@media screen`, target only cards, groups and the empty state; print and target checks in the browser check; a test places every `:checked` rule inside `@media screen` |
| T-RR-06 | Tampering | card rewrite drops or renames a test hook | medium | mitigate | Hooks kept with name, value and order; only UI-SPEC 9 test edits, listed per item in the SUMMARY; the not-examined block is guarded by a whitespace-insensitive diff |
| T-RR-07 | Repudiation | the target line's cap hides a needed transfer gap | medium | mitigate | Needed functions sort first before the cap; the criterion 23 test with chat history needed, and the all-samples test that every need-Yes function appears on its card |
| T-RR-SC | Tampering | package installs | high | mitigate | Nothing is installed; Playwright and Node already on the machine are used from an ignored directory |
</threat_model>

<verification>
Before declaring the plan complete:
- [ ] `uv run ruff check .` and `uv run ruff format --check .` exit 0
- [ ] `uv run pytest -q` exits 0
- [ ] `uv run fazit demo --lang de` and `uv run fazit demo --lang en`, each into a fresh temporary directory, exit 0 and the printed path exists
- [ ] `uv run python site/check_site.py` prints "No errors."
- [ ] `node .shots/report-redesign/check.mjs <dir> --only filters` exits 0
- [ ] The CSP meta line of the template is unchanged, and the not-examined block is unchanged apart from indentation
- [ ] No "verdict", "score", "recommended", "Urteil", "Empfehlung" or "empfohlen" in anything this plan added
</verification>

<success_criteria>
- The readiness table is gone; every assessed area is a card in its status group, named as its anchor, with its evidence and a target line that never hides a needed gap
- The report has no readiness bar; the status filter's counts carry the distribution
- Filters work by keyboard without script and change nothing else
- All existing tests pass with only UI-SPEC section 9 edits
</success_criteria>

<output>
Create `.planning/report-redesign/RR-02-SUMMARY.md` when done. Record: the context names added in `report.py` and their shapes (`status_groups`, `area_count`, the evidence counts, the target-line functions), and that `status_counts` now follows display order; the final card markup of one Needs work card and one Ready card from the English town report; every edited existing assertion with its UI-SPEC section 9 item; every locale key deleted; a native-review table of any German string added (expected: none); the result of each `filters` check per report, width and scheme; whether Playwright could query pages with scripting disabled; helpers found moved; the test count and runtime of `uv run pytest -q`. Note for RR-03: the readiness bar and its `data-segment` stay in `readiness` (do not move them), `ul.status-legend` is gone, `readiness.counts` is still in the locales, and `area_count` is the catalogue's assessed-area count for "Of {n} areas". Note for RR-04: the not-examined index is still the last element of `readiness`, without `id="not-examined"` and without gap items.
</output>

---
phase: report-redesign
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - src/fazit/rules/findings.yaml
  - src/fazit/catalogue.py
  - src/fazit/mappings.py
  - src/fazit/rules/status.yaml
  - src/fazit/status.py
  - src/fazit/report.py
  - src/fazit/templates/report.html.j2
  - src/fazit/locales/en.yaml
  - src/fazit/locales/de.yaml
  - tests/test_model.py
  - tests/test_rules.py
  - tests/test_locales.py
  - tests/test_inputs.py
  - tests/test_evidence_cli.py
  - tests/test_simulation.py
  - tests/test_cli.py
  - .planning/phases/01.1-ai-assistants-and-decision-window/01.1-CONTEXT.md
  - README.md
  - README.de.md
  - site/index.html
  - site/de/index.html
  - site/pilots/index.html
  - site/de/pilots/index.html
  - site/demo/en/index.html
  - site/demo/de/index.html
autonomous: true
requirements: [RULE-02, RULE-03, I18N-01, I18N-02]

estimate:
  tokens: 200000
  raw_tokens: 200000
  tasks: 3
  confidence: low

must_haves:
  truths:
    - "Licences carries no move-readiness status: it has no status rules, no readiness row or card, no category, and is not counted; its evidence still feeds the other areas and the recorded inventory, and every licence-evidence gap stays visible (launch critique C2)"
    - "`rules/findings.yaml` has five categories in the spec's order without `contracts_costs`, and every assessed area has exactly one; the catalogue refuses a missing, unregistered or unused category, a category on an unassessed area, and a category label missing in either locale; a mapping file refuses a function on an unassessed area"
    - "Every readiness row carries `data-category` and shows its category label in both languages; changing an area's category in a copied catalogue changes the rendered `data-category` with no template edit (UI-SPEC 2.2, criterion 20)"
    - "Every status rule carries `next_step` with `kind` (`clarify`, `decide` or `replace`, chosen from the action the sentence names) and one English and one German sentence naming no target product and no import or export; the status-rule loader refuses a rule without `next_step`, without `kind`, with another `kind`, or without either text"
    - "The kind reaches the report context on every decided row (`row.deciding.next_step.kind`), so RR-04 can split the steps without touching the rules"
    - "The town report shows each deciding rule's next step under its reason, in both languages; every German sentence, with its kind, is listed for the maintainer's native review"
    - "Every key of UI-SPEC section 8 (revision 4.1) exists in both locales with the spec's wording; no locale value and no status-rule text contains score, verdict, recommended, recommendation, best, safe, easy, saving, Urteil, Empfehlung or empfohlen, and no reason fix tells the reader to import or supply an export this version cannot read (C7)"
    - "The READMEs, the pilots pages, the home-page tally and the report-card alt text say 14 areas (the home figures strip and `publiccode.yml` stay for RR-05's follow-ups); 01.1-CONTEXT.md records the D-81 amendment, adjusted for Licences having no card and for the new area count"
    - "`STATUSES` keeps its value and order; the cost model and rule evaluation are unchanged apart from Licences leaving the evaluated set"
  artifacts:
    - path: "src/fazit/rules/findings.yaml"
      provides: "Five categories, one per assessed area; Licences marked as not assessed"
      contains: "assessed: false"
    - path: "src/fazit/rules/status.yaml"
      provides: "No Licences block; a bilingual next step with its kind on every remaining problem rule"
      contains: "next_step:"
    - path: "src/fazit/locales/de.yaml"
      provides: "German copy of UI-SPEC section 8 revision 4.1, the launch-critique copy and the category labels"
      contains: "Umstiegsszenarien"
    - path: ".planning/phases/01.1-ai-assistants-and-decision-window/01.1-CONTEXT.md"
      provides: "D-81 amendment"
      contains: "D-81 amendment"
  key_links:
    - from: "src/fazit/rules/findings.yaml"
      to: "src/fazit/status.py"
      via: "the status-rule loader and the evaluation cover exactly the assessed areas"
      pattern: "assessed"
    - from: "src/fazit/rules/findings.yaml"
      to: "src/fazit/templates/report.html.j2"
      via: "the catalogue's workload category reaches the readiness row as data-category through the report context"
      pattern: "data-category="
    - from: "src/fazit/rules/status.yaml"
      to: "src/fazit/status.py"
      via: "StatusRule.next_step with kind and both texts, required by the status-rule loader"
      pattern: "next_step"
---

# Plan RR-01: data for the report redesign (Licences without status, categories, next steps with kind, copy)

## Goal

The report puts the findings first: what a move would take, what stops it, what is still open and what it costs. It shows every area as a card the reader can filter by status and category, draws the costs, and looks like the website, without changing what is measured, provided or unknown and without a score, verdict or proposed resolution (`.planning/report-redesign/UI-SPEC.md`, revision 4.1, section 0). On 2026-11-22 the founder folded the launch critique (`.planning/research/launch-critique/SYNTHESIS.md`, section C and A3) and the usefulness review (`.planning/research/report-usefulness/SYNTHESIS.md`, sections A and C) into this work.

<objective>
Put into data everything the new report needs and prove it reaches the rendered report: Licences loses its move-readiness status (C2), every assessed area gets a category (UI-SPEC 2.2), every problem rule gets a bilingual next step with its kind (UI-SPEC 2.3; usefulness A11), both locales get every string of UI-SPEC section 8 revision 4.1 and the launch-critique copy (C7 fixes), a ban-list test guards the copy, the area count is corrected where it is written as text, and the D-81 amendment is recorded.

Purpose: the cards, filters, summary and "What to do next" of the later plans read these fields and keys; data, not code, holds judgement (AGENTS.md). Later plans use RR-01's keys and never add copy of section 8 (`REV4-CHANGE-MAP.md`).
Output: catalogue, status rules, loaders, both locales, a few lines of template, tests, the D-81 amendment, the area count on the site and in the READMEs, regenerated site demo reports.

Run order of the plan set: RR-01, RR-06, RR-07, RR-02, RR-03, RR-04, RR-05. RR-01 data and copy; RR-06 rule and validation fixes, the simulated label and the scan format; RR-07 target-aware readiness, the mapping review and the scope-statement data; RR-02 frame, area cards and filters; RR-03 section order, summary, cost tiles with break-even, cost chart; RR-04 navigation, "What to do next", remaining sections, print and phone; RR-05 design checks, real-PDF page-one check, screenshots, decisions and the Phase 1.1 hand-over.
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
- DECISIONS.md (Principles)
- .planning/report-redesign/UI-SPEC.md (revision 4.1; sections 2.2, 2.3, 8 and 9 for this plan; 1.2, 3.3 and 4.1 for what the copy is used for)
- .planning/report-redesign/REV4-CHANGE-MAP.md (binding: rules for every plan, who owns what, the interfaces, and the revision 4.1 owners)
- .planning/research/report-usefulness/SYNTHESIS.md (sections A and C)
- .planning/research/launch-critique/SYNTHESIS.md (section C and A3), with CRITIC-astra.md and CRITIC-fable.md in the same folder for detail
- .planning/quick/261122-rv9-round3/SUMMARY.md and .planning/quick/261122-rv10-consistency/SUMMARY.md (what the release review changed last)
- .planning/phases/01-demo-and-report/01-CONTEXT.md (D-17, D-21, D-31, D-41, D-43, D-58, D-59, D-66 still bind except where this plan says)
- .planning/phases/01.1-ai-assistants-and-decision-window/01.1-CONTEXT.md (D-81)

Base: current `main` (df36196 or later). Since this plan was first written against 709bd17, `0ae2be2` (licence reconciliation as one rule: unreconciled licences leave licence readiness incomplete and inferred absences Unknown), `6e36d71` (bounded decimal training days) and `acf9be9` (D31 load-time scan checks in `model.py`) landed. The planner re-checked every symbol, test name and count below against df36196. If `.planning/quick/261122-rv11-truthful` has landed by the time you run, it may add a licence reason (assigned seats above purchased); it falls under the same rule as every other licence gap in Task 1.

Facts checked on df36196 (re-check with grep before relying on them):
- `catalogue.workload_ids` lists all 15 workloads and is used by `licences.py` (derived signals for every workload), `mappings.py` (the `no_function` union must equal all workloads) and `status.py` (`load_status_rules`, `evaluate`). Keep its meaning; add a separate property for the assessed workloads and use it only in `status.py`.
- The per-rule reader of the status loader is `_workload_rules` in `src/fazit/status.py` (UI-SPEC 2.3 says "`rules.py`"; `rules.py` only reads files and checksums).
- `src/fazit/rules/status.yaml` has 31 rules; Task 1 deletes `licences-terms-unknown`, leaving 30 (UI-SPEC 2.3's "all 31" predates C2). RR-06 adds or rewords rules after RR-01 and gives each `next_step` and `kind`.
- The town demo (opendesk) shows today: Licences Ready; 4 Ready, 9 Needs work, 1 Blocker, 1 Unknown over 15 areas. After Task 1: 3 Ready, 9 Needs work, 1 Blocker, 1 Unknown over 14.
- The reconciliation results `licence_assignments_conflict` and `licence_directory_unverified`, and `licence_products_missing`, sit on `licences.product_count.missing_reason`, which the found section's licence block already prints through `reason_detail`. The inventory's coverage gap (`coverage_partial`, `coverage_unknown`) and a scan without any licence inventory are today visible only as gaps on the Licences row.
- There is no ban-list test yet; Task 3 adds it. The only hand-built status rule in the tests is in `test_disputed_count_blocks_every_workload_that_uses_it` (`tests/test_rules.py`). The row helper is `readiness_row` in `tests/helpers.py`.

Scope precedence: the founder's launch-critique and usefulness decisions win over UI-SPEC where they differ. In this plan that means: Licences has no status, card or category, so the category table of UI-SPEC 2.2 has no `contracts_costs`; the status code changes for the `assessed` flag as well as `next_step`; and the D-81 amendment is worded for Licences having no card.

Size: three tasks, one executor run. Task 3 carries most of the copy (about 45 new or changed keys per locale, the C7 fixes and the ban list); it stays one task because every string goes through one native-review pass. If it runs long, finish the locale values and tests first and the D-81 amendment last; do not split it.

Environment:
- The executor cannot commit. Leave every change in the working tree; the orchestrator reviews and commits.
- Run every command from the repository root. Every Python command goes through `uv`; if the shell does not find it, run `export PATH="$HOME/.local/bin:$PATH"` first. Install nothing and add no dependency. Add no module.
- Locate every Python symbol with grep at execution time (for example `grep -n "class StatusRule" src/fazit/status.py`), never by line number. Re-read every file immediately before you edit it; never revert, reformat or rewrite changes you did not make. The site pages may carry uncommitted edits from other work (the about page): change only the lines this plan names.
- Never weaken a test or a principle. Existing tests change only as UI-SPEC section 9 permits (this plan uses items 9, 10 and 11) or where C2 changes the behaviour a test asserts (Licences has no status); list each such edit with its item in the SUMMARY. Principle tests (unknown is never Ready, a skipped collector never improves a status, no invented numbers) may only get stricter.
- Every report command builds into a fresh temporary output directory and checks exit code, file existence and content separately (D-56). No network.
- Every user-facing string goes into both locale files. English is British; German is native administrative German with the formal "Sie", written as German, with no abbreviations such as "z. B." and the status names exactly Bereit, Handlungsbedarf, Hindernis, Unbekannt. Every new or changed German string is a draft and goes into the native-review table of the SUMMARY; German values that UI-SPEC section 8 gives (marked *draft* or not) are used as given.
- Site: change only the lines this plan names, on both languages. Do not publish the site from any intermediate plan.
</context>

<tasks>

<task type="tracer">
  <name>Task 1: Licences not assessed and a category per assessed area, through loaders, evaluation, locales, report context and the readiness row; the area count where it is written</name>
  <files>src/fazit/rules/findings.yaml, src/fazit/catalogue.py, src/fazit/mappings.py, src/fazit/rules/status.yaml, src/fazit/status.py, src/fazit/report.py, src/fazit/templates/report.html.j2, src/fazit/locales/en.yaml, src/fazit/locales/de.yaml, tests/test_model.py, tests/test_rules.py, tests/test_inputs.py, tests/test_evidence_cli.py, tests/test_simulation.py, tests/test_cli.py, README.md, README.de.md, site/index.html, site/de/index.html, site/pilots/index.html, site/de/pilots/index.html, site/demo/en/index.html, site/demo/de/index.html</files>
  <read_first>AGENTS.md, DESIGN.md ("Copy"), .planning/report-redesign/REV4-CHANGE-MAP.md, .planning/research/launch-critique/SYNTHESIS.md (C2), .planning/research/launch-critique/CRITIC-fable.md (comment 4), .planning/report-redesign/UI-SPEC.md (section 2.2 "Categories" and its table, section 9 items 10 and 11), src/fazit/rules/findings.yaml (`workloads`, the `licences.` findings), src/fazit/rules/status.yaml (the `licences` block), src/fazit/catalogue.py (grep `class WorkloadEntry`, `class Catalogue`, `def workload_ids`, `_LABEL`, `def _workloads`, `def _parse_catalogue`, `def load_catalogue`, `def _require_label`), src/fazit/validation.py (grep `class Validator`), src/fazit/status.py (grep `def load_status_rules`, `def evaluate`), src/fazit/mappings.py (grep `no_function`), src/fazit/licences.py (grep `def licence_findings`, `def _directory_cross_check`, `def _inventory_evidence`), src/fazit/report.py (grep `def _formatting_context`, `workload_labels`, `product_count`, `def _evidence_context`), src/fazit/templates/report.html.j2 (the readiness table row, the licence products block in `found`, the `moves` loop over `status_by_workload`), tests that read the Licences readiness row or list its status (run `grep -rn '"licences"\|licences-terms\|workload="licences"\|contract_terms_known' tests`), tests/helpers.py (grep `def readiness_row`), tests/test_model.py (grep `def test_catalogue_refuses_an_unlisted_workload`), tests/test_rules.py (grep `def test_bad_catalogue_label_exits_with_a_localised_sentence`, `def test_bad_mapping_names_the_file_and_field`, `def test_bad_status_rule_names_the_file_and_field`), tests/test_inputs.py (grep `def test_every_provided_finding_is_used_by_the_report`), site/check_site.py (grep `def check_tally`), site/index.html and site/de/index.html (the `p.tally` sentence and the report-card `img` alt text), site/pilots/index.html and site/de/pilots/index.html ("15 areas" / "15 Bereichen"), README.md and README.de.md ("fifteen areas" / "fünfzehn Bereiche")</read_first>
  <behavior>
    - A workload entry may carry `assessed: false`; only `licences` does; `load_catalogue()` exposes it on the workload entry (default true) and offers the assessed workload ids in catalogue order; `workload_ids` keeps listing all workloads
    - The status-rule loader requires a block for every assessed workload and refuses one for an unassessed workload; the `licences` block and its rule are gone; evaluation returns rows for assessed workloads only, in catalogue order
    - A mapping file that maps a function to an unassessed workload, or leaves it out of `no_function`, is refused with the field `no_function`
    - `licences.contract_terms_known` becomes `headline: true`, so an answer in an existing inputs file is still accepted and shown in the recorded inventory
    - No report has a Licences readiness row; the licence products, their count and every licence reason code still appear: `licence_products_missing`, `licence_assignments_conflict` and `licence_directory_unverified` in the found section's licence block as today; the inventory's `coverage_partial` or `coverage_unknown` gap now also in that block (reason and fix); a scan without any licence inventory shows the licence block with Unknown and its reason instead of nothing; the classification gaps (`licence_plan_list_missing`, `licence_plan_list_incomplete`, `licence_not_classified`) on every area whose rules read licence signals, as today; licence-derived signals decide the other areas as before
    - `load_catalogue()` exposes the categories `communication`, `files`, `identity_devices`, `automation_ai`, `security` in that order, each with label `category.<id>`; every assessed workload has the category of UI-SPEC 2.2's table
    - A missing category on an assessed workload, an unregistered value (`workloads[<index>].category`), a category on the unassessed workload, a registered category that no workload uses (`categories[<index>].id`) and a duplicate category id are refused, each naming `findings.yaml`; a missing `category.<id>` label in one locale makes `fazit demo` exit 2 naming `categories[<index>].label`
    - The town demo's mail row carries `data-category="communication"` and shows "Communication" / "Kommunikation"; with a copied `findings.yaml` in which mail's category is `files`, the mail row shows `data-category="files"` with no template edit
    - The home-page tally reads "All 14 areas in the sample: 3 Ready, 9 Needs work, 1 Blocker, 1 Unknown." / "Alle 14 Bereiche im Beispiel: 3 Bereit, 9 Handlungsbedarf, 1 Hindernis, 1 Unbekannt." (confirm against the regenerated report), the report-card alt text gives the same counts, and `site/check_site.py` passes
  </behavior>
  <action>
    Licences without status (C2). In `rules/findings.yaml`, give the `licences` workload `assessed: false`; set `licences.contract_terms_known` to `headline: true`. In `rules/status.yaml`, delete the `licences` block. In `catalogue.py`, read the optional `assessed` key (boolean, default true) onto `WorkloadEntry` as a field named `assessed` (RR-02 relies on this name) and add a property on `Catalogue` for the assessed workload ids in catalogue order. Add no area count to the report context: RR-02 adds `area_count`. In `status.py`, make `load_status_rules` require blocks for exactly the assessed workloads and `evaluate` iterate them; leave `licence_finding_types`, `licences.py` and every other use of `workload_ids` unchanged. In `mappings.py`, refuse a mapping in which an unassessed workload is not in `no_function` (field `no_function`); the mapping files keep `no_function: [licences]`.

    Licence evidence stays visible (C2, T-RR-16). Before changing any licence test, run the licence tests and note which reason codes they read from the Licences row. In the found section's licence block, add the inventory's coverage gap (through `reason_detail`, only when coverage is partial or unknown and no other reason is shown) and render the block when the scan has no licence inventory, with the Unknown provenance word and a reason (use an existing reason code such as `not_in_scan`; add none). Keep every existing hook in that block. Every reason code a test used to find on the Licences row must now be found in the found section (`report_section(html, "found")` from `tests/helpers.py`), or on the areas that read licence signals.

    Categories (UI-SPEC 2.2, without `contracts_costs`). Add a top-level `categories` list between `workloads` and `findings` with the five entries of the spec's table in order, each with `id` and `label` (`category.<id>`), and give every assessed workload its `category` (14 entries; the spec's `copilot` row arrives with Phase 1.1). Add a small frozen dataclass for a category and a `categories` tuple on the catalogue; `_parse_catalogue` accepts exactly the top-level keys `workloads`, `categories`, `findings` and `codes`; category ids use `_CODE`; `_LABEL` admits `category.` next to `workload.` and `finding.`; apply the refusals of the behaviour list with the shared validator's failure codes. Refusing an unused category is planner's discretion (a filter option that can never match is useless); record it in the SUMMARY. Extend `load_catalogue`'s locale label check to the categories. Add a top-level `category` group with the five labels of the spec's table to both locales.

    Report context and template. In `_formatting_context`, expose one mapping workload to category id, one mapping category id to label in the report's language, and the ordered category list for RR-02's filters. In today's readiness row, add `data-category` directly after the optional `data-incomplete` attribute and before `role`, and append the category label to the area cell as a `span` with class `finding-category`. Add no CSS.

    Tests. In `tests/test_model.py`, next to `test_catalogue_refuses_an_unlisted_workload`, add the catalogue refusals. In `tests/test_rules.py`: add the `categories[0].label` case to `test_bad_catalogue_label_exits_with_a_localised_sentence`; add a case to `test_bad_mapping_names_the_file_and_field` that maps a function to `licences`; add the item 11 test "every workload has a registered category and a matching `data-category`" over the assessed workloads, including the copied catalogue with mail moved to `files` (criterion 20); add a test that the status loader refuses a block for `licences` and that no sample report in any language or profile has a Licences readiness row; add a test, per licence gap of the behaviour list, that its reason code appears in the found section. C2 test edits: where a test expects a Licences status (the sample status sets in `tests/test_inputs.py`, the reconciliation checks in `tests/test_simulation.py`, the Licences row reads in `tests/test_evidence_cli.py`), expect the assessed workloads and read licence evidence from the found section; keep every assertion about licence evidence itself. List each edit in the SUMMARY.

    Area count as text. "15 areas" is now wrong wherever it means assessed areas. Change "fifteen areas" / "fünfzehn Bereiche" in `README.md` and `README.de.md` to fourteen / vierzehn, and "15 areas" / "15 Bereichen" on `site/pilots/index.html` and `site/de/pilots/index.html` to 14, each in its existing sentence. Change nothing else in those files.

    Site. Regenerate both site demo reports (`uv run fazit demo --lang <lang> --sample town --profile opendesk --out <fresh temporary directory>`, copy the printed report over `site/demo/<lang>/index.html`). Count the regenerated report's readiness rows by status and update only the tally sentence and the counts in the report-card `img` alt text on both home pages, in their existing wording (the screenshots themselves are RR-05's).
  </action>
  <verify>
    <automated>uv run pytest -q && uv run ruff check . && uv run ruff format --check . && out="$(mktemp -d)" && log="$(mktemp)" && uv run fazit demo --lang en --out "$out" > "$log" && report="$(tail -n 1 "$log")" && test -f "$report" && grep -q 'data-workload="mail" data-status="[a-z_]*"[^>]*data-category="communication"' "$report" && ! grep -q 'data-workload="licences" data-status=' "$report" && grep -q "Licence products found" "$report" && outde="$(mktemp -d)" && logde="$(mktemp)" && uv run fazit demo --lang de --out "$outde" > "$logde" && test -f "$(tail -n 1 "$logde")" && grep -q "Kommunikation" "$(tail -n 1 "$logde")" && uv run python site/check_site.py</automated>
  </verify>
  <acceptance_criteria>
    - `uv run pytest -q` exits 0 and `uv run python site/check_site.py` prints "No errors."
    - `grep -c "assessed: false" src/fazit/rules/findings.yaml` [HEAD=0 EXPECT==1]
    - `grep -c "^  licences:" src/fazit/rules/status.yaml` [HEAD=1 EXPECT==0]
    - `grep -c "^      - id:" src/fazit/rules/status.yaml` [HEAD=31 EXPECT==30]
    - `grep -c "^categories:" src/fazit/rules/findings.yaml` [HEAD=0 EXPECT==1] and `grep -c "^    category: " src/fazit/rules/findings.yaml` [HEAD=0 EXPECT==14]
    - Guard: `grep -c "contracts_costs" src/fazit/rules/findings.yaml` still prints 0 (the category is never added)
    - `grep -c "data-category=" src/fazit/templates/report.html.j2` [HEAD=0 EXPECT==1]
    - `grep -c "All 14 areas in the sample" site/index.html` [HEAD=0 EXPECT==1] and `grep -c "Alle 14 Bereiche im Beispiel" site/de/index.html` [HEAD=0 EXPECT==1]
    - `grep -rci "fifteen areas\|fünfzehn Bereiche\|15 areas\|15 Bereichen" README.md README.de.md site/pilots/index.html site/de/pilots/index.html` prints 0 for each file [HEAD=1 each]
    - The SUMMARY lists every edited existing assertion with its item (UI-SPEC 9 item, or C2) and where each licence gap is now shown
    - Follows DESIGN.md (copy rules for the category labels)
  </acceptance_criteria>
  <done>Licences has no readiness status but keeps all its evidence in view, each assessed area's category travels from the catalogue to the rendered row in both languages, bad catalogue and mapping data is refused with the field named, and every written area count says 14.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: A bilingual next step with its kind on every problem rule, required by the loader, in the report context and shown under the deciding reason</name>
  <files>src/fazit/status.py, src/fazit/rules/status.yaml, src/fazit/rules/findings.yaml, src/fazit/catalogue.py, src/fazit/locales/en.yaml, src/fazit/locales/de.yaml, src/fazit/templates/report.html.j2, tests/test_rules.py, tests/test_model.py, site/demo/en/index.html, site/demo/de/index.html</files>
  <read_first>AGENTS.md ("Words"), DESIGN.md ("Copy"), .planning/report-redesign/REV4-CHANGE-MAP.md ("Interfaces between plans": next-step kind), .planning/research/launch-critique/SYNTHESIS.md (C7), .planning/research/report-usefulness/SYNTHESIS.md (A4, A11, B5), .planning/report-redesign/UI-SPEC.md (section 2.3 "Next step", section 4.1, section 8, section 9 "Honesty" and items 10 and 11), src/fazit/status.py (grep `class StatusRule`, `def _workload_rules`, `def load_status_rules`, `STATUSES`; StatusRule is frozen), src/fazit/validation.py (grep `def bilingual`, `def fields`, `def choice`), src/fazit/rules/status.yaml (every rule and its reason), src/fazit/templates/report.html.j2 (the readiness row's reason cell and the `status_reason` macro), tests/test_rules.py (grep `def test_bad_status_rule_names_the_file_and_field`, `def test_telephony_needs_replacement_or_explicit_non_use`, `def test_disputed_count_blocks_every_workload_that_uses_it`), tests/test_report.py (grep `def test_rendered_text_is_autoescaped`)</read_first>
  <behavior>
    - Every rule of the shipped status file (30 after Task 1) has `next_step` with `kind` and non-empty `en` and `de` texts; `kind` is `clarify` (find out, count, review), `decide` (the organisation must choose) or `replace` (work that only makes sense for a move); each text is one sentence (it ends with a full stop and contains no other ". ", "? " or "! "), differs from the rule's reason, names no target supplier or product, and contains none of the words import, export, Import or Export, because no import command exists yet (C7)
    - A rule without `next_step` is refused with the field `workloads.directory.rules[0].next_step`; without its German text with `workloads.directory.rules[0].next_step.de`; without `kind` with `workloads.directory.rules[0].next_step.kind`; with `kind: fix` with the same field; all name `status.yaml`
    - The ready block takes no `next_step` (Ready has none, UI-SPEC 2.1)
    - Every finding in `rules/findings.yaml` carries `owner`, one of the six role ids (`it_team`, `licence_management`, `service_owner`, `data_protection`, `information_security`, `procurement`), so RR-04 can name the role that closes each open point; the catalogue refuses a missing or unregistered `owner` with the field named
    - Evaluating the town gives telephony a deciding rule whose `next_step.kind` is one of the three kinds; the report context reaches it as `row.deciding.next_step.kind`; nothing renders the kind before RR-04
    - The town demo's telephony row shows "Next step" / "Nächster Schritt" and the `next_step` text of `telephony-no-replacement` in its language; markup in a `next_step` text is escaped
  </behavior>
  <action>
    Rule model and loader. Add `STEP_KINDS = ("clarify", "decide", "replace")` and a small frozen dataclass for a next step (`kind`, and the language-to-text mapping like `reason`) to `status.py`, and a `next_step` field on the frozen `StatusRule` after `reason`. In `_workload_rules`, require `next_step` next to `id`, `when`, `status` and `reason`; read it as a mapping with exactly `kind`, `en` and `de`: `kind` with `reader.choice` against `STEP_KINDS` (field `<rule>.next_step.kind`), the two texts with the same checks as `reader.bilingual` (fields `<rule>.next_step.en` and `.de`). Change nothing in evaluation; `STATUSES` keeps its order. The report context needs no new name: `statuses` already carries each row's deciding rule and notes, so the kind is `row.deciding.next_step.kind` (REV4-CHANGE-MAP, next-step kind interface).

    The sentences (status.yaml). Add `next_step` directly after each rule's `reason`, in this shape:

    ```yaml
        next_step:
          kind: clarify
          en: The IT team lists every system that sends mail through the organisation's account and plans a new sending route for each.
          de: Die IT-Abteilung erfasst alle Systeme, die über das Konto der Organisation E-Mails versenden, und plant für jedes einen neuen Versandweg.
    ```

    Draft each from that rule's reason: one sentence naming the action and who typically owns it, using one owner from this set consistently: the IT team / die IT-Abteilung; licence management / die Lizenzverwaltung; the service owner (the department that relies on the service) / die fachlich verantwortliche Stelle; the data protection officer / die oder der Datenschutzbeauftragte; the information security officer / die oder der Informationssicherheitsbeauftragte; procurement / die Beschaffung. Set `kind` per sentence from the action it names, not per rule type or status (usefulness A11): counting, listing, reviewing or asking is `clarify`; a choice the organisation must make (keep, give up, accept a limit) is `decide`; planning or building a replacement, a new route or a conversion that only makes sense for a move is `replace`. If a sentence names two actions of different kinds, rewrite it to name one. Rules for every sentence: no target supplier or product and no recommendation; no effort estimate, date or deadline; avoid Microsoft product names where the area name already says it; no "score", "verdict", "recommended", "best", "safe" or "easy"; "move" / "Umstieg"; status names exactly as in UI-SPEC section 8; never point to a command or an import this version does not have (C7): name actions a person can take today; no abbreviations with full stops ("zum Beispiel", not "z. B."). Keep the YAML style of the file. RR-06 rewords the Windows-software rule for C6 and adds rules; they follow the same rules and carry `kind`.

    Owner role per finding (for RR-04's open points, usefulness A4). In `rules/findings.yaml`, give every finding an `owner` with one of the six role ids, taken from the person `docs/interview-checklist.md` names for that question, mapped to the nearest of the six roles (the IT lead and measured admin-centre figures: `it_team`; licence questions: `licence_management`; a department that relies on the service: `service_owner`; retention and protection: `information_security` or `data_protection` as the question says; contracts: `procurement`). In `catalogue.py`, read `owner` with `reader.choice` against a `ROLES` tuple of the six ids (field `findings.<id>.owner`) onto the finding entry. The `role.*` locale group of Task 3 labels the ids. RR-04 derives a collector's open point from its findings' owner and an Unknown area's from its first missing finding. Record the owner of every finding in the SUMMARY table so the maintainer can check it against the checklist. In `tests/test_model.py`, add the refusal case next to the category refusals.

    Show it. Add `readiness.next_step` ("Next step" / "Nächster Schritt") to both locales. In today's readiness reason cell, after the deciding rule's reason, render a paragraph with class `finding-next` with the label in `strong` and the deciding rule's `next_step` text in the report's language, only when a rule decided the row. Add no data attribute for the kind (RR-04 adds `dd[data-step-kind]` in `path`). RR-02 moves the paragraph onto the card.

    Tests (UI-SPEC 9 items 10 and 11). In `tests/test_rules.py`: the four cases of the behaviour list in `test_bad_status_rule_names_the_file_and_field`; the test "next_step in both languages on all problem rules" over the loaded rule set with every check of the behaviour list; the test "every next step has a kind" (one of `STEP_KINDS`, and the town's telephony row exposes it through `evaluate`); the town telephony row shows its next step in both languages; a copied `status.yaml` whose telephony `next_step.en` contains `<b>` renders it escaped. Give the hand-built rule in `test_disputed_count_blocks_every_workload_that_uses_it` a `next_step` with `kind` (item 10).

    Native-German review. In the SUMMARY, add a table with one row per rule id: kind, the English and the German `next_step`, and the verb that justifies the kind. Regenerate both site demo reports as in Task 1.
  </action>
  <verify>
    <automated>uv run pytest tests/test_rules.py tests/test_locales.py -q && uv run pytest -q && uv run ruff check . && uv run ruff format --check . && uv run python -c 'from fazit.catalogue import load_catalogue; from fazit.status import load_status_rules; rules = [rule for block in load_status_rules(load_catalogue()).workloads.values() for rule in block.rules]; banned = ("opendesk", "nextcloud", "collabora", "keycloak", "nubus", "element", "jitsi", "open-xchange", "openproject", "libreoffice", "univention", "xwiki", "cryptpad", "import", "export"); bad = [rule.id for rule in rules for text in rule.next_step.text.values() if any(word in text.lower() for word in banned)]; kinds = {rule.next_step.kind for rule in rules}; assert rules and not bad and kinds <= {"clarify", "decide", "replace"}, (bad, kinds)' && out="$(mktemp -d)" && log="$(mktemp)" && uv run fazit demo --lang de --out "$out" > "$log" && report="$(tail -n 1 "$log")" && test -f "$report" && grep -q "Nächster Schritt" "$report" && uv run python site/check_site.py</automated>
    <human-check>Native-German review of the German `next_step` sentences and of each kind, run by the maintainer after this plan (the SUMMARY table lists them). Until then the German text is a draft.</human-check>
  </verify>
  <acceptance_criteria>
    - `uv run pytest -q` exits 0 and `uv run python site/check_site.py` prints "No errors."
    - `grep -c "next_step:" src/fazit/rules/status.yaml` [HEAD=0 EXPECT==30], equal to the number of rules
    - `grep -cE "^          kind: (clarify|decide|replace)$" src/fazit/rules/status.yaml` [HEAD=0 EXPECT==30]
    - The import check in `<verify>` (adjust the attribute name if you named the text mapping differently, and record it) finds no target product, import or export word in any `next_step`, and only the three kinds
    - The SUMMARY contains the review table of all rules with their kinds, and the owner of every finding
    - `uv run python -c 'from fazit.catalogue import load_catalogue; c = load_catalogue(); print(all(f.owner for f in c.findings))'` prints True (adjust to the catalogue's real attribute names and record them)
    - Follows DESIGN.md ("Copy": British English, native formal German, the same word for the same thing)
  </acceptance_criteria>
  <done>Every problem rule carries a bilingual one-sentence next step that a person can act on today and a kind taken from its action, the loader refuses a rule without either, the kind is reachable per row for RR-04, the town report shows the step, and the German drafts are listed for review.</done>
</task>

<task type="auto">
  <name>Task 3: The copy of UI-SPEC section 8 (revision 4.1) and of the launch critique in both locales, the ban-list test, and the D-81 amendment</name>
  <files>src/fazit/locales/en.yaml, src/fazit/locales/de.yaml, tests/test_locales.py, .planning/phases/01.1-ai-assistants-and-decision-window/01.1-CONTEXT.md, site/demo/en/index.html, site/demo/de/index.html</files>
  <read_first>AGENTS.md ("Words"), DESIGN.md ("Copy"), .planning/report-redesign/REV4-CHANGE-MAP.md (first row of "Who owns what" and the revision 4.1 table), .planning/report-redesign/UI-SPEC.md (section 8 in full; sections 1.2, 3, 3.3, 4.1 and 5 for where each string appears; section 9 "Decisions to record when this is built"), .planning/research/report-usefulness/SYNTHESIS.md (A7, A12, A14), .planning/research/launch-critique/SYNTHESIS.md (B7 and C2, C7), .planning/research/launch-critique/CRITIC-astra.md (the "Published sample report" table), src/fazit/locales/en.yaml, src/fazit/locales/de.yaml (the `reason` group with every `fix`, the `costs` group with `input_fields`, `groups`, `line_items` and `formulas`, the `provenance` group, the `path` group), tests/test_locales.py (grep `def flatten_keys`, `def test_locale_key_parity`, `def test_catalogue_labels_and_reason_codes_have_translations`, `def test_template_uses_locale_for_visible_text`), .planning/phases/01.1-ai-assistants-and-decision-window/01.1-CONTEXT.md, site/check_site.py (grep `def check_demo_reports`)</read_first>
  <behavior>
    - Every key of UI-SPEC section 8 (revision 4.1) exists in both locales with the spec's wording; existing keys keep their names and change only their values; new top-level groups are `summary`, `filter`, `nav` and `role`
    - The cost formulas say "move scenario" and "Umstiegsszenarien"; no "exit" or "Ausstieg" remains in either locale's values
    - The German `mapping_coverage` values for `in_suite`, `in_suite_with_limits` and `open_source_community` read as section 8 gives them; the German `readiness.evidence_summary` uses the report's provenance words "erhoben" and "bereitgestellt"
    - `summary.define.ready` reads "The current checks found no blocker and no missing evidence." with a German counterpart (C2); the status names stay exactly Ready, Needs work, Blocker, Unknown / Bereit, Handlungsbedarf, Hindernis, Unbekannt
    - No reason `fix` in either locale contains the words import, export, Import or Export (C7)
    - No locale value and no `status.yaml` text contains score, verdict, recommended, recommendation, best, safe, easy or saving (whole words, any case), or Urteil, Empfehlung or empfohlen (as word beginnings, any case); a test in `tests/test_locales.py` checks both
    - 01.1-CONTEXT.md carries the D-81 amendment adjusted for Licences having no card and for the area count, and nothing else there changes
    - The locale parity test passes; `site/demo/*` equal fresh demo runs and `site/check_site.py` passes
  </behavior>
  <action>
    Locales (UI-SPEC section 8, revision 4.1). Apply every row of the table to both files, using the spec's English and German exactly, with these keys:
    - Changed values: `header.title`, `readiness.title`, `costs.title`, `costs.partial_exit`, `costs.full_exit`, `moves.title`, `attention.title`, `path.title`, `found.title` ("What Fazit recorded" / "Was Fazit erfasst hat"), `appendix.title`, and the three German `mapping_coverage` values.
    - Productivity loss (section 3, "internal estimate, not a payment"): `costs.groups.productivity_loss`, `costs.line_items.productivity_loss` and `costs.input_fields.productivity_loss` all take "Lost working time (internal estimate, not a payment)" / "Verlorene Arbeitszeit (interne Schätzung, keine Zahlung)", and the productivity sentence of `costs.formulas` names "lost working time" / "verlorene Arbeitszeit". Using one value for all three is planner's discretion (one word for one thing); record it.
    - New `summary`: `title`, `of_areas`, `blockers` ("What blocks this move"), `confirmed`, `all_blockers`, `caveat`, `unknown`, `not_examined` ("All open points"), `define.blocker`, `define.needs_work`, `define.unknown`, `define.ready` (C2's Ready definition without the status name: "The current checks found no blocker and no missing evidence." / "Die aktuellen Prüfungen haben kein Hindernis und keine fehlenden Nachweise ergeben."; this replaces the separate `summary.ready_definition` of earlier drafts), `scope_title`, `scope_of`, `scope_needed`, `scope_unknown` (placeholders `{profile}` and `{n}` as in the spec; RR-07 builds the data, RR-03 renders it).
    - New in existing groups: `readiness.evidence_summary` (German "Nachweise · {measured} erhoben, {provided} bereitgestellt, {unknown} unbekannt"), `readiness.all_replacements`; `costs.total_label`, `costs.stay_basis`, `costs.comparison_unknown`, `costs.stay_assumption` ("Staying assumes no price change." / "Für den Verbleib ist keine Preisänderung angenommen."), `costs.break_even` and `costs.break_even_none` (placeholders `{scenario}`, `{amount}`, `{entered}` exactly as the spec), `costs.vat_note`, `costs.profile_note`, `costs.less`, `costs.more`, `costs.same`, `costs.sub_cent`, `costs.total_unknown`, `costs.known_blocks`, `costs.inputs_missing`, `costs.missing_fix`; `path.even_if_staying`, `path.for_move`; `appendix.not_looked`, `appendix.not_looked_text`.
    - New `filter`: `status_legend`, `category_legend`, `all`, `all_categories`, `empty`, `search_hint` ("Filtered-out areas and, in some browsers, closed sections are not searched." / "Ausgeblendete Bereiche und, je nach Browser, geschlossene Abschnitte werden nicht durchsucht.").
    - New `nav`, in section order: `summary`, `next_steps`, `areas`, `costs`, `replacements`, `closer_look`, `appendix`.
    - Cost formulas: "exit scenario" becomes "move scenario" and "Ausstiegsszenarien" becomes "Umstiegsszenarien", with the German sentence adjusted.

    Copy that section 8 implies but does not list, drafted now so the German review covers it in one pass (record each in the SUMMARY as planner's discretion): `nav.label` ("Report sections" / "Abschnitte des Berichts"); `nav.skip` ("Skip to content" / "Zum Inhalt springen"); singular forms `summary.caveat_one` ("{n} area is Unknown or has incomplete evidence, so a Blocker cannot be ruled out.") and `costs.inputs_missing_one` ("{n} input is missing"), following the `units` and `unit_one` precedent; `moves.status_link` ("{area}: {status}", section 4's `aria-label`); a new value for `moves.workload_status` ("Area status" / "Status des Bereichs", section 4's column); and a `role` group with the six owner roles of Task 2 (`it_team`, `licence_management`, `service_owner`, `data_protection`, `information_security`, `procurement`, as short labels: "IT team" / "IT-Abteilung" and so on) for the owner role of each open point (UI-SPEC 4.1, used by RR-04). Placeholders must match between languages. Do not add `path.needs_work` or a new `path.unknown`: revision 4 removed the status timeline they were for.

    Reason fixes (C7). Rewrite every `reason.*.fix` that asks the reader to supply an export, import one, check an export, or rebuild from an export (today `not_in_export`, `source_not_supplied`, `needs_recipient_export`, `licence_plan_list_incomplete` and `not_recognised`; re-check with grep), so it names what a person can do today (for example ask the service owner and enter the answer in the inputs file, or note that this version keeps the figure Unknown); the reason labels may still say that an export would establish the figure. These fixes become the next steps of Unknown cards and the "what closes it" of open points (UI-SPEC 2.3, 4.1).

    Tests. In `tests/test_locales.py`, add: a test that no `fix` in either locale contains import, export, Import or Export; and the ban-list test of the behaviour list over every flattened value of both locales (reuse `flatten_keys`) and every `reason` and `next_step` text of the loaded status rules. If an existing value trips the ban list, reword the value; never narrow the list.

    D-81 amendment (UI-SPEC section 9, adjusted by C2). In `01.1-CONTEXT.md`, directly below the D-81 bullet, add a bullet "D-81 amendment (report redesign, 2026-11-22)": area cards are grouped by status; inside a group they keep catalogue order; Licences, first in the catalogue, has no readiness status since the launch critique, so Copilot is the first card of whichever status group it is in; in the category filter Copilot is first under Automation and AI; it stays second in the catalogue and first in the replacements table; the report sorts a display copy and never reorders `STATUSES`; because Licences is no longer assessed, the counts D-81 names become 15 assessed areas when the phase ships (14 before), and the figure tile reads "15 areas assessed, from AI agents to mail" / "15 Bereiche, von KI-Agenten bis E-Mail". Change nothing else in that file.

    Regenerate both site demo reports as in Task 1. If a test fails only because a value changed, follow the locale (UI-SPEC 9 item 9) and list it.
  </action>
  <verify>
    <automated>uv run pytest -q && uv run ruff check . && uv run ruff format --check . && outen="$(mktemp -d)" && logen="$(mktemp)" && uv run fazit demo --lang en --out "$outen" > "$logen" && test -f "$(tail -n 1 "$logen")" && grep -q "What leaving Microsoft 365 would take" "$(tail -n 1 "$logen")" && outde="$(mktemp -d)" && logde="$(mktemp)" && uv run fazit demo --lang de --out "$outde" > "$logde" && test -f "$(tail -n 1 "$logde")" && grep -q "Was ein Umstieg von Microsoft 365 erfordert" "$(tail -n 1 "$logde")" && uv run python site/check_site.py</automated>
    <human-check>Native-German review of every German value added or changed in this plan, run by the maintainer together with the next steps.</human-check>
  </verify>
  <acceptance_criteria>
    - `uv run pytest -q` exits 0 and `uv run python site/check_site.py` prints "No errors."
    - `grep -ci "ausstieg" src/fazit/locales/de.yaml` [HEAD=3 EXPECT==0]
    - `grep -ci "exit scenario\|partial exit\|full exit" src/fazit/locales/en.yaml` [HEAD=3 EXPECT==0]
    - `grep -c "^nav:\|^summary:\|^filter:\|^role:" src/fazit/locales/en.yaml` [HEAD=0 EXPECT==4], and the same for `de.yaml`
    - `grep -c "break_even\|stay_assumption\|scope_unknown\|even_if_staying\|not_looked_text" src/fazit/locales/en.yaml` [HEAD=0 EXPECT>=6]
    - `grep -c "erhoben, {provided} bereitgestellt" src/fazit/locales/de.yaml` [HEAD=0 EXPECT==1]
    - `grep -c "ready_definition" src/fazit/locales/en.yaml` [HEAD=0 EXPECT==0] (folded into `summary.define.ready`)
    - `grep -c "D-81 amendment" .planning/phases/01.1-ai-assistants-and-decision-window/01.1-CONTEXT.md` [HEAD=0 EXPECT==1]
    - The SUMMARY's native-review table lists every German value added or changed, with its English counterpart
    - Follows DESIGN.md ("Copy")
  </acceptance_criteria>
  <done>Both locales carry the redesign's and the launch critique's copy with unchanged key names, no fix points to an import, banned words are tested, the D-81 amendment is recorded, and the site's sample reports match the package.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| rule, catalogue and mapping YAML → report | Consultants edit these files; their text is printed into the report |
| next step and copy → the reader's decision | An action sentence can read as advice, as a supplier recommendation, as a verdict or as a promise of a feature |

## STRIDE Threat Register

Security level: ASVS 1. Blocking threshold: high.

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-RR-01 | Tampering | `status.yaml` `next_step`: markup in a rule text | low | mitigate | Autoescape covers every expression (`test_rendered_text_is_autoescaped`); Task 2 adds an escaped-markup case for `next_step` |
| T-RR-02 | Repudiation | `next_step`, its kind or a fix that names a supplier, gives a verdict or points to a missing command | medium | mitigate | Drafting rules in Task 2; product, import and export checks in Tasks 2 and 3; the ban-list test in Task 3; the maintainer's review of sentences and kinds |
| T-RR-03 | Tampering | `findings.yaml` or a mapping: a bad category or assessed flag silently drops an area | medium | mitigate | The catalogue refuses missing, unregistered, unused and misplaced categories; the status loader checks blocks against the assessed areas; the mapping loader refuses a function on an unassessed area (Task 1) |
| T-RR-16 | Repudiation | Licences without status hides a licence gap | medium | mitigate | Every licence gap stays visible in the found section's licence block or on the areas that read licence signals, one test per gap; licence tests keep their evidence assertions (Task 1) |
| T-RR-SC | Tampering | package installs | high | mitigate | This plan installs nothing and adds no dependency |
</threat_model>

<verification>
Before declaring the plan complete:
- [ ] `uv run ruff check .` and `uv run ruff format --check .` exit 0
- [ ] `uv run pytest -q` exits 0
- [ ] `uv run fazit demo --lang de` and `uv run fazit demo --lang en`, each into a fresh temporary directory, exit 0 and the printed path exists
- [ ] `uv run python site/check_site.py` prints "No errors."
- [ ] `STATUSES` and the cost model are unchanged
</verification>

<success_criteria>
- Licences carries no move-readiness status and loses no evidence
- Categories and next steps with their kinds are data, validated on load and visible in the report or its context
- The section 8 (revision 4.1) and launch-critique copy exists in both locales, guarded by the ban list; the area count is right wherever it is written; the D-81 amendment is recorded
- The German drafts are listed for the maintainer's native review
</success_criteria>

<output>
Create `.planning/report-redesign/RR-01-SUMMARY.md` when done. Record: the final signatures of the category dataclass, the workload entry, the next-step dataclass and `StatusRule`, and the name of the assessed-workloads property; the context names the template now reads; where each licence gap is now shown; the review table of all next steps (kind, English, German, the verb behind the kind) and of every German value added or changed, with both languages; the planner's-discretion items you implemented; every edited existing assertion with its item; the regenerated town counts written to the home pages; helpers found moved; the test count and runtime of `uv run pytest -q`.
</output>

## Source coverage for the plan set

Run order: RR-01, RR-06, RR-07, RR-02, RR-03, RR-04, RR-05. Owners follow `REV4-CHANGE-MAP.md` (including its revision 4.1 table); a plan that does not own a change only relies on it.

| Source | Item | Plan | Status |
|--------|------|------|--------|
| SPEC 0, 1 | Findings first, no verdict; ten sections, `SECTION_ORDER` with `path` third; display order Blocker, Needs work, Unknown, Ready on a copy, `STATUSES` untouched | RR-03 (order), RR-02 (display order of cards) | COVERED |
| SPEC 1.1 | Header with `.page-intro`, meta row, sample note; local and offline sentences in run details | RR-04 | COVERED |
| SPEC 1.2 items 1-3 | `dl.status-summary` with "Of {n}" from the catalogue, counts and definitions, no bar; blockers with conditional count line and "All blockers"; unknowns with "All open points" before the costs | RR-03 (copy: RR-01) | COVERED |
| SPEC 1.2 item 4 | Scope statement after the unknowns: data | RR-07 | COVERED |
| SPEC 1.2 item 4 | Scope statement: rendering | RR-03 (copy: RR-01) | COVERED |
| SPEC 1.2 item 5, 3.3 | Three totals in whole units, Stay basis, Comparison unknown, Stay assumption, break-even (town full move EUR 39,130) | RR-03 (copy: RR-01) | COVERED |
| SPEC 1.2 item 6 | Decision-window tiles | Phase 1.1 ("absent before"); RR-05 lists the Phase 1.1 steps | COVERED by hand-over |
| SPEC 1.2 page one | Header and summary fill A4 page one for town, non-profit and all-Unknown, both languages; all-Unknown fixture | RR-03 (fixture), RR-04 (print breaks), RR-05 (real-PDF check) | COVERED |
| SPEC 2, 2.1, 2.3, 2.4 | Cards with the area name as anchor, readiness bar above the filters as their visual, evidence disclosure, provenance sentence; target line with a needed gap first | RR-02 (gap data `row.transfer_gaps`: RR-07) | COVERED |
| SPEC 2.2 | Filters without script; categories (five, after C2) | RR-01 (categories), RR-02 (filters) | COVERED |
| SPEC 2.3 | `next_step` with `kind` on every problem rule, required by the loader, reachable per row | RR-01 (Task 2); RR-06 for the rules it adds or rewords; RR-07 for its two `target_gaps` templates | COVERED |
| SPEC 3 | Chart from known totals, no bar on an unknown total, table, missing inputs, cost inputs, intro, profile and VAT notes, productivity-loss label | RR-03 (copy: RR-01; deleting the old `table:not(.cost-table)` rules: RR-04, once the other tables use `.coverage`) | COVERED |
| SPEC 4.1 | "What to do next": `clarify`/`decide` steps, then open points under "Evidence still needed" grouped by the evidence requested, with owner role; `replace` steps under "Needed for a move"; timeline, pilot sentences and stock steps removed | RR-04 (copy, role labels and finding `owner`: RR-01; kinds: RR-01, RR-06, RR-07) | COVERED |
| SPEC 4, 5, 6, 7 | Remaining sections, "What Fazit does not look at", navigation in section order, `circle` coverage symbol, tokens and components, phone and print | RR-04 (copy: RR-01), RR-05 (design checks) | COVERED |
| SPEC 8 | Copy in both locales, revision 4.1; ban list | RR-01 (Task 3) | COVERED |
| SPEC 9, 11 | Hooks kept; permitted edits; decisions; acceptance criteria | RR-01 to RR-07; RR-05 | COVERED |
| CRITIQUE C1 | Readiness takes the target profile into account; never Blocker on an undocumented transfer alone | RR-07 alone (engine and scope-statement data); no card wording in RR-02 | COVERED |
| CRITIQUE C2 | Licences without status; deeper Ready rules (Teams, SharePoint); Ready definition on page one | RR-01 (Licences, copy), RR-06 (rules), RR-03 (definition shown) | COVERED |
| CRITIQUE C3 | Windows subtotal larger than the device total is caught (drop what D31 in `acf9be9` already covers) | RR-06 | COVERED |
| CRITIQUE C4 | `.xls` and legacy macro-capable formats among risky file types | RR-06 | COVERED |
| CRITIQUE C5 | openDesk XWiki, CryptPad, Notes; specific citations; "Direct transfer undocumented"; mapping files marked unreviewed | RR-07 | COVERED |
| CRITIQUE C5 answers | Interview fields for SharePoint workflows and VBA | RR-06 | COVERED |
| CRITIQUE C6 | Windows desktop need stays Unknown unless answered; no Needs work reason says "blocks" / "Hindernis", with a test | RR-06 | COVERED |
| CRITIQUE C7 | No fix or next step points to a missing command; open evidence in decided areas listed; generated "What to do next" instead of the stock sequence | RR-01 (fixes, next steps), RR-04 (open points) | COVERED |
| CRITIQUE C8 | No confident saving on invented prices: three totals with origin and a break-even line | RR-03 (copy: RR-01) | COVERED |
| CRITIQUE C9 | `docs/scan-format.md` with one minimal example | RR-06 | COVERED |
| CRITIQUE A3 | "Simulated" in sample runs; fictional inventory heading | RR-06 | COVERED (README text: coordinator) |
| USEFULNESS A1, A7, C8, C13 | No verdict wording; scoped blocker heading; status name Blocker kept; ban list | RR-01 (copy, ban list), RR-03 (summary goal and must-haves) | COVERED |
| USEFULNESS A2, C2 | Page one for the council, same on screen and in print; OUTP-03 pulled into the redesign | RR-03, RR-04, RR-05 (decision and ROADMAP note) | COVERED |
| USEFULNESS A3, C6 | Three totals, Stay assumption, break-even now; VAT and staff time later | RR-03 (copy: RR-01) | COVERED |
| USEFULNESS A4, A11 | One open-points list after the summary; steps classified by kind | RR-04; RR-01 (kinds, owner roles), RR-06 and RR-07 (kinds of their rules) | COVERED |
| USEFULNESS A5 | Coverage symbol no status uses (`circle`) | RR-04 (icon), RR-05 (check) | COVERED |
| USEFULNESS A6, C4 | Scope statement after RR-06 and RR-07; operator review of mappings before ship | RR-07, RR-03; RR-05 lists the gate | COVERED |
| USEFULNESS A8, C5 | "Of n" from the assessed catalogue; Licences inventory only; D21 and RULE-02 amended | RR-01 (catalogue, written counts), RR-03, RR-05 (decisions) | COVERED |
| USEFULNESS A9 | Unfavourable report designed and checked (non-profit, all-Unknown) | RR-03, RR-05 | COVERED |
| USEFULNESS A10, C3 | No bar on page one; bar only as the filters' visual | RR-02, RR-03 | COVERED |
| USEFULNESS A12 | Costs print as a unit; productivity loss labelled; VAT not stated | RR-03, RR-04 (copy: RR-01) | COVERED |
| USEFULNESS A13 | One council reader before RR-02 | RR-05 lists the founder action | COVERED by follow-up (not a build criterion) |
| USEFULNESS A14 | "What Fazit does not look at"; legal procedures named, not cited | RR-04 (copy: RR-01) | COVERED |
| Founder | Report-card screenshots show the redesigned first screen in light and dark, desktop and phone, EN and DE; alt text and caption match | RR-05 (RR-01 updates only the alt-text counts) | COVERED |
| CONTEXT | D-81 (amended, area count adjusted), D-19, D-21, D-26, D-59, D-61, D-64 (departures recorded), D-80, D-90 (Phase 1.1) | RR-01, RR-05 | COVERED |
| REQ | RULE-02, RULE-03, COST-03, OUTP-03, REPT-01 to REPT-05, I18N-01, I18N-02, SAFE-04 | RR-01 to RR-07 | COVERED |
| Coordinator | DESIGN.md in every task's `read_first`; at most three tasks and one executor run per plan; design checks in `check_site.py` and the report tests; plans based on current `main` (172f278 or later) with every symbol re-checked | RR-01 to RR-07; RR-05 Task 1 | COVERED |

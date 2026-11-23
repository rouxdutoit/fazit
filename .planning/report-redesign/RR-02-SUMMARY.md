---
phase: report-redesign
plan: "02"
subsystem: report
tags: [readiness, area-cards, evidence, offline-filters]
requires:
  - phase: RR-01
    provides: Assessed areas, catalogue categories and bilingual rule actions
  - phase: RR-06
    provides: Simulated evidence labels and the fictional inventory heading
  - phase: RR-07
    provides: Target-aware readiness, transfer gaps and scope data
provides:
  - Assessed-area cards grouped by status
  - Evidence disclosures, provenance sentences and target lines
  - Keyboard-operable status and category filters
affects: [RR-03, RR-04, RR-05]
actuals:
  tasks: 3
  commits: 0
tech-stack:
  added: []
key-files:
  created: [.planning/report-redesign/RR-02-SUMMARY.md]
  modified:
    - src/fazit/report.py
    - src/fazit/templates/report.html.j2
    - src/fazit/locales/en.yaml
    - src/fazit/locales/de.yaml
    - site/check_site.py
    - site/demo/en/index.html
    - site/demo/de/index.html
    - tests/report_expectations.py
    - tests/helpers.py
    - tests/test_report.py
    - tests/test_cli.py
    - tests/test_evidence_cli.py
    - tests/test_inputs.py
    - tests/test_rules.py
    - tests/test_simulation.py
key-decisions:
  - The status filters show the distribution by count.
  - The target line prioritises confirmed needs from the evaluated transfer gaps.
  - A linked card is visible with its heading under both filters.
requirements-completed: [REPT-02, REPT-04, REPT-05, RULE-03]
coverage:
  - id: D1
    description: Each assessed area has one named card in its status group.
    requirement: REPT-02
    verification:
      - kind: integration
        ref: tests/test_report.py#test_readiness_cards_keep_status_order_and_show_the_area_and_action
        status: pass
    human_judgment: false
  - id: D2
    description: Cards show evidence with provenance and keep incomplete evidence visible.
    requirement: RULE-03
    verification:
      - kind: integration
        ref: tests/test_report.py#test_card_disclosures_count_each_observation_once
        status: pass
      - kind: integration
        ref: tests/test_simulation.py#test_incomplete_required_evidence_prevents_ready
        status: pass
    human_judgment: false
  - id: D3
    description: Target lines put needed transfer gaps first.
    verification:
      - kind: integration
        ref: tests/test_report.py#test_needed_teams_chat_history_comes_first_on_the_card
        status: pass
    human_judgment: false
  - id: D4
    description: The keyboard filters work at phone and desktop widths in both colour schemes, and print includes every card.
    requirement: REPT-04
    verification:
      - kind: automated_ui
        ref: node .shots/report-redesign/check.mjs <report-directory> --only filters
        status: pass
    human_judgment: false
  - id: D5
    description: Each card and status option pairs the status text with its symbol.
    requirement: REPT-05
    verification:
      - kind: integration
        ref: tests/test_report.py#test_readiness_cards_keep_status_order_and_show_the_area_and_action
        status: pass
      - kind: integration
        ref: tests/test_report.py#test_readiness_filters_use_the_card_counts_and_catalogue
        status: pass
    human_judgment: false
completed: 2026-11-22
status: complete
---

# RR-02 summary

Fazit shows each assessed area as a card with its reason, evidence and relevant replacements. Readers can narrow the list with two keyboard-accessible filters in the offline report. The filter labels give the status counts.

All three tasks ran in order. The run resumed the Task 1 implementation in the working tree at `6bde931` and verified it before starting Task 2. The final working tree contains both regenerated town openDesk demos and the ignored Playwright check.

## Changes by task

| Task | Files | Changes |
| --- | --- | --- |
| 1 | `src/fazit/report.py`, `src/fazit/templates/report.html.j2` | Added a report display order and the assessed-area count. Applied the site frame and tokens, replaced the readiness table with grouped cards and removed the bar and legend. Unknown cards show the evidence reason and fix separately. |
| 1 | `src/fazit/locales/en.yaml`, `src/fazit/locales/de.yaml` | Removed the two table labels. |
| 1 | `tests/report_expectations.py`, `tests/helpers.py`, `tests/test_report.py`, `tests/test_cli.py`, `tests/test_inputs.py`, `tests/test_rules.py`, `tests/test_simulation.py` | Added the display-order expectation, the shared card-order check and the four bilingual sample cases. Migrated the assertions listed below. |
| 1 | `site/check_site.py`, `site/demo/en/index.html`, `site/demo/de/index.html` | Counted cards for the home-page tally and regenerated both demos. |
| 2 | `src/fazit/report.py`, `src/fazit/templates/report.html.j2` | Used the same evidence table in each assessed card and in the Licences disclosure in recorded inventory. Added closed disclosure counts, a provenance sentence, compact Ready cards and target lines that prioritise confirmed needs. |
| 2 | `src/fazit/locales/en.yaml`, `src/fazit/locales/de.yaml`, `tests/test_report.py`, `tests/test_cli.py`, `tests/test_evidence_cli.py`, `site/demo/en/index.html`, `site/demo/de/index.html` | Removed five retired inventory keys, checked disclosure counts and target order and migrated evidence assertions to their new locations. Regenerated both demos. |
| 3 | `src/fazit/templates/report.html.j2`, `tests/test_report.py`, `site/demo/en/index.html`, `site/demo/de/index.html`, `.shots/report-redesign/check.mjs` | Added the two radio groups, screen-only filter rules and the empty state. Verified keyboard use, focus, links and print in Chromium. Regenerated both demos. |

## Report context

| Name | Shape and source |
| --- | --- |
| `status_groups` | `list[tuple[str, tuple[WorkloadStatus, ...]]]` for populated statuses. Each group preserves catalogue order. |
| `status_counts` | `list[tuple[str, int]]` including zero counts. This and `status_groups` use Blocker, Needs work, Unknown, Ready. |
| `area_count` | `int` from `len(catalogue.assessed_workload_ids)`. |
| `catalogue_evidence` | `dict[str, list[tuple[FindingEntry, Finding]]]` keyed by workload, using catalogue order. |
| `inventory_workloads` | `tuple[str, ...]` of unassessed catalogue workload IDs, currently Licences. |
| `evidence_counts` | `dict[str, dict[str, int]]` keyed by workload, then by `measured`, `provided` and `unknown`. It counts the primary observation once per finding ID across both displays, and each displayed competing observation once. |
| `target_functions` | `dict[str, tuple[FunctionMapping, ...]]` keyed by assessed workload. Functions whose `row.transfer_gaps` need is `yes` move first in mapping order. The line takes the first two. |

`STATUSES` retains the rule engine’s order. The `scope_statement` supplied by RR-07 remains available to RR-03. The shared `readiness_row`, `report_section`, `rebuild_report` and sample path helpers live in `tests/helpers.py`. The new `assert_readiness_order` helper checks the populated group order, order within each group and exactly one card per assessed workload.

## Existing assertions migrated

| Test or checker | Basis | Change |
| --- | --- | --- |
| `tests/helpers.py::readiness_row` | UI-SPEC §9 item 2 | Matches the article and its closing tag. Existing callers keep the shared helper. |
| `tests/test_cli.py::test_report_shows_function_mapping_and_workload_evidence` | §9 item 2 | Reads the same status from the article start tag. |
| `tests/test_cli.py::test_scan_only_report_explains_readiness_and_missing_evidence` | §9 items 2, 3 and 4 and Task 1 caption amendment | Reads articles, checks order within groups and counts cards in display order. It checked the sample caption in `found` during Task 1 and checks it in `readiness` after Task 2. |
| `tests/test_cli.py::test_sample_reports_label_simulated_measurements_and_fictional_inventory` and `test_scan_format_example_has_no_sample_labels` | Task 1 heading amendment | Both heading matches include `class="sec-label"`. |
| `tests/test_cli.py::test_sample_measurement_labels_and_directory_note` | §9 item 5 | Reads the directory note inside `readiness`. The assertions on simulated tables and captions still apply. |
| `tests/test_inputs.py::test_sample_inputs_and_rendered_statuses` and `test_software_list_escapes_names_and_shows_confirmed_and_missing_answers` | §9 item 2 | Reads the same status and evidence from articles. |
| `tests/test_rules.py::test_demo_rows_show_the_categories_of_assessed_workloads` | Task 1 category amendment and §9 item 3 | Uses the shared group order check. The category checks apply to every area. |
| `tests/test_simulation.py::_statuses` | §9 items 2 and 3 | Reads articles and checks the group and within-group order for generated tenants. |
| `tests/test_evidence_cli.py::test_measured_positive_count_cannot_be_overridden_by_zero` | §9 item 6 | Checks the same conflict and ordered measured and provided values in the single rule-evidence record for `integrations.application_count`. The status, completeness and precedence assertions still apply. |
| `tests/test_evidence_cli.py::test_disagreeing_provided_answers_remain_visible_and_undecided` | §9 item 6 | Checks both answers, their sources and dates in the single `small_apps.in_use` rule-evidence record. The Unknown, incomplete and conflict checks still apply. |
| `site/check_site.py::Page.handle_starttag` | §9 item 2 | Counts articles whose IDs begin with `readiness-`. |

### Test changes beyond the permitted list

| File | Test | Old expectation | New expectation | Required by |
| --- | --- | --- | --- | --- |
| `tests/test_rules.py` | `test_town_telephony_shows_deciding_next_step` in EN and DE | The next-step paragraph was absent from both OneDrive and Security and compliance. | Ready OneDrive still has no paragraph. Unknown Security and compliance has `p.finding-next` with the existing localised `reason.licensed_use_not_measured.fix`. The deciding Telephony action still follows its reason. | UI-SPEC §2.3 and §11 criterion 4 require a localised fix as the next step for an Unknown area. |

The existing disclosure-presence test passed with its original assertions. A separate fixture exercises an area with derived licence evidence alone. The scan loader, D31 catalogue and validation, rule evaluation, privacy and resource assertions, and costs passed their source or test guards.

## Verification

| Check | Result |
| --- | --- |
| Previously halted Task 1 run | 862 passed and two language cases failed on the next-step assertion recorded above. |
| Task 1 `<automated>` | **864 passed in 151.10 s.** Both Ruff checks, both fresh demos, the card count and order assertions and the site checker passed. The checker inspected 20 pages and 719 references. |
| Task 1 source guards | One article template, seven `sec grid` section frames and one test `DISPLAY_ORDER`. The removed table, legend, bar and segment hooks each had zero occurrences. The whitespace-insensitive not-examined diff was empty. |
| Task 2 tests before and after implementation | 19 expected failures and one pass in 4.07 s before the implementation. The focused report, CLI, evidence CLI and inputs tests passed all 425 cases in 44.86 s. |
| Task 2 `<automated>` | **884 passed in 154.32 s.** Both Ruff checks, the fresh demo disclosure and target assertions and the site checker passed. The checker inspected 20 pages and 747 references. The offline evidence tables opened with Enter and fit at 360 px in both languages and colour schemes. |
| Task 3 tests before implementation | Four expected failures in 1.25 s for the absent filter groups. |
| First Task 3 `<automated>` run | The 91 report tests passed in 14.58 s. The full suite reported 883 passes and five failures in 155.61 s because quoted CSS selectors matched the existing HTML section-order assertions. The selector spelling was corrected and the five cases, including the installed offline demo, passed in 3.36 s. |
| Final Task 3 `<automated>` | **91 report tests passed in 14.42 s.** **888 full-suite tests passed in 158.50 s.** `uv run ruff check .` passed and `uv run ruff format --check .` reported 166 formatted files. Four fresh demos passed the Playwright check and the site checker inspected 20 pages and 747 references with “No errors.” |
| Final demo and source checks | `uv run fazit demo --lang de` and `uv run fazit demo --lang en` exited 0 with fresh output files that match the site copies byte for byte. The literal CSP and section hooks, not-examined block, font and resource tests, D31 source files, website pages and styling, and ignored-script status passed their guards. `git diff --check` passed. |
| Copied catalogue and reduced motion | A temporary catalogue moved Mail into Files and documents and used a dotted category ID. Keyboard selection followed the new category. The filter and disclosure transitions had a computed duration of `0s` with reduced motion. |

The plan’s final `node .shots/report-redesign/check.mjs <report-directory> --only filters` run exited 0. Playwright could query the pages with scripting disabled. Each case checked the exact CSP, rejected external requests, reached both named groups once by Tab and confirmed the focus ring and 44 px hit targets. The cases also checked status counts and disabled options, each category, combined filters and empty results, both All resets, a linked card outside the selection, and identical printed text before and after filtering. All cards were visible in print media.

| Report | 1280 × 800 light | 1280 × 800 dark | 360 × 800 light | 360 × 800 dark |
| --- | --- | --- | --- | --- |
| Town EN | Pass | Pass | Pass | Pass |
| Town DE | Pass | Pass | Pass | Pass |
| Non-profit EN | Pass | Pass | Pass | Pass |
| Non-profit DE | Pass | Pass | Pass | Pass |

## Deviations and implementation choices

- The founder’s decision in UI-SPEC §2 and the change map takes precedence over older references to a bar in the objective, task text and RR-03 handoff note. The implementation removes the bar, its segments and its hooks from the report.
- Task 1 carries forward the existing section frame and uses the shared `readiness` list-spacing class on the areas container. The footer width follows the section gutter. The scan-only card count assertion uses the actual branch baseline in display order, town `0, 3, 11, 0` and non-profit `0, 1, 12, 1`.
- The Task 2 evidence tables use the site’s stacked coverage layout. Their single value cell spans the row at 600 px and below. The same table macro handles the licence and card disclosures. A derived-only disclosure renders the rule evidence list.
- The filter tracks wrap where the content column requires it. The category track uses the card radius at desktop widths as well because its bilingual labels can exceed that column. The selected segment’s shadow colour is a token in the report’s second `:root`.
- The filter CSS uses `[data-section=readiness]` so existing HTML section-order assertions keep matching the literal HTML attributes. Category selectors match the ID attribute to support the catalogue’s allowed identifier syntax. A linked card is excluded from the hide rules along with its group. The empty message is suppressed while the linked card is visible.
- Verification ran from the installed environment with `UV_OFFLINE=1` and `UV_NO_SYNC=1`. The working-tree handoff follows the user’s instruction for commits and phase bookkeeping.

## Locale keys removed

Both locales drop `readiness.workload`, `readiness.evidence`, `found.evidence`, `found.source`, `found.collected`, `found.period` and `found.coverage`. `readiness.counts` is available for RR-03.

## Native German review

RR-02 uses the existing locale and rule values for German copy. The labels that first appear in the disclosure and filters are listed here with their English counterparts.

| Key or rendered label | English | German |
| --- | --- | --- |
| `readiness.evidence_summary` | Evidence · {measured} measured, {provided} provided, {unknown} unknown | Nachweise · {measured} erhoben, {provided} bereitgestellt, {unknown} unbekannt |
| `readiness.all_replacements` | All replacements | Alle Ersatzlösungen |
| `filter.status_legend` | Show areas by status | Bereiche nach Status anzeigen |
| `filter.category_legend` | Show areas by category | Bereiche nach Kategorie anzeigen |
| `filter.all` with count | All · {n} | Alle · {n} |
| `filter.all_categories` | All categories | Alle Kategorien |
| `filter.search_hint` | Filtered-out areas and, in some browsers, closed sections are not searched. | Ausgeblendete Bereiche und, je nach Browser, geschlossene Abschnitte werden nicht durchsucht. |
| `filter.empty` | No area matches this selection. Choose "All" to see every area. | Kein Bereich entspricht dieser Auswahl. Wählen Sie „Alle“, um alle Bereiche anzuzeigen. |

## Open and handoff

RR-03 can use `area_count`, display-ordered `status_counts` and `scope_statement` for the summary. RR-04 takes over the not-examined index, which is currently the last element in `readiness` and still uses its original hooks. RR-05 owns the home-page screenshots, design sign-off and full A4 layout review. The council-reader follow-up and the earlier plans’ native German and mapping-operator reviews remain part of release review.

## Rendered cards

These cards are from the English town openDesk demo. Blank lines and indentation from template expansion have been compacted.


### Integrations (Needs work)

```html
<article data-workload="integrations" data-status="needs_work" data-category="automation_ai" class="finding" id="readiness-integrations" aria-labelledby="area-integrations">
  <h4 class="finding-area" id="area-integrations">Integrations · <span class="finding-category">Automation and AI</span></h4>
  <p class="finding-status"><span class="status needs_work"><svg class="icon" viewBox="0 -960 960 960" aria-hidden="true" focusable="false"><path d="M109-120q-11 0-20-5.5T75-140q-5-9-5.5-19.5T75-180l370-640q6-10 15.5-15t19.5-5q10 0 19.5 5t15.5 15l370 640q6 10 5.5 20.5T885-140q-5 9-14 14.5t-20 5.5H109Zm371-120q17 0 28.5-11.5T520-280q0-17-11.5-28.5T480-320q-17 0-28.5 11.5T440-280q0 17 11.5 28.5T480-240Zm0-120q17 0 28.5-11.5T520-400v-120q0-17-11.5-28.5T480-560q-17 0-28.5 11.5T440-520v120q0 17 11.5 28.5T480-360Z"/></svg> Needs work</span>
  </p>
  <div class="finding-reason">
    Applications connected to Microsoft 365 need their integrations reviewed before the move.
  </div>
    <p class="finding-next"><strong>Next step</strong> The IT team records what data each integration transfers and what actions it triggers.</p>
    <details class="workload-evidence" data-evidence-workload="integrations">
      <summary id="evidence-integrations"><svg class="icon" viewBox="0 -960 960 960" aria-hidden="true" focusable="false"><path d="M504-480 348-636q-11-11-11-28t11-28q11-11 28-11t28 11l184 184q6 6 8.5 13t2.5 15q0 8-2.5 15t-8.5 13L404-268q-11 11-28 11t-28-11q-11-11-11-28t11-28l156-156Z"/></svg>Evidence · 1 measured, 1 provided, 0 unknown</summary>
        <ul class="rule-evidence" role="list">
            <li data-evidence="integrations.application_count">
              <strong>Applications integrated with Microsoft 365</strong>
              <div data-provenance="provided">
    3 applications
    <small class="evidence-meta"><span class="prov">Provided</span> · Sample input · 10 November 2026</small>
  </div>
            </li>
            <li data-evidence="integrations.licence_bundled_assigned">
              <strong>Included licence assigned for Integrations</strong>
              <div data-provenance="measured">
    Yes
    <small class="evidence-meta"><span class="prov">Measured (simulated)</span> · Sample licence inventory · 2 November 2026 · Complete, 3 of 3 scanned, 0 failed</small>
  </div>
            </li>
        </ul>
      <div class="table-scroll" role="region" aria-labelledby="evidence-integrations" tabindex="0">
    <table class="coverage" role="table">
      <caption data-sample>Scan measurements are simulated.</caption>
      <thead role="rowgroup">
        <tr role="row">
          <th scope="col" role="columnheader" data-label="Finding">Finding</th>
          <th scope="col" role="columnheader" data-label="Value">Value</th>
        </tr>
      </thead>
      <tbody role="rowgroup">
          <tr data-finding="integrations.application_count" data-provenance="provided" role="row">
            <th scope="row" role="rowheader" data-label="Finding">Applications integrated with Microsoft 365</th>
            <td role="cell" data-label="Value">
              <div data-provenance="provided">
    3 applications
    <small class="evidence-meta"><span class="prov">Provided</span> · Sample input · 10 November 2026</small>
  </div>
            </td>
          </tr>
      </tbody>
    </table>
  </div>
    </details>
  <p class="finding-target">
      <span data-target-function="application_integrations">Interfaces in the openDesk components · In the suite with limits ·
    <time datetime="2026-11-22">22 November 2026</time>
  </span>
    <a class="more" href="#moves-title">All replacements<svg class="icon" viewBox="0 -960 960 960" aria-hidden="true" focusable="false"><path d="M504-480 348-636q-11-11-11-28t11-28q11-11 28-11t28 11l184 184q6 6 8.5 13t2.5 15q0 8-2.5 15t-8.5 13L404-268q-11 11-28 11t-28-11q-11-11-11-28t11-28l156-156Z"/></svg></a>
  </p>
</article>
```

### Small applications (Ready)

```html
<article data-workload="small_apps" data-status="ready" data-category="automation_ai" class="finding" id="readiness-small_apps" aria-labelledby="area-small_apps">
  <h4 class="finding-area" id="area-small_apps">Small applications · <span class="finding-category">Automation and AI</span></h4>
  <p class="finding-status"><span class="status ready"><svg class="icon" viewBox="0 -960 960 960" aria-hidden="true" focusable="false"><path d="m424-408-86-86q-11-11-28-11t-28 11q-11 11-11 28t11 28l114 114q12 12 28 12t28-12l226-226q11-11 11-28t-11-28q-11-11-28-11t-28 11L424-408Zm56 328q-83 0-156-31.5T197-197q-54-54-85.5-127T80-480q0-83 31.5-156T197-763q54-54 127-85.5T480-880q83 0 156 31.5T763-763q54 54 85.5 127T880-480q0 83-31.5 156T763-197q-54 54-127 85.5T480-80Z"/></svg> Ready</span>
  </p>
  <div class="finding-reason">
    The organisation confirms it does not use smaller Microsoft applications such as Forms, Planner or Bookings.
  </div>
    <details class="workload-evidence" data-evidence-workload="small_apps">
      <summary id="evidence-small_apps"><svg class="icon" viewBox="0 -960 960 960" aria-hidden="true" focusable="false"><path d="M504-480 348-636q-11-11-11-28t11-28q11-11 28-11t28 11l184 184q6 6 8.5 13t2.5 15q0 8-2.5 15t-8.5 13L404-268q-11 11-28 11t-28-11q-11-11-11-28t11-28l156-156Z"/></svg>Evidence · 1 measured, 1 provided, 0 unknown</summary>
        <ul class="rule-evidence" role="list">
            <li data-evidence="small_apps.in_use">
              <strong>Small Microsoft applications in use</strong>
              <div data-provenance="provided">
    No
    <small class="evidence-meta"><span class="prov">Provided</span> · Sample input · 10 November 2026</small>
  </div>
            </li>
            <li data-evidence="small_apps.licence_bundled_assigned">
              <strong>Included licence assigned for Small applications</strong>
              <div data-provenance="measured">
    Yes
    <small class="evidence-meta"><span class="prov">Measured (simulated)</span> · Sample licence inventory · 2 November 2026 · Complete, 3 of 3 scanned, 0 failed</small>
  </div>
            </li>
        </ul>
      <div class="table-scroll" role="region" aria-labelledby="evidence-small_apps" tabindex="0">
    <table class="coverage" role="table">
      <caption data-sample>Scan measurements are simulated.</caption>
      <thead role="rowgroup">
        <tr role="row">
          <th scope="col" role="columnheader" data-label="Finding">Finding</th>
          <th scope="col" role="columnheader" data-label="Value">Value</th>
        </tr>
      </thead>
      <tbody role="rowgroup">
          <tr data-finding="small_apps.in_use" data-provenance="provided" role="row">
            <th scope="row" role="rowheader" data-label="Finding">Small Microsoft applications in use</th>
            <td role="cell" data-label="Value">
              <div data-provenance="provided">
    No
    <small class="evidence-meta"><span class="prov">Provided</span> · Sample input · 10 November 2026</small>
  </div>
            </td>
          </tr>
      </tbody>
    </table>
  </div>
    </details>
  <p class="finding-target">
      <span data-target-function="forms_tasks_bookings">OpenProject and OX App Suite for tasks · In the suite with limits ·
    <time datetime="2026-11-22">22 November 2026</time>
  </span>
    <a class="more" href="#moves-title">All replacements<svg class="icon" viewBox="0 -960 960 960" aria-hidden="true" focusable="false"><path d="M504-480 348-636q-11-11-11-28t11-28q11-11 28-11t28 11l184 184q6 6 8.5 13t2.5 15q0 8-2.5 15t-8.5 13L404-268q-11 11-28 11t-28-11q-11-11-11-28t11-28l156-156Z"/></svg></a>
  </p>
</article>
```

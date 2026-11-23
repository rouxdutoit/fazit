---
phase: report-redesign
plan: "04"
subsystem: report
tags: [open-points, navigation, print, accessibility, offline]
requires:
  - phase: RR-01
    provides: Localised actions, action kinds and finding roles
  - phase: RR-06
    provides: Simulated provenance and current evidence fields
  - phase: RR-07
    provides: Profile-aware statuses and anchored transfer gaps
  - phase: RR-02
    provides: Area cards, disclosures and keyboard filters
  - phase: RR-03
    provides: Council summary, cost tiles, chart and all-Unknown fixture
provides:
  - Evidence requests grouped by input or collector and actions grouped by kind
  - Report navigation, shared coverage symbols and expandable recorded evidence
  - A4 page one, compact mobile navigation and browser regression checks
actuals:
  tasks: 3
  commits: 0
tech-stack:
  added: []
  patterns: [Frozen display records, CSS-only navigation and print]
affects: [RR-05]
key-files:
  created:
    - site/icons/circle.svg
    - src/fazit/icons/circle.svg
    - src/fazit/icons/contrast.svg
    - src/fazit/icons/code.svg
    - src/fazit/icons/cancel.svg
    - .planning/report-redesign/RR-04-SUMMARY.md
  modified:
    - src/fazit/report.py
    - src/fazit/templates/report.html.j2
    - src/fazit/locales/en.yaml
    - src/fazit/locales/de.yaml
    - site/style.css
    - site/demo/en/index.html
    - site/demo/de/index.html
    - tests/test_report.py
    - tests/test_rules.py
    - tests/test_cli.py
    - tests/test_evidence_cli.py
    - .shots/report-redesign/check.mjs
requirements-completed: [REPT-01, REPT-03, REPT-04, REPT-05, OUTP-03, OUTP-04]
coverage:
  - id: D1
    description: The working section contains each open point and each fired action in order.
    requirement: OUTP-04
    verification:
      - kind: integration
        ref: tests/test_report.py#test_open_points_include_every_gap_unknown_finding_and_skipped_collector
        status: pass
      - kind: integration
        ref: tests/test_report.py#test_next_steps_render_every_fired_rule_in_display_order
        status: pass
    human_judgment: false
  - id: D2
    description: Bilingual navigation resolves locally and the shared coverage symbols are distinct from statuses.
    requirement: REPT-05
    verification:
      - kind: integration
        ref: tests/test_report.py#test_report_navigation_resolves_and_appendix_explains_scope
        status: pass
      - kind: integration
        ref: tests/test_report.py#test_replacements_use_coverage_symbols_distinct_from_status
        status: pass
    human_judgment: false
  - id: D3
    description: The four reports are readable at 360 px and the A4 printout opens with the full council summary.
    requirement: OUTP-03
    verification:
      - kind: automated_ui
        ref: node .shots/report-redesign/check.mjs <report-directory>
        status: pass
    human_judgment: false
completed: 2026-11-22
status: complete
---

# RR-04 summary

The report opens with the council summary and follows it with actions and grouped evidence requests. Readers can reach the working sections from the report bar. The complete summary fits on one A4 page for both samples in English and German.

All three tasks ran in order from `fca1649` on `report-redesign`. The changes and regenerated town openDesk demos are in the working tree.

## Changes by task

| Task | Files | Changes |
| --- | --- | --- |
| 1 | `src/fazit/report.py`, `src/fazit/templates/report.html.j2` | Grouped open findings, gaps and skipped collectors by the evidence requested. Moved `not-examined` to the new working section and linked each affected area. Rendered `clarify` and `decide` actions before the evidence requests and `replace` actions after them. Removed the pilot sentences, stock steps and old status lists. |
| 1 | `src/fazit/locales/en.yaml`, `tests/test_report.py`, `tests/test_rules.py`, `tests/test_cli.py`, `tests/test_evidence_cli.py` | Used the existing role ID with the English label “Service lead”. Checked the completeness and grouping of open points, the rule actions, the empty state and all affected evidence scenarios. |
| 2 | `src/fazit/templates/report.html.j2`, `src/fazit/report.py` | Added the skip link and sticky report bar, shortened the header, and moved the local and offline statements into run details. Applied the site's table, tile, list and disclosure components to the replacements, closer look, recorded inventory and appendix sections. Added the existing scope-of-collection copy. |
| 2 | `site/style.css`, `site/icons/circle.svg`, `src/fazit/icons/{circle,contrast,code,cancel}.svg`, `tests/test_report.py`, `tests/test_rules.py`, `tests/test_evidence_cli.py` | Made full coverage use the Material Symbols circle in the site and report. Added the other shared coverage paths to the package. Checked the fragment links, coverage symbols and accessible status names. Adapted the existing locators listed below. |
| 3 | `src/fazit/templates/report.html.j2`, `src/fazit/locales/{en,de}.yaml`, `tests/test_report.py`, `.shots/report-redesign/check.mjs` | Fitted the desktop opening, kept the phone summary in source order, and applied print typography, page breaks, borders and open disclosures. Removed retired selectors and strings. Added print tests and the `layout` and `print` browser parts. |
| 1–3 | `site/demo/en/index.html`, `site/demo/de/index.html` | Regenerated both town openDesk demos after each task. The final files match fresh default CLI builds byte for byte. |

## Report context and existing helpers

`_evidence_context` in `src/fazit/report.py` uses `_open_points` and `_next_steps`. The context exposes `open_points` as a tuple of frozen records with each request's key, items, affected areas, owners, input path and distinct reason codes. `staying_steps` and `move_steps` contain area and `NextStep` pairs in display order. The rendered `data-open-point` hook lives on the term in the template.

The current `tests/helpers.py` contains `ReportDocument`, `report_section`, `readiness_row`, `rebuild_report`, the sample paths and `ALL_UNKNOWN_SCAN`. `FindingEntry.owner` and `ROLES` are in `catalogue.py`. `MissingEvidence`, `NextStep` and `WorkloadStatus` are in `status.py`. `_prepare_report` and `_evidence_context` remain in `report.py`. The current `load_inputs_text` distinguishes `provided_counts`, `confirmations` and `windows_only_software`.

## English town open points

| Request key | Items | Areas linked | Owner shown |
| --- | --- | --- | --- |
| `collector.exchange_recipients` | `mail.shared_mailbox_count` and skipped `exchange_recipients` | Mail | IT team (`it_team`) |
| `confirmations.sharepoint.workflows_in_use` | `sharepoint.workflows_in_use` | SharePoint | Service lead (`service_owner`) |
| `confirmations.office_files.vba_macros_in_use` | `office_files.vba_macros_in_use` | Office files | Service lead (`service_owner`) |
| `confirmations.device_management.windows_desktops_required` | `device_management.windows_desktops_required` | Device management | IT team (`it_team`) |
| `confirmations.security_compliance.protection_or_retention_in_use` | `security_compliance.protection_or_retention_in_use` | Security and compliance (`data-unexamined-workload`) | Information security officer (`information_security`) |

The shipped sample runs contain no `area.*` row. A synthetic `area.small_apps` used `service_owner` from its first finding and used `it_team` with an empty finding list. A copied catalogue assigned the two Windows software figures different roles and the shared `windows_only_software` request returned `it_team` then `service_owner`, in `ROLES` order. Derived licensing evidence uses `licence_management`. A collector-only row uses the roles of its registered findings, with `licence_management` for the licence inventory and `it_team` when another collector has no registered finding. The all-Unknown fixture exercised the collector-only licence row.

## Existing test changes

| File and test | Old expectation | New expectation | Basis |
| --- | --- | --- | --- |
| `tests/test_rules.py::test_suggested_path_lists_only_the_designated_workload_statuses` | Status lists for Blocker, Unknown and Ready, plus pilot and stock steps. | Renamed to `test_next_steps_and_open_evidence_follow_the_findings`. The Telephony action comes from its deciding rule, action groups surround the evidence heading in order, Mail links from its gap, and the path omits pilot and stock-step markup. | UI-SPEC §4.1 and §9 item 12 |
| `tests/test_rules.py::test_suggested_path_explains_empty_lists` | The scan-only report carried the old empty Blocker and Ready strings. | Renamed to `test_next_steps_explain_the_empty_state`. Complete evidence gives all Ready cards, both prescribed empty sentences and no action or evidence rows. | UI-SPEC §4.1 and §9 item 12 |
| `tests/test_rules.py::test_complete_counts_must_agree_but_a_partial_count_can_be_consistent` | Integrations absent from the Ready path list for a complete dispute. | The existing Unknown card also has a link from the open points. | UI-SPEC §4.1 and §9 item 12 |
| `tests/test_rules.py::test_disputed_count_blocks_every_workload_that_uses_it` | Both affected areas absent from the Ready path list. | Open points link to both Unknown cards. The status, dispute and competing-value assertions still apply. | UI-SPEC §4.1 and §9 item 12 |
| `tests/test_cli.py::test_scan_only_report_explains_readiness_and_missing_evidence` | Not-examined hooks in `readiness`. | The same hooks and values in `path`. The card order, status counts and evidence caption remain scoped to `readiness`. | UI-SPEC §2.4, §4.1 and §9 item 12 |
| `tests/test_evidence_cli.py::test_supplied_zero_preserves_a_skipped_observation` | Integrations absent from the Ready path list. | Open points link to the incomplete Unknown Integrations card. | UI-SPEC §4.1 and §9 item 12 |
| `tests/test_evidence_cli.py::test_incomplete_bound_collector_is_reported_without_a_scan_finding` | Integrations absent from the Ready path list. | The evidence list links to Integrations for both Unknown and Needs work cases. | UI-SPEC §4.1 and §9 item 12 |
| `tests/test_evidence_cli.py::test_licensed_accounts_make_zero_assignments_inconclusive` | Licences absent from the Ready path list. | Licences has no area card. Open points link to Unknown Telephony. | UI-SPEC §2.1, §4.1 and §9 item 12 |
| `tests/test_evidence_cli.py::test_licence_pilots_require_reconciled_directory_headcount` | Four areas qualify for the baseline Ready list and drop out after reconciliation fails. Licences has no list entry. | Four baseline cards are Ready. Each unreconciled card is Unknown and linked from the open points. Licences has no area card. | UI-SPEC §2.1, §4.1 and §9 item 12 |
| `tests/test_evidence_cli.py::test_measured_positive_count_cannot_be_overridden_by_zero` | Integrations absent from the Ready path list. | The evidence list links to the incomplete Integrations card. | UI-SPEC §4.1 and §9 item 12 |
| `tests/test_evidence_cli.py::test_disagreeing_provided_answers_remain_visible_and_undecided` | Small applications absent from the Ready path list. | Open points link to the incomplete Unknown Small applications card. | UI-SPEC §4.1 and §9 item 12 |
| `tests/test_evidence_cli.py::test_headline_qualifies_zero_without_complete_coverage` | Value under `span.figure`. | Value under `span.figure-num`, with the same provenance and qualified-zero wording. | UI-SPEC §4 and §9 item 7 |

### Test changes beyond the permitted list

| File | Test | Old expectation | New expectation | Required by |
| --- | --- | --- | --- | --- |
| `tests/test_report.py` | `test_summary_scope_matches_the_replacements_and_gaps` | Count labels in a separate coverage-and-date cell. | Count the same labels in `.cov-cell strong` within the replacement column. | UI-SPEC §4 “What moves where” and §11 criterion 24 |
| `tests/test_rules.py` | `test_scope_statement_matches_the_replacements_and_gap_lists` and `test_marking_a_mapping_as_a_transfer_gap_adds_it_to_the_gap_list` via `_rendered_coverage_counts` | Read the separate coverage-and-date cell and require one label per function. | Read the replacement cell's coverage label and require the same one-to-one match and counts. | UI-SPEC §4 “What moves where” and §11 criterion 24 |
| `tests/test_rules.py` | `test_licence_inventory_shows_its_coverage_gap` | Evidence paragraph immediately after `h3#licences-title`. | The same evidence paragraph immediately after `summary#licences-title` inside the disclosure. | UI-SPEC §4 “Licence products” |
| `tests/test_evidence_cli.py` | `test_empty_licence_inventory_requires_completed_coverage` | Evidence paragraph immediately after `h3#licences-title`. | The same evidence paragraph after `summary#licences-title`. The production checks and assertions on coverage, reasons, provenance and readiness still apply. | UI-SPEC §4 “Licence products” |
| `tests/test_evidence_cli.py` | `test_headline_qualifies_zero_without_complete_coverage` | The fixture label was in a bare `strong`. | The same label is in `strong.tile-label`. | UI-SPEC §4 “Headline tiles” and RR-04 Task 2 |

## Deviations and implementation choices

- The installed RR-03 baseline is on `report-redesign`. The local task and summary follow the requested working-tree handoff.
- On the first Task 1 full run, the unchanged privacy test caught the word `owner` from the newly rendered English “Service owner” label because its fixture contains an ignored field named `owner`. The locale now uses “Service lead” for the same `service_owner` ID. The unchanged privacy test passed for both commands and their outputs.
- The open-points builder uses the existing licence finding types for derived IDs and considers an Unknown observation retained as alternate evidence. A figure outside an area's readiness gaps can still appear as an open point. Its area link is omitted when the area is Ready. This preserves the inventory gap and the Ready card's role in the working list.
- RR-07 added `transfer_undocumented` after the plan's coverage legend was written. It uses the neutral `cancel` symbol. The site's `.cov-full::before` uses the current encoded SVG and source-comment convention, so the Task 2 command checks for `icons/circle.svg` in that declaration. The checker verifies the embedded bytes. The site started with 34 SVGs and now has 35. The package went from 5 to 9. The site stylesheet diff is one declaration.
- The 360 px browser probe found partially visible links during Tab navigation. The navigation track uses its full content width and snaps to the focused link. The fade clears during focus so the ring stays visible. The bar keeps the shared component style and the specified mask when unfocused.
- The first-screen check needed a compact desktop summary. From 880 px the opening section uses less top spacing, and the first blocker row puts its term beside the reason. The phone retains the stacked layout and source order.
- The first A4 runs put the cost tiles or the last German break-even line on page two. Print now uses shorter page-one spacing, gives the German area labels more room, and spans the third tile across the two print columns. The section padding stays 16 pt and the cards use 12 pt. The header's trailing padding is zero in print because the summary supplies the spacing at that boundary. The non-profit SharePoint evidence preview also exposed two distinct fixes touching. They now have a separating space and a regression assertion.
- The print browser part covers both samples and both languages. Its A4 text checks use the report's own labels and compare the four combinations of filter and background settings for each report.

## Retired CSS

| Former selector or group | Change |
| --- | --- |
| `.not-examined li + li`, `.path-workloads li + li` and print `.path-workloads li` | Removed the old lists and their spacing and break rules. |
| `.page-intro h1 + p`, `.page-intro .sample-note` | The header has a metadata list and shared note. |
| `.headlines`, `.headlines li`, `.headlines strong`, `.figure` | Replaced by the tile selectors. Removed the narrow `.headlines` grid and print `.headlines` and `.headlines li` rules, including the tile break entry. |
| `.collectors` and `.collectors thead th:nth-child(1)`, `:nth-child(2)`, `:nth-child(4)` | Collection methods use `.coverage`. |
| `.licences, .moves`, `.moves thead th:nth-child(-n+3)`, `.licences thead th:first-child`, `.licences thead th:nth-child(2)` and `:nth-child(3)` | Removed the retired fixed table layouts. |
| `.risky-files thead th:first-child`, `:nth-child(2)`, `:nth-child(3)` | File types use the shared coverage table. |
| `.software-counts dt` and `.software-counts dd` | Software counts now use `.rows`. |
| Narrow `table:not(.cost-table, .coverage)` and its `:is(caption, tbody, tr, th, td)`, `thead`, `tbody tr`, `tbody :is(th, td)`, `tbody td + td`, `tbody th + td` and `td[data-label]::before` selectors | Removed the legacy table stack. `.coverage` supplies the 600 px layout and the cost table retains its own 40rem rules. |
| `.workload-evidence, .cost-inputs` border and summary selectors, and their print summary and `::details-content` overrides | Generalised to `details`, `summary` and `details::details-content` for every disclosure. The chevron rules target the direct icon. |
| Print `body` font size, `.page-intro h1` font size and `table` font size | Replaced with the seven print type tokens. |

## Locale keys removed

Both locales removed these 15 keys after checking the template, code, tests and site checker.

- `found.provenance`, `header.organisation`
- `moves.coverage`, `moves.evidence`, `moves.workload_evidence`
- `path.blocker`, `path.empty.ready`, `path.pilot_choice`, `path.pilot_evidence`, `path.ready`, `path.sequence`, `path.steps`, `path.unknown`
- `readiness.counts`, `readiness.not_examined`

## Verification

| Check | Result |
| --- | --- |
| Task 1 focused suite | 576 passed in 72.32 s after correcting the open-point link for an optional observation on a Ready area. The privacy and open-point rerun passed 8 cases in 1.97 s after the English label change. |
| Task 1 final checks | 939 passed in 165.55 s. Both Ruff commands, fresh demos and path guards passed. The site checker inspected 20 pages and 823 references. |
| Task 2 before and after implementation | 17 expected failures in 3.65 s for the missing navigation and coverage changes. The focused green suite passed 50 cases in 8.84 s. The mobile focus follow-up passed all eight phone cases and 31 Python tests in 5.41 s. |
| Task 2 automated checks | 956 passed in 169.37 s. Ruff, shared icon comparisons, the fresh navigation and run-details checks and the source guards passed. The site checker inspected 20 pages and 841 references. |
| Task 3 print regression test | One expected failure before the print rules. The focused report and locale suites passed after implementation. |
| Task 3 final commands | `uv run pytest -q` passed **957 tests in 168.94 s**. `uv run ruff check .` passed. `uv run ruff format --check .` reported 167 formatted files. `node .shots/report-redesign/check.mjs <report-directory>` passed all three parts. `uv run python site/check_site.py` checked 20 pages and 841 references with “No errors.” `uv run pytest tests/test_locales.py -q` passed 15 tests in 0.42 s. |
| Default CLI demos | Both `uv run fazit demo --lang de` and `uv run fazit demo --lang en` exited 0 into fresh output directories. The printed paths existed, the content and language matched, and the tracked copies matched byte for byte. |
| Source guards | The CSP line and status-colour occurrence counts passed. The site pages, checker, D31 validation sources, status engine, cost model and privacy guards passed their Git diff checks. The four `data-block` hooks and the original offline and escaping checks passed. `git diff --check` passed. |
| Supplemental fixtures | The all-Unknown report starts its working section on A4 page two in English and German. A seven-digit cost total stays on one line at 360 px in both languages and both colour schemes. Gapless and multiple-owner cases passed direct checks. |
| Printed pages | Reviewed A4 previews and checked both town PDFs with backgrounds on and off. All 14 card heads and their next steps stay together, and cost table headers appear on both pages of results in both languages. |

The `filters` and `layout` parts ran in Chromium with scripting disabled and network access blocked. The layout check also confirmed the embedded fonts loaded, the desktop blocker or zero-blocker caveat was visible, and the phone controls and outlines remained visible.

| Report | 1280 × 800 light | 1280 × 800 dark | 360 × 800 light | 360 × 800 dark |
| --- | --- | --- | --- | --- |
| Town EN | Pass | Pass | Pass | Pass |
| Town DE | Pass | Pass | Pass | Pass |
| Non-profit EN | Pass | Pass | Pass | Pass |
| Non-profit DE | Pass | Pass | Pass | Pass |

The A4 `print` checks ran at 1280 px in a light browser context. Each row passed with backgrounds on and off, and with the status filter selected by keyboard or cleared. Extracted text and pagination matched. The PDFs and 50 dpi previews are under `.shots/report-redesign/out/`.

| Report | Header and summary | PDF pages | Next steps | Costs | Appendix |
| --- | --- | --- | --- | --- | --- |
| Town EN | 1 page | 35 | 2 | 19 | 28 |
| Town DE | 1 page | 37 | 2 | 20 | 30 |
| Non-profit EN | 1 page | 32 | 2 | 17 | 26 |
| Non-profit DE | 1 page | 32 | 2 | 17 | 26 |

## Native German review

| New or revised German locale values | German draft |
| --- | --- |
| 0 | — |

The German labels, actions and fixes come from the earlier plans. Their native review tables are in [RR-01](RR-01-SUMMARY.md#native-german-review), [RR-06](RR-06-SUMMARY.md#native-german-review) and [RR-07](RR-07-SUMMARY.md#native-german-review).

## Open work

RR-05 owns the full design comparison, the site preview refresh and the redesign decisions. The council-reader follow-up, native review of the earlier drafts and mapping operator review remain release work.

## English town markup

These excerpts come from the regenerated report. Blank lines and indentation were compacted. [English town demo](../../site/demo/en/index.html)

### Report bar

```html
<div class="bar">
  <div class="bar-in">
    <a class="wordmark" href="#main">fazit</a>
    <nav class="bar-links" aria-label="Report sections">
      <div class="bar-links-in">
        <a href="#summary-title">Summary</a>
        <a href="#path-title">Next steps</a>
        <a href="#readiness-title">Areas</a>
        <a href="#costs-title">Costs</a>
        <a href="#moves-title">Replacements</a>
        <a href="#attention-title">Closer look</a>
        <a href="#appendix-title">Appendix</a>
      </div>
    </nav>
  </div>
</div>
```

### Telephony action

```html
<div>
  <dt><a href="#readiness-telephony">Telephony</a></dt>
  <dd data-step-kind="replace">The IT team plans a replacement that keeps the required phone services running during the move.</dd>
</div>
```

### Exchange recipient export open point

```html
<div>
  <dt data-open-point="collector.exchange_recipients">Exchange recipient export</dt>
  <dd>
    <ul class="open-items" role="list">
      <li data-unexamined-finding="mail.shared_mailbox_count" data-unexamined-gap="mail.shared_mailbox_count">
        Shared mailboxes · <a href="#readiness-mail">Mail</a>
      </li>
      <li data-unexamined-collector="exchange_recipients">
        Exchange recipient export · <span data-reason="source_not_supplied">The data source was missing.</span>
      </li>
    </ul>
    <p>
      <strong>IT team</strong>
      · Ask the mail administrator to check the count separately. It stays Unknown in this report. Find out which source can provide the missing information. It stays Unknown while it is absent from the scan and inputs file.
    </p>
  </dd>
</div>
```

### Mail and calendar replacement

```html
<tr data-function="mail_and_calendar" data-workload="mail" data-status="needs_work" role="row">
  <th scope="row" role="rowheader" data-label="Microsoft function">Exchange Online mail and calendar</th>
  <td role="cell" data-label="Target replacement">
    <span class="cov-cell">
      <span class="cov"><svg class="icon" viewBox="0 -960 960 960" aria-hidden="true" focusable="false"><path d="M480-80q-83 0-156-31.5T197-197q-54-54-85.5-127T80-480q0-83 31.5-156T197-763q54-54 127-85.5T480-880q83 0 156 31.5T763-763q54 54 85.5 127T880-480q0 83-31.5 156T763-197q-54 54-127 85.5T480-80Z"/></svg></span>
      <span><strong>In the suite</strong>Open-Xchange (OX App Suite)</span>
    </span>
  </td>
  <td role="cell" data-label="Checked on">
    <time datetime="2026-11-22">22 November 2026</time>
  </td>
  <td role="cell" data-label="Area status">
    <a href="#readiness-mail" aria-label="Mail: Needs work"><span class="status needs_work"><svg class="icon" viewBox="0 -960 960 960" aria-hidden="true" focusable="false"><path d="M109-120q-11 0-20-5.5T75-140q-5-9-5.5-19.5T75-180l370-640q6-10 15.5-15t19.5-5q10 0 19.5 5t15.5 15l370 640q6 10 5.5 20.5T885-140q-5 9-14 14.5t-20 5.5H109Zm371-120q17 0 28.5-11.5T520-280q0-17-11.5-28.5T480-320q-17 0-28.5 11.5T440-280q0 17 11.5 28.5T480-240Zm0-120q17 0 28.5-11.5T520-400v-120q0-17-11.5-28.5T480-560q-17 0-28.5 11.5T440-520v120q0 17 11.5 28.5T480-360Z"/></svg> Needs work</span>
      <small class="note-text">Evidence incomplete</small></a>
  </td>
</tr>
```

## Self-check

All three task gates passed. The final site demos, browser evidence and summary are present.

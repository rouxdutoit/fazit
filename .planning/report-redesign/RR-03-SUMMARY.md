---
phase: report-redesign
plan: "03"
subsystem: report
tags: [summary, costs, break-even, offline-report]
requires:
  - phase: RR-01
    provides: Assessed areas and bilingual summary and cost copy
  - phase: RR-06
    provides: Explicit evidence and simulated provenance
  - phase: RR-07
    provides: Profile coverage and transfer gaps
  - phase: RR-02
    provides: Section frames, display-ordered counts, area cards and filters
provides:
  - Council summary with status definitions, blockers, open questions and target scope
  - Whole-unit totals and exact operations break-even
  - Five-year cost chart and a stacked cost table at phone widths
  - All-Unknown fixture for report and print checks
affects: [RR-04, RR-05]
actuals:
  tokens: 168008
  tasks: 3
  commits: 0
tech-stack:
  added: []
  patterns: [Shared exact cost results for the chart, tiles and table]
key-files:
  created:
    - tests/fixtures/all_unknown_scan.json
    - .planning/report-redesign/RR-03-SUMMARY.md
  modified:
    - src/fazit/report.py
    - src/fazit/i18n.py
    - src/fazit/templates/report.html.j2
    - tests/report_expectations.py
    - tests/helpers.py
    - tests/test_report.py
    - tests/test_rules.py
    - tests/test_costs.py
    - site/demo/en/index.html
    - site/demo/de/index.html
key-decisions:
  - Use RR-02's status counts without a readiness bar.
  - Build break-even and the shared chart scale from the existing exact cost results.
requirements-completed: [REPT-02, REPT-04, REPT-05, COST-03, OUTP-03]
coverage:
  - id: D1
    description: The summary gives status definitions and counts, capped evidence lists and the target scope.
    requirement: REPT-02
    verification:
      - kind: integration
        ref: tests/test_report.py#test_summary_counts_and_links_match_the_report
        status: pass
      - kind: integration
        ref: tests/test_report.py#test_summary_caps_blockers_and_open_areas_in_catalogue_order
        status: pass
      - kind: integration
        ref: tests/test_report.py#test_summary_scope_matches_the_replacements_and_gaps
        status: pass
    human_judgment: false
  - id: D2
    description: The tiles show whole figures and the operations break-even uses exact scenario results.
    requirement: COST-03
    verification:
      - kind: unit
        ref: tests/test_costs.py#test_break_even_matches_the_cost_model
        status: pass
      - kind: integration
        ref: tests/test_costs.py#test_town_cost_tiles_use_whole_units_and_show_the_break_even
        status: pass
      - kind: integration
        ref: tests/test_costs.py#test_known_move_total_with_unknown_cost_comparison
        status: pass
    human_judgment: false
  - id: D3
    description: Known costs share one chart scale and the chart values agree with the table.
    requirement: REPT-05
    verification:
      - kind: integration
        ref: tests/test_costs.py#test_cost_chart_uses_one_scale
        status: pass
      - kind: integration
        ref: tests/test_costs.py#test_cost_chart_text_equals_the_table_subtotals
        status: pass
      - kind: integration
        ref: tests/test_costs.py#test_nonprofit_chart_shows_unknown_without_a_bar
        status: pass
    human_judgment: false
  - id: D4
    description: The area filters continue to work in the offline report.
    requirement: REPT-04
    verification:
      - kind: automated_ui
        ref: node .shots/report-redesign/check.mjs <report-directory> --only filters
        status: pass
    human_judgment: false
  - id: D5
    description: The redesigned report fits the council summary on one A4 page.
    requirement: OUTP-03
    verification: []
    human_judgment: true
    rationale: RR-04 owns the header and print layout. RR-05 checks page one in real PDFs.
duration: 20 min from the first recorded context check
completed: 2026-11-22
status: complete
---

# RR-03 summary

Fazit opens with assessed-area status definitions, blockers, open evidence questions, target coverage and three five-year cost totals. The costs section draws known totals on one scale and shows the same break-even figures as the summary.

All three tasks ran in order from `4e6777e`. The changes and both regenerated town openDesk demos are in the working tree.

## Changes by task

| Task | Files | Changes |
| --- | --- | --- |
| 1 | `src/fazit/report.py`, `src/fazit/templates/report.html.j2` | Added the council summary using RR-02's counts and RR-07's scope data. It shows up to three blockers and four distinct open areas in catalogue order. Put the existing path third and moved recorded inventory after attention. Added the summary's open-points and missing-cost targets. |
| 1 | `tests/report_expectations.py`, `tests/helpers.py`, `tests/fixtures/all_unknown_scan.json`, `tests/test_report.py`, `tests/test_rules.py` | Updated the shared section order. Added the skipped-collector fixture and tests for counts, caps, evidence fixes, links, scope and the zero-blocker states. |
| 2 | `src/fazit/i18n.py`, `src/fazit/report.py`, `src/fazit/templates/report.html.j2`, `tests/test_costs.py` | Added whole-unit money formatting, comparisons, exact operations break-even and three cost tiles. Tested the English and German formats, unknown comparison and total, seven-digit amounts, and break-even against the cost model. |
| 3 | `src/fazit/report.py`, `src/fazit/templates/report.html.j2`, `tests/test_costs.py` | Added chart rows on a shared scale, the dashed Unknown marker, the finance intro, the VAT and profile notes and a stacked layout for both cost tables. Moved the inputs disclosure to the end and reused the Stay and break-even notes. |
| 1–3 | `site/demo/en/index.html`, `site/demo/de/index.html` | Regenerated the matching town openDesk demos after each task. The final files match fresh default CLI builds byte for byte. |

## Interfaces

```python
_summary_rows(statuses: tuple[WorkloadStatus, ...], strings: dict) -> _SummaryRows
_missing_cost_paths(scenarios: tuple[ScenarioResult, ...]) -> tuple[str, ...]
_cost_comparison(difference: Fraction | None) -> _CostComparison
_break_even(result: ScenarioResult, operations_per_year: Decimal | None) -> _BreakEven | None
_cost_tiles(scenarios: tuple[ScenarioResult, ...], inputs: Inputs) -> tuple[_CostTile, ...]
_cost_chart_rows(tiles: tuple[_CostTile, ...]) -> tuple[_CostChartRow, ...]
Formatter.money(self, amount: Fraction | Decimal, currency: str, *, whole: bool = False) -> str
```

`_SummaryRows` holds the blocker rows and the open areas with their localised fixes. The template reads the existing `status_counts`, `area_count` and `scope_statement`. Each tile uses its `ScenarioResult` for the scenario, total and distinct missing paths, and carries its comparison, known-block sum and break-even result. Each chart row uses that same tile and adds its blocks, unknown block IDs and share. `cost_notes()` renders the same note content in the summary and the costs section.

The existing helpers are in the same modules recorded by RR-02. `report_section`, `readiness_row`, `rebuild_report`, `sample_scan_path`, `sample_inputs_path` and the new `ALL_UNKNOWN_SCAN` are in `tests/helpers.py`. `SECTION_ORDER` is in `tests/report_expectations.py`. `plain_amount` and `reason_text` come from `src/fazit/i18n.py`.

## Verification

| Check | Result |
| --- | --- |
| Task 1 focused summary and rule tests | 10 passed in 2.58 s. The complete-evidence fixture used successful collectors to match its supplied evidence. |
| Task 1 `<automated>` | **898 passed in 156.75 s.** Both Ruff checks, the fresh English town and German all-Unknown reports, section order, source counts and site checker passed. |
| Task 2 tests before implementation | Seven expected failures in 1.72 s. Reports rendered and the tests found the cost tiles absent. JUnit verification returned `RED_EVIDENCE_OK`. |
| Task 2 `<automated>` | 42 cost tests passed in 2.69 s. **914 full-suite tests passed in 158.78 s.** Both Ruff checks, the demo amounts and break-even assertions, the site checker and the cost-model diff passed. |
| Task 3 tests before implementation | Eight expected failures in 1.88 s. The old cost section lacked the chart, intro and shared notes. JUnit verification returned `RED_EVIDENCE_OK`. |
| Task 3 `<automated>` | 156 cost and report tests passed in 22.55 s. **928 full-suite tests passed in 164.96 s.** Both Ruff checks, the fresh non-profit chart assertions, the German build, the site checker and the cost and status diff passed. |
| Final default demos and all-Unknown fixture | The English and German `uv run fazit demo` commands succeeded with fresh output directories. Each printed path existed and matched the corresponding site file. The fixture rendered in both languages with three Unknown cost tiles and no chart. |
| RR-02 filter check | `node .shots/report-redesign/check.mjs <report-directory> --only filters` passed all 16 Chromium cases. Both samples and both languages ran at 1280 px and 360 px in light and dark with scripting disabled and the browser offline. |
| Cost layout | At 360 px, both samples in each language and colour scheme had no page or table overflow. The chart values stacked, the scale matched the rendered bar widths and the dashed marker appeared at 48 px. Both embedded fonts loaded and the inputs disclosure opened by keyboard. The seven-digit tile was one line in both languages at 360 px and 1280 px. Chromium's print styles kept each chart row together. |
| Source and safeguard checks | The CSP matched HEAD byte for byte. The cost model, status engine, D31 checks and site pages outside the two demos matched HEAD. The cost table hooks retained their hosts, values and attribute order. All four sample renders had four `data-block` hooks and the summary copy and bar guards passed. No safeguard assertions changed. The site checker covered 20 pages and 769 references with “No errors.” `git diff --check` passed. |

## Existing test changes

| File | Test or expectation | Old expectation | New expectation | Basis |
| --- | --- | --- | --- | --- |
| `tests/report_expectations.py` | `SECTION_ORDER`, shared by the CLI, report, rules and installed-package suites | Nine sections, with `found` and `costs` after `header` and `path` after `attention`. | `header, summary, path, readiness, costs, moves, attention, found, appendix, footer`. | UI-SPEC §1 and §9 item 1. |
| `tests/test_costs.py` | `test_money_format` | Three default-format assertions. | The three default-format assertions still apply. Added whole-unit cases that round half away from zero for a positive amount and two negative amounts in each language. | RR-03 Task 2 and UI-SPEC §1.2 item 5 and §9 item 11. |

### Test changes beyond the permitted list

None.

## Deviations and implementation choices

- The founder's no-bar decision in UI-SPEC §2 and the current RR-02 baseline supersede the plan's references to a bar in `readiness`. The section's single markup edit adds the `not-examined` ID after its existing hook.
- RR-07's `reviewed_on` controls the existing unreviewed notice in the summary. The review date stays in the replacements section and appendix.
- The current legacy table selector is `table:not(.cost-table, .coverage)`. The Task 3 acceptance check used that spelling to confirm the other mobile table rules. Both cost tables use the coverage padding and header style, with content-based desktop columns and stacked rows on phones.
- The existing bilingual singular and plural keys covered every message. The English money formatter already places the sign on the amount, so the whole-unit half case displays `EUR -1`.
- The checks used the installed environment with `UV_OFFLINE=1` and `UV_NO_SYNC=1`. The first supplemental browser probe treated all CLI output as a file path. It passed after reading the last line, as the plan's checks do.
- The working-tree handoff follows the user’s no-commit instruction. Phase bookkeeping stays with the coordinating run.

## Rendered break-even figures

Amounts are the annual target operations cost and the entered value. Both the summary and costs use the same lines.

| Sample | Scenario | English threshold and entered amount | German threshold and entered amount |
| --- | --- | --- | --- |
| Town | Partial move | EUR 20,440 · EUR 6,000 | 20.440 EUR · 6.000 EUR |
| Town | Full move | EUR 39,130 · EUR 12,000 | 39.130 EUR · 12.000 EUR |
| Non-profit | Partial move | EUR 26 · EUR 1,600 | 26 EUR · 1.600 EUR |
| Non-profit | Full move | Absent because the lost working time input is missing | Absent |

## Open work

At 1280 × 800, the current header pushes the first blocker, or the zero-blocker caveat, below the initial viewport in both samples and languages. RR-04 owns the header, path and print layout. RR-05 owns the A4 page-one, site screenshot and design checks. The earlier native German review and mapping operator review remain open for release.

## Native German review

RR-03 uses the existing locale values throughout. The table records the wording used in the new summary, tiles and chart for the release review. Area names, coverage labels and evidence fixes also come from the existing locales and rule files.

| Key | English | German draft for review |
| --- | --- | --- |
| `summary.title` | Where the organisation stands | Wo die Organisation steht |
| `summary.of_areas` | Of {n} areas: | Von {n} Bereichen: |
| `summary.blockers` | What blocks this move | Was diesem Umstieg entgegensteht |
| `summary.confirmed` | Confirmed blockers: {shown} of {total} | Bestätigte Hindernisse: {shown} von {total} |
| `summary.all_blockers` | All blockers | Alle Hindernisse |
| `summary.caveat` | {n} areas are Unknown or have incomplete evidence, so a Blocker cannot be ruled out. | {n} Bereiche sind unbekannt oder unvollständig belegt; ein Hindernis lässt sich daher nicht ausschließen. |
| `summary.caveat_one` | {n} area is Unknown or has incomplete evidence, so a Blocker cannot be ruled out. | Bei {n} Bereich ist der Status unbekannt oder die Nachweise sind unvollständig, sodass sich ein Hindernis nicht ausschließen lässt. |
| `summary.unknown` | What is still unknown | Was noch unbekannt ist |
| `summary.not_examined` | All open points | Alle offenen Punkte |
| `summary.define.blocker` | A confirmed obstacle that must be resolved before this move. | Ein bestätigtes Problem, das vor diesem Umstieg gelöst sein muss. |
| `summary.define.needs_work` | The checks found work to do before a move. | Die Prüfungen haben Aufgaben ergeben, die vor einem Umstieg zu erledigen sind. |
| `summary.define.unknown` | Evidence is missing, so this version cannot assess the area. | Es fehlen Nachweise, daher kann diese Version den Bereich nicht bewerten. |
| `summary.define.ready` | The current checks found no blocker and no missing evidence. | Die aktuellen Prüfungen haben kein Hindernis und keine fehlenden Nachweise ergeben. |
| `summary.scope_title` | What {profile} covers | Was {profile} abdeckt |
| `summary.scope_of` | Of the {n} functions Fazit checks for {profile}: | Von den {n} Funktionen, die Fazit für {profile} prüft: |
| `summary.scope_needed` | Outside {profile} and needed here | Nicht in {profile} enthalten und hier benötigt |
| `summary.scope_unknown` | {n} more are outside {profile} and still Unknown here. | Weitere {n} sind nicht in {profile} enthalten; ob sie hier benötigt werden, ist unbekannt. |
| `status.blocker` | Blocker | Hindernis |
| `status.needs_work` | Needs work | Handlungsbedarf |
| `status.unknown` | Unknown | Unbekannt |
| `status.ready` | Ready | Bereit |
| `readiness.incomplete` | Evidence incomplete | Datengrundlage unvollständig |
| `path.empty.blocker` | The evidence identified no blocker. | Die Bestandsaufnahme hat kein Hindernis ergeben. |
| `path.empty.unknown` | Every area has a known status. | Der Status ist für alle Bereiche bekannt. |
| `moves.unreviewed` | This mapping has not yet been reviewed by someone who operates the target system. | Diese Zuordnung wurde noch nicht von einer Person geprüft, die das Zielsystem betreibt. |
| `header.unnamed_organisation` | This organisation | Diese Organisation |
| `header.scan_date` | Evidence date (scan.json) | Stand der Erhebung (scan.json) |
| `header.inputs_date` | Inputs as of (inputs.yaml) | Stand der Angaben (inputs.yaml) |
| `common.date_not_supplied` | Date not supplied | Datum nicht angegeben |
| `costs.stay` | Stay | Verbleib |
| `costs.partial_exit` | Partial move | Teilweiser Umstieg |
| `costs.full_exit` | Full move | Vollständiger Umstieg |
| `costs.total_label` | {scenario} · five-year total | {scenario} · Summe über fünf Jahre |
| `costs.stay_basis` | Today's yearly costs for five years | Heutige Jahreskosten über fünf Jahre |
| `costs.comparison_unknown` | Comparison unknown | Vergleich unbekannt |
| `costs.difference` | Difference from staying | Unterschied zum Verbleib |
| `costs.less` | less than staying | weniger als beim Verbleib |
| `costs.more` | more than staying | mehr als beim Verbleib |
| `costs.same` | the same as staying | gleich viel wie beim Verbleib |
| `costs.sub_cent` | differs by less than one cent | weicht um weniger als einen Cent ab |
| `costs.total_unknown` | Total unknown | Summe unbekannt |
| `costs.known_blocks` | Total of known blocks {amount} | Summe der bekannten Blöcke: {amount} |
| `costs.inputs_missing` | {n} inputs are missing | {n} Angaben fehlen |
| `costs.inputs_missing_one` | {n} input is missing | {n} Angabe fehlt |
| `costs.missing_fix` | Enter the missing amounts in the inputs file and build the report again. | Tragen Sie die fehlenden Beträge in die Eingabedatei ein und erstellen Sie den Bericht erneut. |
| `costs.stay_assumption` | Staying assumes no price change. | Für den Verbleib ist keine Preisänderung angenommen. |
| `costs.break_even` | {scenario} costs the same as staying if target operations cost {amount} a year (entered: {entered}). | {scenario} kostet gleich viel wie der Verbleib, wenn der Betrieb des Zielsystems {amount} pro Jahr kostet (angegeben: {entered}). |
| `costs.break_even_none` | {scenario} costs more than staying even with no operations cost. | {scenario} kostet auch ohne Betriebskosten mehr als der Verbleib. |
| `costs.profile_note` | The costs come from the inputs file and are the same for every target profile. | Die Kosten stammen aus der Eingabedatei und sind für jedes Zielprofil gleich. |
| `costs.vat_note` | Amounts are as entered. The inputs file does not say whether they include VAT. | Beträge wie angegeben. Die Eingabedatei gibt nicht an, ob sie Umsatzsteuer enthalten. |
| `costs.provide_inputs` | Supply a cost input file with the report command's --inputs option. | Übergeben Sie die Datei mit den Kostenangaben über die Option --inputs des Befehls report. |
| `costs.not_provided` | Not provided | Nicht angegeben |
| `costs.origins.invented` | Invented amount | Erfunden für das Beispiel |
| `costs.origins.provided` | Provided | Bereitgestellt |
| `costs.origins.calculated` | Calculated from inputs | Aus den bereitgestellten Angaben berechnet |
| `costs.origins.calculated_with_examples` | Calculated from sample inputs | Aus Beispielangaben berechnet |
| `costs.groups.running` | Running costs | Laufende Kosten |
| `costs.groups.direct_project` | Direct project costs | Direkte Projektkosten |
| `costs.groups.productivity_loss` | Lost working time (internal estimate, not a payment) | Verlorene Arbeitszeit (interne Schätzung, keine Zahlung) |
| `costs.groups.parallel_running` | Parallel running | Parallelbetrieb |

## Rendered markup

The English town examples come from the regenerated demo. The non-profit examples come from its English openDesk run. Blank lines from template expansion were removed. [English town demo](../../site/demo/en/index.html)

<details>
<summary>Town summary</summary>

```html
<section data-section="summary">
      <div class="sec grid">
        <h2 class="sec-label" id="summary-title">Where the organisation stands</h2>
        <div class="sec-body">
          <p class="sec-intro">Of 14 areas:</p>
          <dl class="status-summary">
              <div>
                <dt><span class="status blocker"><svg class="icon" viewBox="0 -960 960 960" aria-hidden="true" focusable="false"><path d="M480-280q17 0 28.5-11.5T520-320q0-17-11.5-28.5T480-360q-17 0-28.5 11.5T440-320q0 17 11.5 28.5T480-280Zm0-160q17 0 28.5-11.5T520-480v-160q0-17-11.5-28.5T480-680q-17 0-28.5 11.5T440-640v160q0 17 11.5 28.5T480-440ZM363-120q-16 0-30.5-6T307-143L143-307q-11-11-17-25.5t-6-30.5v-234q0-16 6-30.5t17-25.5l164-164q11-11 25.5-17t30.5-6h234q16 0 30.5 6t25.5 17l164 164q11 11 17 25.5t6 30.5v234q0 16-6 30.5T817-307L653-143q-11 11-25.5 17t-30.5 6H363Z"/></svg> Blocker</span> 1</dt>
                <dd>A confirmed obstacle that must be resolved before this move.</dd>
              </div>
              <div>
                <dt><span class="status needs_work"><svg class="icon" viewBox="0 -960 960 960" aria-hidden="true" focusable="false"><path d="M109-120q-11 0-20-5.5T75-140q-5-9-5.5-19.5T75-180l370-640q6-10 15.5-15t19.5-5q10 0 19.5 5t15.5 15l370 640q6 10 5.5 20.5T885-140q-5 9-14 14.5t-20 5.5H109Zm371-120q17 0 28.5-11.5T520-280q0-17-11.5-28.5T480-320q-17 0-28.5 11.5T440-280q0 17 11.5 28.5T480-240Zm0-120q17 0 28.5-11.5T520-400v-120q0-17-11.5-28.5T480-560q-17 0-28.5 11.5T440-520v120q0 17 11.5 28.5T480-360Z"/></svg> Needs work</span> 9</dt>
                <dd>The checks found work to do before a move.</dd>
              </div>
              <div>
                <dt><span class="status unknown"><svg class="icon" viewBox="0 -960 960 960" aria-hidden="true" focusable="false"><path d="M478-240q21 0 35.5-14.5T528-290q0-21-14.5-35.5T478-340q-21 0-35.5 14.5T428-290q0 21 14.5 35.5T478-240Zm2 160q-83 0-156-31.5T197-197q-54-54-85.5-127T80-480q0-83 31.5-156T197-763q54-54 127-85.5T480-880q83 0 156 31.5T763-763q54 54 85.5 127T880-480q0 83-31.5 156T763-197q-54 54-127 85.5T480-80Zm4-572q25 0 43.5 16t18.5 40q0 22-13.5 39T502-525q-23 20-40.5 44T444-427q0 14 10.5 23.5T479-394q15 0 25.5-10t13.5-25q4-21 18-37.5t30-31.5q23-22 39.5-48t16.5-58q0-51-41.5-83.5T484-720q-38 0-72.5 16T359-655q-7 12-4.5 25.5T368-609q14 8 29 5t25-17q11-15 27.5-23t34.5-8Z"/></svg> Unknown</span> 1</dt>
                <dd>Evidence is missing, so this version cannot assess the area.</dd>
              </div>
              <div>
                <dt><span class="status ready"><svg class="icon" viewBox="0 -960 960 960" aria-hidden="true" focusable="false"><path d="m424-408-86-86q-11-11-28-11t-28 11q-11 11-11 28t11 28l114 114q12 12 28 12t28-12l226-226q11-11 11-28t-11-28q-11-11-28-11t-28 11L424-408Zm56 328q-83 0-156-31.5T197-197q-54-54-85.5-127T80-480q0-83 31.5-156T197-763q54-54 127-85.5T480-880q83 0 156 31.5T763-763q54 54 85.5 127T880-480q0 83-31.5 156T763-197q-54 54-127 85.5T480-80Z"/></svg> Ready</span> 3</dt>
                <dd>The current checks found no blocker and no missing evidence.</dd>
              </div>
          </dl>
          <div class="subsection" data-summary="blockers">
            <h3>What blocks this move</h3>
              <dl class="rows">
                  <div>
                    <dt><a href="#readiness-telephony">Telephony</a></dt>
                    <dd>The organisation uses Microsoft telephony and has confirmed that it has no replacement.
  </dd>
                  </div>
              </dl>
              <p><a class="more" href="#status-blocker">All blockers<svg class="icon" viewBox="0 -960 960 960" aria-hidden="true" focusable="false"><path d="M504-480 348-636q-11-11-11-28t11-28q11-11 28-11t28 11l184 184q6 6 8.5 13t2.5 15q0 8-2.5 15t-8.5 13L404-268q-11 11-28 11t-28-11q-11-11-11-28t11-28l156-156Z"/></svg></a></p>
          </div>
          <div class="subsection" data-summary="unknown">
            <h3>What is still unknown</h3>
              <dl class="rows">
                  <div>
                    <dt><a href="#readiness-mail">Mail</a></dt>
                    <dd>Ask the mail administrator to check the count separately. It stays Unknown in this report.</dd>
                  </div>
                  <div>
                    <dt><a href="#readiness-sharepoint">SharePoint</a></dt>
                    <dd>Find out the answer and enter it in the inputs file.</dd>
                  </div>
                  <div>
                    <dt><a href="#readiness-office_files">Office files</a></dt>
                    <dd>Find out the answer and enter it in the inputs file.</dd>
                  </div>
                  <div>
                    <dt><a href="#readiness-device_management">Device management</a></dt>
                    <dd>Find out the answer and enter it in the inputs file.</dd>
                  </div>
              </dl>
            <p>
              <a class="more" href="#not-examined">All open points<svg class="icon" viewBox="0 -960 960 960" aria-hidden="true" focusable="false"><path d="M504-480 348-636q-11-11-11-28t11-28q11-11 28-11t28 11l184 184q6 6 8.5 13t2.5 15q0 8-2.5 15t-8.5 13L404-268q-11 11-28 11t-28-11q-11-11-11-28t11-28l156-156Z"/></svg></a>
            </p>
          </div>
            <div class="subsection" data-summary="scope">
              <h3>What openDesk covers</h3>
              <p>Of the 22 functions Fazit checks for openDesk:
                  In the suite 6 ·
                  In the suite with limits 8 ·
                  Direct transfer undocumented 3 ·
                  Not available 5
              </p>
                <dl class="rows">
                  <div>
                    <dt>Outside openDesk and needed here</dt>
                    <dd><a href="#transfer-gap-device_management">Device management with Microsoft Intune</a> · <a href="#transfer-gap-windows_applications">Running Windows-only applications</a> · <a href="#transfer-gap-automation_and_low_code">Power Platform automation and low-code applications</a> · <a href="#transfer-gap-telephony">Teams Phone and public telephone calling</a></dd>
                  </div>
                </dl>
                <p>3 more are outside openDesk and still Unknown here.</p>
              <p class="note-text">This mapping has not yet been reviewed by someone who operates the target system.</p>
            </div>
          <ul class="tiles tiles-3" role="list">
              <li data-cost-tile="stay">
                <p class="tile-label">Stay · five-year total</p>
                  <span class="figure-num">EUR 600,000</span>
                    <p class="tile-title">Today&#39;s yearly costs for five years</p>
                  <p data-cost-origin="calculated_with_examples">Calculated from sample inputs</p>
              </li>
              <li data-cost-tile="partial_exit">
                <p class="tile-label">Partial move · five-year total</p>
                  <span class="figure-num">EUR 527,800</span>
                    <p class="tile-title" data-comparison="less"><span>
      <span class="cost-value">EUR 72,200</span>
    less than staying
  </span></p>
                  <p data-cost-origin="calculated_with_examples">Calculated from sample inputs</p>
              </li>
              <li data-cost-tile="full_exit">
                <p class="tile-label">Full move · five-year total</p>
                  <span class="figure-num">EUR 464,350</span>
                    <p class="tile-title" data-comparison="less"><span>
      <span class="cost-value">EUR 135,650</span>
    less than staying
  </span></p>
                  <p data-cost-origin="calculated_with_examples">Calculated from sample inputs</p>
              </li>
          </ul>
          <div class="cost-notes">
    <p class="note-text">Staying assumes no price change.</p>
      <p class="note-text" data-break-even="partial_exit">Partial move costs the same as staying if target operations cost EUR 20,440 a year (entered: EUR 6,000).</p>
      <p class="note-text" data-break-even="full_exit">Full move costs the same as staying if target operations cost EUR 39,130 a year (entered: EUR 12,000).</p>
  </div>
        </div>
      </div>
    </section>
```

</details>

<details>
<summary>Town cost section</summary>

```html
<section data-section="costs">
      <div class="sec grid">
        <h2 class="sec-label">What staying and moving cost over five years</h2>
        <div class="sec-body">
          <p class="sec-intro">
            Stadtverwaltung Musterstadt
            · Evidence date (scan.json) <time datetime="2026-11-02T09:00:00Z">2 November 2026</time>
            · Inputs as of (inputs.yaml)
            <time datetime="2026-11-10">10 November 2026</time>
            · Invented amount
          </p>
          <p class="note-text">The costs come from the inputs file and are the same for every target profile.</p>
          <div class="cost-bars">
    <ul class="legend" role="list">
        <li><span class="cost-swatch cost-running" aria-hidden="true"></span>Running costs</li>
        <li><span class="cost-swatch cost-direct_project" aria-hidden="true"></span>Direct project costs</li>
        <li><span class="cost-swatch cost-productivity_loss" aria-hidden="true"></span>Lost working time (internal estimate, not a payment)</li>
        <li><span class="cost-swatch cost-parallel_running" aria-hidden="true"></span>Parallel running</li>
    </ul>
      <div class="cost-chart-row" data-chart-scenario="stay">
        <div class="cost-chart-heading">
          <h3>Stay</h3>
            <p>
              <strong class="cost-value">EUR 600,000.00</strong>
              <small data-cost-origin="calculated_with_examples">Calculated from sample inputs</small>
            </p>
        </div>
          <div class="cost-bar" aria-hidden="true" style="--share: 1.0000">
              <span class="cost-segment cost-running" data-chart-block="running" style="flex-grow: 600000.00"></span>
          </div>
          <ul class="cost-chart-values" role="list">
              <li>Running costs · <span class="cost-value" data-chart-value="running">EUR 600,000.00</span></li>
              <li>Direct project costs · <span class="cost-value" data-chart-value="direct_project">EUR 0.00</span></li>
              <li>Lost working time (internal estimate, not a payment) · <span class="cost-value" data-chart-value="productivity_loss">EUR 0.00</span></li>
              <li>Parallel running · <span class="cost-value" data-chart-value="parallel_running">EUR 0.00</span></li>
          </ul>
      </div>
      <div class="cost-chart-row" data-chart-scenario="partial_exit">
        <div class="cost-chart-heading">
          <h3>Partial move</h3>
            <p>
              <strong class="cost-value">EUR 527,800.00</strong>
                · <span>
      <span class="cost-value">EUR 72,200.00</span>
    less than staying
  </span>
              <small data-cost-origin="calculated_with_examples">Calculated from sample inputs</small>
            </p>
        </div>
          <div class="cost-bar" aria-hidden="true" style="--share: 0.8797">
              <span class="cost-segment cost-running" data-chart-block="running" style="flex-grow: 422800.00"></span>
              <span class="cost-segment cost-direct_project" data-chart-block="direct_project" style="flex-grow: 46000.00"></span>
              <span class="cost-segment cost-productivity_loss" data-chart-block="productivity_loss" style="flex-grow: 9000.00"></span>
              <span class="cost-segment cost-parallel_running" data-chart-block="parallel_running" style="flex-grow: 50000.00"></span>
          </div>
          <ul class="cost-chart-values" role="list">
              <li>Running costs · <span class="cost-value" data-chart-value="running">EUR 422,800.00</span></li>
              <li>Direct project costs · <span class="cost-value" data-chart-value="direct_project">EUR 46,000.00</span></li>
              <li>Lost working time (internal estimate, not a payment) · <span class="cost-value" data-chart-value="productivity_loss">EUR 9,000.00</span></li>
              <li>Parallel running · <span class="cost-value" data-chart-value="parallel_running">EUR 50,000.00</span></li>
          </ul>
      </div>
      <div class="cost-chart-row" data-chart-scenario="full_exit">
        <div class="cost-chart-heading">
          <h3>Full move</h3>
            <p>
              <strong class="cost-value">EUR 464,350.00</strong>
                · <span>
      <span class="cost-value">EUR 135,650.00</span>
    less than staying
  </span>
              <small data-cost-origin="calculated_with_examples">Calculated from sample inputs</small>
            </p>
        </div>
          <div class="cost-bar" aria-hidden="true" style="--share: 0.7739">
              <span class="cost-segment cost-running" data-chart-block="running" style="flex-grow: 213350.00"></span>
              <span class="cost-segment cost-direct_project" data-chart-block="direct_project" style="flex-grow: 126000.00"></span>
              <span class="cost-segment cost-productivity_loss" data-chart-block="productivity_loss" style="flex-grow: 25000.00"></span>
              <span class="cost-segment cost-parallel_running" data-chart-block="parallel_running" style="flex-grow: 100000.00"></span>
          </div>
          <ul class="cost-chart-values" role="list">
              <li>Running costs · <span class="cost-value" data-chart-value="running">EUR 213,350.00</span></li>
              <li>Direct project costs · <span class="cost-value" data-chart-value="direct_project">EUR 126,000.00</span></li>
              <li>Lost working time (internal estimate, not a payment) · <span class="cost-value" data-chart-value="productivity_loss">EUR 25,000.00</span></li>
              <li>Parallel running · <span class="cost-value" data-chart-value="parallel_running">EUR 100,000.00</span></li>
          </ul>
      </div>
  </div>
          <div class="cost-notes">
    <p class="note-text">Staying assumes no price change.</p>
      <p class="note-text" data-break-even="partial_exit">Partial move costs the same as staying if target operations cost EUR 20,440 a year (entered: EUR 6,000).</p>
      <p class="note-text" data-break-even="full_exit">Full move costs the same as staying if target operations cost EUR 39,130 a year (entered: EUR 12,000).</p>
  </div>
          <h3 id="cost-results-title">Costs by scenario</h3>
          <div class="table-scroll" role="region" aria-labelledby="cost-results-title" tabindex="0">
            <table class="cost-table" role="table">
              <caption data-invented-amounts>Amounts in this table are based on invented prices for the demonstration.</caption>
              <thead role="rowgroup">
    <tr role="row">
      <th scope="col" role="columnheader" data-label="Cost category">Cost category</th>
      <th scope="col" role="columnheader" data-label="Stay">Stay</th><th scope="col" role="columnheader" data-label="Partial move">Partial move</th><th scope="col" role="columnheader" data-label="Full move">Full move</th>
    </tr>
  </thead>
                <tbody data-block="running" role="rowgroup">
                  <tr role="row">
                    <th scope="rowgroup" role="rowheader" colspan="4" data-label="Cost category">Running costs</th>
                  </tr>
                    <tr role="row" data-cost-line="microsoft_licences">
                      <th scope="row" role="rowheader" data-label="Cost category">
    Current Microsoft licences
      <small data-cost-origin="calculated_with_examples">Calculated from sample inputs</small>
  </th>
                        <td role="cell" data-label="Stay" data-amount="500000.00">
                          EUR 500,000.00
                        </td>
                        <td role="cell" data-label="Partial move">
                          Not applicable
                        </td>
                        <td role="cell" data-label="Full move">
                          Not applicable
                        </td>
                    </tr>
                    <tr role="row" data-cost-line="other_it">
                      <th scope="row" role="rowheader" data-label="Cost category">
    Existing other IT costs
      <small data-cost-origin="calculated_with_examples">Calculated from sample inputs</small>
  </th>
                        <td role="cell" data-label="Stay" data-amount="100000.00">
                          EUR 100,000.00
                        </td>
                        <td role="cell" data-label="Partial move" data-amount="100000.00">
                          EUR 100,000.00
                        </td>
                        <td role="cell" data-label="Full move" data-amount="100000.00">
                          EUR 100,000.00
                        </td>
                    </tr>
                    <tr role="row" data-cost-line="retained_licences">
                      <th scope="row" role="rowheader" data-label="Cost category">
    Retained Microsoft licences
      <small data-cost-origin="calculated_with_examples">Calculated from sample inputs</small>
  </th>
                        <td role="cell" data-label="Stay">
                          Not applicable
                        </td>
                        <td role="cell" data-label="Partial move" data-amount="270000.00">
                          EUR 270,000.00
                        </td>
                        <td role="cell" data-label="Full move" data-amount="0.00">
                          EUR 0.00
                        </td>
                    </tr>
                    <tr role="row" data-cost-line="hosting">
                      <th scope="row" role="rowheader" data-label="Cost category">
    Hosting
      <small data-cost-origin="calculated_with_examples">Calculated from sample inputs</small>
  </th>
                        <td role="cell" data-label="Stay">
                          Not applicable
                        </td>
                        <td role="cell" data-label="Partial move" data-amount="15300.00">
                          EUR 15,300.00
                        </td>
                        <td role="cell" data-label="Full move" data-amount="43350.00">
                          EUR 43,350.00
                        </td>
                    </tr>
                    <tr role="row" data-cost-line="operations">
                      <th scope="row" role="rowheader" data-label="Cost category">
    Target system operations
      <small data-cost-origin="calculated_with_examples">Calculated from sample inputs</small>
  </th>
                        <td role="cell" data-label="Stay">
                          Not applicable
                        </td>
                        <td role="cell" data-label="Partial move" data-amount="30000.00">
                          EUR 30,000.00
                        </td>
                        <td role="cell" data-label="Full move" data-amount="60000.00">
                          EUR 60,000.00
                        </td>
                    </tr>
                    <tr role="row" data-cost-line="other_recurring">
                      <th scope="row" role="rowheader" data-label="Cost category">
    Other recurring target costs
      <small data-cost-origin="calculated_with_examples">Calculated from sample inputs</small>
  </th>
                        <td role="cell" data-label="Stay">
                          Not applicable
                        </td>
                        <td role="cell" data-label="Partial move" data-amount="7500.00">
                          EUR 7,500.00
                        </td>
                        <td role="cell" data-label="Full move" data-amount="10000.00">
                          EUR 10,000.00
                        </td>
                    </tr>
                  <tr class="subtotals" role="row">
                    <th scope="row" role="rowheader" data-label="Cost category">
    Subtotal
      <small data-cost-origin="calculated_with_examples">Calculated from sample inputs</small>
  </th>
                      <td role="cell" data-label="Stay" data-amount="600000.00">EUR 600,000.00</td>
                      <td role="cell" data-label="Partial move" data-amount="422800.00">EUR 422,800.00</td>
                      <td role="cell" data-label="Full move" data-amount="213350.00">EUR 213,350.00</td>
                  </tr>
                </tbody>
                <tbody data-block="direct_project" role="rowgroup">
                  <tr role="row">
                    <th scope="rowgroup" role="rowheader" colspan="4" data-label="Cost category">Direct project costs</th>
                  </tr>
                    <tr role="row" data-cost-line="one_time_migration">
                      <th scope="row" role="rowheader" data-label="Cost category">
    One-time migration
      <small data-cost-origin="calculated_with_examples">Calculated from sample inputs</small>
  </th>
                        <td role="cell" data-label="Stay">
                          Not applicable
                        </td>
                        <td role="cell" data-label="Partial move" data-amount="15000.00">
                          EUR 15,000.00
                        </td>
                        <td role="cell" data-label="Full move" data-amount="40000.00">
                          EUR 40,000.00
                        </td>
                    </tr>
                    <tr role="row" data-cost-line="application_adaptation">
                      <th scope="row" role="rowheader" data-label="Cost category">
    Application adaptation
      <small data-cost-origin="calculated_with_examples">Calculated from sample inputs</small>
  </th>
                        <td role="cell" data-label="Stay">
                          Not applicable
                        </td>
                        <td role="cell" data-label="Partial move" data-amount="4000.00">
                          EUR 4,000.00
                        </td>
                        <td role="cell" data-label="Full move" data-amount="10000.00">
                          EUR 10,000.00
                        </td>
                    </tr>
                    <tr role="row" data-cost-line="external_advice">
                      <th scope="row" role="rowheader" data-label="Cost category">
    External advice
      <small data-cost-origin="calculated_with_examples">Calculated from sample inputs</small>
  </th>
                        <td role="cell" data-label="Stay">
                          Not applicable
                        </td>
                        <td role="cell" data-label="Partial move" data-amount="3000.00">
                          EUR 3,000.00
                        </td>
                        <td role="cell" data-label="Full move" data-amount="8000.00">
                          EUR 8,000.00
                        </td>
                    </tr>
                    <tr role="row" data-cost-line="training">
                      <th scope="row" role="rowheader" data-label="Cost category">
    Training
      <small data-cost-origin="calculated_with_examples">Calculated from sample inputs</small>
  </th>
                        <td role="cell" data-label="Stay">
                          Not applicable
                        </td>
                        <td role="cell" data-label="Partial move" data-amount="24000.00">
                          EUR 24,000.00
                        </td>
                        <td role="cell" data-label="Full move" data-amount="68000.00">
                          EUR 68,000.00
                        </td>
                    </tr>
                  <tr class="subtotals" role="row">
                    <th scope="row" role="rowheader" data-label="Cost category">
    Subtotal
      <small data-cost-origin="calculated_with_examples">Calculated from sample inputs</small>
  </th>
                      <td role="cell" data-label="Stay" data-amount="0.00">EUR 0.00</td>
                      <td role="cell" data-label="Partial move" data-amount="46000.00">EUR 46,000.00</td>
                      <td role="cell" data-label="Full move" data-amount="126000.00">EUR 126,000.00</td>
                  </tr>
                </tbody>
                <tbody data-block="productivity_loss" role="rowgroup">
                  <tr role="row">
                    <th scope="rowgroup" role="rowheader" colspan="4" data-label="Cost category">Lost working time (internal estimate, not a payment)</th>
                  </tr>
                    <tr role="row" data-cost-line="productivity_loss">
                      <th scope="row" role="rowheader" data-label="Cost category">
    Lost working time (internal estimate, not a payment)
      <small data-cost-origin="calculated_with_examples">Calculated from sample inputs</small>
  </th>
                        <td role="cell" data-label="Stay">
                          Not applicable
                        </td>
                        <td role="cell" data-label="Partial move" data-amount="9000.00">
                          EUR 9,000.00
                        </td>
                        <td role="cell" data-label="Full move" data-amount="25000.00">
                          EUR 25,000.00
                        </td>
                    </tr>
                  <tr class="subtotals" role="row">
                    <th scope="row" role="rowheader" data-label="Cost category">
    Subtotal
      <small data-cost-origin="calculated_with_examples">Calculated from sample inputs</small>
  </th>
                      <td role="cell" data-label="Stay" data-amount="0.00">EUR 0.00</td>
                      <td role="cell" data-label="Partial move" data-amount="9000.00">EUR 9,000.00</td>
                      <td role="cell" data-label="Full move" data-amount="25000.00">EUR 25,000.00</td>
                  </tr>
                </tbody>
                <tbody data-block="parallel_running" role="rowgroup">
                  <tr role="row">
                    <th scope="rowgroup" role="rowheader" colspan="4" data-label="Cost category">Parallel running</th>
                  </tr>
                    <tr role="row" data-cost-line="parallel_running">
                      <th scope="row" role="rowheader" data-label="Cost category">
    Current Microsoft licences during parallel running
      <small data-cost-origin="calculated_with_examples">Calculated from sample inputs</small>
  </th>
                        <td role="cell" data-label="Stay">
                          Not applicable
                        </td>
                        <td role="cell" data-label="Partial move" data-amount="50000.00">
                          EUR 50,000.00
                        </td>
                        <td role="cell" data-label="Full move" data-amount="100000.00">
                          EUR 100,000.00
                        </td>
                    </tr>
                  <tr class="subtotals" role="row">
                    <th scope="row" role="rowheader" data-label="Cost category">
    Subtotal
      <small data-cost-origin="calculated_with_examples">Calculated from sample inputs</small>
  </th>
                      <td role="cell" data-label="Stay" data-amount="0.00">EUR 0.00</td>
                      <td role="cell" data-label="Partial move" data-amount="50000.00">EUR 50,000.00</td>
                      <td role="cell" data-label="Full move" data-amount="100000.00">EUR 100,000.00</td>
                  </tr>
                </tbody>
              <tbody role="rowgroup">
                <tr class="totals" role="row">
                  <th scope="row" role="rowheader" data-label="Cost category">
    Five-year total
      <small data-cost-origin="calculated_with_examples">Calculated from sample inputs</small>
  </th>
                    <td data-scenario="stay" data-total="600000.00" role="cell" data-label="Stay">EUR 600,000.00</td>
                    <td data-scenario="partial_exit" data-total="527800.00" role="cell" data-label="Partial move">EUR 527,800.00</td>
                    <td data-scenario="full_exit" data-total="464350.00" role="cell" data-label="Full move">EUR 464,350.00</td>
                </tr>
                <tr role="row">
                  <th scope="row" role="rowheader" data-label="Cost category">
    Difference from staying
      <small data-cost-origin="calculated_with_examples">Calculated from sample inputs</small>
  </th>
                    <td role="cell" data-label="Stay">EUR 0.00</td>
                    <td role="cell" data-label="Partial move">EUR -72,200.00</td>
                    <td role="cell" data-label="Full move">EUR -135,650.00</td>
                </tr>
              </tbody>
            </table>
          </div>
          <p class="muted">Amounts are rounded to two decimal places for display. Totals use the unrounded amounts, so the displayed lines can differ slightly from their displayed sum.</p>
          <p class="note-text">Amounts are as entered. The inputs file does not say whether they include VAT.</p>
          <details class="cost-inputs">
            <summary id="cost-inputs-title"><svg class="icon" viewBox="0 -960 960 960" aria-hidden="true" focusable="false"><path d="M504-480 348-636q-11-11-11-28t11-28q11-11 28-11t28 11l184 184q6 6 8.5 13t2.5 15q0 8-2.5 15t-8.5 13L404-268q-11 11-28 11t-28-11q-11-11-11-28t11-28l156-156Z"/></svg>Cost inputs</summary>
            <div class="table-scroll" role="region" aria-labelledby="cost-inputs-title" tabindex="0">
              <table class="cost-table" role="table">
                <caption data-invented-amounts>Amounts in this table are based on invented prices for the demonstration.</caption>
                <thead role="rowgroup">
    <tr role="row">
      <th scope="col" role="columnheader" data-label="Input">Input</th>
      <th scope="col" role="columnheader" data-label="Stay">Stay</th><th scope="col" role="columnheader" data-label="Partial move">Partial move</th><th scope="col" role="columnheader" data-label="Full move">Full move</th>
    </tr>
  </thead>
                <tbody role="rowgroup">
  <tr data-cost-input="microsoft_licences_per_year" role="row">
    <th scope="row" role="rowheader" data-label="Input">
      Current Microsoft licences per year
        <small data-cost-origin="invented">Invented amount</small>
    </th>
      <td role="cell" data-label="Stay">
        EUR 100,000.00
      </td>
      <td role="cell" data-label="Partial move">
        EUR 100,000.00
      </td>
      <td role="cell" data-label="Full move">
        EUR 100,000.00
      </td>
  </tr>
  <tr data-cost-input="other_it_per_year" role="row">
    <th scope="row" role="rowheader" data-label="Input">
      Existing other IT costs per year
        <small data-cost-origin="invented">Invented amount</small>
    </th>
      <td role="cell" data-label="Stay">
        EUR 20,000.00
      </td>
      <td role="cell" data-label="Partial move">
        EUR 20,000.00
      </td>
      <td role="cell" data-label="Full move">
        EUR 20,000.00
      </td>
  </tr>
  <tr data-cost-input="users" role="row">
    <th scope="row" role="rowheader" data-label="Input">
      Users on the target system
        <small data-cost-origin="sample_input">Sample input</small>
    </th>
      <td role="cell" data-label="Stay">
        Not applicable
      </td>
      <td role="cell" data-label="Partial move">
        30
      </td>
      <td role="cell" data-label="Full move">
        85
      </td>
  </tr>
  <tr data-cost-input="retained_microsoft_licences_per_year" role="row">
    <th scope="row" role="rowheader" data-label="Input">
      Retained Microsoft licences per year
        <small data-cost-origin="invented">Invented amount</small>
    </th>
      <td role="cell" data-label="Stay">
        Not applicable
      </td>
      <td role="cell" data-label="Partial move">
        EUR 60,000.00
      </td>
      <td role="cell" data-label="Full move">
        EUR 0.00
      </td>
  </tr>
  <tr data-cost-input="hosting_per_user_per_month" role="row">
    <th scope="row" role="rowheader" data-label="Input">
      Hosting per user per month
        <small data-cost-origin="invented">Invented amount</small>
    </th>
      <td role="cell" data-label="Stay">
        Not applicable
      </td>
      <td role="cell" data-label="Partial move">
        EUR 8.50
      </td>
      <td role="cell" data-label="Full move">
        EUR 8.50
      </td>
  </tr>
  <tr data-cost-input="operations_per_year" role="row">
    <th scope="row" role="rowheader" data-label="Input">
      Target system operations per year
        <small data-cost-origin="invented">Invented amount</small>
    </th>
      <td role="cell" data-label="Stay">
        Not applicable
      </td>
      <td role="cell" data-label="Partial move">
        EUR 6,000.00
      </td>
      <td role="cell" data-label="Full move">
        EUR 12,000.00
      </td>
  </tr>
  <tr data-cost-input="other_recurring_per_year" role="row">
    <th scope="row" role="rowheader" data-label="Input">
      Other target costs per year
        <small data-cost-origin="invented">Invented amount</small>
    </th>
      <td role="cell" data-label="Stay">
        Not applicable
      </td>
      <td role="cell" data-label="Partial move">
        EUR 1,500.00
      </td>
      <td role="cell" data-label="Full move">
        EUR 2,000.00
      </td>
  </tr>
  <tr data-cost-input="one_time_migration" role="row">
    <th scope="row" role="rowheader" data-label="Input">
      One-time migration
        <small data-cost-origin="invented">Invented amount</small>
    </th>
      <td role="cell" data-label="Stay">
        Not applicable
      </td>
      <td role="cell" data-label="Partial move">
        EUR 15,000.00
      </td>
      <td role="cell" data-label="Full move">
        EUR 40,000.00
      </td>
  </tr>
  <tr data-cost-input="application_adaptation" role="row">
    <th scope="row" role="rowheader" data-label="Input">
      Application adaptation
        <small data-cost-origin="invented">Invented amount</small>
    </th>
      <td role="cell" data-label="Stay">
        Not applicable
      </td>
      <td role="cell" data-label="Partial move">
        EUR 4,000.00
      </td>
      <td role="cell" data-label="Full move">
        EUR 10,000.00
      </td>
  </tr>
  <tr data-cost-input="external_advice" role="row">
    <th scope="row" role="rowheader" data-label="Input">
      External advice
        <small data-cost-origin="invented">Invented amount</small>
    </th>
      <td role="cell" data-label="Stay">
        Not applicable
      </td>
      <td role="cell" data-label="Partial move">
        EUR 3,000.00
      </td>
      <td role="cell" data-label="Full move">
        EUR 8,000.00
      </td>
  </tr>
  <tr data-cost-input="training_days_per_person" role="row">
    <th scope="row" role="rowheader" data-label="Input">
      Training days per person
        <small data-cost-origin="sample_input">Sample input</small>
    </th>
      <td role="cell" data-label="Stay">
        Not applicable
      </td>
      <td role="cell" data-label="Partial move">
        2
      </td>
      <td role="cell" data-label="Full move">
        2
      </td>
  </tr>
  <tr data-cost-input="training_day_rate" role="row">
    <th scope="row" role="rowheader" data-label="Input">
      Training cost per person per day
        <small data-cost-origin="invented">Invented amount</small>
    </th>
      <td role="cell" data-label="Stay">
        Not applicable
      </td>
      <td role="cell" data-label="Partial move">
        EUR 400.00
      </td>
      <td role="cell" data-label="Full move">
        EUR 400.00
      </td>
  </tr>
  <tr data-cost-input="training_staff" role="row">
    <th scope="row" role="rowheader" data-label="Input">
      People to train
        <small data-cost-origin="sample_input">Sample input</small>
    </th>
      <td role="cell" data-label="Stay">
        Not applicable
      </td>
      <td role="cell" data-label="Partial move">
        30
      </td>
      <td role="cell" data-label="Full move">
        85
      </td>
  </tr>
  <tr data-cost-input="productivity_loss" role="row">
    <th scope="row" role="rowheader" data-label="Input">
      Lost working time (internal estimate, not a payment)
        <small data-cost-origin="invented">Invented amount</small>
    </th>
      <td role="cell" data-label="Stay">
        Not applicable
      </td>
      <td role="cell" data-label="Partial move">
        EUR 9,000.00
      </td>
      <td role="cell" data-label="Full move">
        EUR 25,000.00
      </td>
  </tr>
  <tr data-cost-input="parallel_running_months" role="row">
    <th scope="row" role="rowheader" data-label="Input">
      Months running both systems
        <small data-cost-origin="sample_input">Sample input</small>
    </th>
      <td role="cell" data-label="Stay">
        Not applicable
      </td>
      <td role="cell" data-label="Partial move">
        6
      </td>
      <td role="cell" data-label="Full move">
        12
      </td>
  </tr>
                </tbody>
              </table>
            </div>
          </details>
        </div>
      </div>
    </section>
```

</details>

<details>
<summary>Non-profit full-move tile</summary>

```html
<li data-cost-tile="full_exit">
                <p class="tile-label">Full move · five-year total</p>
                  <span class="figure-num"><span class="status unknown"><svg class="icon" viewBox="0 -960 960 960" aria-hidden="true" focusable="false"><path d="M478-240q21 0 35.5-14.5T528-290q0-21-14.5-35.5T478-340q-21 0-35.5 14.5T428-290q0 21 14.5 35.5T478-240Zm2 160q-83 0-156-31.5T197-197q-54-54-85.5-127T80-480q0-83 31.5-156T197-763q54-54 127-85.5T480-880q83 0 156 31.5T763-763q54 54 85.5 127T880-480q0 83-31.5 156T763-197q-54 54-127 85.5T480-80Zm4-572q25 0 43.5 16t18.5 40q0 22-13.5 39T502-525q-23 20-40.5 44T444-427q0 14 10.5 23.5T479-394q15 0 25.5-10t13.5-25q4-21 18-37.5t30-31.5q23-22 39.5-48t16.5-58q0-51-41.5-83.5T484-720q-38 0-72.5 16T359-655q-7 12-4.5 25.5T368-609q14 8 29 5t25-17q11-15 27.5-23t34.5-8Z"/></svg> Unknown</span></span>
                  <p class="tile-title">Total of known blocks EUR 40,600</p>
                  <p>
  <a class="more" href="#costs-missing">1 input is missing<svg class="icon" viewBox="0 -960 960 960" aria-hidden="true" focusable="false"><path d="M504-480 348-636q-11-11-11-28t11-28q11-11 28-11t28 11l184 184q6 6 8.5 13t2.5 15q0 8-2.5 15t-8.5 13L404-268q-11 11-28 11t-28-11q-11-11-11-28t11-28l156-156Z"/></svg></a></p>
              </li>
```

</details>

<details>
<summary>Non-profit full-move chart row</summary>

```html
      <div class="cost-chart-row" data-chart-scenario="full_exit">
        <div class="cost-chart-heading">
          <h3>Full move</h3>
            <p>Total unknown</p>
        </div>
          <span class="cost-segment is-unknown" aria-hidden="true"><svg class="icon" viewBox="0 -960 960 960" aria-hidden="true" focusable="false"><path d="M478-240q21 0 35.5-14.5T528-290q0-21-14.5-35.5T478-340q-21 0-35.5 14.5T428-290q0 21 14.5 35.5T478-240Zm2 160q-83 0-156-31.5T197-197q-54-54-85.5-127T80-480q0-83 31.5-156T197-763q54-54 127-85.5T480-880q83 0 156 31.5T763-763q54 54 85.5 127T880-480q0 83-31.5 156T763-197q-54 54-127 85.5T480-80Zm4-572q25 0 43.5 16t18.5 40q0 22-13.5 39T502-525q-23 20-40.5 44T444-427q0 14 10.5 23.5T479-394q15 0 25.5-10t13.5-25q4-21 18-37.5t30-31.5q23-22 39.5-48t16.5-58q0-51-41.5-83.5T484-720q-38 0-72.5 16T359-655q-7 12-4.5 25.5T368-609q14 8 29 5t25-17q11-15 27.5-23t34.5-8Z"/></svg></span>
            <p class="cost-known-blocks">Total of known blocks EUR 40,600.00</p>
            <ul class="cost-chart-values" role="list">
                <li>Lost working time (internal estimate, not a payment) · <span data-chart-value="productivity_loss"><span class="status unknown"><svg class="icon" viewBox="0 -960 960 960" aria-hidden="true" focusable="false"><path d="M478-240q21 0 35.5-14.5T528-290q0-21-14.5-35.5T478-340q-21 0-35.5 14.5T428-290q0 21 14.5 35.5T478-240Zm2 160q-83 0-156-31.5T197-197q-54-54-85.5-127T80-480q0-83 31.5-156T197-763q54-54 127-85.5T480-880q83 0 156 31.5T763-763q54 54 85.5 127T880-480q0 83-31.5 156T763-197q-54 54-127 85.5T480-80Zm4-572q25 0 43.5 16t18.5 40q0 22-13.5 39T502-525q-23 20-40.5 44T444-427q0 14 10.5 23.5T479-394q15 0 25.5-10t13.5-25q4-21 18-37.5t30-31.5q23-22 39.5-48t16.5-58q0-51-41.5-83.5T484-720q-38 0-72.5 16T359-655q-7 12-4.5 25.5T368-609q14 8 29 5t25-17q11-15 27.5-23t34.5-8Z"/></svg> Unknown</span></span></li>
            </ul>
      </div>
```

</details>

## Self-check

All three task chains and their source guards passed. Both site demos, the fixture and this summary are present.

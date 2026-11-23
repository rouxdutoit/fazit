# RR-10 summary

Implemented all 17 review items in the working tree. The published English and German demos were rebuilt from the town sample. The browser captures cover the site and the offline report.

## Changes by item

| Item | Files | Change |
| --- | --- | --- |
| 1 | `site/{index.html,de/index.html,style.css}` | The sample report action uses an outlined secondary capsule with the description symbol. It shares the primary button's height, radius and 16 px gap. The actions wrap into two equal-width rows when their combined width exceeds the space available. |
| 2 | `src/fazit/templates/report.html.j2` | The category select has a quiet capsule and a keyboard focus ring. Supporting browsers show a rounded picker with a soft shadow, a dark-mode hairline, a selected fill and aligned option labels beside the native tick. The select closes after selection and continues to combine with the status radios through CSS. |
| 3 | `src/fazit/templates/report.html.j2`, `site/{index.html,de/index.html,style.css}` | Shared capsule styling centres the status symbol and the label. The text is trimmed to its capital height where supported. The same badges appear in the report cards, summary rows, home Mail card and replacement status cells. The replacement chevron is centred on the status capsule. |
| 4 | Eight `site/images/readiness-*.webp` files, `site/{index.html,de/index.html}` | The crop begins at the summary heading and ends after the complete All blockers link, with 16 CSS px of padding at each edge. The preceding rule and following section heading are outside the frame. All four definitions and the full Telephony row remain visible. The picture dimensions and download sizes match the files. |
| 5 | `site/style.css` | The divider uses both edges of the content grid track. The command block fills the same track as the cards and lists. |
| 6 | `site/{index.html,de/index.html,style.css}` | Each home section begins with the shared lead style. The report contents and project status sections bring existing copy forward to supply their introductions. Subsequent paragraphs use the body treatment, with caption styling for notes. |
| 7 | `site/style.css`, `src/fazit/templates/report.html.j2` | Inline code uses 0.9 em, preserving the dedicated sizes for command blocks and the preview's title bar. |
| 8 | `src/fazit/templates/report.html.j2` | Area links use the text colour and a chevron in summary rows, action groups and the open-evidence list. Standalone navigation links retain the quiet treatment. |
| 9 | `src/fazit/templates/report.html.j2` | Status and coverage counts use body type and the same right-aligned count column. Needed functions are a body-size list with links to their rows. |
| 10 | `src/fazit/report.py`, `src/fazit/locales/{en,de}.yaml` | Transfer actions read as sentences that name the work. The Telephony action uses the requested wording. Locale entries handle several individual functions, and a shared action still names all the functions in a grouped request. |
| 11 | `src/fazit/report.py`, `src/fazit/templates/report.html.j2`, `src/fazit/locales/{en,de}.yaml`, `site/{index.html,de/index.html}` | Area cards use the same registered questions as the summary, with the responsible role and the actual `inputs.yaml` field where one exists. Collector details and specific remedies remain available for failed, skipped and incomplete collection. The home Mail example matches the report card. |
| 12 | `src/fazit/report.py`, `src/fazit/templates/report.html.j2`, `src/fazit/locales/{en,de}.yaml` | Each open-evidence entry starts with its question or grouped questions. It then shows the area links, the responsible role, the source or input field, and up to one sentence of guidance. The shared-mailbox entry names the Exchange export once. Each area link appears once per entry, even when several findings refer to it. |
| 13 | `src/fazit/i18n.py`, `src/fazit/templates/report.html.j2`, `src/fazit/locales/{en,de}.yaml` | Currency displays omit zero cents, retain cents when present and use a true minus for a negative table value. One caption covers calculated amounts in Costs, and one covers the council summary tiles. Input rows label provenance when it differs from the section's stated input origin. The rounding note explains the display precision. |
| 14 | `src/fazit/templates/report.html.j2` | A common check date appears once in the replacement table caption. Distinct dates and the generic profile's no-check labels remain in a dedicated column. The desktop column widths leave room for full dates and both badges. |
| 15 | `src/fazit/i18n.py`, `src/fazit/templates/report.html.j2`, `site/{index.html,de/index.html}` | Dates use non-breaking spaces within each date, including dates at both ends of a period. The format applies to headers, target lines, Closer look and the home Mail example. |
| 16 | `src/fazit/templates/report.html.j2`, `src/fazit/locales/{en,de}.yaml`, `site/{index.html,de/index.html,style.css}` | Evidence counts sit below the disclosure label in secondary footnote type at every width. |
| 17 | `src/fazit/templates/report.html.j2`, `src/fazit/locales/{en,de}.yaml` | The replacements caption explains why licences are omitted from the table in one sentence. The appendix relies on that explanation. |

## Implementation choices

- Both home button pairs stack at 360 px with the existing gap and gutters. The English pair needs 329 px and the German pair needs 363 px. Each has 328 px available at that viewport.
- The category menu uses browser-provided option selection, focus management and the checkmark. Firefox uses the native fallback. [Chrome's customizable select guide](https://developer.chrome.com/docs/modern-web-guidance/guides/forms/branded-select-styling)
- The print stylesheet retains the compact scope layout so the complete council summary fits on the first A4 page. Its calculation origin appears once for the three tiles. The cost section carries its own caption for readers who go directly to it.
- The refreshed preview frames measure 2016 × 1116 and 800 × 1312 pixels in English, and 2016 × 1166 and 800 × 1418 in German. Each light and dark pair uses matching dimensions.

## Test changes

| File | Changed expectations and added checks |
| --- | --- |
| `tests/test_cli.py` | `test_report_shows_function_mapping_and_workload_evidence` checks common dates in the caption and other dates in their rows. The appendix still supplies dated references and the same evidence and status links are checked. The scan-only, partial-coverage, demo-copy and scan-date tests expect non-breaking spaces in the rendered dates. |
| `tests/test_costs.py` | `test_money_format` and the two chart copy tests expect whole units where applicable and a true minus. The tile and chart tests check for one calculation caption per section. The section intro test normalises whitespace when comparing a date with surrounding prose. `test_demo_cost_comparison` also checks the rendered negative difference. |
| `tests/test_evidence_cli.py` | `test_disagreeing_provided_answers_remain_visible_and_undecided` expects non-breaking dates for the same evidence and keeps its status, comparison and provenance assertions. |
| `tests/test_inputs.py`, `tests/test_locales.py` | The supplied-date display test and `test_formatter` expect non-breaking spaces within dates and date ranges. |
| `tests/test_report.py` | The replacement symbol and status test follows the new badge markup and date column rule. A new bilingual mixed-date case checks every row's date. The open-point tests check the new layout while still comparing every finding, collector and gap with its source, including every gap's linked areas. The manual-question test also verifies the card's question, owner and input field. Grouped action, scope link, card badge, evidence count and run-detail tests check the revised presentation with their original values. |
| `tests/test_rules.py` | The reviewed-mapping test expects the same date with non-breaking spaces. The open-evidence test checks the new association of the question, area link and one-sentence guidance. The Windows software test still checks the confirmed dependency and partial evidence and now checks the specific missing question and input field. |
| `tests/test_simulation.py` | The independent cost display expectation uses the requested whole-unit and minus formatting. The exact-fraction comparison still checks every cost line, subtotal, result and difference. The invented-price and offline CSP checks retain their assertions. |
| `.shots/report-redesign/check.mjs` | The browser check enters and commits the enhanced picker with the keyboard and checks Escape. It checks the shared print caption, missing-input links, all three totals and the first-page section boundary. Firefox's tab check ends at the final disclosure, where baseline headless Firefox retained focus. Both filter controls must appear once before that boundary. |

## Verification

| Check | Result |
| --- | --- |
| `uv run pytest -q` | 955 passed in 177.08 seconds. |
| `uv run ruff check .` | Passed. |
| `uv run ruff format --check .` | Passed. 178 files formatted. |
| `uv run python site/check_site.py` | Passed. Checked 22 pages and 859 references. |
| `uv run fazit demo --lang de` and `uv run fazit demo --lang en` | Passed in fresh temporary output directories. Both generated reports match the published HTML byte for byte. |
| RR-02 and RR-04 Chromium checks | Passed for both samples and languages at 1280 and 360 px in both themes. Verified the category and status combinations, focus, disabled choices, empty states, fragment navigation and print behaviour. Report pages opened offline with scripting disabled and zero external requests. |
| Native select in Firefox | Passed all 16 sample, language, viewport and theme filter cases. |
| Narrow layouts and dated rows | All 22 site pages have no horizontal overflow at 360 px in either theme. All three report profiles passed page and replacement-cell width checks at 12 widths from 320 to 1280 px in both languages and themes. Each rendered date occupied one line. |
| A4 page one | Both samples and the all-Unknown report fit the full council summary on the first page in both languages with backgrounds enabled and disabled. Compared all 12 first pages with the starting revision after accounting for non-breaking spaces and repeated cost origins. Next steps start on page two. Filtering preserves PDF text and pagination for both samples. |
| Screen captures and previews | Verified 40 PNGs at the requested dimensions and eight lossless WebP previews. The previews contain the full blocker row and link, with four definitions and no clipped content. |
| `git diff --check` | Passed. |

The [viewport screenshots](../../.shots/report-redesign/rr10/) cover the hero, open category menu, the Mail card with both badges, Costs and Replacements. The [print renders](../../.shots/report-redesign/rr10/print/) show the 12 first A4 pages.

## German copy

| Location or locale key | German |
| --- | --- |
| Home, report contents lead | Der Bericht zeigt, welche Funktionen Ihre Organisation benötigt. |
| Home, project status lead | Sie können Fazit aus dem Quellcode starten und Berichte aus den Beispieldaten mit eigenen Antworten und Kosten erstellen. |
| Home, current project status | Die Messwerte in den Beispielen sind simuliert. Das Paket ist noch nicht auf PyPI veröffentlicht. |
| Home, demo download | HTML herunterladen, 423 KB |
| `readiness.evidence` | Nachweise |
| `readiness.evidence_summary` | {measured} erhoben, {provided} bereitgestellt, {unknown} unbekannt |
| `path.who_answers` | Wer gibt Auskunft: |
| `path.source` | Quelle: |
| `path.input_field` | Feld in inputs.yaml: |
| `path.finding_question` | Was geht aus den Nachweisen zu „{finding}“ hervor? |
| `path.area_question` | Welche Nachweise fehlen im Bereich {area}? |
| `path.collector_question` | Welche Nachweise fehlen aus dieser Erhebung? |
| `path.guidance.not_in_export` | Erfragen Sie die fehlende Angabe bei der fachlich verantwortlichen Stelle. |
| `path.guidance.needs_recipient_export` | Lassen Sie die Zahl gesondert von der für E-Mail zuständigen Stelle ermitteln. |
| `path.guidance.source_not_supplied` | Klären Sie, aus welcher Quelle die fehlenden Daten stammen. |
| `path.transfer_actions.not_available` | Die fachlich verantwortliche Stelle und die IT-Abteilung legen fest, womit sie {functions} nach dem Umstieg ersetzen. |
| `path.transfer_actions.not_available.device_management` | Die fachlich verantwortliche Stelle und die IT-Abteilung legen fest, wie die Geräte nach dem Umstieg verwaltet werden. |
| `path.transfer_actions.not_available.desktop_operating_system` | Die fachlich verantwortliche Stelle und die IT-Abteilung legen fest, wie das Betriebssystem für die Arbeitsplatzrechner nach dem Umstieg bereitgestellt wird. |
| `path.transfer_actions.not_available.windows_applications` | Die fachlich verantwortliche Stelle und die IT-Abteilung legen fest, wie reine Windows-Anwendungen nach dem Umstieg betrieben werden. |
| `path.transfer_actions.not_available.automation_and_low_code` | Die fachlich verantwortliche Stelle und die IT-Abteilung legen fest, wie die automatisierten Abläufe und Low-Code-Anwendungen nach dem Umstieg betrieben werden. |
| `path.transfer_actions.not_available.telephony`, town demo | Die fachlich verantwortliche Stelle und die IT-Abteilung legen fest, wie Teams Phone und Anrufe ins öffentliche Telefonnetz nach dem Umstieg bereitgestellt werden. |
| `costs.rounding` | Die Gesamtkosten in der Übersicht und die Beträge im Vergleich der jährlichen Betriebskosten sind auf ganze Währungseinheiten gerundet. Die Tabellen zeigen bei Bedarf zwei Nachkommastellen. Die Summen beruhen auf ungerundeten Beträgen und können daher von der Summe der angezeigten Beträge abweichen. |
| `moves.licences_excluded` | Lizenzen stehen nicht in dieser Tabelle, weil hier keine Funktion zu übertragen ist. |
| `moves.area_excluded` | Der Bereich {area} steht nicht in dieser Tabelle, weil hier keine Funktion zu übertragen ist. |

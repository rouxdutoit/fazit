# RR-09 summary

Completed all RR-09 items in plan order, with the command component (17) before the final review (16). The work started from a clean working tree at `5261f77`. All changes are local to the working tree.

## Changes by task

| Item | Files | Changes |
| --- | --- | --- |
| 1 | `src/fazit/templates/report.html.j2`, `src/fazit/locales/{en,de}.yaml` | Added a sticky 24 px inset index from 880 px and a native disclosure on narrower screens. The report's headings sit above their content in the right column. Both index variants use the same seven RR-04 destinations and labels. The skip link takes keyboard focus to the report. Scroll tracking and fragment highlighting are CSS-only. |
| 2 | `src/fazit/templates/report.html.j2`, `src/fazit/locales/{en,de}.yaml` | Kept the status radios, counts and disabled states in one segmented control. Replaced the category track with a labelled native select. It displays the selected category and combines with status through `:has()` and `option:checked`. The empty state names both reset options. |
| 3 | `src/fazit/templates/report.html.j2` | Aligned the four status names and tabular counts on one baseline, with the counts in a fixed 4ch column. Each definition sits below its name in the footnote size and secondary colour. |
| 4 | `src/fazit/templates/report.html.j2` | Applied the standalone link style and first-line chevron to area names and other report jumps. The thin grey underline remains available for links in running text. Reviewed the index, area and open-point links, replacement links and cost links together. |
| 5 | `src/fazit/templates/report.html.j2`, `src/fazit/locales/{en,de}.yaml` | The desktop replacements table fills the reading column and reserves width for the function and replacement. Below 70 rem each function heads a row with labelled coverage, replacement and need. The check date and linked area status retain their labels. Need comes from the existing transfer-gap evidence, with provenance where known. |
| 6 | `src/fazit/templates/report.html.j2`, `site/style.css` | Used 24 px card padding, 12 px card and heading gaps, and 32 px subsection gaps where elements share a rank. Set the page rhythm to 48 px between section boundaries and content on desktop, and 32 px on phones. Tightened the opening and its simulated-data caption so the first blocker fits at 1280 × 800. |
| 7 | `site/{index.html,de/index.html,style.css,check_site.py}` | Removed both figures strips and their CSS. Put the 14 areas, three named targets, two languages and offline file in a single caption sentence per home page. The checker reads the area count from the demo cards and checks the caption and both pilot pages. |
| 8 | `src/fazit/templates/report.html.j2`, `src/fazit/locales/{en,de}.yaml`, `site/{index.html,de/index.html,style.css}`, `DESIGN.md`, `DECISIONS.md` | Used the area name as the heading, with the category beneath it and status and incomplete-evidence badges at the right or below on phones. Matched the home Mail card to the demo Mail card, including the reason, action, evidence and target order. Updated the design rule and recorded the founder's decision as D36. |
| 9 | `site/{index.html,de/index.html,style.css,check_site.py}` | Replaced the comma-separated tally with an inline list that wraps on phones. Each status keeps its symbol, label and count together. The checker compares the list's labels, order and counts with the demo. |
| 10 | `src/fazit/report.py`, `src/fazit/templates/report.html.j2`, `src/fazit/locales/{en,de}.yaml` | Grouped actions by area under the existing stay and move headings. Combined repeated transfer-template actions per area and included the affected function names. Specific actions and their order stay visible. |
| 11 | `src/fazit/report.py`, `src/fazit/templates/report.html.j2`, `src/fazit/locales/{en,de}.yaml` | Replaced generic missing-answer instructions with the actual question in the summary and working list. The working list shows the input key when one exists. It retains proof requests, ownership, grouping and any specific remedy. |
| 12 | `src/fazit/templates/report.html.j2` | Gave each coverage count its own label and right-aligned number. Needed functions are standalone links to their individual rows in Replacements. Existing target scope totals and the coverage terminology carry through. |
| 13 | `src/fazit/templates/report.html.j2`, `src/fazit/locales/{en,de}.yaml` | Moved the five-year heading above the tiles and reserved each tile label for its scenario. The desktop totals share a baseline, with space for existing origins and comparisons. Set `hyphens: manual` across the report. |
| 14 | `src/fazit/templates/report.html.j2` | Stacked blocker and open-area rows with the same heading, category, badges and description layout. The All blockers fragment reveals its group even during restrictive filtering. |
| 15 | `src/fazit/templates/report.html.j2` | Applied and checked the same 32 px gap after the status list and between all subsequent summary subsections. |
| 17 | `site/{index.html,de/index.html,start/index.html,de/start/index.html,style.css,site.js,check_site.py}` | Used identical command markup on Home and Start for each language. The button has a `btn-icon` symbol, a success tick, a live status and a manual-copy fallback. Each block has separate feedback and timing. The muted prompt stays out of the copied text. The checker verifies both pages and the German `--lang de`. |
| 16 | `src/fazit/templates/report.html.j2`, `src/fazit/locales/{en,de}.yaml`, `site/style.css` | In Costs, put provenance below the chart total, matched label and value type in the phone tables and aligned the scenario rows. In Replacements, gave the need and status columns room for their German labels and moved the incomplete-evidence note below the status link. In Closer look, widened the useful desktop columns and made table notes span the phone row. In Recorded inventory, let service-plan details use the full row on phones and aligned the inventory tiles to the shared padding. In the Appendix, regularised the gaps around disclosures, headings and run-detail lists. Kept Microsoft 365 on one line in the title, corrected the singular scope sentence and aligned wrapped command lines with the command text. Constrained the area groups to the reading column so long German titles stay inside the card. |
| Verification and assets | `tests/{test_report.py,test_rules.py,test_costs.py}`, `site/demo/{en,de}/index.html`, eight `site/images/readiness-*.webp`, `site/og.png`, `site/{index.html,de/index.html}`, `.shots/report-redesign/` | Updated affected presentation assertions and added coverage for grouped transfer actions and named input questions. Rebuilt both demos, all eight homepage previews and the social image. Updated the download sizes and checked the existing image alternatives against every frame. Captured and inspected the responsive report, site and print views. |

## Verification

| Check | Result |
| --- | --- |
| `uv run pytest -q` | 953 passed. |
| `uv run ruff check .` | Passed. |
| `uv run ruff format --check .` | Passed. Ruff found 172 formatted files. |
| `uv run fazit demo --lang de` and `uv run fazit demo --lang en` | Passed with explicit temporary output directories. The two generated HTML files match the published demos byte for byte. |
| `uv run python site/check_site.py` | Checked 22 pages and 885 references. No errors. |
| RR-02 and RR-04 browser checks, with RR-05 print and site comparisons | Passed in Chromium. Both samples and languages passed the status/category combinations, zero-count and empty states, selected category labels, keyboard and pointer interaction, fragment navigation and disclosure checks. The report opened offline, with scripting disabled, embedded fonts loaded and zero external requests. Checked 360 px and 1280 px in light and dark, with the site comparison also at 375 px. |
| Index fallback | With Chromium's CSS scroll-target group feature disabled, fragment highlighting passed in both languages at both widths. The regular run verified sticky positioning, scroll-driven highlighting and phone disclosure focus. |
| Breakpoints | At 12 widths from 320 to 1280 px, both town languages passed viewport and replacements-cell width checks for openDesk, Nextcloud and the product-neutral checklist. The check covered both sides of the index and table breakpoints. |
| Home and Start command | Passed all eight language, page and width combinations. Tested clipboard success and denial, exact command text, the tick and screen-reader message, manual selection, independent feedback for two blocks, and text availability with scripting disabled. |
| A4 | Both samples and the all-Unknown report fit the council summary on page one in both languages with either background setting. Index, skip link and filters are hidden. Next steps start on page two. For both samples, changing the filter left the PDF text and pagination identical. |
| Homepage previews and social image | All eight WebPs retained the RR-05 dimensions and matched their source PNGs pixel for pixel. Each shows four definitions and the complete Telephony row. File sizes are 38,736–44,234 bytes. The light social image is 1200 × 630 and 60,546 bytes. |
| Source comparison and `git diff --check` | Passed. About pages, edited pages' footers, preview window controls, D31 and the report/site CSPs match the starting revision. The report contains no script or readiness bar. |

### A4 results

| Report | Total pages | Next steps / Costs / Appendix |
| --- | ---: | --- |
| Town EN | 36 | 2 / 19 / 29 |
| Town DE | 38 | 2 / 20 / 30 |
| Non-profit EN | 32 | 2 / 17 / 26 |
| Non-profit DE | 33 | 2 / 18 / 27 |
| All-Unknown EN | 28 | First-page check passed |
| All-Unknown DE | 29 | First-page check passed |

### Screenshots and PDFs

The 44 requested report screenshots are in [.shots/report-redesign/rr09/](../../.shots/report-redesign/rr09/), grouped by language, width and colour scheme. Desktop screenshots show the sticky index at the start and while scrolled. The phone screenshots show it closed and open. Each combination has the summary, filters, a card group and replacements.

The [detail screenshots](../../.shots/report-redesign/rr09/detail/) include scope, cost tiles, next steps, open questions, Costs, Closer look, inventory and licence disclosures, and the Appendix. The [site screenshots](../../.shots/report-redesign/rr09/site/) cover the preview with window controls, the Mail card, the tally and both command examples. The [print folder](../../.shots/report-redesign/rr09/print/) contains 12 full A4 PDFs and their first-page PNGs, one with backgrounds and one without for every sample and language. Inspected the report and site screenshots and the rendered A4 first pages.

## Deviations and implementation choices

- D32 already records RR-07's target-profile decision. The new badge decision is D36, dated 2026-11-22.
- The two-column breakpoint remains 880 px. The index occupies the left column and the section headings sit above the right-column content. Recorded inventory sits between the Closer look and Appendix destinations, following the seven-link RR-04 index. Browsers that support CSS scroll tracking follow the section in view. Other browsers with `:has()` mark the selected fragment. The bundled Firefox check did not complete, so an explicit Chromium feature-off run verified that fallback.
- The category menu is a native select. The phone layout places it on the line after the status track. Browsers without `:has()` keep all cards visible with the filter controls hidden.
- Replacement rows without a transfer-gap need assessment say “Not assessed”. A gap with missing evidence says “Unknown”. The device-management question uses the registered key `confirmations.device_management.windows_desktops_required`. The plan's illustrative `devices.managed` key is absent from the inputs schema.
- The concrete questions cover all 28 findings with an input key and the shared-mailbox count. Collector and non-interview requests continue to specify the evidence they need. The working list retains a specific remedy such as asking the mail administrator for a separate count.
- A4 keeps each definition below its status and uses two columns of status rows, coverage counts beside needed functions, and three cost tiles side by side. This fits the full council summary on a single page. The Town reports and German Non-profit report each gain one later page compared with the RR-05 print results. The print checks now verify phrases through both reading-order and positional text extraction so they account for the two columns.
- The new preview images keep RR-05's lossless sizes and filenames. Homepage image alternatives still describe the four definitions and the Telephony blocker. The social card uses the same wordmark, title and framed excerpt as before, with the current first-page status layout and blocker.
- The RR-02 Task 1 amendments are present on the branch and passed with their existing assertions. The additional edits below follow RR-09's new presentation requirements. The offline, privacy, escaping and D31 safeguards were kept in place.

## Test changes beyond the permitted list

| File | Test or checker | Old expectation | New expectation | Required by |
| --- | --- | --- | --- | --- |
| `tests/test_report.py` | `test_report_navigation_resolves_and_appendix_explains_scope` | One navigation list in `.bar-links`. | Both responsive index lists have the same accessible name, seven fragment links, order and wording. The skip target still resolves. | RR-09 item 1 and UI-SPEC §5 |
| `tests/test_report.py` | `test_replacements_use_coverage_symbols_distinct_from_status` | Three data cells and an area status link without a standalone link class. | Four data cells including need, checked against the existing transfer gaps. Area status uses the standalone link class. Link names, target and distinct symbols are still asserted. | RR-09 items 4 and 5 |
| `tests/test_report.py` | `test_summary_counts_and_links_match_the_report` and `test_summary_keeps_all_unknown_areas_unknown`, via `_assert_status_summary` | Count follows the status span as unwrapped text. | Count is in `.row-count`. The same counts, status labels, order and definitions are asserted. | RR-09 item 3 and UI-SPEC §1.2 |
| `tests/test_report.py` | `test_summary_caps_blockers_and_open_areas_in_catalogue_order` and `test_summary_keeps_all_unknown_areas_unknown`, via `_summary_area_rows` | A plain definition term contains the area link. | The area link is in the card header inside the definition term. The same area limits, identity, order and deduplication are asserted. | RR-09 items 8 and 14 and UI-SPEC §1.2 |
| `tests/test_report.py` | `test_summary_caps_blockers_and_open_areas_in_catalogue_order` | The open row equals the generic reason's fix. | The open row names the exact evidence question, and includes the same specific fix when one exists. | RR-09 item 11 |
| `tests/test_report.py` | `test_next_steps_render_every_fired_rule_in_display_order`, now `test_next_steps_group_actions_by_area_in_display_order` | One area heading and one `dd[data-step-kind]` per fired rule. | One heading per area per phase with ordered `li[data-step-kind]` entries, exact specific actions and one named entry per shared transfer action. | RR-09 item 10 supersedes the markup in UI-SPEC §4.1 |
| `tests/test_report.py` | `test_summary_scope_matches_the_replacements_and_gaps` | Coverage counts are joined by middle dots in the intro paragraph, and needed functions link to Closer look. The coverage cell has a single label attribute. | Each label and original count is a dedicated list row. Each needed function links to its replacement row. The cell also has a phone-specific coverage label. Totals and mapping data still agree. | RR-09 items 5 and 12 and UI-SPEC §11 criterion 24 |
| `tests/test_report.py` | `test_readiness_filters_use_the_card_counts_and_catalogue` | Two radio groups with a middle dot between a status and its count. | One status radio group with the same default, counts and disabled states. The native category select has the same default and complete ordered options. | RR-09 item 2 supersedes the shape in UI-SPEC §2.2 |
| `tests/test_report.py` | `test_print_hides_controls_opens_disclosures_and_starts_working_sections_on_new_pages` | Print hides `.bar`. | Print hides both index variants along with the existing controls. The print page-break and disclosure assertions are unchanged. | RR-09 item 1 and UI-SPEC §7 |
| `tests/test_rules.py` | `test_scope_statement_matches_the_replacements_and_gap_lists` and `test_marking_a_mapping_as_a_transfer_gap_adds_it_to_the_gap_list`, via `_rendered_coverage_counts` | The replacement-cell matcher ends after `data-label`. | The matcher includes `data-coverage-label`. Both tests still compare exactly the same coverage counts to the same sources. | RR-09 item 5 and UI-SPEC §11 criterion 24 |
| `tests/test_rules.py` | `test_next_steps_and_open_evidence_follow_the_findings` | Telephony's exact action is in a standalone definition. | Telephony's exact action is in its grouped list. The evidence and group assertions still apply. | RR-09 item 10 and UI-SPEC §11 criterion 22 |
| `tests/test_costs.py` | `test_town_cost_tiles_use_whole_units_and_show_the_break_even` | Every tile repeats its scenario plus the five-year-total wording. | Each tile has its scenario label and one shared five-year heading precedes the tiles. Money, origins and break-even expectations are unchanged. | RR-09 item 13 |
| `site/check_site.py` | `check_area_counts`, `check_tally` | The home figure contains the area count and the tally is a comma-separated paragraph. | The home preview caption supplies the count and the tally is a list. Both still compare their values with the demo. | RR-09 items 7 and 9 |

The added assertions check that incomplete-evidence badges agree with `data-incomplete`, that the manual questions use their actual keys, and that a fixture with two related device-management gaps lists both functions in one transfer action. The new site command check compares the Home and Start components. The local browser harness was migrated to the select, sticky index and two-column print summary and kept its resource, focus, filter and pagination checks.

## Native review

The table records the new or revised German copy and the command wording reused on Home. Placeholders in braces stay as written in the locale.

| Location or key | German |
| --- | --- |
| `header.title` | Was ein Umstieg von Microsoft 365 erfordert |
| `nav.on_this_page` | Auf dieser Seite |
| `filter.empty` | Kein Bereich entspricht diesen Filtern. Wählen Sie „Alle“ und „Alle Kategorien“, um alle Bereiche anzuzeigen. |
| `filter.all_categories`, selected menu label | Alle Kategorien |
| `moves.coverage` | Funktionsabdeckung |
| `moves.need` | Hier benötigt |
| `moves.need_not_assessed` | Nicht geprüft |
| `readiness.incomplete`, report and home card | Nachweise unvollständig |
| `summary.scope_unknown_one` | Eine weitere Funktion fehlt in {profile}. Ob sie hier benötigt wird, ist unbekannt. |
| `costs.total`, shared heading | Gesamtkosten für fünf Jahre |
| `path.input_field` | Feld in inputs.yaml |
| `path.transfer_actions.not_available` | Die fachlich verantwortliche Stelle und die IT-Abteilung legen fest, wie die betreffenden Funktionen nach dem Umstieg bereitgestellt werden ({functions}). |
| `path.transfer_actions.transfer_undocumented` | Die fachlich verantwortliche Stelle und die IT-Abteilung planen und erproben die Übernahme oder den Neuaufbau der Inhalte für {functions}. |
| Home preview caption | 14 Bereiche, drei Ziele (openDesk, Nextcloud und eine produktneutrale Prüfliste), auf Deutsch und Englisch als offline lesbare HTML-Datei. |
| Home download label | HTML herunterladen, 420 KB |
| Home tally, punctuation and layout | Von 14 Bereichen im Beispiel: Hindernis 1 Handlungsbedarf 9 Unbekannt 1 Bereit 3 |
| Home and Start, command caption | Im Terminal ausführen |
| Home and Start, copy accessible name | Befehl kopieren |
| Home and Start, copy tooltip | Kopieren |
| Home and Start, success message | Kopiert |
| Home and Start, manual-copy message | Kopieren Sie den markierten Befehl. |
| Home and Start, German demo command | `uv run fazit demo --lang de` |

### Interview questions

Keys in this table are under `path.questions` in `src/fazit/locales/de.yaml`.

| Finding | German |
| --- | --- |
| `licences.contract_terms_known` | Hat die Vergabestelle die Vertragsbedingungen der Microsoft-Lizenzen geprüft? |
| `directory.account_list_reviewed` | Hat die IT-Abteilung die aktuelle Kontenliste geprüft? |
| `mail.shared_mailbox_count` | Wie viele freigegebene Postfächer hat die Organisation? |
| `mail.other_systems_send_mail` | Versenden andere Systeme E-Mails über Microsoft? |
| `onedrive.external_sharing_in_use` | Gibt Ihre Organisation OneDrive-Dateien für Externe frei? |
| `sharepoint.custom_solutions_in_use` | Setzt Ihre Organisation individuell angepasste SharePoint-Lösungen ein? |
| `sharepoint.workflows_in_use` | Werden über SharePoint-Websites, Listen oder Bibliotheken Workflows oder automatisierte Genehmigungen ausgeführt oder gestartet? |
| `teams.chat_history_must_be_kept` | Muss der Chatverlauf aus Teams erhalten bleiben? |
| `teams.apps_in_use` | Sind in Teams Apps, Registerkarten, Bots oder Konnektoren eingebunden? |
| `office_files.kind.macro` | Wie viele Dateien haben Endungen, die Makros zulassen? |
| `office_files.kind.access` | Wie viele Access-Datenbankdateien gibt es? |
| `office_files.kind.publisher` | Wie viele Publisher-Dateien gibt es? |
| `office_files.kind.visio` | Wie viele Visio-Zeichnungsdateien gibt es? |
| `office_files.kind.onenote` | Wie viele OneNote-Dateien gibt es? |
| `office_files.vba_macros_in_use` | Sind die Beschäftigten auf VBA-Makros in Office-Dateien angewiesen? |
| `device_management.device_count` | Wie viele Geräte umfasst der von der IT-Abteilung erfasste Bestand? |
| `device_management.windows_device_count` | Wie viele dieser Geräte laufen unter Windows? |
| `device_management.in_use` | Verwaltet Ihre Organisation Geräte über Microsoft? |
| `device_management.windows_desktops_required` | Benötigen Sie Windows-Arbeitsplätze für Anwendungen, Geräte oder Peripherie? |
| `windows_software.application_count` | Welche Anwendungen laufen ausschließlich unter Windows? |
| `windows_software.without_web_version_count` | Für welche reinen Windows-Anwendungen gibt es keine Webversion? |
| `power_platform.in_use` | Nutzt Ihre Organisation Dienste der Power Platform? |
| `telephony.in_use` | Läuft die Telefonie Ihrer Organisation ganz oder teilweise über Microsoft? |
| `telephony.replacement_available` | Steht für die eingesetzte Microsoft-Telefonie eine Alternative zur Verfügung? |
| `identity_access.sso_application_count` | Wie viele Anwendungen nutzen die zentrale Anmeldung über Microsoft? |
| `identity_access.conditional_access_in_use` | Setzt Ihre Organisation den bedingten Zugriff von Microsoft ein? |
| `security_compliance.protection_or_retention_in_use` | Nutzt Ihre Organisation Schutz- oder Aufbewahrungsfunktionen von Microsoft? |
| `small_apps.in_use` | Nutzen die Fachbereiche kleinere Microsoft-Anwendungen wie Forms, Planner oder Bookings? |
| `integrations.application_count` | Wie viele Fachanwendungen sind an Microsoft 365 angebunden? |

## Open items

RR-09 implementation and verification are complete. The maintainer's native review and the two human sign-offs from RR-05 remain open.

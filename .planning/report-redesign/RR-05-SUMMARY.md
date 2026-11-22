---
phase: report-redesign
plan: "05"
subsystem: report
tags: [design, print, offline, site, verification]
requires:
  - phase: RR-01
    provides: Assessed catalogue, bilingual copy and rule actions
  - phase: RR-06
    provides: Explicit evidence and simulated provenance labels
  - phase: RR-07
    provides: Profile-aware readiness and target scope
  - phase: RR-02
    provides: Area cards and CSS filters
  - phase: RR-03
    provides: Council summary, costs and the all-Unknown fixture
  - phase: RR-04
    provides: Actions, navigation, replacements and A4 print styles
provides:
  - Design checks for the report and the site
  - A4 verification for both samples and the all-Unknown report in both languages
  - Refreshed town reports and eight bilingual homepage previews
  - D33 to D35 and the council-summary requirement
affects: [RR-08, Phase 1.1, Phase 1.2]
actuals:
  tasks: 3
  commits: 0
tech-stack:
  added: []
  patterns: [One stylesheet reference per language, A4 text checked against the report]
key-files:
  created: [.planning/report-redesign/RR-05-SUMMARY.md, site/icons/help.svg, site/icons/warning.svg]
  modified: [tests/test_report.py, site/check_site.py, site/style.css, src/fazit/templates/report.html.j2, site/index.html, site/de/index.html, DECISIONS.md, .planning/ROADMAP.md, .planning/REQUIREMENTS.md]
key-decisions:
  - Validate the existing encoded site symbols against their shared source files.
  - Record the founder's removal of the readiness bar in D33.
  - Move the council summary from Phase 1.2 into the redesign in D35.
requirements-completed: [SAFE-04, REPT-01, REPT-02, REPT-04, REPT-05, RULE-02, OUTP-03]
coverage:
  - id: D1
    description: The report and site enforce shared design rules and distinct coverage symbols.
    requirement: REPT-05
    verification:
      - kind: integration
        ref: tests/test_report.py#test_report_styles_follow_the_design_rules
        status: pass
      - kind: integration
        ref: uv run python site/check_site.py
        status: pass
    human_judgment: false
  - id: D2
    description: Header and summary fit page one in the tested A4 reports.
    requirement: OUTP-03
    verification:
      - kind: automated_ui
        ref: node .shots/report-redesign/check.mjs <report-directory> --only pageone
        status: pass
    human_judgment: false
  - id: D3
    description: The site and report share a visual design and the bilingual previews describe the summary.
    requirement: REPT-04
    verification:
      - kind: automated_ui
        ref: node .shots/report-redesign/check.mjs <report-directory> --only site
        status: pass
    human_judgment: true
    rationale: Both reviewers sign off criterion 19 and the maintainer reviews the German copy and preview.
completed: 2026-11-22
status: complete
---

# RR-05 summary

The refreshed homepage previews show the report's status definitions and first blocker. The council summary fits the first A4 page for the town, the non-profit and the all-Unknown report in English and German with either background setting. The site and report now check their shared fonts, colours and symbols.

All three tasks ran in order from a clean working tree at `076cfd8` on `report-redesign`. The changes are in the working tree.

## Changes by task

| Task | Files | Changes |
| --- | --- | --- |
| 1 | `tests/test_report.py` | Cached two town openDesk reports for the test session. The stylesheet checks run once per language. The document matrix confirms that each report has one stylesheet and that it matches its language's reference. Added the design assertions below. |
| 1 | `site/check_site.py` | Added `check_design` for the shared stylesheet. It checks colour and font declarations, the use of local font sources, and coverage symbol paths. Its resource checks use the existing CSS reference parser. |
| 1 | `site/style.css`, `src/fazit/templates/report.html.j2` | Used `var(--bg) 70%` in place of `#000 70%` in the site preview mask and `var(--bg) 32px` in place of `#000 32px` in the report's navigation fade. Both colours are opaque, so both alpha masks have the same stops. Removed SFMono-Regular, Menlo and Consolas from the site's `--mono` token, matching the report's existing Geist Mono and generic fallbacks. |
| 1 | `site/icons/help.svg`, `site/icons/warning.svg` | Restored the two shared symbols from the packaged files, byte for byte. All nine packaged SVGs now have identical counterparts under `site/icons/`. |
| 1–2 | `site/demo/en/index.html`, `site/demo/de/index.html` | Refreshed the town openDesk demos for the Task 1 site check and again from the fresh Task 2 builds. Both agree byte for byte with the final default demo runs. |
| 2 | `.shots/report-redesign/check.mjs`, `.shots/report-redesign/shots.mjs` | Added the A4 first-page and site comparison checks to the existing browser script. Added the screenshot capture and lossless WebP encoder. Both scripts and their evidence are in the ignored `.shots/` directory. |
| 2 | Eight `site/images/readiness-*.webp` files listed below, `site/index.html`, `site/de/index.html` | Replaced the preview images with the summary frames. Updated the two image alternatives and the HTML download sizes. |
| 3 | `DECISIONS.md`, `.planning/ROADMAP.md`, `.planning/REQUIREMENTS.md` | Recorded D33 for the ten-section design, D34 for Licences as inventory and D35 for page one. Cross-referenced D21, RULE-02 and REPT-02 and mapped OUTP-03 to the redesign as Pending. Phase 1.2 now has three requirements. |

### Stylesheet assertions

| Original assertion in `test_report_styles_work_in_light_dark_narrow_and_print` | Where it runs now |
| --- | --- |
| Viewport includes `width=device-width` and the document declares `color-scheme="light dark"` | Both original assertions run in every `test_report_document_structure` case. |
| The symbol path selected for each status present is distinct from every other status's selected path | The original symbol assertion runs in every `test_report_document_structure` case. |
| The report has one stylesheet | The two reference cases still unpack one stylesheet. The matrix additionally requires exactly one matching stylesheet for every sample, language and profile. |
| Retired comments are absent, link hover matches the expected rule, both palettes pass the contrast checks, hover is lighter and the four status colours differ | Same stylesheet test, in both languages. |
| The narrow table rules, A4 margins, print rules, break avoidance, exact colour adjustment and print disclosure styles are present | Same stylesheet test, in both languages. |

An AST comparison against `076cfd8` found every original assertion in `tests/test_report.py`. `test_report_and_website_share_colour_tokens` stayed as written. The existing escaping, resource and document matrices still cover all sample and profile cases they covered at the start.

### Test changes beyond the permitted list

None.

### Design rules and mutation checks

- Colour literals in hex, RGB, RGBA, HSL and HSLA are confined to the token blocks. The report permits `rgb(0 0 0 / 12%)` in `box-shadow` for the selected segment, although the branch already uses `--segment-shadow`. The site's three existing exceptions are `rgb(0 0 0 / 4%)`, `rgb(0 0 0 / 8%)` and `rgb(0 0 0 / 18%)` in `box-shadow`. The dark report hover already uses `--link-glow`.
- The two font families are Figtree and Geist Mono. Other family declarations use `--sans`, `--mono` or `inherit`. The font tokens allow only the listed generic fallbacks. The site checker limits `@font-face` URLs to files in `site/fonts/`. Other stylesheet URLs must use the site's embedded SVG convention with a checked source under `site/icons/`.
- The report test compares the rendered coverage and status paths and checks the shared source files by bytes. The site checker reads the four status names from the template's symbol map and compares their path data with that of its coverage icons. In-suite coverage uses `circle.svg` in both places.
- Both template mutations failed the new test as expected in English and German. A `#123456` declaration in a code rule failed the colour check. In-suite coverage using `check-circle` failed the disjoint-path assertion.
- Both site mutations made `check_site.py` exit 1. The new colour check identified `#123456`. The coverage check also rejected a byte-identical copy of `check-circle.svg` under a temporary name, whose source comment passed the original byte check. All planted changes were restored.

## Verification

| Check | Result |
| --- | --- |
| Task 1 selection and report suite | The original stylesheet selection had 12 cases. The new collection has two original stylesheet cases and two design cases. All 121 report tests passed in 19.42 s. All nine shared SVG byte comparisons passed. |
| Task 1 full gate | 949 passed in 166.45 s. Ruff lint, Ruff formatting and the site checker passed. |
| Task 2 browser and assets | All five browser parts passed. Pillow confirmed the eight output dimensions and each encoded image's pixel equality with its source PNG. All eight were newer than both refreshed reports and under 150,000 bytes. The old alt phrases each had zero matches. The site checker passed. |
| Task 3 final `uv run pytest -q` | **949 passed in 168.60 s.** RR-04 recorded 957 on the starting branch. The plan's 722 count was from `df36196`. The stylesheet parametrisation removes ten repeated cases and the design rules add two. |
| Final `uv run ruff check .` and `uv run ruff format --check .` | Both passed. Ruff reported 168 formatted files. |
| Final `uv run fazit demo --lang en` and `uv run fazit demo --lang de` | Each completed in a fresh temporary output directory. Both printed paths existed and matched the published demo for that language byte for byte. |
| Final `uv run python site/check_site.py` | Checked 20 pages and 841 references. No errors. |
| Final `node .shots/report-redesign/check.mjs <report-directory>` | Exit 0 with 16 filter checks, 16 layout checks, four print checks, six first-page checks covering 12 PDFs, and 12 site comparisons. The evidence is in `.shots/report-redesign/out/`, with the last run in `check-final.log`. |
| Offline opening and bilingual structure | Both checked-in demos and both all-Unknown reports opened at 360 px in light and dark with Chromium offline and JavaScript disabled. The browser saw zero external requests and no horizontal overflow. Each of the three report kinds had identical English and German tag and attribute-name sequences. |
| Scope guards | The D31 entry and its implementation and tests match the starting tree. The report's CSP, escaping, privacy, cost model and status rules retain their safeguards. Phase 1.1 has an empty diff. D33–D35, the OUTP-03 traceability check and `git diff --check` passed. |

### Browser and A4 results

The viewport was 800 px tall for the screen checks. Both the filters and layout passed in each cell below. They exercise keyboard and accessible names, selection and reset, link targets, the exact report CSP, no external requests, the first screen and the phone layout.

| Report | 1280 light | 1280 dark | 360 light | 360 dark |
| --- | --- | --- | --- | --- |
| Town EN | Pass | Pass | Pass | Pass |
| Town DE | Pass | Pass | Pass | Pass |
| Non-profit EN | Pass | Pass | Pass | Pass |
| Non-profit DE | Pass | Pass | Pass | Pass |

The two PDF parts ran at 1280 px with a light colour scheme and print media. `print` used `pdftotext -layout` and compared text and pagination with the filter cleared or selected by keyboard, each with backgrounds on and off. `pageone` used default `pdftotext` in all 12 cases. It checked the text from the report DOM, including both date fields, all status rows, the blocker or both zero-blocker sentences, open questions, the scope heading, the three totals and their origins or missing-input notes, the Stay assumption and any break-even lines. Page two starts with What to do next. `pdfinfo` identified A4 in every case. The two-page previews are saved at 50 dpi.

| Report | `print`, backgrounds on and off with both filter settings | `pageone` backgrounds on | `pageone` backgrounds off | Total pages | Next steps / costs / appendix in `print` |
| --- | --- | --- | --- | ---: | --- |
| Town EN | Pass | Pass | Pass | 35 | 2 / 19 / 28 |
| Town DE | Pass | Pass | Pass | 37 | 2 / 20 / 30 |
| Non-profit EN | Pass | Pass | Pass | 32 | 2 / 17 / 26 |
| Non-profit DE | Pass | Pass | Pass | 32 | 2 / 17 / 26 |
| All-Unknown EN | — | Pass | Pass | 28 | — |
| All-Unknown DE | — | Pass | Pass | 29 | — |

The site comparison serves `site/` on loopback and matches each home page to its town report. It also reads the start page for the intro and the Integrators page for the site's note. It compares font family, size, weight, foreground, background, padding and radius. The site and report are side by side in `site-*-opening.png` and `site-*-card.png`.

| Town report and matching site | 1280 light | 1280 dark | 360 light | 360 dark | 375 light | 375 dark |
| --- | --- | --- | --- | --- | --- | --- |
| EN | Pass | Pass | Pass | Pass | Pass | Pass |
| DE | Pass | Pass | Pass | Pass | Pass | Pass |

Accepted differences were the same in both languages.

| UI-SPEC §6.2 exception | Site to report |
| --- | --- |
| 3, the phone bar | At 360 and 375 px, bar padding goes from 6 × 16 px to 8 × 16 px. Nav links go from 17 to 12 px, from 11 px block padding to zero and from full text colour to the 80 % text blend in each theme. |
| 6, cards in status groups | The area name goes from 14 to 24 px and from secondary to primary text colour. The status goes from 40 px at 1280 and 32 px on phones to 17 px. |

### Homepage previews and copy

The 1008 × 560 and 400 × 720 CSS-pixel frames were captured at 2×. Every frame includes the summary heading, assessed-area total, four status counts and definitions, blocker heading and complete first blocker row.

| File in `site/images/` | Pixels | Bytes | First blocker row |
| --- | --- | ---: | --- |
| `readiness-en-light.webp` | 2016 × 1120 | 34,084 | Yes |
| `readiness-en-dark.webp` | 2016 × 1120 | 39,720 | Yes |
| `readiness-en-mobile-light.webp` | 800 × 1440 | 31,074 | Yes |
| `readiness-en-mobile-dark.webp` | 800 × 1440 | 35,446 | Yes |
| `readiness-de-light.webp` | 2016 × 1120 | 37,746 | Yes |
| `readiness-de-dark.webp` | 2016 × 1120 | 43,346 | Yes |
| `readiness-de-mobile-light.webp` | 800 × 1440 | 33,032 | Yes |
| `readiness-de-mobile-dark.webp` | 800 × 1440 | 37,038 | Yes |

The two HTML files are 371,666 and 383,667 bytes respectively. The caption rounds decimal KB to the nearest 10. These are the two home-page diffs, limited to the attribute and caption content.

```diff
--- site/index.html
- alt="Readiness section of the sample report: 3 areas Ready, 9 Needs work, 1 Blocker, 1 Unknown."
+ alt="Summary of the sample report. The status list for 14 areas shows Blocker (1), Needs work (9), Unknown (1) and Ready (3), with a definition for each. The finding that blocks this move follows."
- Download HTML, 290 KB
+ Download HTML, 370 KB
--- site/de/index.html
- alt="Abschnitt zur Bereitschaft aus dem Beispielbericht: 3 Bereiche Bereit, 9 Handlungsbedarf, 1 Hindernis, 1 Unbekannt."
+ alt="Überblick aus dem Beispielbericht. Die Statusliste für 14 Bereiche zeigt „Hindernis“ (1), „Handlungsbedarf“ (9), „Unbekannt“ (1) und „Bereit“ (3) mit jeweils einer Erläuterung. Darunter steht der Befund, der dem Umstieg entgegensteht."
- HTML herunterladen, 300 KB
+ HTML herunterladen, 380 KB
```

## Deviations and implementation choices

- The branch's existing checker requires encoded SVG masks with source comments. RR-05 keeps that representation, including the button icons and window controls, and extends its checks. A direct stylesheet URL to an icon is still rejected. The branch already used `circle.svg` for in-suite coverage, the `--link-glow` hover token and the report's generic mono fallbacks.
- The report-wide removal of the readiness bar in UI-SPEC §2 and the change map supersedes the old filter-bar sentence in Task 3 and the remaining wireframe references. D33 documents the founder's decision. The report's separate horizontal navigation fade uses the opaque background token in §6.2 exception 3.
- Both demos were brought forward into Task 1's gate because the existing site checker requires current package output. Task 2 generated a fresh matching pair. The all-Unknown fixture needed no inputs file.
- The site note lives on Integrators. The browser harness places a copy in that page's intro for the style comparison, since the report's note inherits the intro text colour. The change is limited to the test page's live DOM. The harness runs at 375 px as well as the plan's 360 px to supply the criterion 19 review size.
- The first focused Task 1 run exposed an unhashable pytest factory in the helper and a namespace wildcard used with the wrong XML iterator. The session fixture now supplies the cache and the SVG check uses the namespace-aware lookup. The next focused checks and both full gates passed.
- The first combined browser run was interrupted with exit 143 while producing its log. The repeat with output redirected to a file completed all five parts. Task 3 repeated the same complete browser run.
- The planning workflow's finalisation is the requested working-tree handoff. The Phase 1.1 plans are addressed in the list below.

## Native German review

| Location | English | German for native review |
| --- | --- | --- |
| Homepage report preview alt, `site/index.html` and `site/de/index.html` | Summary of the sample report. The status list for 14 areas shows Blocker (1), Needs work (9), Unknown (1) and Ready (3), with a definition for each. The finding that blocks this move follows. | Überblick aus dem Beispielbericht. Die Statusliste für 14 Bereiche zeigt „Hindernis“ (1), „Handlungsbedarf“ (9), „Unbekannt“ (1) und „Bereit“ (3) mit jeweils einer Erläuterung. Darunter steht der Befund, der dem Umstieg entgegensteht. |
| Homepage download caption, numeric update | Download HTML, 370 KB | HTML herunterladen, 380 KB |

## Founder action

UI-SPEC called for a council clerk or Kämmerer to read page one without explanation before RR-02, then say what the report supports and what remains open. The planning directory contains the instruction and follow-up references. There is no reader response beside UI-SPEC.md in this checkout. Record the response there after the founder's reader check. The check sits outside the build gate.

## Phase 1.1 plan steps to update

| Plan and field | What it says now | Update against the redesigned report |
| --- | --- | --- |
| 01.1-01 frontmatter truth 1, objective, Task 1 behaviour, test action, verify, acceptance and done, final verification and D-81 source coverage | Copilot is the second row of the readiness table and second evidence group. The town assertion is `rows[1] == ("copilot", "needs_work")` with 15 → 16 rows. | Keep Copilot second in the full catalogue. Licences is inventory only. Copilot leads its status group and appears first under Automation and AI. It carries its own evidence disclosure, and its functions come first in the replacements table. Count 14 existing and 15 resulting `article.finding` cards. Check the Copilot card as Unknown in the scan-only report and as Needs work in the town demo. Reuse `assert_readiness_order` and `readiness_row` from `tests/helpers.py`. |
| 01.1-01 Task 1 catalogue and Tasks 1–2 finding entries | Insert a workload with a label and add seven findings without owners. | Register the workload with `category: automation_ai`. Give each finding an owner from the catalogue's fixed roles. Use `test_every_provided_finding_is_used_by_the_report` for the answer-field coverage check named under its older test name. |
| 01.1-01 Tasks 1–2 status rule action, tests and acceptance | Place the block after Licences and add only a bilingual reason per problem rule. Task 2 expects two existing Blocker rules. | Licences has no status block. Put Copilot first under `workloads` in the assessed order. Each of the eight rules needs a bilingual, product-neutral `next_step` naming the responsible role from RR-01 and a kind chosen from the action itself. Use `clarify`, `decide` or `replace`. Include the German sentences and kinds in native review. Needs work reasons comply with `test_only_blocker_rules_can_describe_a_blocker`. There are 32 workload rules and two target templates, giving 34 `next_step:` and 34 `kind:` lines now, 35 after the tracer and 42 after all eight rules. The single existing Blocker plus Copilot gives two. D32's operator review gate applies to the new Blocker. |
| 01.1-01 Tasks 1 and 3 mappings, tests, verify and acceptance | First function and five AI mapping rows per profile, gap wording “Direct transfer unverified”, five dated matches expected from zero. | Keep the first mapping position and use RR-07's conventions. Cite the relevant source for each product-profile row and give each gap its declared need finding. Use Direct transfer undocumented only where the method is undocumented. Product-profile date counts already have 22 openDesk and one Nextcloud match for 2026-11-22. Assert the source and date on the five new rows rather than counting the entire files. Use the profile-aware evaluator and `test_attention_lists_each_transfer_gap_from_the_profile`. Keep `operator_review: unreviewed` until operator review. Dated profiles' scope counts follow the replacements automatically. Generic continues without a scope statement. |
| 01.1-01 Task 2 verify and final sample assertions | The non-profit grep looks for `data-workload="copilot" data-status="needs_work" data-incomplete`. Several prose checks still say readiness row. | The grep already matches the card's attributes. Refer to cards in the descriptions and verify the status and completeness against the chosen profile. |
| 01.1-02 Task 1 behaviour, done and verify | The report check searches for `<tr data-workload="copilot"…</tr>` and its measured evidence. | Select the Copilot `article` and its `li[data-evidence]` in the closed disclosure. Continue checking the same measured add-on and the separate `data-product` record. |
| 01.1-02 Task 2 reading list, report action, file lists and optional-plans grep | References the licence table and classification code in `rules.py`. | The licence table is in the closed products disclosure under What Fazit recorded, after Closer look. Read and edit the licence classification in `licences.py` and use adjoining helpers in the current modules. Point the `optional_plans` grep and metadata at the file implementing it. |
| 01.1-03 frontmatter, objective and Tasks 1–2 report behaviours, actions and checks | Renewal and notice date appear in a `licence-contract` subsection in What we found. Partial or missing fields are handled there. | Keep that subsection in `found` between the headline tiles and the licence-products disclosure, using the existing report classes and tokens. Add two summary tiles after the cost tiles and Stay and break-even notes. “Next renewal” and “Latest notice date” are `li` elements with `data-decision` and `data-provenance`. Reuse the one date function, answer source and `as_of` fallback. An end date without a notice period yields a Provided renewal and an Unknown notice date. Each tile names the input it needs when evidence is missing. Test the two tiles and partial cases in both languages, and rerun `pageone` with the added content. |
| 01.1-03 Task 2 report tests | Adds a subsection and checks the partial contract cases. | Add `licence-contract` to the order assertion in `test_report_document_structure` between `cannot-be-moved` and `run-details`. The order then is `not-examined` (in `path`), `cannot-be-moved`, `licence-contract`, `run-details`. RR-04's scope-of-collection heading has no extra `data-subsection`. Read the existing test helpers in `tests/helpers.py`. |
| 01.1-01 Task 3, 01.1-02 Task 2 and 01.1-03 Task 2 demo publication and site verification | Each publishes the new demos and expects the full site checker to pass before 01.1-04 updates the home counts. | Verify intermediate package builds with temporary demos. Run the release copy and full site check with the matching updated tally in 01.1-04. The checker derives its tally from the published sample's card counts. |
| 01.1-04 frontmatter, objective, Task 1 counts, behaviour, verify and acceptance | The tally, figure, alt text and verification assume 16 readiness rows, `rows[1][0] == "copilot"` and Ready first. | Count 15 assessed cards and check the amended D-81 grouping. Read the counts from the final demo and use Blocker, Needs work, Unknown, Ready in the summary alt text. Check the current tally format after RR-08. Use 15 in both language figure tiles, tallies, pilot pages, README counts and `publiccode.yml`. |
| 01.1-04 Task 2 reading, finding-card checks, coverage and report outline | Reads Telephony's readiness row and edits its licence evidence. Puts renewal in “What we found” and refers to the home coverage table. | Telephony's source is its report card and evidence disclosure. After RR-08, compare the site's Mail example to its own regenerated card. Follow the coverage table and its checker to their current route. The Copilot function group still comes first. Mention the decision window in the council summary description. |
| 01.1-04 Task 2 project status and pilot count | Advances the old timeline labels in the order of Phases 1.2, 1.3, 2 and 3. Says 16 areas in the pilot pages. | Use the status labels and locations that ship in RR-08. Follow ROADMAP's execution notes, which put import and launch before Phase 1.1. The pilot count moves from 14 to 15. |
| 01.1-04 Task 3 and frontmatter | Lists eight PNGs, frames the readiness table, verifies the second row is Copilot and documents sixteen areas in the READMEs, `publiccode.yml` and decision entry. | Reuse `.shots/report-redesign/shots.mjs` for the same eight lossless WebP names and summary framing. Keep the count-and-definition alt text with the new observed counts. Review the first blocker area if it fits. Use fifteen assessed areas in each publication and the amended D-81 placement in the decision entry. Describe renewal and notice dates under the council summary and as detail in recorded inventory. |
| All four plans' reading lists and stale symbol references | Pre-redesign layout and a combined rule module. Some test instructions refer to table rows and `.figure` rather than current selectors. | Include DESIGN.md and UI-SPEC.md. Follow rule functions to `status.py`, `mappings.py`, `licences.py`, `evidence.py` and `validation.py`. `rules.py` still handles rule file reads and checksums. Use `article.finding`, `.figure-num` and the existing helpers where appropriate. Assertions about the local and offline header sentences target run details. |
| REQUIREMENTS.md AIAS-01 and ROADMAP Phase 1.1 criteria and publish line | AIAS-01 calls it the second area after Licences. The roadmap repeats the second area everywhere and 16 areas at publication. | Align placement and count with the D-81 amendment. The dated target-source requirement applies to the product profiles under the current generic mapping rules. Include the summary placement of the decision window. |

## Follow-ups outside this scope

- RR-08 covers the homepage rebuild on the parallel branch. On this branch the home figures display 15, the tally is Ready first and `check_tally` uses `STATUSES`, “What you get” still includes Suggested path, and the sole finding example is Telephony. RR-08 owns the assessed count, tally order, Mail example, revised outline and the other changes in the Apple-lens review. Both pilot pages already say 14. The social card `site/og.png` still shows the old readiness bar and Licences row. The browser comparison can follow the coverage table and legend as they move to their new route.
- The READMEs already say fourteen and use the move terminology for costs. Their report outlines still follow the old order. Both descriptions in `publiccode.yml` still give 15. Its English cost feature still says partial and full exit.
- DESIGN.md's Checks paragraph still describes the design checks as work to add with the redesign. It needs the wording update under its own change rule.
- The three target mappings still say `operator_review: unreviewed`. The named operator review is the founder's release gate for the scope statement. RR-06's inputs consistency rule is recorded in D31. RR-07's target decision is D32. RR-06 leaves the README link and DOCS-04 scan-format filename reference for the coordinator.
- The coordinator ticks OUTP-03 when the redesign merges. Until then it is Pending.
- Before merge, the maintainer reviews all German drafts in RR-01 through RR-07, including the rule actions and kinds, the UI-SPEC §8 drafts, the category, rule and mapping copy, and this plan's preview text. The maintainer reviews the six reports' PDF previews with both background settings and the live homepage card in each language, theme and frame size. Both reviewers sign off criterion 19. The automated checks and the visual inspection during this run supply the evidence for those human checks.

## UI-SPEC §11 acceptance

| Criterion | Evidence |
| --- | --- |
| 1 | The existing one-file and resource guard tests passed. The browser exercised the exact CSP and opened the report with scripts disabled and external requests blocked. |
| 2 | `layout` checked the title, status definitions and blocker or zero-blocker caveat at 1280 × 800 for both samples and languages. The summary has no readiness bar. |
| 3 | Summary tests cover the catalogue count, one status list, the blocker cap and link conditions, the zero-blocker caveat and capped, deduplicated unknowns before costs. The locale and report checks cover the prohibited copy. |
| 4 | Card tests check assessed-area coverage, status grouping and order, category, reason, next step and closed evidence disclosures. |
| 5 | `filters` checked the status and category filters individually and in combination and restored both All options. |
| 6 | `filters` checked the empty state, hidden empty headings and disabled zero-count options. |
| 7 | `filters` verified keyboard traversal, arrow selection, focus and accessible option and group names. The spoken position and state need the maintainer's screen-reader check. |
| 8 | `filters` verified that outside content stays the same and the linked card appears under restrictive filters. The no-`:has()` fallback is covered by the stylesheet assertion. |
| 9 | `print` compared identical print text and pagination with and without an active filter under both background settings. |
| 10 | Cost tests cover known and Unknown totals, whole-unit tiles, missing inputs, differences and the dashed Unknown marker with its named blocks. |
| 11 | Cost tests compare the scale, chart and table amounts, origins, null chart, Stay assumptions and exact break-even results. The English town full-move threshold is EUR 39,130. |
| 12 | Card, evidence and design checks cover text labels, provenance and coverage paths. The replacements table and homepage use the neutral circle for in-suite coverage. |
| 13 | `layout` verified mobile overflow, cost cells, navigation fade and focus, filter wrapping and target sizes. The seven-digit tile test and RR-04's browser evidence cover the large figure. The all-Unknown report also fit at 360 px in both themes and languages. |
| 14 | The original contrast and palette checks passed. `layout` checked focus, known chart outlines and the dashed marker in both themes. |
| 15 | Document tests cover the headings, labelled areas and area-specific link names. Cost tests cover the accessible chart text. Browser keyboard checks cover the skip link, nav and a disclosure. The maintainer can exercise every disclosure during the keyboard review. |
| 16 | `pageone` checked 12 A4 PDFs. `print` checked the Ready evidence, licence table, appendix, section page breaks and absence of filter text. RR-04's card-head and repeat-header print checks still apply. This run visually inspected the first page of each PDF and representative second pages. |
| 17 | The six reports match their language counterparts in tag and attribute-name sequence. Locale tests passed. German wording awaits native review. |
| 18 | The `site` part compared the shared component properties at all three widths and in both themes. The only measured differences are exceptions 3 and 6. Review the remainder of the declarations and spacing against DESIGN.md as part of the design sign-off. |
| 19 | The side-by-side evidence covers 1280, 360 and 375 px in both schemes and languages. Both reviewers' sign-off is open. |
| 20 | `test_changing_the_catalogue_category_changes_the_rendered_row` and RR-02's copied-catalogue browser test confirm that moving an area to a different category reaches its card and filter. |
| 21 | All six repository commands passed, both demos matched the release copies, the limited test migration is recorded above and D33–D35 are present. |
| 22 | Open-point and action tests verify grouped requests, links, owner roles, fixes and action kinds in the order of §4.1. |
| 23 | The target-line tests verify the needed Teams chat history gap ahead of the two-function cap. |
| 24 | Scope tests compare the counts with the replacements table and the needed anchors with transfer gaps. The generic profile has no scope statement. |

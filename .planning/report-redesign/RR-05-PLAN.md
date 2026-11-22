---
phase: report-redesign
plan: 05
type: execute
wave: 7
depends_on: ["RR-01", "RR-06", "RR-07", "RR-02", "RR-03", "RR-04"]
files_modified:
  - tests/test_report.py
  - site/check_site.py
  - site/style.css
  - site/icons/help.svg
  - site/icons/warning.svg
  - src/fazit/templates/report.html.j2
  - site/demo/en/index.html
  - site/demo/de/index.html
  - site/images/readiness-en-light.webp
  - site/images/readiness-en-dark.webp
  - site/images/readiness-en-mobile-light.webp
  - site/images/readiness-en-mobile-dark.webp
  - site/images/readiness-de-light.webp
  - site/images/readiness-de-dark.webp
  - site/images/readiness-de-mobile-light.webp
  - site/images/readiness-de-mobile-dark.webp
  - site/index.html
  - site/de/index.html
  - DECISIONS.md
  - .planning/ROADMAP.md
  - .planning/REQUIREMENTS.md
autonomous: true
requirements: [SAFE-04, REPT-01, REPT-02, REPT-04, REPT-05, RULE-02, OUTP-03]

estimate:
  tokens: 150000
  raw_tokens: 150000
  tasks: 3
  confidence: low

must_haves:
  truths:
    - "The report's stylesheet is checked once per language, and the sample-by-profile matrix proves it is the same stylesheet everywhere, so no assertion is lost"
    - "A machine checks DESIGN.md's rules for both site and report: colours only in the token blocks (listed shadow values excepted), only Figtree and Geist Mono, symbols only from the shared set in `site/icons/`, no coverage symbol equal to a status symbol, and the shared palette"
    - "A real A4 PDF proves, in both languages, that header and summary are page one and fit it for the town, the non-profit sample and RR-03's all-Unknown report, with backgrounds on and off"
    - "A browser check proves that shared components compute the same styles on the site and in the report, apart from UI-SPEC 6.2's six named exceptions"
    - "`site/demo/*` equal fresh demo runs; the eight WebP shots on the home card show the redesigned report's summary (the status list with counts and definitions, then 'What blocks this move'), in light and dark, desktop and phone, English and German, at their declared sizes, each under 150 KB, with alt text that describes that screen"
    - "DECISIONS.md records the departure from D-19, D-26 and D-64, Licences without a status (amending D21 and RULE-02), and page one for the council (OUTP-03 pulled into the redesign); ROADMAP.md and REQUIREMENTS.md carry the matching notes"
    - "The SUMMARY lists exactly which Phase 1.1 plan steps must change, the founder action and the follow-ups outside this scope, without editing them"
  artifacts:
    - path: "tests/test_report.py"
      provides: "Stylesheet checked once per language with a matrix guard; design-rule test for the report, including coverage symbols"
      contains: "def test_report_styles_follow_the_design_rules"
    - path: "site/check_site.py"
      provides: "Design checks for site/style.css"
      contains: "def check_design"
    - path: "DECISIONS.md"
      provides: "Dated entry for the report redesign"
      contains: "D-64"
  key_links:
    - from: "tests/test_report.py"
      to: "site/icons/"
      via: "every packaged icon is byte-identical to the site icon of the same name"
      pattern: "site\" / \"icons"
    - from: "site/check_site.py"
      to: "site/style.css"
      via: "check_design reads colours, fonts, url() values and coverage symbols of the stylesheet"
      pattern: "check_design"
    - from: ".shots/report-redesign/check.mjs"
      to: "tests/fixtures/all_unknown_scan.json"
      via: "part `pageone` prints the all-Unknown report in both languages beside the two samples"
      pattern: "pageone"
---

# Plan RR-05: design checks, page one on paper, site assets, decisions and the hand-over

## Goal

The report puts the findings first: what a move would take, what stops it, what is still open and what it costs. Page one (header and summary) is written for the council, the same on screen and on paper; every area is a card the reader can filter; the costs are drawn; the report looks like the website. What is measured, provided or unknown does not change (`.planning/report-redesign/UI-SPEC.md`, revision 4.1, section 0).

<objective>
Make the design rules machine-checked, prove page one on real A4 PDFs, prove the report's likeness to the site in a browser, bring the site's sample reports and home-card screenshots up to date, record the decisions with their notes in the roadmap and requirements, and hand over an exact list of what Phase 1.1 and the site must still change.

Purpose: UI-SPEC sections 7, 9 ("Decisions to record") and 11, DESIGN.md "Checks", and the RR-05 rows of `.planning/report-redesign/REV4-CHANGE-MAP.md`. Reviews should confirm the rules, not discover them.
Output: restructured and new report tests, design checks in `site/check_site.py`, the token, symbol and icon fixes they force, browser check parts `pageone` and `site`, regenerated demos and screenshots with new alt text, a DECISIONS.md entry with ROADMAP and REQUIREMENTS notes, and the hand-over lists in the SUMMARY.

This is the last plan of the redesign. Run order: RR-01, RR-06, RR-07, RR-02, RR-03, RR-04, RR-05.
</objective>

<execution_context>
Read these two files before starting. They are plain paths, not includes.
- $HOME/.claude/gsd-core/workflows/execute-plan.md
- $HOME/.claude/gsd-core/templates/summary.md
</execution_context>

<context>
Read these files first. They are plain paths from the repository root.
- AGENTS.md
- DESIGN.md (binding; "Symbols", "Accessibility and weight" and "Checks")
- DECISIONS.md (principles, D20, D21, D31 for the entry style)
- .planning/report-redesign/REV4-CHANGE-MAP.md (binding: rules for every plan, who owns what, the revision 4.1 table)
- .planning/report-redesign/UI-SPEC.md (revision 4.1; sections 1.2, 6, 7, 9, 10, 11 and the closing founder action)
- .planning/research/report-usefulness/SYNTHESIS.md (sections A and C)
- .planning/research/apple-lens/REVIEW.md (section 2 "Report preview", section 5, section 6)
- .planning/report-redesign/RR-01-SUMMARY.md, RR-06-SUMMARY.md, RR-07-SUMMARY.md, RR-02-SUMMARY.md, RR-03-SUMMARY.md, RR-04-SUMMARY.md
- .planning/quick/261122-rv6-tests/PLAN.md (item 1, which Task 1 carries out for `tests/test_report.py`)
- .planning/phases/01-demo-and-report/01-CONTEXT.md (D-19, D-26, D-64, D-80)
- .planning/phases/01.1-ai-assistants-and-decision-window/01.1-CONTEXT.md and the plans 01.1-01 to 01.1-04 in that directory
- .planning/ROADMAP.md and .planning/REQUIREMENTS.md

Precondition: RR-01, RR-06, RR-07, RR-02, RR-03 and RR-04 are complete (their SUMMARY files exist). If one is missing, stop and hand back.

Base: committed `main`. This plan was checked against `df36196`, which includes `0ae2be2`, `6e36d71` and `acf9be9` (D31 load-time scan checks, licence reconciliation, value bounds, `status.py` without special cases). Every count marked `[HEAD=…]` below is from that commit; re-check it with the same grep before relying on it.

Site files move under other hands. When this plan was written, other sessions had uncommitted edits to `site/` (index pages, `style.css`, `check_site.py`, an about page). Re-read every `site/` file at run time, find selectors and strings by grep, never by line number, and never revert or reformat a change you did not make. If a site file has uncommitted changes from someone else when you start, record that in the SUMMARY and edit around them.

Environment:
- The executor cannot commit. Leave every change in the working tree; the orchestrator reviews and commits. No state-changing git commands.
- Run every Python command through `uv`; if the shell does not find it, run `export PATH="$HOME/.local/bin:$PATH"` first. Install nothing and add no dependency. Two tools run outside `uv`, from `.shots/` (ignored by git) and never added to the repository: `node` with Playwright at `/home/roux/.local/share/playwright-1.62.1/node_modules/playwright`, and the system `python3` with its Pillow, used only to encode screenshots as lossless WebP. Poppler's `pdftotext`, `pdfinfo` and `pdftoppm` are on the path.
- Locate Python symbols with grep at run time, never by line number. Re-read every file before editing.
- Never weaken a test or a principle. Task 1 keeps every assertion of `tests/test_report.py`; it only stops repeating stylesheet checks that cannot differ. The design checks are new tests that DESIGN.md "Checks" assigns to the redesign and the change map assigns to this plan; other existing tests change only as UI-SPEC section 9 permits.
- No network except the local static server the browser check starts on 127.0.0.1 for `site/`.
- Do not edit the Phase 1.1 plans, `01.1-CONTEXT.md` (RR-01 writes the D-81 amendment), the READMEs, `publiccode.yml`, DESIGN.md, UI-SPEC.md, the change map or any other RR plan. On the home pages, change only the report card's `img` alt text and, if it no longer matches, the download size in its caption (Task 2). Task 3 lists everything else.
- Principles (change map): no score, overall judgement, proposed resolution, effort estimate or supplier recommendation in anything written here; Unknown never improves a status; no person names; no script in the report.
- German: every new or changed German string (the two alt texts) is a draft and goes into the native-review table of the SUMMARY. Formal "Sie", no abbreviations such as "z. B.", status names exactly Bereit, Handlungsbedarf, Hindernis, Unbekannt.
</context>

<tasks>

<task type="tracer">
  <name>Task 1 (size M): Design rules end to end: stylesheet checked once with a matrix guard, the report's colour, font and symbol rules, no coverage symbol equal to a status symbol, and the same rules for site/style.css in check_site.py</name>
  <files>tests/test_report.py, site/check_site.py, site/style.css, site/icons/help.svg, site/icons/warning.svg, src/fazit/templates/report.html.j2</files>
  <read_first>DESIGN.md ("Tokens", "Symbols", "Accessibility and weight", "Checks"), .planning/report-redesign/UI-SPEC.md (6.1, 6.2 with its six exceptions and the coverage-symbol paragraph, 9), .planning/quick/261122-rv6-tests/PLAN.md (item 1), tests/test_report.py (grep `SAMPLES =`, `PROFILES`, `def _sample_report`, `def test_report_document_structure`, `def test_report_styles_work_in_light_dark_narrow_and_print`, `def test_report_and_website_share_colour_tokens`, and the per-status symbol assertion that reads `<span class="status {status}"><svg`), tests/helpers.py (grep `class ReportDocument`, `def rebuild_report`, `def report_section`), site/check_site.py (grep `def main`, `CSS_REFS`, `def css_references`, `EMBEDDED_FONT`), site/style.css (every `:root` block, every `box-shadow`, every `mask-image`, every `font`/`font-family` declaration and `--sans`/`--mono`, every `url(`, the `.cov-*::before` and `.status-shape*` rules), src/fazit/templates/report.html.j2 (the style block in full; the `status_label` macro's status-to-symbol map; the coverage cell markup in `moves`), src/fazit/report.py (grep `_ICONS`), src/fazit/icons/ and site/icons/ (file lists)</read_first>
  <behavior>
    - `test_report_styles_work_in_light_dark_narrow_and_print` runs once per language on the town report with the openDesk profile and keeps every stylesheet assertion it has; the per-status symbol assertion, whose result depends on which statuses a sample has, moves unchanged into `test_report_document_structure`, which keeps its sample-by-profile matrix and now also asserts that each report's single stylesheet equals that language's reference stylesheet
    - New `test_report_styles_follow_the_design_rules`, once per language: outside the `:root` token blocks the report's CSS has no hex, `rgb`, `rgba`, `hsl` or `hsla` value except `rgb(0 0 0 / 12%)` inside `box-shadow` (UI-SPEC 2.2, selected segment); `@font-face` declares only Figtree and "Geist Mono"; every other `font-family` or `font` declaration names its family only through `var(--sans)`, `var(--mono)` or `inherit`; `--sans` starts with Figtree and `--mono` with "Geist Mono", followed only by the generic families `ui-sans-serif`, `system-ui`, `sans-serif`, `ui-monospace`, `monospace`; every SVG in `src/fazit/icons/` is byte-identical to the file of the same name in `site/icons/`; the set of symbol paths drawn in the replacements table's coverage cells and the set drawn in `span.status` labels are both non-empty and share no path (DESIGN.md "Symbols"; UI-SPEC 11 criterion 12)
    - `test_report_and_website_share_colour_tokens` (the shared palette) stays as it is
    - `site/check_site.py` gains `check_design`, called from `main`: in `site/style.css`, outside `:root` blocks, no hex, `rgb`, `rgba`, `hsl` or `hsla` value except the shadow values named in one constant, each only inside `box-shadow`; the same font rules as the report; every `url()` is `fonts/<file>.woff2` inside `@font-face` with the file in `site/fonts/`, or `icons/<file>.svg` with the file in `site/icons/`; no `.cov-*` rule draws an SVG whose path data equals that of a status symbol (the four files the report's `status_label` uses); each error names the file and the offending value
    - The site and the report pass: in `site/style.css` the report-card mask's opaque stop is `var(--bg)` instead of `#000`, `--mono` lists "Geist Mono" followed only by generic families, and `.cov-full::before` draws `icons/circle.svg` instead of Ready's `check-circle` (RR-04 made that change; this plan only checks it); in the report, any colour literal left outside the token blocks takes its token (the bar mask's opaque stop `var(--bg)`; RR-04 already gave the dark-mode hover glow `var(--link-glow)`); `site/icons/` gains `help.svg` and `warning.svg`, byte-identical to the packaged ones, so the shared set holds every symbol the report inlines
  </behavior>
  <action>
    Stylesheet once (rv6 item 1 for this file). Add to `tests/test_report.py` a cached helper that renders the town report with the openDesk profile for one language into its own temporary directory and returns the HTML, so each language renders once per test session. Re-parametrise the styles test over the two languages using that helper; keep every assertion. Move the per-status symbol assertion, as it is, into the document-structure test, and add there the assertion that the report's single stylesheet equals the reference stylesheet of its language: this guard makes the single check complete. Keep the escaping and structure tests on their matrix, because their results can differ by sample and profile (status groups come and go).

    Report design test. Write `test_report_styles_follow_the_design_rules` with small, readable helpers in the test module: remove the embedded font data and every `:root { … }` block, read each `property: value;` declaration, and check colours, fonts and the font tokens as the behaviour says; compare the icon files by bytes; collect the `path d` values inside the coverage cells of `report_section(html, "moves")` (read RR-04's markup for the cell selector) and inside every `span.status`, and assert both sets are non-empty and disjoint. Report each failure with the property and value, or the symbol path's owner.

    Site design check. In `site/check_site.py`, add `check_design()` with the same declaration reading; the shadow values as a named constant with a one-line comment saying why they are allowed: at `df36196` they are `rgb(0 0 0 / 4%)`, `rgb(0 0 0 / 8%)` and `rgb(0 0 0 / 18%)`, so grep every `box-shadow` at run time and list exactly what is there, never a value that appears outside `box-shadow`; the font rules; the `url()` rule; and the coverage-symbol rule, reading the status symbol names from the template's `status_label` map (`check-circle`, `warning`, `report`, `help` at `df36196`) and comparing SVG path data, so a renamed copy is caught. Call it from `main()` with the other checks. Keep it short; it guards only what a machine can check (DESIGN.md "Checks").

    Make both pass. In `site/style.css`, change the report-card mask's `#000` to `var(--bg)` (a mask reads only alpha, so nothing changes on screen), and drop "SFMono-Regular", Menlo and Consolas from `--mono`. Do not edit `.cov-full::before`: RR-04 owns the switch to `icons/circle.svg`, and `check_design` only confirms it. In the template, change only colour or font literals the new test reports, as the behaviour says, and keep the report's `--mono` equal to the site's. UI-SPEC 6.2 exception 3 writes the bar mask with `#000 32px`; `var(--bg) 32px` draws the same mask, so record the substitution in the SUMMARY. Copy `src/fazit/icons/help.svg` and `src/fazit/icons/warning.svg` to `site/icons/` unchanged; the licence file is already there. The site-lean batch deleted both as unused; they come back because DESIGN.md "Symbols" makes `site/icons/` the shared set the report inlines from, which Task 3 records.
  </action>
  <verify>
    <automated>uv run pytest tests/test_report.py -q && uv run pytest -q && uv run ruff check . && uv run ruff format --check . && uv run python site/check_site.py && for f in src/fazit/icons/*.svg; do cmp -s "$f" "site/icons/$(basename "$f")" || exit 1; done</automated>
  </verify>
  <acceptance_criteria>
    - `uv run pytest tests/test_report.py -q` exits 0, and `uv run pytest tests/test_report.py -q --collect-only -k "styles_work"` collects 2 items [HEAD=12 EXPECT==2]
    - `uv run pytest tests/test_report.py -q --collect-only -k "follow_the_design_rules"` collects 2 items [HEAD=0 EXPECT==2]
    - `grep -c "def check_design" site/check_site.py` [HEAD=0 EXPECT==1]
    - `grep -c "#000 70%" site/style.css` [HEAD=1 EXPECT==0] (the `#000000` inside the `:root` token block is a token and stays)
    - `grep -c "Menlo\|Consolas\|SFMono" site/style.css` [HEAD=1 EXPECT==0]
    - `grep -c "icons/check-circle.svg" site/style.css` [HEAD=0 after RR-04, EXPECT==0] (a check, not an edit of this plan)
    - `uv run python site/check_site.py` ends with "No errors."
    - Mutation check, then restored: putting `#123456` in a report rule outside the tokens, or pointing a coverage symbol at `check-circle`, makes the new test fail; the same edits in `site/style.css` make `check_design` fail. The SUMMARY records each
    - No assertion that existed in `tests/test_report.py` before this task is missing after it (the SUMMARY maps each moved assertion to its new place)
    - Follows DESIGN.md ("Checks": colours only as tokens, two font families, symbols from the shared set and never a status symbol for anything else, shared palette)
  </acceptance_criteria>
  <done>The stylesheet is checked once per language without losing an assertion, and DESIGN.md's machine-checkable rules, including the coverage-symbol rule, fail the build for both the site and the report.</done>
</task>

<task type="auto">
  <name>Task 2 (size L): Page one on real A4 PDFs, the site comparison, regenerated sample reports, and the home card's eight screenshots with new alt text</name>
  <files>site/demo/en/index.html, site/demo/de/index.html, site/images/readiness-en-light.webp, site/images/readiness-en-dark.webp, site/images/readiness-en-mobile-light.webp, site/images/readiness-en-mobile-dark.webp, site/images/readiness-de-light.webp, site/images/readiness-de-dark.webp, site/images/readiness-de-mobile-light.webp, site/images/readiness-de-mobile-dark.webp, site/index.html, site/de/index.html</files>
  <precondition>`node --version` succeeds, Playwright exists at `/home/roux/.local/share/playwright-1.62.1/node_modules/playwright` with its Chromium, `python3 -c "import PIL"` succeeds, and `pdftotext`, `pdfinfo` and `pdftoppm` are on the path. If any is missing, regenerate the sample reports only, record what did not run, and hand back.</precondition>
  <read_first>DESIGN.md ("Symbols", "Accessibility and weight": images in WebP, 360 px), .planning/report-redesign/UI-SPEC.md (1.2 with "Page one", 6.2 and its six exceptions, 7 "Print", 10 the unfavourable cases, 11 criteria 1, 2, 13 to 19), .planning/research/apple-lens/REVIEW.md (section 2 "Report preview", section 5 item 2), .planning/report-redesign/RR-03-SUMMARY.md (the all-Unknown fixture `tests/fixtures/all_unknown_scan.json`, `ALL_UNKNOWN_SCAN`), .planning/report-redesign/RR-04-SUMMARY.md (the `print` part), .shots/report-redesign/check.mjs (argument contract, parts `filters`, `layout`, `print`), site/index.html and site/de/index.html (the `figure.report-preview`: `picture` sources, sizes, media queries, `img` alt text, caption with the download size), site/check_site.py (grep `def check_assets`, `def check_demo_reports`, `def check_tally`, `def webp_dimensions`), .planning/quick/261122-site-lean/SUMMARY.md (how the WebP files were encoded)</read_first>
  <behavior>
    - Part `pageone` of `.shots/report-redesign/check.mjs` reads six reports: the four sample reports and `allunknown-en` and `allunknown-de` (RR-03's all-Unknown fixture rendered in each language). For each, with backgrounds on and off, it prints an A4 PDF with Chromium (print media, light scheme), checks the page size with `pdfinfo`, and reads the text of page 1 and page 2 with `pdftotext`. Page 1 must contain, read from the same report's DOM and never from literals in the script: the organisation (`.eyebrow`), the `h1`, every date of the meta row, the sample note when the report has one, every row of `dl.status-summary` (status name, count, definition), the "What blocks this move" heading with either its first row's area name or the zero-blocker sentence and its caveat, the "What is still unknown" heading with its first row's area name, the scope statement heading when the report has one, the three tile labels with their anchors (amount or the Unknown label), the Stay assumption and every break-even line present. Page 2 must begin with the `path` section's heading, so nothing of the summary spilled over. Page 1 contains no readiness bar, filter legend or search hint text
    - The other parts keep reading only `town-en`, `town-de`, `nonprofit-en` and `nonprofit-de`; if a part iterates every subdirectory, it is restricted to those four names
    - Part `site`: it serves `site/` from a local static server on 127.0.0.1, opens the English and German home pages (and, for `.page-intro`, the start pages) and the matching town reports at 1280 and 360 px in light and dark, and compares the computed styles of the shared components present on both (body text, `.bar-in`, `.wordmark`, `.bar-links a`, `.sec-label`, `.eyebrow`, `.tiles li`, `.figure-num`, `.coverage thead th`, `.coverage td`, `.note`, `.legend`, `.finding` surface and padding, `.finding-area`, `.finding-status`): font family, size, weight, colour, background colour, padding, radius. Every difference is either one of UI-SPEC 6.2's six exceptions, named in the script with its number (exception 6 covers the card's area name as anchor and the status at body size), or a failure. A listed selector missing on one side is reported, never skipped silently
    - It saves side-by-side screenshots of the home page and the report, first screen and a card, at 1280 and 360 px in light and dark, to `.shots/report-redesign/out/`
    - The whole check (`filters`, `layout`, `print`, `pageone`, `site`) exits 0; the CSP check compares the meta content with the unchanged string and no request leaves the report file
    - `site/demo/en/index.html` and `site/demo/de/index.html` equal fresh `fazit demo --sample town --profile opendesk` runs
    - The eight `site/images/readiness-*.webp` show the regenerated report's summary: the section heading, "Of {n} areas:", the four status rows each with count and definition, then "What blocks this move" with its first row where the frame has room. 2016 by 1120 (desktop) and 800 by 1440 (mobile) pixels, lossless, each under 150,000 bytes, with the file names and declared sizes the home pages already use. No readiness bar is in any shot
    - Both home pages' report-card `img` alt text describes that screen, with the counts read from the regenerated report in display order (Blocker, Needs work, Unknown, Ready); the caption's download size matches the regenerated report
  </behavior>
  <action>
    All-Unknown reports. RR-03's fixture is `tests/fixtures/all_unknown_scan.json`, exposed to tests as `ALL_UNKNOWN_SCAN` (grep both to confirm). For each language run `uv run fazit report tests/fixtures/all_unknown_scan.json --lang <lang> --profile opendesk --out <dir>/allunknown-<lang>`, adding `--inputs <file>` only if RR-03-SUMMARY names an inputs file for the fixture. Add no fixture and commit no generated file.

    Page one. Add the part `pageone` to `.shots/report-redesign/check.mjs` as the behaviour says, keeping its argument contract and one-line-per-failure output. Use Chromium's `page.pdf` with `format: "A4"` and `printBackground` true and false; write the PDFs and `pdftoppm` previews of pages 1 and 2 at 50 dpi to `.shots/report-redesign/out/pageone-<report>-<bg>.*`. Split pages on form feeds; compare after collapsing whitespace. Use `pdftotext` without `-layout` (or `-raw` if the reading order splits an element), and record which mode passed. If a report's page one overflows, do not change the template: record the report, language and what spilled, and hand back, because print rules belong to RR-04.

    Site comparison. Add the part `site` as the behaviour says. The static server uses only `node:http` and `node:fs`, binds to 127.0.0.1 on a free port, serves files under `site/` and nothing else, and stops at the end. Read the expected values from the site's computed styles, never from literals in the script.

    Sample reports. For each of `en` and `de`, run `uv run fazit demo --lang <lang> --sample town --profile opendesk --out <fresh temporary directory>` and copy the printed report over `site/demo/<lang>/index.html`.

    Screenshots (the home card shows the report's best first screen). Write `.shots/report-redesign/shots.mjs`: for each language, each frame (desktop 1008 by 560 CSS pixels, mobile 400 by 720) and each colour scheme, open `site/demo/<lang>/index.html` through `file://` with the frame's width, a height of 900, device scale factor 2 and that scheme; wait for `document.fonts.ready`; take the top of `[data-section="summary"] h2`, subtract the height of `.bar` and 32 px, so the heading sits below the sticky bar; set the viewport to the frame; scroll there; wait 150 ms; check that the four `dl.status-summary` rows are inside the frame (record whether the first "What blocks this move" row is too); save a PNG in `.shots/report-redesign/out/`. Encode each PNG with the system `python3` and Pillow as lossless WebP (`lossless=True, exact=True, method=6`) to `site/images/readiness-<lang>-<scheme>.webp` or `site/images/readiness-<lang>-mobile-<scheme>.webp`. The names stay, because the home pages and `check_assets` (`images/readiness-*`) use them. Check each file's pixel size and that it is under 150,000 bytes; never raise the limit in `check_site.py`; if a file is over it, keep the old file and record the size.

    Alt text. In `site/index.html` and `site/de/index.html`, replace only the report card's `img` alt text, keeping its attributes and the `picture` sources unchanged. Read the counts from the regenerated report's `dl.status-summary`. Drafts, with the counts of the town at 14 areas:
    - English: "Summary of the sample report: of 14 areas, 1 Blocker, 9 Needs work, 1 Unknown and 3 Ready, each with what the status means, then what blocks this move."
    - German (*draft*, native review): "Überblick aus dem Beispielbericht: von 14 Bereichen 1 Hindernis, 9 Handlungsbedarf, 1 Unbekannt und 3 Bereit, jeweils mit der Bedeutung des Status, danach, was diesem Umstieg entgegensteht."
    If the caption's "Download HTML, … KB" / German equivalent no longer matches the regenerated file rounded to 10 KB as today, update the number only. Leave the tally sentence (RR-01's, checked by `check_tally`) and everything else on the home pages to the follow-ups.

    Run the full check and `uv run python site/check_site.py`.
  </action>
  <verify>
    <automated>d="$(mktemp -d)" && for s in town nonprofit; do for l in en de; do uv run fazit demo --lang "$l" --sample "$s" --out "$d/$s-$l" > "$d/$s-$l.log" && test -f "$(tail -n 1 "$d/$s-$l.log")" || exit 1; done; done && for l in en de; do uv run fazit report tests/fixtures/all_unknown_scan.json --lang "$l" --profile opendesk --out "$d/allunknown-$l" > "$d/allunknown-$l.log" && test -f "$(tail -n 1 "$d/allunknown-$l.log")" || exit 1; done && node .shots/report-redesign/check.mjs "$d" && uv run python site/check_site.py && python3 -c 'from PIL import Image; from pathlib import Path; sizes = {"": (2016, 1120), "mobile-": (800, 1440)}; files = [(Path(f"site/images/readiness-{l}-{m}{s}.webp"), size) for l in ("en", "de") for m, size in sizes.items() for s in ("light", "dark")]; bad = [(str(p), Image.open(p).size, p.stat().st_size) for p, size in files if Image.open(p).size != size or p.stat().st_size >= 150000]; assert not bad, bad'</automated>
    If RR-03-SUMMARY names an inputs file for the fixture, add `--inputs <file>` to the two `fazit report` calls. The `pageone` part fails if either all-Unknown report is missing.
    <human-check>Criterion 19: both reviewers compare the side-by-side screenshots in `.shots/report-redesign/out/` at 1280 and 360 px, light and dark, and sign off that site and report look like one product. The maintainer opens the page-one previews (all six reports, backgrounds on and off) and the home page on localhost in light and dark, desktop and phone, English and German, and confirms the card shows the summary and the alt text matches it.</human-check>
  </verify>
  <acceptance_criteria>
    - `node .shots/report-redesign/check.mjs <dir>` exits 0 with all five parts, and part `pageone` covers six reports times two background settings
    - `uv run python site/check_site.py` ends with "No errors."
    - The eight WebP files are newer than `site/demo/en/index.html`, have the declared sizes and are under 150,000 bytes each
    - `grep -c "Readiness section of the sample report" site/index.html` [HEAD=1 EXPECT==0] and `grep -c "Abschnitt zur Bereitschaft aus dem Beispielbericht" site/de/index.html` [HEAD=1 EXPECT==0]
    - This task's own edits to the two home pages are the `img` alt attribute and, at most, the caption's size number (the SUMMARY shows both diffs)
    - Follows DESIGN.md (images in WebP; every page works at 360 px; one product; symbols never reused for another meaning)
  </acceptance_criteria>
  <done>Page one is proved on paper for the favourable, the unfavourable and the all-Unknown report in both languages, the browser proves the report's likeness to the site, and the home card shows and describes the redesigned summary.</done>
</task>

<task type="auto">
  <name>Task 3 (size M): Record the decisions with their roadmap and requirements notes, run every check, and list the founder action, the Phase 1.1 changes and the other follow-ups</name>
  <files>DECISIONS.md, .planning/ROADMAP.md, .planning/REQUIREMENTS.md</files>
  <read_first>DESIGN.md ("Copy"), DECISIONS.md (principles, D20, D21, D31 for style), .planning/report-redesign/UI-SPEC.md (section 9 "Decisions to record", the closing founder action), .planning/report-redesign/REV4-CHANGE-MAP.md (RR-05 rows and the revision 4.1 table), .planning/research/report-usefulness/SYNTHESIS.md (section C, decisions 2, 3, 5, 6, 13), .planning/research/apple-lens/REVIEW.md (sections 5 and 6), .planning/phases/01-demo-and-report/01-CONTEXT.md (D-19, D-26, D-64), .planning/phases/01.1-ai-assistants-and-decision-window/01.1-CONTEXT.md (D-81 as amended by RR-01, D-90), the plans 01.1-01 to 01.1-04, .planning/ROADMAP.md (Phase 1.2, "Notes on Order and Mapping"), .planning/REQUIREMENTS.md (RULE-02, REPT-02, OUTP-03, AIAS-01, the traceability table and coverage counts), src/fazit/templates/report.html.j2 (the finished template), src/fazit/rules/status.yaml (count `next_step:` and `kind:`), the RR-01 to RR-04, RR-06 and RR-07 SUMMARY files</read_first>
  <behavior>
    - DECISIONS.md has a new dated entry directly below the principles, headed with the run date and "Report redesign", in the file's style (a bold decision line per number, short bullets, plain statements, no plan ids), taking the next free D numbers (grep `^\*\*D[0-9]+\.` and `^- \*\*D[0-9]+\.`; RR-06 or RR-07 may have taken some)
    - First decision, the report's structure, departing from D-19, D-26 and D-64 (named by id) and from the order in REPT-02: ten sections in the order header, summary, path ("What to do next"), readiness, costs, moves, attention, found, appendix, footer; one card per assessed area, grouped by status in the display order Blocker, Needs work, Unknown, Ready on a copy, with the rule engine's status order unchanged; the area name is each card's anchor with the status under it; the readiness bar stays only as the visual of the area filter, and the summary has no bar or other part-of-whole picture; categories and next steps (with their kind: clarify, decide or replace) are catalogue and rule data; filters use radio inputs and CSS only and change no count, status, summary or printed page; "What to do next" holds what is worth doing even if the organisation stays and what only a move needs, with no stock steps or timeline; costs show three five-year totals in whole units with the Stay assumption and a break-even line on target operations, computed from the cost model without changing it, and the chart draws one scale from known totals and no bar for an unknown total; the site's tokens and components are reused with six named exceptions; coverage symbols never reuse a status symbol (`in_suite` is a filled circle, on the site too); `site/icons/` holds every symbol the report inlines, even ones the site does not use; the design rules are checked by `site/check_site.py` and the report tests; the D-81 amendment in `01.1-CONTEXT.md` by reference
    - Second decision: Licences is inventory only, with no status, card or category; its evidence stays in the recorded inventory; the area count comes from the assessed catalogue (14 before Phase 1.1). It amends D21 and RULE-02; D21 gains "(amended by D…)" after its bold line, as D24 and D25 name their replacements
    - Third decision: page one (header and summary) is written for the council and is the same on screen and on paper; it carries the organisation, evidence and answer dates, the sample or invented-price note, each status with its count and definition, the blockers or the zero-blocker sentence with its caveat, the open questions and the three totals with their origin, and never a proposed resolution; it is checked on real A4 PDFs for both samples and an all-Unknown report in both languages; pasting into a council paper is best effort. This pulls OUTP-03 from Phase 1.2 into the redesign
    - Decisions that RR-06 or RR-07 own (desktop inference, target-aware readiness, the mapping review gate) are not written here; if their SUMMARY says an entry is still owed, it goes into the follow-ups
    - REQUIREMENTS.md: RULE-02 and REPT-02 each gain a short note naming the amending decision; OUTP-03's text matches the third decision (counts and definitions in place of "status per area", print tested, paste best effort); its traceability row reads "Report redesign | Pending"; the coverage counts gain "Report redesign: 1" and Phase 1.2 drops to 3; the "Last updated" line says why. ROADMAP.md: Phase 1.2's requirements drop OUTP-03, and "Notes on Order and Mapping" gains one bullet saying OUTP-03 moved into the report redesign by founder decision on 2026-11-22, naming the DECISIONS entry
    - All six "Done means" commands of AGENTS.md and the browser check pass
    - The SUMMARY contains "Founder action", "Phase 1.1 plan steps to update" and "Follow-ups outside this scope", each item checked against the finished template and the plan text
  </behavior>
  <action>
    Decisions (UI-SPEC section 9). Write the entry of the behaviour list. Name the decisions it departs from or amends by their ids (D-19, D-26, D-64, D21, RULE-02, OUTP-03) so a reader can find them. Say what the report does, in plain statements; the entry itself carries no score, overall judgement or recommendation.

    Roadmap and requirements notes. Make only the edits of the behaviour list. Leave OUTP-03 unchecked: the orchestrator ticks it when the redesign merges.

    Final run. Run `uv run ruff check .`, `uv run ruff format --check .`, `uv run pytest -q`, `uv run fazit demo --lang de` and `uv run fazit demo --lang en` (each into a fresh temporary directory), `uv run python site/check_site.py`, and the browser check on the six reports of Task 2. Open one report with the network off to confirm the offline claim.

    Founder action. Under "Founder action", state UI-SPEC's closing step: before RR-02, one council clerk or Kämmerer reads page one unexplained and says what it supports and what is still open, with the answer recorded beside UI-SPEC.md. Check whether that record exists; if it does not, say so plainly. It is not a build criterion.

    Phase 1.1 list. Do not edit the Phase 1.1 plans. Under "Phase 1.1 plan steps to update", list each step the redesign affects, with the plan, task and field, what it says now and what it must say. Confirm or correct each item below against the finished template and the plan text, and add any further item you find (search the four plans for table-row regexes, "second row", "second area", "readiness table", "evidence group", "found section", `.figure`, `.png`, `next_step`, `rules.py`, "16" and the header sentences):
    - 01.1-01, must_haves truth 1, Task 1 behaviour and acceptance ("second row of the readiness table", `rows[1] == ("copilot", "needs_work")`, "[HEAD=15 EXPECT==16]"): becomes the amended D-81: `copilot` stays second in the catalogue; Licences has no card, so Copilot is the first card of whichever status group it is in; first under Automation and AI in the category filter; evidence on the card; its functions first in the replacements table. Cards are counted, not rows: 14 today, 15 with Copilot.
    - 01.1-01, Task 1 "Catalogue": the new workload entry needs `category: automation_ai`, or the catalogue refuses it.
    - 01.1-01, "Status rules" in Tasks 1 and 2: each of the eight `copilot-*` rules needs `next_step` in English and German with its `kind` (clarify, decide or replace, set per sentence from the action it names), an owner role from RR-01's fixed set, no supplier or product, and native-German review; no Needs work reason may say "blocks" or "Hindernis" (RR-06's test). The acceptance counts of `next_step:` and `kind:` in `status.yaml` become today's count plus 8 (32 workload rules after RR-06, plus RR-07's two `target_gaps` templates outside `workloads`, so 34 `next_step:` lines before Phase 1.1; recount).
    - 01.1-01, Task 3 mappings: Copilot's mapping rows follow RR-07's conventions (a specific citation per row, "Direct transfer undocumented" where only the method is undocumented, the unreviewed marker until the operator review), and the rules must work with RR-07's profile-aware evaluator; the scope statement then counts them without a template change.
    - 01.1-01 Task 2 `<verify>` (`data-workload="copilot" data-status="needs_work" data-incomplete`): still matches the card; no change.
    - 01.1-02, Task 1 `<verify>`: the Copilot regex reads the `article` card; its `li[data-evidence]` sits inside the card's closed disclosure, still in the HTML.
    - 01.1-02, Task 2 read_first: the licence table is in a closed `details` in the recorded-inventory section ("What Fazit recorded"), which now follows "attention" near the end.
    - 01.1-03: the `licence-contract` subsection stays in `found`, between the headline tiles and the licence-products disclosure, on the redesign's classes and tokens. New work from UI-SPEC 1.2 item 6 (D-90): two summary tiles after the cost tiles and the Stay and break-even lines, "Next renewal" and "Latest notice date", each `li` with `data-decision` and `data-provenance`, reusing the plan's date function, answer source and `as_of` fallback; an end date without a notice period gives a Provided renewal and an Unknown notice date; each tile names only the input it lacks; tests for both tiles and the partial case; and page one must still fit A4, so the plan reruns part `pageone`.
    - 01.1-03, Task 2 tests: the `data-subsection` order assertion becomes not-examined (now in `path`), cannot-be-moved, licence-contract, run-details, plus any subsection RR-04 added (read the current assertion); helpers come from `tests/helpers.py`.
    - 01.1-04, Task 1 "Counts" and `<verify>`: count `article` cards, not table rows; replace `rows[1][0] == "copilot"` with the amended-D-81 check. With Licences unassessed the site says 15 areas, not 16, in the figure tile, the tally, the pilots pages, `publiccode.yml` and the READMEs; the tally is checked against the demo by `check_tally`.
    - 01.1-04, Task 2 read_first: "the telephony readiness row and its licence evidence" becomes the telephony card and its evidence disclosure.
    - 01.1-04, Task 3 and frontmatter: the screenshots are `.webp` (the plan still says `.png`) of the summary frame; reuse `.shots/report-redesign/shots.mjs`; the alt text keeps this plan's form with the new counts in display order; drop "the second row visible in each is the AI assistants area" and its human check.
    - All four plans: references to functions in `src/fazit/rules.py` predate the split into `status.py`, `mappings.py`, `licences.py`, `evidence.py` and `validation.py`; add DESIGN.md and UI-SPEC.md to their reading lists.
    - REQUIREMENTS.md AIAS-01 and ROADMAP's 01.1-04 line still say "second area, after licences" and "16 areas": they follow the amended D-81 and the assessed count when Phase 1.1 is planned again.

    Follow-ups outside this scope, also in the SUMMARY. Check each against the files and drop any that is already done:
    - Home pages (site work, not this plan's code): "15 areas" in the figures strip (`site/index.html`, `site/de/index.html`) becomes 14 assessed areas (RR-01 already changed `/pilots/`, the tally and the alt-text counts); the tally lists statuses in display order (Blocker, Needs work, Unknown, Ready), which needs `check_tally` in `site/check_site.py` to follow (it iterates `STATUSES`); "What you get" still names the nine old sections, including the suggested path; the "One finding in full" card still makes the status its anchor, while report cards now lead with the area name; `site/og.png` shows an older excerpt.
    - Optional founder calls (Apple-lens review, section 6): Mail in place of Telephony as the homepage example, and dropping the readiness bar above the filters.
    - README.md and README.de.md: "What the report shows" lists the nine old sections and "partial exit" (RR-01 already changed "fifteen areas" to fourteen); `publiccode.yml` says 15 areas in both descriptions.
    - DESIGN.md "Checks" still says the design checks are added with the redesign; after this plan they exist, which needs a wording change under DESIGN.md's own rule.
    - The operator review of the mapping files (founder decision C4) gates shipping the redesign's scope statement; RR-07 marks the files unreviewed until it happens.
    - Any decision entry RR-06 or RR-07 left owed; OUTP-03 to be ticked on merge.
    - Human checks before merge, below.
  </action>
  <verify>
    <automated>uv run ruff check . && uv run ruff format --check . && uv run pytest -q && outen="$(mktemp -d)" && logen="$(mktemp)" && uv run fazit demo --lang en --out "$outen" > "$logen" && test -f "$(tail -n 1 "$logen")" && outde="$(mktemp -d)" && logde="$(mktemp)" && uv run fazit demo --lang de --out "$outde" > "$logde" && test -f "$(tail -n 1 "$logde")" && uv run python site/check_site.py && grep -q "Report redesign" DECISIONS.md && grep -q "D-64" DECISIONS.md && grep -q "RULE-02" DECISIONS.md && grep -q "OUTP-03" DECISIONS.md && ! grep -q "OUTP-03 | Phase 1.2" .planning/REQUIREMENTS.md</automated>
    <human-check>Before merge: the maintainer's native-German review of every German string drafted in RR-01 to RR-07: the `next_step` sentences of all problem rules, every section 8 value marked *draft*, the category labels, the copy RR-06 and RR-07 added for their rules, labels and mappings, and this plan's German alt text; both reviewers' sign-off of criterion 19; the maintainer's look at the page-one PDF previews and at the home card on localhost in both themes.</human-check>
  </verify>
  <acceptance_criteria>
    - All six AGENTS.md "Done means" commands succeed, and the browser check exits 0 with all five parts
    - `grep -c "Report redesign" DECISIONS.md` [HEAD=0 EXPECT>=1]
    - `grep -c "OUTP-03 | Phase 1.2" .planning/REQUIREMENTS.md` [HEAD=1 EXPECT==0]
    - `git diff --stat -- .planning/phases/01.1-ai-assistants-and-decision-window/` is empty
    - The SUMMARY has the sections "Founder action", "Phase 1.1 plan steps to update" and "Follow-ups outside this scope", and the native-review table with the two alt texts
    - Follows DESIGN.md ("Copy" for the DECISIONS.md entry and the notes)
  </acceptance_criteria>
  <done>The decisions are recorded with their notes in the roadmap and requirements, every check passes, and the founder, Phase 1.1 and the site each know exactly what is still theirs to do.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| package output → public site | Sample reports and screenshots are copied to a public website |
| design rules → future changes | Checks decide what later changes may do |
| page one → council file | A printed page one is filed with a Beschlussvorlage and read without the rest |

## STRIDE Threat Register

Security level: ASVS 1. Blocking threshold: high.

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-RR-13 | Tampering | test restructure drops an assertion | medium | mitigate | Every assertion kept; the matrix guard proves one stylesheet per language; the SUMMARY maps each moved assertion; mutation checks for the new rules (Task 1) |
| T-RR-14 | Tampering | site: a new external resource or script | medium | mitigate | No new resource; `check_site.py` reference and design checks; the local server binds to 127.0.0.1 only and serves `site/` only |
| T-RR-15 | Information disclosure | screenshots and PDFs | low | accept | They show invented sample data and a synthetic all-Unknown report; PDFs stay in the ignored `.shots/` directory |
| T-RR-16 | Repudiation | page one printed without its caveats | medium | mitigate | Part `pageone` proves the definitions, the zero-blocker caveat, the open questions and the cost origins are on page one for all three report kinds in both languages (Task 2) |
| T-RR-SC | Tampering | package installs | high | mitigate | Nothing is installed; Node, Playwright, Pillow and poppler already on the machine are used from an ignored directory |
</threat_model>

<verification>
Before declaring the plan complete:
- [ ] `uv run ruff check .` and `uv run ruff format --check .` exit 0
- [ ] `uv run pytest -q` exits 0
- [ ] `uv run fazit demo --lang de` and `uv run fazit demo --lang en`, each into a fresh temporary directory, exit 0 and the printed path exists
- [ ] `uv run python site/check_site.py` ends with "No errors."
- [ ] `node .shots/report-redesign/check.mjs <dir>` exits 0 with the parts `filters`, `layout`, `print`, `pageone` and `site`, the directory holding the four sample reports and the two all-Unknown reports
- [ ] UI-SPEC section 11 criteria 1 to 24 are each met or named in the SUMMARY with the human check that covers them (19: both reviewers)
</verification>

<success_criteria>
- Design rules are machine-checked for site and report, including the coverage-symbol rule
- Page one fits A4 for the town, the non-profit sample and the all-Unknown report in both languages, proved on real PDFs
- The site shows the redesigned summary with matching alt text
- Decisions recorded with their roadmap and requirements notes; Phase 1.1, the site and the founder have their exact lists
</success_criteria>

<output>
Create `.planning/report-redesign/RR-05-SUMMARY.md` when done. Record: the map of moved assertions in `tests/test_report.py`; the design-check rules, their allowed exceptions and the mutation checks; the template and site literals replaced by tokens (including the UI-SPEC 6.2 exception 3 substitution); the result of every browser check part per report, width, scheme and background setting, the `pdftotext` mode used, and the differences the site comparison accepted with their exception numbers; each screenshot's pixel and byte size and whether the first blocker row is in frame; the home-page diffs; the native-review table (the two alt texts); the "Founder action", "Phase 1.1 plan steps to update" and "Follow-ups outside this scope" lists; UI-SPEC section 11 criteria with how each was proved; the test count and runtime of `uv run pytest -q` (722 tests collected at `df36196`).
</output>

---
plan: RR-10
title: Coordinator's screenshot review fixes before landing
depends_on: ["RR-09"]
autonomous: true
---

# RR-10: fixes from the coordinator's screenshot review (2026-11-23)

The coordinator reviewed the built site and report at 1280 px and 360 px, light and dark, English and German, after RR-09, the lean pass, the visual pass and the German review. Fix every item below. Read `AGENTS.md` and `DESIGN.md` first (binding). Keep code lean: prefer deleting and reusing over adding. German must be native and formal.

## Founder requests (2026-11-23)
1. **Hero: "View sample report" becomes a secondary button.** On both home pages, make the hero's second action `btn btn-secondary` with a leading symbol (`icon-description`, as every button leads with one), next to the solid "Get started". Apple's own hero pairs a filled and an outlined capsule. Same height, same radius, same gap. On phones they sit side by side if they fit at 360 px, otherwise stacked at equal width.
2. **The category menu looks like an Apple menu.** Today Chromium shows its default select popup (square corners, blue highlight), and the trigger shows a heavy black border.
   - **Trigger:** the quiet capsule from the segmented control's family, no heavy border. The focus ring shows only on `:focus-visible`, in the site's focus style.
   - **Menu:** a floating rounded panel (radius from the scale, about 12 px), soft shadow, background `--bg` with a hairline border in dark mode; items with comfortable padding, a rounded hover/selected fill in `--fill`, no blue; a tick symbol before the selected item (space reserved on every item so labels align).
   - **How, without script:** use the customizable select (`appearance: base-select` with `::picker(select)`, `::picker-icon`, `option::checkmark`) as a progressive enhancement. Browsers without it keep their native menu, which on macOS and iOS is already the system menu. Keep the CSS-only filter working with keyboard and without script; RR-02's browser check must still pass. If a `details` menu works better without script, you may use it instead, but it must close after a choice; explain in the summary.
3. **Badges centred like Apple's.** In the status and "Evidence incomplete" badges, the word sits low and the symbol is not centred with it.
   - **Layout:** `inline-flex`, `align-items: center`, `line-height: 1`, equal top and bottom padding, the symbol sized to the cap height and centred on it.
   - **Trim:** use `text-box: trim-both cap alphabetic` (with the longhands as needed) so the capsule centres on the capitals. Without support, the fallback must still look centred.
   - **Same everywhere:** the same component in the report cards, summary lists, the home Mail card and the replacements table's status cells (their trailing chevron also sits low today: centre it).

## Home page
4. **Hero screenshot crop:** the report screenshot in the hero card starts with a stray horizontal rule at its top edge and cuts "All blockers ›" at the bottom. Re-crop (RR-05's recipe) so it starts at the section heading with even padding and ends cleanly after a whole element. Same for German and the phone image. Keep alt text accurate.
5. **One right edge:** section dividers end at 1200 px while cards end at 1180 and the command block at 1172. Use one content width for dividers, cards, command block and lists.
6. **Section ledes are inconsistent:** "Find the blockers" and "What stays on your computer" use a large dark lede; "Evidence…" and "Free and open source" use a smaller grey one; in "Free and open source" the second paragraph ("Claude and Codex write the code…") is dark after a grey one. Pick one lede style (DESIGN.md) for the first paragraph of every section and body style for what follows, on all home pages.
7. **Inline code** ("uv run --offline fazit demo") renders larger than the text around it. Size inline code to match the surrounding text optically (about 0.9em), here and in the report.

## Report
8. **Card titles are the anchor.** Area names that link (summary lists, "What to do next" groups, "Evidence still needed") render in the quiet grey link colour and look disabled. A title is in the text colour, with the chevron; only standalone "All …" links are quiet.
9. **"What openDesk covers":** the counts list is in footnote size while the "needed here" links below are in body size. Use one size: the counts list like the status list (body, counts right-aligned in the same column), the needed functions as a plain list in body size.
10. **Generic steps read as templates.** "For the functions listed here (Teams Phone and public telephone calling), the service lead and IT team plan how to provide them after the move." Write it as a plain sentence: "The service lead and IT team decide how Teams Phone and public telephone calling are provided after the move." German to match, natively. Fix in the locale/rules, not the template.
11. **Open points in cards are still vague.** The cards' "Evidence still needed" says "The answer is missing. Find out the answer and enter it in the inputs file." (SharePoint, Office files, Device management). Use the same specific question the summary already shows, plus who answers and the `inputs.yaml` field. RR-09 item 11 applies to the cards too.
12. **"Evidence still needed" list is inconsistent.** The first item (Exchange recipient export) has a different structure and repeats "Exchange recipient export" twice, then two run-on sentences. Give every item one structure: question as the title; then the area link; then "Who answers: IT team" (label in `--fg-2`, not a grey bold pseudo-heading); then the source (export or `inputs.yaml` field, field in code); then at most one sentence of guidance. No duplicated text.
13. **Costs:**
    - The tiles show whole euros, the table shows ".00" on every amount. Show whole euros in the table too (the rounding note then says amounts are rounded to whole euros), unless an amount has cents.
    - Negative differences render "EUR -72,200.00". Use a true minus or wording: "EUR 72,200 less" / the tile's wording.
    - "Calculated from sample inputs" repeats under every row and every tile. Say it once, as the caption of the cost section, and drop the per-row and per-tile repeats. Keep per-row provenance only where it differs.
14. **Replacements table:** "Checked on" repeats the same date on every row and wraps ("22 November / 2026"). If all rows share the date, state it once in the caption and drop the column; otherwise keep dates on one line (`white-space: nowrap`).
15. **Dates never break:** keep "22 November 2026" / "22. November 2026" together everywhere (non-breaking spaces in the formatter), including card target lines and the closer-look table.
16. **Evidence disclosure on phones:** "Evidence · 4 measured, 1 provided, 1 unknown" wraps mid-phrase at 360 px. Put the counts on their own line in `--fs-footnote` `--fg-2` under the "Evidence" label at narrow widths (or always, if it reads better).
17. **"Licences · There is no function to move."** reads oddly. Write it as a sentence in the caption style: "Licences have no function to move, so they are not in this table." German to match.

## Verify
- `uv run pytest -q`, `uv run ruff check .`, `uv run ruff format --check .`, `uv run python site/check_site.py` pass; RR-02's and RR-04's browser checks still pass.
- Screenshots at 1280 × 800 and 360 × 800, light and dark, EN and DE, into `.shots/report-redesign/rr10/`: the hero, the category menu open, a card with both badges, costs, replacements.
- No horizontal scroll at 360 px on any page. The printed A4 page one is unchanged in content.

## Summary
Write `.planning/report-redesign/RR-10-SUMMARY.md`: each item's change and files, deviations, test changes, and a table of new German strings.

---
plan: RR-09
title: UX polish to Apple's standard before the redesign lands
depends_on: ["RR-01", "RR-06", "RR-07", "RR-02", "RR-03", "RR-04", "RR-05", "RR-08"]
autonomous: true
---

# RR-09: UX polish before the redesign lands

The redesign is built (RR-01 to RR-08) but held on its branch. The founder reviewed the in-progress report on 2026-11-22 and found flaws that no plan fixes ("we need 10/10 UX/UI"). This plan fixes them, together with everything the coordinator's screen-by-screen review finds after RR-05 (section "Review findings", filled in before this plan runs). Nothing lands on main until it passes.

## Read first
- `AGENTS.md`, `DESIGN.md` (binding).
- `.planning/report-redesign/UI-SPEC.md`.
- The SUMMARY files of RR-01 to RR-08.
- The rendered `site/demo/en/index.html` and `site/demo/de/index.html`, viewed in a browser at 1280 px and 360 px, in light and dark mode.

## Founder decisions (2026-11-22)
1. **A sticky index on the left.** On wide screens (from the width where the section grid has two columns), the report shows an "On this page" index as a card in the left column. Apple's developer documentation is the model.
   - **Position:** it stays in view while the page scrolls, below the top of the viewport by the spacing scale.
   - **Content:** it lists the report's sections in order with the same labels as RR-04's navigation, and marks the section in view.
   - **Marking without script** (the report runs none): marking the current section must work in CSS only. Use `:target` for the section jumped to. If scroll-driven marking is not possible without script, mark only the target and say so in the summary; do not add script.
   - **On phones and narrow widths:** the index becomes a compact control at the top of the report that opens the same list (a `details` element styled as a button).
   - **Replaces RR-04's top bar** on wide screens. Keep the skip link. Section labels stay where they are; the index card sits above them or replaces their left-column position. Choose the cleaner layout and describe it in the summary.
   - **Print:** the index never prints.
2. **One segmented control for the filters.** The area filters show one segmented control: status (All, Blocker, Needs work, Unknown, Ready, each with its count). Category becomes a single compact menu button next to it, "All categories ▾" / "Alle Kategorien ▾", that opens the list of categories.
   - **Without script:** use `details` and `summary` with radio inputs inside, or a native `select` if the CSS-only filter rules can read it. Keep the filter working with keyboard and without script, as RR-02's browser check proves.
   - **When a category is chosen,** the button's label shows it.

## Founder findings to fix
3. **Status list in the summary.** Today the counts follow the names in a different size and baseline, and the definitions trail on the same line in tiny type.
   - **Row 1:** one row per status, in display order, with the status symbol, the status name and the count. Name and count in the same size, on one baseline; the count aligned right in a fixed column, with tabular figures.
   - **Row 2:** the definition, in `--fs-footnote` and `--fg-2`, aligned with the name.
   - **Phones:** it must read cleanly at 360 px.
4. **Underlined titles.** Area titles in the summary lists ("What blocks this move", "What is still unknown") and in similar lists are standalone links: no underline. Use the site's standalone-link look (text colour, with a chevron if it leads elsewhere), per DESIGN.md "Links and buttons". Check every link in the report against that rule: running-text links get the thin grey underline; standalone links and card titles get none.
5. **Replacements table ("What replaces what").** Today the columns are so narrow that words break with hyphens.
   - **Wide screens:** use the full content width, set `hyphens: manual`, and give the function and replacement columns a sensible minimum width.
   - **Below the width where the table fits:** turn each row into a stacked block: function as the anchor, then coverage, replacement and need, each with its label.
   - **Everywhere:** no horizontal scroll and no mid-word breaks at 360 px.
6. **Spacing.** Make vertical rhythm consistent across the report, using the spacing scale only.
   - **Equal steps:** the same gaps between equal elements: cards in a group, groups, subsections, a heading and its content.
   - **Card padding:** the same on every card type.
   - **Fix every inconsistency found** in the review.

7. **Remove the home page's figures strip.** The two remaining figure tiles ("14 areas", "3 targets") look empty at full width. Delete the strip on both home pages, along with any CSS only it used. Fold its facts into one quiet line in the report preview's caption:
   - EN: "14 areas, three targets (openDesk, Nextcloud and a product-neutral checklist), in English and German, as one file that opens offline."
   - DE, natively worded, for example: "14 Bereiche, drei Ziele (openDesk, Nextcloud und eine produktneutrale Prüfliste), auf Deutsch und Englisch, in einer Datei, die sich ohne Internet öffnet."

   Read the area count from the demo report, as the checker requires for the stated count. Update `site/check_site.py` if it checked the figure tiles.

8. **Card hierarchy, Apple style (founder, 2026-11-22).** Every area card (report cards, summary lists where they show an area, and the home page's Mail card) follows one structure:
   - **Header row:**
     - left: the area name as the anchor (`--fs-headline`), with the category under it as a caption (`--fs-footnote`, `--fg-2`);
     - right, top-aligned: the status as a **badge**, a non-interactive capsule with the status symbol and word, quiet fill, no border;
     - when the evidence is incomplete, a second neutral badge "Evidence incomplete" / "Nachweise unvollständig" sits next to it.

     On phones, the badges wrap under the name, aligned left.
   - **Body:** the reason, then "Next step" as a labelled block, then "Evidence still needed" (when present), then the evidence disclosure, then the target line as the card's footer.
   - **The home page's Mail card** (shown alone) uses the same structure, with no giant status word; the badge carries the status.
   - **DESIGN.md:** amend the rule "Labels, not pills": non-interactive **badges** (capsules) may show a state such as a status or "Evidence incomplete", top right in a card. Pills that look pressable stay reserved for controls. Record this as decision D32 in DECISIONS.md, dated 2026-11-22, founder's decision.
9. **The home page tally line** under the example card ("Of 14 areas in the sample: …") has symbols, words and commas on different baselines, with stray commas. Set it as a clean inline list with no commas: each item is symbol, word and count on one baseline, separated by space from the scale. Or reuse the report's status list component in compact form. Same in German.

## Review findings (coordinator, 2026-11-22, desktop EN after RR-04)
10. **"What to do next" repeats areas and generic steps.** The same area title appears up to four times (Office files), and the step "The service owner and the IT team decide how this function is provided after a move" appears four times.
    - **Group by area:** the area name once, then its steps as a list.
    - **Generic steps:** collapse identical generic steps into one line per area that names the affected functions, for example "Decide how these are provided after a move: Teams Phone, public telephone calling".
    - **Order:** keep the groups ("Worth doing even if you stay", "Needed for a move").
11. **Vague open points.** "Find out the answer and enter it in the inputs file." repeats for SharePoint, Office files and Device management, and tells the reader nothing.
    - **Each open point names its question:** the interview question or `inputs.yaml` key in plain words, for example "How many devices are managed in Intune? (inputs: `devices.managed`)".
    - **German:** the same, in German.
    - **Where:** the wording lives in the locales or rules (findings.yaml or status.yaml), not hard-coded.
12. **The scope statement ("What openDesk covers")** runs on as one long line of dot-separated counts and underlined function names.
    - **Counts:** show them as a compact list, one coverage label per row with its count right-aligned, like the status list.
    - **Needed functions:** list them as plain text, not underlined links, or as standalone links with chevrons if they jump to the replacements table.
13. **Cost tiles.**
    - **Labels:** "Partial move · five-year total" wraps and hyphenates ("five-/year"), so the amounts in the three tiles sit at different heights. Make the label one short line ("Partial move") with "Five-year total" as a shared caption above the tiles, or a non-wrapping second line, so all three amounts align on one baseline.
    - **No mid-word hyphenation anywhere in the report:** set `hyphens: manual`. This also fixes "sign-/in" in "What to do next".
14. **Blocker summary row.** The Telephony blocker in "What blocks this move" lays out title and reason in two columns, while "What is still unknown" stacks them. Use one layout for both: the stacked one.
15. **Vertical rhythm in the summary.** The gap from the status list to "What blocks this move" is much smaller than the gap between the later subsections. Use one subsection gap from the scale throughout. Covered by item 6; listed so it gets checked.
17. **One command component (founder, 2026-11-22).** The home page's "How it works" shows the three commands as a plain code block. Use the start page's command component instead, identical in markup, styles and behaviour: the muted `$` prompt that is never copied, the copy button with its symbol and the tick after copying, the screen-reader status, and the manual-copy fallback.
    - **The script:** `site/site.js` handles one `[data-copy]` block today, looked up by `id`. Make it handle every command block on a page, keyed per block, with no duplicate ids. The start page keeps working unchanged.
    - **Language:** in German, the command ends with `--lang de`, as on the German start page.
    - **Check:** `site/check_site.py` checks both pages.
16. **Before finishing,** review the rest of the report the same way at 1280 px and 360 px: Costs, Replacements, Closer look, Recorded inventory, Appendix. Fix every misalignment, mixed type size on one baseline, stray underline, hyphenation, and inconsistent spacing or card padding. List each fix in the summary.

## Verify
- `uv run pytest -q`, `uv run ruff check .`, `uv run ruff format --check .` and `uv run python site/check_site.py` pass. RR-02's and RR-04's browser checks still pass.
- **Screenshots:** 1280 × 800 and 360 × 800, light and dark, both languages, saved to `.shots/report-redesign/rr09/`. Show the summary, the filters, a card group, the replacements table and the index (open and closed on phones).
- **Print:** a printed A4 PDF of each sample still has the council summary as page one, with no index or filters on it.
- **Screenshots and alt text:** if the report's first screen changed visibly, regenerate the site's report screenshots and keep their alt text accurate. That is RR-05's recipe; RR-08's `og.png` follows the same page one.

## Summary
Write `.planning/report-redesign/RR-09-SUMMARY.md` with:
- each item's change and files;
- the screenshots;
- deviations;
- test changes beyond the permitted list;
- a native-review table of new German strings.

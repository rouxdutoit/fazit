# Symbol and label alignment

`site/style.css` and `src/fazit/templates/report.html.j2` use identical `.symbol-label` rules. The inline flex row centres its items, uses a gap from the spacing scale and sets a unit line height. The label trims to the cap band with `text-box: trim-both cap alphabetic`. The fallback trims equal leading from Figtree’s line box. Symbols default to `1em`, chevrons use the cap height, and wrapped labels keep the symbol beside their first line. Capsules pad evenly above and below the label.

## Components moved

- Solid and secondary buttons, the small navigation action, the language toggle, the phone menu button and navigation links, and the footer mail icon.
- The copy button in both the copy and tick states, and the terminal prompts beside commands.
- Standalone site and report links, report section navigation, and the Evidence, Cost inputs, On this page, licence and appendix summaries.
- Status filter segments and counts, the category picker trigger and option ticks, status and Evidence incomplete badges, and both symbols in linked replacement status cells.
- Report status summary rows and group headings, and the home tally introduction and status counts.
- Coverage legends and cells, and the report’s cost legend swatches and unknown-cost marker.
- The never-do list, icon card headings, circled chevrons on the pilots and other linked cards, timeline dots, and the report preview window controls beside the filename.

## CSS removed

Removed fixed button line heights, badge-only trimming and symbol sizing, chevron vertical-align adjustments, absolute placement in the category trigger and status rows, per-component first-line margins, and offsets on the timeline dots and card chevrons. The native category select uses a customisable button and options where supported and the browser’s standard picker elsewhere.

| CSS source | Before | After |
| --- | ---: | ---: |
| `site/style.css` | 1,722 | 1,612 |
| Report template’s inline style | 1,172 | 1,147 |
| Total | 2,894 | 2,759 |

## Verification

- `node site/check_alignment.mjs` passed 6,544 measurements across 22 pages at 360, 768 and 1280 px in light and dark. The largest offset was **0.30 px** against a **0.75 px** limit. The check uses a baseline probe and canvas cap-height metrics, and measures the open menus, disclosures and copy feedback. A temporary 2 px shift of the category chevron caused the check to fail in all 12 report views.
- A separate Firefox run exercised the text-box fallback and the native category select. Its 6,328 measurements had a maximum offset of 0.51 px.
- `uv run pytest -q` passed 959 tests. `uv run ruff check .` and `uv run ruff format --check .` passed. `uv run python site/check_site.py` passed for all 22 pages and 861 references.
- Regenerated the English and German demo reports. Both opened offline with JavaScript disabled and their category filters worked. Updated the home download labels to the resulting 424 KB and 436 KB.
- A4 first-page verification passed for the town, nonprofit and all-Unknown reports in both languages, with page backgrounds on and off.
- Captured five before and after pairs at device scale factor 3 in the ignored `.shots/align/` directory. The pairs show the category trigger, badge pair, secondary button, replacement status cell and standalone link.

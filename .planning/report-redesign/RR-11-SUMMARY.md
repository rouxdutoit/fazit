# RR-11 summary

Applied the founder's follow-up decisions dated 2026-11-23 on top of RR-10. The report uses the sticky top bar and the website's section grid. Both published demos come from fresh offline runs.

## Changes

| Item | Change | Files |
| --- | --- | --- |
| 1. Cost tiles and scrollbars | Removed the scroll box around tile figures. Amounts can wrap at the currency space, and very long amounts can wrap within a number. Tables reflow inside their columns. The site and report pages scroll vertically without showing a viewport scrollbar. | `src/fazit/templates/report.html.j2`, `site/style.css` |
| 2. Replacement status chevrons | Used the shared standalone link icon immediately after the status text inside its badge. The icon scales with the text and is centred on the capitals. The status symbol remains at the start of the badge. | `src/fazit/templates/report.html.j2`, `site/style.css` |
| 3. Sticky section links | Removed the left index, its grid column and its styles. Restored RR-04's wordmark and seven section links in the sticky bar. The bar marks the section containing the current fragment, the skip link focuses the report, and print hides the navigation. Recorded the founder's reversal of RR-09 item 1. | `src/fazit/templates/report.html.j2`, `UI-SPEC.md`, `RR-09-SUMMARY.md`, `DECISIONS.md` (D37) |
| 3. Published reports and previews | Regenerated both demos, the eight lossless homepage crops and the social image. The crops show the sticky bar, all four status definitions, the full Telephony blocker and its link. Updated each picture's declared dimensions and checked the existing image alternatives against the crops. | `site/demo/{en,de}/index.html`, `site/images/readiness-*.webp`, `site/og.png`, `site/{index.html,de/index.html}`, `.shots/report-redesign/shots.mjs` |
| 4. Website section grid | Restored the 4:8 columns from 880 px and the divider across the content column, with the same heading style as the site. On phones the heading sits above its content. Direct links such as `#readiness-title` align the desktop heading with the filters. The layout retains the RR-09 and RR-10 status list, cards and badges, segmented status control and category picker, replacements table and cost tiles. | `src/fazit/templates/report.html.j2`, `UI-SPEC.md` |

## Implementation choices and deviations

- The original RR-04 row overflowed at 360 px in both languages. RR-11 uses the compact disclosure below 40 rem and shows the inline links from 40 rem. Both use the same template and destinations. The phone menu stays open after a section jump and closes with its native toggle.
- The replacements columns size to their content within the narrower desktop grid. Verified shared and per-row dates across the openDesk, Nextcloud and product-neutral reports. The seven-digit tile still fits on one line at the three requested widths in both languages.
- The refreshed hero crops follow the RR-05 lossless WebP recipe with the sticky bar in view. Desktop frames are 2016 × 1218, English phone frames are 800 × 1424, and German phone frames are 800 × 1530. The social image uses the actual English report excerpt at 1200 × 630. All nine files are under 150 KB.

## Test changes

| File | Change |
| --- | --- |
| `tests/test_report.py` | Checked the seven link labels and destinations in both top-bar arrangements, and print hiding for the bar. Each replacement status link must place the shared chevron immediately after its localised label. Existing assertions for link resolution, status, evidence and coverage still run. |
| `tests/test_costs.py` | Kept the full formatted seven-digit amount assertion and removed the CSS requirement to force it onto one line. Verified the rendered figure in Chromium. |
| `.shots/report-redesign/check.mjs` | Updated the navigation checks for the sticky bar and disclosure. Verified keyboard focus, fragment marking, heading alignment, skip navigation and print hiding. Compared the replacement chevron with the summary's All blockers link and compared each section grid and divider with the website. Added 768 px to the layout and filter checks. |
| `tests/browser/check-scrollbars.mjs` | Added a classic-scrollbar check for the viewport and its elements at 360, 768 and 1280 px. Checks the website and tests offline reports with their disclosures closed and open. Against the RR-10 demo it detects both the viewport scrollbar and the cost-tile scrollbar. |

## Verification

| Check | Result |
| --- | --- |
| `uv run pytest -q` | 955 passed. |
| `uv run ruff check .` and `uv run ruff format --check .` | Passed. |
| `uv run python site/check_site.py` | Passed. Checked 22 pages and 861 references. |
| `uv run fazit demo --lang de` and `uv run fazit demo --lang en` | Passed with fresh output directories. Both published HTML files match the corresponding demo output byte for byte. |
| RR-02 filters and RR-04 browser checks | Passed for both samples, languages and themes at 360, 768 and 1280 px in offline Chromium with scripting disabled. The site grid comparisons also passed at 375 px. |
| Print | Both samples and the all-Unknown report fit the full council summary on A4 page one in both languages with and without backgrounds. The navigation and filters are hidden. Filtered and unfiltered print text and pagination match. |
| No visible scrollbar or horizontal scrolling | Passed in Chromium with classic scrollbars on all 22 site pages and 14 offline report variants at all three widths in both themes. Large valid cost values fit in the report. The three profiles also passed checks for replacement-cell widths and unbroken dates at 12 widths from 320 to 1280 px. |
| Screenshots | Verified 40 PNGs at 1280 × 800 and 360 × 800, in English and German, light and dark. The set shows the summary, areas, open category picker, cost tiles and replacements table. |

The [viewport screenshots](../../.shots/report-redesign/rr11/) and [browser comparison and print files](../../.shots/report-redesign/rr11/checks/) show the verified layouts.

## German copy

The phone disclosure reuses `nav.on_this_page` (“Auf dieser Seite”). The existing homepage download label now reads “HTML herunterladen, 424 KB”. No new German locale strings were needed.

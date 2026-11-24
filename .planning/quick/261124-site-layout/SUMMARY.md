# Shared website and report layout

The English and German inner pages use the home page’s opening, section and footer gaps. Space separates the sections, and headings and content still align at the top when they sit in columns. The legal pages use the same rhythm between their sections. [Decision D50](../../../DECISIONS.md#2026-11-24--shared-website-and-report-layout) · [Design rules](../../../DESIGN.md)

Every report uses the website’s sticky bar, navigation geometry and content column on screen. The bar switches from the 52 px phone layout to the 60 px desktop layout at 820 px. The report keeps its section links, “On this page” disclosure and 40, 56 or 64 px of space on each side of a section rule.

The organisation name follows the title on screen so it can wrap without shifting the opening gap. Its original position above the title is preserved in print. Both sample reports were regenerated from the template with their existing copy.

## Measurements

The measurements cover the home page (`/`), Pilots (`/pilots/`) and the English report (`/demo/en/`) in Chromium 151.0.7922.34. Each row applies to all three pages. Boxes give `x, y, width, height` in CSS pixels. Text edges are the left and right limits of the heading’s column. The opening gap runs from the bar to the home eyebrow or the page title.

| Viewport | Bar height | Wordmark box | Menu button or desktop links box | Text edges | Opening gap |
| ---: | ---: | --- | --- | --- | ---: |
| 360 | 52 | 16, 8, 284, 36 | 300, 4, 44, 44 | 16–344 | 72 |
| 390 | 52 | 16, 8, 314, 36 | 330, 4, 44, 44 | 16–374 | 72 |
| 768 | 52 | 42.23, 8, 639.53, 36 | 681.77, 4, 44, 44 | 42.23–725.77 | 104 |
| 1024 | 60 | 56.31, 12, 35, 36 | 115.31, 8, 852.38, 44 | 56.31–967.69 | 104 |
| 1280 | 60 | 144, 12, 35, 36 | 203, 8, 933, 44 | 144–1136 | 136 |
| 1440 | 60 | 224, 12, 35, 36 | 283, 8, 933, 44 | 224–1216 | 136 |

WebKit 26.5 gave the same matches across all three pages. Its desktop wordmark measured 34.44 px wide, so the links box started 0.56 px further left. The right edge was the same.

| Viewport | Home and Pilots section gap | Home and Pilots gap above the footer |
| ---: | ---: | ---: |
| 390 | 120 | 96 |
| 768 | 120 | 96 |
| 1024 | 143.36 | 122.88 |
| 1280 | 179.19 | 136 |
| 1440 | 200 | 136 |

## Verification

- `uv run ruff check .` passed. `uv run ruff format --check .` passed for all 52 Python files.
- `uv run pytest -q` passed all 1,115 tests.
- `uv run python site/check_site.py --write-demos` regenerated both sample reports. `uv run python site/check_site.py` passed for 24 pages and 1,022 references. `uv run python site/generate_llms.py` produced the same text index.
- The unpacked source distribution step in CI ran with Python 3.12.16. It passed 1,097 tests with 18 expected skips for checkout-only files.
- Both CLI demos opened at six widths with zero network requests in Chromium and WebKit. A generated report with a 120-character organisation name wrapped the name at 360 px and kept the 72 px opening gap in both engines.

| Browser check | Chromium 151.0.7922.34 | WebKit 26.5 |
| --- | --- | --- |
| `node site/check_alignment.mjs` | 67,112 measurements, 0 failures | 67,112 measurements, 0 failures |
| `node site/check_spacing.mjs` | 432 views and 26,700 spacing measurements, 0 failures | 432 views and 26,700 spacing measurements, 0 failures |
| `node site/check_home_layout.mjs` | 48 views and 132 keyboard stops, 0 failures | 48 views and 132 keyboard stops, 0 failures |
| `node tests/browser/check-scrollbars.mjs` | 24 pages and two offline reports per width and theme, 0 failures | 24 pages and two offline reports per width and theme, 0 failures |

The spacing check compares each page with the home page at eight widths, including both sides of the 820 px menu breakpoint, and in 390 px iPhone emulation. It checks the closed bar, the position and width of the open phone menu, the text column and the documented rhythm. The home layout check now also runs when invoked directly.

## HTML files touched

- `src/fazit/templates/report.html.j2`
- `site/demo/en/index.html`
- `site/demo/de/index.html`

## Screenshots

English report captures in Chromium. The 390 px captures use iPhone emulation. The A4 preview shows the complete council summary on the first page. Raster comparison against the original found identical output on all 33 English pages and 34 German pages.

| View | Light | Dark |
| --- | --- | --- |
| 1440 px | [Screenshot](../../../.shots/site-layout/report-en-1440-light.png) | [Screenshot](../../../.shots/site-layout/report-en-1440-dark.png) |
| 390 px | [Screenshot](../../../.shots/site-layout/report-en-390-light.png) | [Screenshot](../../../.shots/site-layout/report-en-390-dark.png) |
| 390 px, menu open | [Screenshot](../../../.shots/site-layout/report-en-390-light-menu.png) | [Screenshot](../../../.shots/site-layout/report-en-390-dark-menu.png) |
| A4 print preview | [First page](../../../.shots/site-layout/report-en-print-page-1.png) | |

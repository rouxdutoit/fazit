# Website vertical rhythm

The website uses the spacing of a product page. The report keeps its document layout for reading on screen and in print. [Design rules](../../../DESIGN.md#vertical-rhythm) · [Decision D48](../../../DECISIONS.md#2026-11-23--website-section-spacing)

| Viewport | Website bar to first content | Website divider and footer gap | Report bar to heading | Report divider and footer gap |
| --- | ---: | ---: | ---: | ---: |
| Below 768 px | 72 px | 56 px | 64 px | 40 px |
| 768–1079 px | 104 px | 72 px | 64 px | 56 px |
| 1080 px and up | 136 px | 96 px | 64 px | 64 px |

The website measurement starts at the bottom of the bar and ends at the home or 404 eyebrow, or at the introduction heading on other pages. The section gap applies on each side of a divider, including the first divider after the opening block, and above the footer. The checker compares website pages with the home page and compares both report demos with each other at each width and theme.

The report template and regenerated demos match their previous bytes after normalising the two renamed CSS tokens.

## Verification

- `uv run ruff check .` and `uv run ruff format --check .` passed. `uv run pytest -q` passed all 1,089 tests.
- `uv run python site/check_site.py` passed for 24 pages and 1,027 references. Both CLI demos generated and opened offline in Chromium and WebKit.
- `node site/check_alignment.mjs` passed in Chromium and WebKit, with 67,620 measurements and a maximum offset of 0.50 px in each engine.
- `node site/check_spacing.mjs` passed in both engines at 360, 390, 768 and 1280 px, with 12,680 measurements per engine. Additional measurements passed at 767, 768, 1079 and 1080 px. A temporary copy confirmed that the checker catches a displaced home eyebrow and a changed gap in one report.
- At 390 and 1280 px in both engines, the website's measured section interiors and print layout matched the previous stylesheet across all 22 website pages.
- `node tests/browser/check-scrollbars.mjs` passed in both engines, including both offline reports.

## Screenshots

Full-page Chromium captures in light mode. The 390 px captures use iPhone emulation. Git ignores `.shots/breathing/`.

| Home page | Width | Before | After |
| --- | ---: | --- | --- |
| English | 1280 px | [Before](../../../.shots/breathing/before-en-1280.png) | [After](../../../.shots/breathing/after-en-1280.png) |
| English | 390 px | [Before](../../../.shots/breathing/before-en-390.png) | [After](../../../.shots/breathing/after-en-390.png) |
| German | 1280 px | [Before](../../../.shots/breathing/before-de-1280.png) | [After](../../../.shots/breathing/after-de-1280.png) |
| German | 390 px | [Before](../../../.shots/breathing/before-de-390.png) | [After](../../../.shots/breathing/after-de-390.png) |

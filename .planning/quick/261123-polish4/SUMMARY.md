# Site and report polish

## Changes

| Item | Change | Files |
| --- | --- | --- |
| Browser checks | Alignment, spacing and scrollbar checks run in Chromium and WebKit by default and report each engine separately. `PLAYWRIGHT_ENGINE=chromium` or `PLAYWRIGHT_ENGINE=webkit` runs one. The checks use reduced motion before measuring the bar. | `AGENTS.md`, `site/check_browser.mjs`, `site/check_alignment.mjs`, `site/check_spacing.mjs`, `tests/browser/check-scrollbars.mjs` |
| Home preview | The hero button opens the sample. The link under the preview downloads the HTML and uses the standard standalone-link colour and hover. It is centred 16 px below the preview. The site checker requires exactly one link in the caption and verifies its download destination. | `site/index.html`, `site/de/index.html`, `site/style.css`, `site/check_site.py` |
| Section spacing | One responsive token covers both sides of the divider, including the gap from the opening block, and the gap above the footer. Privacy and Legal notice use it for their section rules too. When the Privacy summary stacks, the first legal section starts after a divider. The 404 pages use the same gap above their footers. The spacing check compares each page to the home page at the same width and theme. | `site/style.css`, `src/fazit/templates/report.html.j2`, `site/check_spacing.mjs`, `DESIGN.md`, `DECISIONS.md` |
| Command block | The shared Home and Start component uses `--card-padding` for the top, bottom and left. The command component sets the token to 20 px on phones and uses 24 px at wider widths. Lines use a 1.7 line height with zero extra gap. The 44 px copy target is centred vertically and its symbol takes the same right inset as the text takes on the left. The checks measure the padding and alignment. | `site/style.css`, `site/check_spacing.mjs`, `site/check_alignment.mjs`, `DESIGN.md` |
| Report wordmark | The demo render flag gives the wordmark an ordinary link to `https://fazit.dev/` in English or `https://fazit.dev/de/` in German. The organisation report points to `#main`. The published demos were copied from fresh CLI output. | `src/fazit/report.py`, `src/fazit/templates/report.html.j2`, `site/demo/en/index.html`, `site/demo/de/index.html` |
| Roadmap timeline | Opaque dots sit above the rail in both themes. The future steps use the page background for the centres of their dots. The alignment check measures the rail and dot centres, verifies the fill and stacking, and keeps the cap-band check for the title. | `site/style.css`, `site/check_alignment.mjs`, `DESIGN.md` |

## Section gaps on screen

| Viewport | Above the divider | Below the divider | End of section to start of next section | Last section to footer |
| --- | ---: | ---: | ---: | ---: |
| Below 768 px | 40 px | 40 px | 81 px | 40 px |
| 768–1079 px | 56 px | 56 px | 113 px | 56 px |
| 1080 px and up | 64 px | 64 px | 129 px | 64 px |

Both engines verified the transitions at 767, 768, 1079 and 1080 px. The report header, sections and footer have the same rendered print geometry as the prior demos in both languages.

## WebKit findings

- The first WebKit alignment run reported 432 chevron gap failures. Its Canvas measurements included the advance in the right edge of most glyphs. Scanning the painted ink gave the true side bearings in both engines. The chevron targets and tolerances were kept.
- The English home page at 360 px could time out while Playwright waited for an animation frame after measuring layout. The check now scrolls the copy button into view, verifies the pointer hits its centre and clicks it in both engines. Copy feedback is still required.
- Headless WebKit uses overlay scrollbars and its offline flag rejects local file navigation. The scrollbar check applies a 15 px classic gutter in WebKit and verifies that a probe reserves space for it. The report check opens the local file with JavaScript disabled and blocks and records HTTP and HTTPS requests. Neither demo attempted a network request.
- Under reduced motion, the closed phone menu in the report could give its undisplayed navigation a 44 px wide scrolling box in both engines. The report CSS now removes that box while the menu is closed. The expanded menu still fits at the checked widths.

## Tests and results

| Browser check | Chromium 151.0.7922.34 | WebKit 26.5 |
| --- | --- | --- |
| Alignment | 16,864 measurements across 144 views. Maximum offset 0.38 px. | 16,864 measurements across 144 views. Maximum offset 0.40 px. |
| Spacing | 9,524 measurements across 144 initial, 12 expanded and 12 empty-filter views. | 9,524 measurements across 144 initial, 12 expanded and 12 empty-filter views. |
| Scrollbars | 144 site views and 24 offline report views, including open and closed disclosures. | 144 site views and 24 offline report views, including open and closed disclosures. |

All browser checks passed at 360, 768 and 1280 px in light and dark. The alignment limit is 0.75 px, with the existing tighter limits for individual geometry checks. The spacing tolerance is 0.02 px. The download link's normal and hover colours were checked in each language and theme in both engines. Screenshots verified that the rail shows between steps and the centre of each future dot matches the page background.

- `uv run ruff check .`, `uv run ruff format --check .` and `uv run pytest -q` passed. The checkout suite passed 1,008 tests with zero failures.
- Both `fazit demo` runs passed. `uv run python site/check_site.py` passed for 24 pages and 969 references, including byte-for-byte checks of the published demos.
- The CI unpacked source-distribution step ran with local CPython 3.12.16 and uv 0.13.9. It passed 1,002 tests with six expected skips and zero failures. The archive and its unpacked directory omit `site/`.
- The two new bilingual cases in `tests/test_report.py` check the wordmark destinations and offline markup with an imported scan and organisation inputs. `tests/helpers.py` permits the precise demo anchor in that check. The CLI rebuild and clock tests in `tests/test_cli.py` compare report output after accounting for the one different destination. The added Python cases use fixtures available in the source distribution.
- In a temporary copy, the spacing check rejected a different section gap on Security and an 8 px command inset. The alignment check rejected timeline dots painted behind the rail.

## German copy

No new German strings. The home preview drops “Beispielbericht öffnen” and keeps “HTML herunterladen, 433 KB”. The English download remains 420 KB.

# Home page redesign

The English and German home pages open with a centred hero and the sample report in a Linux window. Four status tiles and two detail cards use a shared label row, value size and caption style. Five sections pair the copy with panels for the blocker, evidence, cost, privacy and commands. The panels alternate sides from 880 px and follow the copy on narrower screens. The closing repeats the two hero buttons. [Design rules](../../../DESIGN.md) · [Decision D49](../../../DECISIONS.md#2026-11-23--home-page-redesign)

The website gutter widens above 600 px. Standalone links use the text colour, body size and weight 500. Text buttons use labels alone, and the copy button keeps its symbol. Both safeguards lists use 16 px of padding above and below the text.

| Viewport | Gutter | Hero status to window | Window to first section and between sections | Last section to closing | Closing to footer |
| --- | ---: | ---: | ---: | ---: | ---: |
| 360 px | 16 px | 48 px | 120 px | 136 px | 96 px |
| 390 px | 16 px | 48 px | 120 px | 136 px | 96 px |
| 768 px | 42.24 px | 53.75 px | 120 px | 136 px | 96 px |
| 960 px | 52.80 px | 67.19 px | 134.39 px | 153.59 px | 115.19 px |
| 1130 px | 62.15 px | 72 px | 158.19 px | 180.80 px | 135.59 px |
| 1280 px | 64 px | 72 px | 179.19 px | 204.80 px | 136 px |

The spacing checker uses the four home tokens and the Start page as the reference for the shared website opening and inner-page section gaps. The English sample report is the reference for report gaps. The tolerance is 0.02 px.

## Verification

- `uv run ruff check .` and `uv run ruff format --check .` passed. `uv run pytest -q` passed all 1,090 tests.
- `uv run python site/check_site.py` passed for 24 pages and 1,022 references. Both demos were regenerated with `--write-demos`. `uv run python site/generate_llms.py` rebuilt `site/llms-full.txt`.
- The English and German CLI demos generated under `TMPDIR` and opened at 360 px with zero network requests in Chromium and WebKit.
- Both security pages measured 44 px for one-line safeguards rows, with 16 px of top and bottom padding. Hero values and captions begin 66 px and 110 px from the top of each card. Longer captions wrap at the subhead size.

| Browser check | Chromium 151.0.7922.34 | WebKit 26.5 |
| --- | --- | --- |
| `node site/check_alignment.mjs` | Passed, 67,112 measurements, 0.50 px maximum offset | Passed, 67,112 measurements, 0.50 px maximum offset |
| `node site/check_spacing.mjs` | Passed, 12,436 measurements | Passed, 12,436 measurements |
| `node tests/browser/check-scrollbars.mjs` | Passed, 24 pages and two offline reports per tested width and theme | Passed, 24 pages and two offline reports per tested width and theme |

The alignment check also verified hover colour and underline behaviour. The scrollbar check covered 360, 768 and 1280 px in light and dark. The six-width overflow check also covered all 22 website pages in both themes, for 264 page views per engine.

Each engine measured 48 home views across the two languages, six widths, two themes and default and increased contrast. The minimum measured text contrast was 4.66:1. The status colours followed `prefers-contrast: more` in both themes.

| Viewport | Horizontal overflow | Card height difference | Hero value offset difference | Hero caption offset difference | Privacy columns | Max. title lines |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 360 px | 0 px | 0 px | 0 px | 0 px | 1 | 1 |
| 390 px | 0 px | 0 px | 0 px | 0 px | 1 | 1 |
| 768 px | 0 px | 0 px | 0 px | 0 px | 3 | 1 |
| 960 px | 0 px | 0 px | 0 px | 0 px | 1 | 1 |
| 1130 px | 0 px | 0 px | 0 px | 0 px | 3 | 1 |
| 1280 px | 0 px | 0 px | 0 px | 0 px | 3 | 1 |

Each engine verified 132 keyboard stops across both home pages at 390 and 1280 px. Tab followed the reading order, the skip link moved focus to the main content, and Escape returned focus from the phone menu to its toggle.

## Screenshots

Full-page Chromium captures in light mode. The 390 px captures use iPhone emulation at device scale 3. Git ignores `.shots/home-redesign/`.

| Home page | Width | Before | After |
| --- | ---: | --- | --- |
| English | 1280 px | [Before](../../../.shots/home-redesign/before-en-1280.png) | [After](../../../.shots/home-redesign/after-en-1280.png) |
| English | 390 px | [Before](../../../.shots/home-redesign/before-en-390.png) | [After](../../../.shots/home-redesign/after-en-390.png) |
| German | 1280 px | [Before](../../../.shots/home-redesign/before-de-1280.png) | [After](../../../.shots/home-redesign/after-de-1280.png) |
| German | 390 px | [Before](../../../.shots/home-redesign/before-de-390.png) | [After](../../../.shots/home-redesign/after-de-390.png) |

## Files changed

- `DECISIONS.md`
- `DESIGN.md`
- `.planning/quick/261123-home-redesign/SUMMARY.md`
- `site/index.html`, `site/de/index.html`
- `site/404.html`, `site/de/404.html`
- `site/about/index.html`, `site/de/about/index.html`
- `site/coverage/index.html`, `site/de/coverage/index.html`
- `site/impressum/index.html`, `site/de/impressum/index.html`
- `site/integrators/index.html`, `site/de/integrators/index.html`
- `site/pilots/index.html`, `site/de/pilots/index.html`
- `site/privacy/index.html`, `site/de/privacy/index.html`
- `site/roadmap/index.html`, `site/de/roadmap/index.html`
- `site/security/index.html`, `site/de/security/index.html`
- `site/start/index.html`, `site/de/start/index.html`
- `site/style.css`
- `site/icons/home.svg` (removed)
- `site/check_site.py`
- `site/check_alignment.mjs`
- `site/check_home_layout.mjs`
- `site/check_link_underlines.mjs`
- `site/check_spacing.mjs`
- `src/fazit/templates/report.html.j2`
- `site/demo/en/index.html`, `site/demo/de/index.html`
- `site/llms-full.txt`
- `.shots/home-redesign/after-en-1280.png`, `.shots/home-redesign/after-en-390.png`
- `.shots/home-redesign/after-de-1280.png`, `.shots/home-redesign/after-de-390.png`

# Button heights and chevrons

The shared label primitive centres the contents of 44 px standard buttons and 28 px desktop bar pills. Standard pills use 16 px horizontal padding and the compact pill uses 12 px. The compact pill extends its clickable area by 8 px above and below the painted pill. The copy button is 44 px square. [Design rules](../../../DESIGN.md#links-and-buttons)

## Button heights by page

Values are rendered CSS pixels, before → after. Page buttons have the listed height at 360, 768 and 1280 px. The navigation measurements use the open phone menu at 360 and 768 px and the visible desktop bar at 1280 px. The report's category picker button was 44 px before it joined the shared height check.

| Pages | Page buttons at all three widths | Menu action at 360 and 768 px | Bar pill at 1280 px |
| --- | --- | ---: | ---: |
| `/`, `/de/` | Get started and View sample report 29 → 44. Copy 44 → 44. | 44 → 44 | 18 → 28 |
| `/404.html`, `/de/404.html` | Back to the home page 29 → 44. | 44 → 44 | 18 → 28 |
| `/about/`, `/de/about/` | — | 44 → 44 | 18 → 28 |
| `/coverage/`, `/de/coverage/` | — | 44 → 44 | 18 → 28 |
| `/impressum/`, `/de/impressum/` | — | 44 → 44 | 18 → 28 |
| `/integrators/`, `/de/integrators/` | — | 44 → 44 | 18 → 28 |
| `/pilots/`, `/de/pilots/` | Express interest 29 → 44. | 44 → 44 | 18 → 28 |
| `/privacy/`, `/de/privacy/` | — | 44 → 44 | 18 → 28 |
| `/roadmap/`, `/de/roadmap/` | — | 44 → 44 | 18 → 28 |
| `/security/`, `/de/security/` | Report a vulnerability 29 → 44. | 44 → 44 | 18 → 28 |
| `/start/`, `/de/start/` | Copy 44 → 44. | 44 → 44 | 18 → 28 |
| `/demo/en/`, `/demo/de/` | Category picker 44 → 44. | — | — |

## Chevron geometry

The founder's reference is Apple's “Learn more about Continuity” link at 21 px, with text set in SF Pro Display at weight 400. The captured glyph uses SF Pro Icons at the same size and weight. [Apple MacBook Air](https://www.apple.com/macbook-air/)

| Measurement | Apple reference | Fazit |
| --- | --- | --- |
| Ink height | 0.50 em, about 0.71 of cap height | 0.50 em, measured against Figtree's 0.703 em cap height |
| Ink width | 0.29 em | 0.29 em |
| Vertical placement | Baseline to x-height | Baseline to x-height on the final line of trailing labels |
| Gap from the text ink | 0.40 em, including the side bearing | 0.40 em target. The rendered path and glyph metrics gave 0.409 em for All blockers, 0.397 em for Get Git and 0.411 em for Alle Hindernisse. |
| Stroke | Same thickness as the text stem | 0.084 em at weight 400 and 0.117 em at weight 600. Figtree at weight 500 measured 0.100 em. |
| Colour | Link colour | Current text colour, including hover and status colours |

Fazit uses a two-segment path with round caps and joins. The path scales inside the stroke so the ink dimensions hold at each weight. The circle on a linked card sits beside its title to keep the chevron within the specified ink gap. The report's disclosures turn the same chevron around its centre on the first line. Leading action and status symbols still align with the cap band.

The comparison images place each before and after crop beside the live Apple reference at 4× device scale. [All blockers](../../../.shots/chevrons/comparison-all-blockers.png) · [Get Git](../../../.shots/chevrons/comparison-card-title.png) · [Alle Hindernisse](../../../.shots/chevrons/comparison-german-link.png)

## Test changes

- `site/check_alignment.mjs` checks each rendered `.btn` against its exact height token and hit-tests the top and bottom of the compact pill's 44 px target. It checks the chevron baseline within 0.75 px, ink height and gap within 0.03 em, and stroke width within 0.5 px of the left stem of a rendered Figtree H. It also checks width, orientation and colour. In a temporary copy, the checker rejected a 29 px pill, a missing hit extension, and chevrons with a shifted baseline, thin stroke and shortened gap.
- The report, costs and rules tests account for the hidden chevron inside the text label and still verify link destinations and text. The SVG path assertions use the package's own icon. The status palette test that reads the site stylesheet is already listed in `checkout_files` in `tests/conftest.py`.

## Verification

| Command | Result |
| --- | --- |
| `uv run ruff check .` | Passed. |
| `uv run ruff format --check .` | 50 files already formatted. |
| `uv run pytest -q` | 1,006 passed, 0 failed. |
| `uv run fazit demo --lang de` and `uv run fazit demo --lang en` | Passed. Regenerated both published reports and updated the home download labels to 433 KB in German and 420 KB in English. |
| `uv run python site/check_site.py` | Passed for 24 pages and 971 references. The published reports match fresh CLI output byte for byte. |
| `node site/check_alignment.mjs` | 16,552 measurements passed across 144 views in light and dark. Largest offset 0.63 px. |
| `node site/check_spacing.mjs` | 9,316 measurements passed across 144 initial, 12 expanded and 12 empty filter views. |
| CI's Test unpacked source distribution step | 1,000 passed, 6 skipped, 0 failed. |

Both reports opened from disk at 360 px with networking and JavaScript disabled. Chromium loaded Figtree and the status filters and disclosures worked. The scrollbar check passed on all 24 routes and both offline reports at the three widths in light and dark. The A4 council summary fit on page one for the town, nonprofit and all-Unknown reports in both languages, with background printing on and off.

The unpacked-source run used the workflow's shell body with the local CPython 3.12.16 path and uv 0.13.9. The archive and its unpacked root omit `site/`, and the package contains the chevron SVG. The six skips cover one test for `.git`, two for the workflow, one for `site/icons` and two for `site/style.css`. [CI workflow](../../../.github/workflows/ci.yml)

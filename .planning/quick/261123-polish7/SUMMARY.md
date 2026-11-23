# Hero copy and button spacing

The home pages use the founder’s wording from 23 November 2026. The previous wording appeared only in the two visible subheads. [English home page](../../../site/index.html) · [German home page](../../../site/de/index.html)

- **English.** What you rely on, what needs work and what it would cost, all in one report written on your computer.
- **German.** Worauf Sie angewiesen sind, was zu klären ist und was es kosten würde, alles in einem Bericht, der auf Ihrem Rechner entsteht.

`--btn-symbol-gap` gives a 0.4 em gap to button and filter labels, category options and the language link. The wider spacing in the report’s status track brings the full labels in at 543 px in English and 609 px in German. Both engines kept the track on one row at those widths with a two-digit status count. [Design rules](../../../DESIGN.md#links-and-buttons)

The category trigger uses the standard 15 px button text and a 44 px hit area. One down chevron serves both picker modes. The native select covers the full pill and the current option determines its displayed label and width. The reports stay interactive with JavaScript disabled. [Report template](../../../src/fazit/templates/report.html.j2)

| Measurement | Before | After |
| --- | ---: | ---: |
| Hero button symbol gap | 4 px | 6 px |
| Desktop bar button symbol gap | 4 px | 4.80 px |
| Category label to chevron, styled picker | 5.09–5.10 px | 6.02–6.11 px |
| Category start and end padding, styled picker | 16 px and 11.99–12.02 px | 16 px and 15.91–15.98 px |
| Status badge symbol gap | 4 px | 4 px |

| Capture | Default category width | Longer category width |
| --- | ---: | ---: |
| Chromium desktop, English | 137.50 px | 212.50 px |
| Chromium desktop, German | 147.50 px | 227.50 px |
| WebKit iPhone, English | 137.67 px | 212.55 px |
| WebKit iPhone, German | 148.36 px | 228.06 px |

## Zoomed screenshots

The PNGs show the baseline at `7d09b9a` and the updated `polish` checkout at three device pixels per CSS pixel. Chromium uses a 1280 × 900 desktop viewport. WebKit uses a 390 × 844 iPhone viewport with mobile and touch emulation. All crops are in light mode.

| Browser and language | Hero button | Category trigger | Open menu | Longer category selected |
| --- | --- | --- | --- | --- |
| Chromium desktop, English | [Before](../../../.shots/polish7/before-chromium-desktop-en-button.png) · [After](../../../.shots/polish7/after-chromium-desktop-en-button.png) | [Before](../../../.shots/polish7/before-chromium-desktop-en-category.png) · [After](../../../.shots/polish7/after-chromium-desktop-en-category.png) | [Before](../../../.shots/polish7/before-chromium-desktop-en-menu.png) · [After](../../../.shots/polish7/after-chromium-desktop-en-menu.png) | [Before](../../../.shots/polish7/before-chromium-desktop-en-category-long.png) · [After](../../../.shots/polish7/after-chromium-desktop-en-category-long.png) |
| Chromium desktop, German | [Before](../../../.shots/polish7/before-chromium-desktop-de-button.png) · [After](../../../.shots/polish7/after-chromium-desktop-de-button.png) | [Before](../../../.shots/polish7/before-chromium-desktop-de-category.png) · [After](../../../.shots/polish7/after-chromium-desktop-de-category.png) | [Before](../../../.shots/polish7/before-chromium-desktop-de-menu.png) · [After](../../../.shots/polish7/after-chromium-desktop-de-menu.png) | [Before](../../../.shots/polish7/before-chromium-desktop-de-category-long.png) · [After](../../../.shots/polish7/after-chromium-desktop-de-category-long.png) |
| WebKit iPhone, English | [Before](../../../.shots/polish7/before-webkit-iphone-en-button.png) · [After](../../../.shots/polish7/after-webkit-iphone-en-button.png) | [Before](../../../.shots/polish7/before-webkit-iphone-en-category.png) · [After](../../../.shots/polish7/after-webkit-iphone-en-category.png) | [Before](../../../.shots/polish7/before-webkit-iphone-en-menu.png) · [After](../../../.shots/polish7/after-webkit-iphone-en-menu.png) | [Before](../../../.shots/polish7/before-webkit-iphone-en-category-long.png) · [After](../../../.shots/polish7/after-webkit-iphone-en-category-long.png) |
| WebKit iPhone, German | [Before](../../../.shots/polish7/before-webkit-iphone-de-button.png) · [After](../../../.shots/polish7/after-webkit-iphone-de-button.png) | [Before](../../../.shots/polish7/before-webkit-iphone-de-category.png) · [After](../../../.shots/polish7/after-webkit-iphone-de-category.png) | [Before](../../../.shots/polish7/before-webkit-iphone-de-menu.png) · [After](../../../.shots/polish7/after-webkit-iphone-de-menu.png) | [Before](../../../.shots/polish7/before-webkit-iphone-de-category-long.png) · [After](../../../.shots/polish7/after-webkit-iphone-de-category-long.png) |

Disabling the `base-select` styles in iPhone emulation exercises the native select. The original trigger shows the native arrow near the far edge and clips the end of both labels.

| Native trigger | Before | After |
| --- | --- | --- |
| English | ![Original native category trigger in English](../../../.shots/polish7/before-webkit-iphone-en-native-category.png) | ![Updated native category trigger in English](../../../.shots/polish7/after-webkit-iphone-en-native-category.png) |
| German | ![Original native category trigger in German](../../../.shots/polish7/before-webkit-iphone-de-native-category.png) | ![Updated native category trigger in German](../../../.shots/polish7/after-webkit-iphone-de-native-category.png) |
| Longer English label | [Before](../../../.shots/polish7/before-webkit-iphone-en-native-category-long.png) | [After](../../../.shots/polish7/after-webkit-iphone-en-native-category-long.png) |
| Longer German label | [Before](../../../.shots/polish7/before-webkit-iphone-de-native-category-long.png) | [After](../../../.shots/polish7/after-webkit-iphone-de-native-category-long.png) |

## Verification

Verification used the `polish` working tree at `7d09b9a`. The local `origin/main` ref advanced to `b0b213d` during the run.

The alignment check measures the symbol gap to within 0.5 px and the category trigger's equal padding. It selects each category in both picker modes with the report's JavaScript disabled. A temporary stylesheet restored the 4 px button gap, set a minimum trigger width and moved the chevron inward. Both engines flagged the gap and padding changes.

Fresh CLI output matches the two published demos byte for byte. The home pages show 427 KB for the English HTML and 440 KB for the German HTML.

The unpacked-source run used CPython 3.12.16 and uv 0.13.9 with cached dependencies. The first run hit three existing one-second CLI timeouts while the browser checks were running. The passing run built a fresh archive and ran the workflow step separately. The six skips cover `.git`, the CI workflow, `site/icons` and `site/style.css`. [CI workflow](../../../.github/workflows/ci.yml)

| Command | Result |
| --- | --- |
| `uv run ruff check .` and `uv run ruff format --check .` | Passed. 50 files already formatted. |
| `uv run pytest -q` | 1,040 passed, zero failures. |
| `uv run fazit demo --lang de` and `uv run fazit demo --lang en` | Passed. |
| `uv run python site/check_site.py` | 24 pages and 969 references checked. |
| `node site/check_alignment.mjs` | 67,620 measurements per engine, including iPhone emulation. Largest offset 0.50 px, zero failures. |
| `node site/check_spacing.mjs` | 12,680 measurements passed per engine, including iPhone emulation. |
| `node tests/browser/check-scrollbars.mjs` | Passed in both engines. The two demos opened from disk with JavaScript disabled and zero network requests. |
| CI unpacked source distribution | 1,034 passed, six expected skips and zero failures. |

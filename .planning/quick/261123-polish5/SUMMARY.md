# Report area filters on iPhone

The same alignment checker ran against `25c27a1` (`polish` and `origin/main`) and the updated working tree. It covered all 24 pages in light and dark at 360, 390, 768 and 1280 px in both engines. WebKit added a 390 × 844 px viewport with mobile and touch emulation at device scale 3. The checker opened the navigation and category menus and ran the reports with JavaScript disabled.

## WebKit screenshots

Each screenshot uses the iPhone settings from the alignment run. The PNGs are 1170 × 2532 pixels and live in the ignored `.shots/polish5/` directory.

| Report | Filters in light mode | Picker open in light mode | Filters in dark mode | Picker open in dark mode |
| --- | --- | --- | --- | --- |
| English | [Before](../../../.shots/polish5/before-en-light.png) · [After](../../../.shots/polish5/after-en-light.png) | [Before](../../../.shots/polish5/before-en-light-category.png) · [After](../../../.shots/polish5/after-en-light-category.png) | [Before](../../../.shots/polish5/before-en-dark.png) · [After](../../../.shots/polish5/after-en-dark.png) | [Before](../../../.shots/polish5/before-en-dark-category.png) · [After](../../../.shots/polish5/after-en-dark-category.png) |
| German | [Before](../../../.shots/polish5/before-de-light.png) · [After](../../../.shots/polish5/after-de-light.png) | [Before](../../../.shots/polish5/before-de-light-category.png) · [After](../../../.shots/polish5/after-de-light-category.png) | [Before](../../../.shots/polish5/before-de-dark.png) · [After](../../../.shots/polish5/after-de-dark.png) | [Before](../../../.shots/polish5/before-de-dark-category.png) · [After](../../../.shots/polish5/after-de-dark-category.png) |

## Filter geometry

At 390 px the two demos have 358 px of available track width. At 360 px they have 328 px. The track now measures 48 px high, with five 44 px segments inset by 2 px. The segments share the track at 63.2 px each at 360 px and 69.2 px each at 390 px. The selected segment has the same height and capsule radius in every keyboard-tested state.

Full labels return according to the width of the report's filter column. The cutoffs allow for a two-digit status count. The table gives the measured intrinsic widths with the embedded font, full label padding and track insets.

| Report | Demo label width in Chromium / WebKit | Width with a two-digit status count in Chromium / WebKit | Full labels at this column width |
| --- | ---: | ---: | ---: |
| English | 518 / 516.91 px | 527 / 525.72 px | 528 px (`33rem`) |
| German | 584 / 579.38 px | 593 / 588.19 px | 594 px (`37.125rem`) |

The category trigger and options use normal line height and block padding. In English iPhone emulation the browser-managed trigger label grew from a 9.80 px box with `scrollHeight` 14 and `clientHeight` 10 to a 17 px box with both heights at 17. The trigger itself measures 44 px. The emulation reproduces the label-slot overflow behind the founder's physical-iPhone clipping report. [Before layout](../../../.shots/polish5/before-layout.log) · [After layout](../../../.shots/polish5/after-layout.log) · [Breakpoint and offline native-picker checks](../../../.shots/polish5/boundaries.log)

The clipping check also flagged the desktop navigation links and the Chromium bar button's hit-area pseudo-element. The text links now use the 44 px hit height. The compact button paints a 28 px capsule inside its 44 px link, so the hit area fits the control's own box.

## Regression checks

| Assertion | Main failures in Chromium | Main failures in WebKit | Fixed failures in Chromium / WebKit |
| --- | ---: | ---: | ---: |
| One row of segments | 40 | 60 | 0 / 0 |
| Label ink inside the padding box | 276 | 312 | 0 / 0 |
| Scroll dimensions within the client box | 408 | 104 | 0 / 0 |
| Selected segment height fits the 2 px inset | 40 | 60 | 0 / 0 |
| Capsule radius | 40 | 60 | 0 / 0 |
| Selected segment starts 2 px inside the track | 14 | 20 | 0 / 0 |
| Localised status title and radio name | 16 | 20 | 0 / 0 |

The baseline exits 1 in both engines. In the WebKit iPhone views, the second row starts 46 px below the first in both languages and themes. Its 44 px segments occupy a 94 px track, 46 px taller than the selected segment plus its insets. The pixel scan flags descender ink up to 3 px outside the category label's trimmed box. The fixed run exits 0, with 47,640 measurements across 192 Chromium views and 59,824 across 240 WebKit views. The largest offset is 0.50 px in each engine. [Main failure log](../../../.shots/polish5/before-check-alignment-final.log) · [Fixed run](../../../.shots/polish5/after-check-alignment.log)

- The alignment check compares the segment tops, checks visible children and text ranges for wraps, and scans the font's painted pixels to locate label ink relative to the rendered padding boxes. It checks horizontal and vertical scroll dimensions, including the browser-managed category text boxes. It also compares the selected and unselected heights, the inset and the compact segment widths.
- A temporary WebKit fixture made the selected segment 52 px high, restored picker text trimming and forced a category option onto three lines. The checker caught the 8 px height mismatch, ink overflow and extra text fragments. [Fixture failures](../../../.shots/polish5/mutation-checks.log)
- The browser check uses arrow keys to select every available status and return to All, then uses Tab, Space, ArrowDown and Enter to operate the category picker. It checks the resulting area cards and the accessible radio names at phone and desktop widths. The Python filter test checks the actual label text and localised titles using bundled reports, so it also runs in the unpacked source distribution.

## German strings

The narrow status track reads **Alle 14**, followed by the four status symbols with counts **1**, **9**, **1** and **3**. The radio names are **Hindernis 1**, **Handlungsbedarf 9**, **Unbekannt 1** and **Bereit 3**. The titles use the status words and the wider layout shows those words beside their symbols. The category trigger reads **Alle Kategorien**. **Bereiche nach Status anzeigen** and **Bereiche nach Kategorie anzeigen** still name the controls. The copy comes from the existing locale keys. The home-page download now reads **HTML herunterladen, 434 KB**.

## Verification

| Command | Result |
| --- | --- |
| `uv run ruff check .` | Passed |
| `uv run ruff format --check .` | 50 files formatted |
| `uv run pytest -q` | 1,040 passed |
| `uv run fazit demo --lang de` and `uv run fazit demo --lang en` | Passed. Fresh outputs match the published demos byte for byte. |
| `uv run python site/check_site.py` | 24 pages and 969 references checked |
| `node site/check_alignment.mjs` | Chromium 151.0.7922.34 and WebKit 26.5 passed |
| `node site/check_spacing.mjs` | 9,524 measurements passed per engine |
| `node tests/browser/check-scrollbars.mjs` | Both engines passed. Both demos opened from disk with JavaScript disabled and zero network requests. |
| CI unpacked source distribution | 1,034 passed, six expected checkout-only skips, zero failures on CPython 3.12.16 |

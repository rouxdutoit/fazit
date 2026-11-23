# Update the status colours and report phone menu

## Status colours

Apple updated the system colour values on 9 June 2025. Accessed on 23 November 2026. [Apple Human Interface Guidelines, Color](https://developer.apple.com/design/human-interface-guidelines/color#System-colors)

| Status | Light, before → after | Dark, before → after | Increased contrast light, before → after | Increased contrast dark, before → after |
| --- | --- | --- | --- | --- |
| Blocker (Orange) | `#FF9500` → `#FF8D28` | `#FF9F0A` → `#FF9230` | `#C93400` → `#C55300` | `#FFB340` → `#FFA056` |
| Needs work (Yellow) | `#FFCC00` → `#FFCC00` | `#FFD60A` → `#FFD600` | `#B25000` → `#A16A00` | `#FFD426` → `#FEDF43` |
| Ready (Green) | `#34C759` → `#34C759` | `#30D158` → `#30D158` | `#248A3D` → `#008932` | `#30DB5B` → `#4AD968` |
| Unknown (`systemGray`) | `#8E8E93` → `#8E8E93` | `#8E8E93` → `#8E8E93` | `#6C6C70` → `#6C6C70` | `#AEAEB2` → `#AEAEB2` |

Symbols use the palette at full strength. Badges tint their background with 12% of the status colour and retain the main text colour on their labels. Increased contrast follows the screen theme. Print uses the default light palette.

## Phone menu

At widths up to 819 px, the report uses the site's 44 × 44 px top-right menu control. The `details` and `summary` disclosure opens a full-width panel with Summary, Next steps, Areas, Costs, Replacements, Closer look and Appendix. The two menu strokes form the site's close symbol when the panel is open. The report marks the section linked by the current fragment. The control retains its localised accessible name and the panel scrolls within short viewports.

## Files

| Files | Change |
| --- | --- |
| `site/style.css`, `src/fazit/templates/report.html.j2` | Set the shared palettes. Match the report control and panel to the phone menu. |
| `site/demo/de/index.html`, `site/demo/en/index.html` | Regenerate the published demos from the template. |
| `site/index.html`, `site/de/index.html` | Round the new demo download sizes to 425 KB and 438 KB respectively. |
| `site/og.png` | Refresh the sharing image from the same English report excerpt with the new palette. |
| `site/check_site.py`, `tests/test_report.py` | Check exact status tokens in both sources and the rendered report, print selection and the report's native navigation. |
| `site/check_alignment.mjs` | Check the closed and open menu, icon and hit target size, panel bounds, keyboard use and active section. |
| `DESIGN.md`, `DECISIONS.md` | Record the palette, source and founder's decision (D39). |

## Verification

- `uv run ruff check .` and `uv run ruff format --check .` passed.
- `uv run pytest -q` passed all 979 tests.
- Both `uv run fazit demo --lang de` and `uv run fazit demo --lang en` passed with temporary output directories. The static site check matched the published HTML byte for byte.
- `uv run python site/check_site.py` passed for 24 pages and 949 references. A separate check confirmed that restoring old palette values or the old print override produced errors for both sources.
- `node site/check_alignment.mjs` passed 8240 measurements across 144 page views at 360, 768 and 1280 px. The largest offset was 0.30 px against the 0.75 px limit.
- Chromium verified 405 symbol colours and 215 badge tints across the screen and print palettes. The lowest badge label contrast was 11.47:1.
- Both published reports opened from disk with the network and scripting disabled. At 360 px, the button and both icon states matched the website, and keyboard navigation reached the Appendix at a viewport height of 320 px. The offline menu also opened and closed with motion enabled in Chromium and Firefox.

## Screenshots

The report colour captures show the first real area card header for each status. The website captures show the homepage report preview.

| Palette | Website symbols and badge | Report symbols and badges |
| --- | --- | --- |
| Light | [Website](../../../.shots/colours/website-status-light.png) | [Report](../../../.shots/colours/report-status-light.png) |
| Dark | [Website](../../../.shots/colours/website-status-dark.png) | [Report](../../../.shots/colours/report-status-dark.png) |
| Increased contrast, light | [Website](../../../.shots/colours/website-status-increased-contrast-light.png) | [Report](../../../.shots/colours/report-status-increased-contrast-light.png) |
| Increased contrast, dark | [Website](../../../.shots/colours/website-status-increased-contrast-dark.png) | [Report](../../../.shots/colours/report-status-increased-contrast-dark.png) |

| Report at 360 px | Hero | Menu open |
| --- | --- | --- |
| English light | [Hero](../../../.shots/colours/report-en-360-light.png) | [Open menu](../../../.shots/colours/report-en-360-light-menu.png) |
| English dark | [Hero](../../../.shots/colours/report-en-360-dark.png) | [Open menu](../../../.shots/colours/report-en-360-dark-menu.png) |
| German light | [Hero](../../../.shots/colours/report-de-360-light.png) | [Open menu](../../../.shots/colours/report-de-360-light-menu.png) |
| German dark | [Hero](../../../.shots/colours/report-de-360-dark.png) | [Open menu](../../../.shots/colours/report-de-360-dark-menu.png) |

The four existing 360 px homepage captures were refreshed. Git ignores the screenshot directory. [Homepage captures](../../../.shots/report-redesign/rr12/)

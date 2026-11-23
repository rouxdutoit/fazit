# Leanness audit summary

Applied the safe findings from [LEAN-AUDIT.md](LEAN-AUDIT.md) against `19d38aa`. Each published demo is 3,471 bytes smaller. The implementation and generated demos use 332 fewer text lines and 42,199 fewer bytes in total.

## Report and website weight

| Finding | Decision | Reason |
| --- | --- | --- |
| Website `latin-ext` fonts | Applied | The 20 authored pages load only the Latin faces. Removed both unused faces and files. |
| Static Geist Mono in the report | Skipped | Chromium switched the PDF font embedding from Type 3 to TrueType. A font-only trial reproduced pixel differences in printed monospace text with identical screen captures. Restoring the variable font eliminated the differences. |
| Demo download sizes | Applied | Regenerated both demos. The English file is 405,338 bytes and the German file is 417,665 bytes. At the existing 10 KB precision, the labels are still 410 KB and 420 KB. |
| `flag`, `handshake`, `person`, `speed` and `wifi-off` site SVGs | Applied | The five files had no references in the site or package. |
| Readiness filter empty state | Applied | One declaration covers all 20 status and category pairs. The target exception has the same effect for links to findings and group headings. |
| Code, cancel and chevron masks | Applied | Each pair shares its original SVG. The source comments, colours and dimensions are preserved. |
| Footer email icon | Applied | The same mail mask draws the envelope as a pseudo-element. All 20 links retain their dimensions, accessible names and tooltips. |
| Website Coverage names | Applied | Direct text occupies the same grid column. The symbol wrappers and screen-reader labels are preserved. |
| Unused report CSS | Applied | Removed the unmatched prose-link selector, overridden base table and header declarations, duplicate `.coverage` defaults, unused `.cov` layout and ineffective `.evidence-meta` order. Kept the `tbody th` weight. |
| Unused site CSS | Applied | `.steps p`, `.note` with its narrow-screen override, and `.tiles .tile-label` have no authored or script-created matches. |
| Report replacement coverage label wrapper | Applied | `<strong>` is the grid item and carries the same visible label. The rules test still checks the label counts and requires one label per row. |
| `data-bar` | Applied | `.bar` selects the same header on each page, including both error pages. The menu still uses `data-open` and `aria-expanded` and restores focus on Escape. |

## Smaller CSS, markup and script findings

| Finding | Decision | Reason |
| --- | --- | --- |
| Copy hover background | Applied | The later rule already supplies the effective background. The earlier rule still sets the foreground colour. |
| Linked tile rules | Applied | The two matching selectors share one block with the same layout and transition. |
| Coverage legend spacing | Applied | Both Coverage pages use the legend, so its computed top margin of zero comes from the base rule. |
| Redundant report print CSS | Applied | The report title uses `--fs-title` in print. The base layout supplies the body margin, section label position and horizontal divider inset. |
| Pilot paragraph wrappers | Applied | The paragraphs are direct children with the same 48 px top margin and text measure. |
| Wordmark animation step | Applied | All 40 animated wordmarks contain five letters, so the calculation always yielded 18 ms. |
| Start command intro selectors | Skipped | The proposed selectors remove the copy button's 24 px top margin and introduce an 8 px gap above the manual-copy message. |
| Site `--fs-title` and report `--link-hover` | Skipped | The design specifies shared token names, and each token has a consumer on the other surface. |

## Python and locales

| Finding | Decision | Reason |
| --- | --- | --- |
| `_SummaryRows` | Applied | The template reads `blockers` and `open_areas` directly in their existing order. |
| Cost and input context fields | Applied | Guarded lookups use `Inputs` directly, break-even uses the sign of the amount, and the chart selects blocks with unknown totals from the blocks it already has. Tests check exact break-even amounts and the message for a negative threshold. |
| Transfer gap tuple conversion | Applied | The template uses the ordered `TransferGap` objects directly. The scope statement keeps its interface and ordering. |
| Repeated population check in `provided_counts` | Applied | The loader sums known parent counts only when all parents are known. Zero still counts as a known value, and D31 assertions and cases are preserved. |
| Long productivity-loss label | Applied | Each locale uses one scalar anchor for its three occurrences. The parsed locale dictionaries compare equal. |
| Short repeated cost labels | Skipped | The audit calls for one anchor per locale. These short labels remain independently editable in the input and line-item contexts. |
| Other locale keys | Skipped | Each key serves its own lookup. The catalogue also requires the byte-unit keys. |
| Report macros, other context entries and production functions | Skipped | The audit found consumers for all of them. |

## Checker and tests

| Finding | Decision | Reason |
| --- | --- | --- |
| Font declaration parser and validator | Applied | Both callers use the same family, fallback, token and shorthand checks. The report and site still apply their own URL and shadow checks. |
| Repeated replacement-label recount | Applied | The rules test counts labels in both languages for both samples and product profiles. The summary test still checks its displayed counts and links. |
| Offline DOM walk | Applied | Both test matrices use the same walk. The generated-tenant test still checks the exact CSP, and the report matrix still checks embedded fonts, the stylesheet and resource-free attributes. |
| Catalogue fixtures | Applied | One function-scoped fixture supplies the immutable catalogue under the socket audit. Tests that create modified catalogues keep their own setup. |
| Duplicate site/package icon comparisons | Applied | One test compares every packaged icon and explicitly requires all four coverage filenames. The separate check for distinct status and coverage SVG paths remains. |
| Font existence check in design URLs | Skipped | Removing the early existence check changes the missing-font diagnostics and makes the standalone design check accept a missing local WOFF2. |
| Nine packaged report icons and inline SVG | Skipped | All nine icons have consumers across the profiles. The inline SVG requirement is part of the report design. |

## Net lines and bytes removed per file

Positive values indicate a reduction. Negative values indicate an increase. Line counts apply to text files. Byte counts use uncompressed sizes.

| File | Lines removed | Bytes removed |
| --- | ---: | ---: |
| `site/404.html` | 0 | 59 |
| `site/about/index.html` | 0 | 59 |
| `site/check_site.py` | 35 | 1,657 |
| `site/coverage/index.html` | 0 | 423 |
| `site/de/404.html` | 0 | 59 |
| `site/de/about/index.html` | 0 | 59 |
| `site/de/coverage/index.html` | 0 | 423 |
| `site/de/impressum/index.html` | 0 | 59 |
| `site/de/index.html` | 0 | 59 |
| `site/de/integrators/index.html` | 0 | 59 |
| `site/de/pilots/index.html` | 2 | 90 |
| `site/de/privacy/index.html` | 0 | 59 |
| `site/de/security/index.html` | 0 | 59 |
| `site/de/start/index.html` | 0 | 59 |
| `site/demo/de/index.html` | 91 | 3,471 |
| `site/demo/en/index.html` | 91 | 3,471 |
| `site/fonts/figtree-latin-ext.woff2` | — | 10,280 |
| `site/fonts/geist-mono-latin-ext.woff2` | — | 13,044 |
| `site/icons/flag.svg` | 1 | 395 |
| `site/icons/handshake.svg` | 1 | 1,221 |
| `site/icons/person.svg` | 1 | 573 |
| `site/icons/speed.svg` | 1 | 577 |
| `site/icons/wifi-off.svg` | 1 | 797 |
| `site/impressum/index.html` | 0 | 59 |
| `site/index.html` | 0 | 59 |
| `site/integrators/index.html` | 0 | 59 |
| `site/pilots/index.html` | 2 | 90 |
| `site/privacy/index.html` | 0 | 59 |
| `site/security/index.html` | 0 | 59 |
| `site/site.js` | 2 | 120 |
| `site/start/index.html` | 0 | 59 |
| `site/style.css` | 46 | 2,847 |
| `src/fazit/fonts/css.py` | -42 | -1,906 |
| `src/fazit/inputs.py` | 4 | 62 |
| `src/fazit/locales/de.yaml` | 0 | 83 |
| `src/fazit/locales/en.yaml` | 0 | 73 |
| `src/fazit/report.py` | 16 | 499 |
| `src/fazit/templates/report.html.j2` | 25 | 560 |
| `tests/conftest.py` | -7 | -131 |
| `tests/helpers.py` | -19 | -804 |
| `tests/test_costs.py` | -10 | -397 |
| `tests/test_inputs.py` | 5 | 108 |
| `tests/test_model.py` | 5 | 76 |
| `tests/test_report.py` | 61 | 2,796 |
| `tests/test_rules.py` | 5 | 82 |
| `tests/test_simulation.py` | 15 | 675 |
| **Total** | **332** | **42,199** |

## Checks

| Command | Result |
| --- | --- |
| `uv run pytest -q` | 953 passed. |
| `uv run ruff check .` | Passed. |
| `uv run ruff format --check .` | Passed. All 174 Python files are formatted. |
| `uv run python site/check_site.py` | Checked 22 pages and 880 references. Both checked-in demos matched fresh renders byte for byte. |
| `uv run fazit demo --lang de --out <tmp>` | Passed. Copied the printed report to `site/demo/de/index.html`. |
| `uv run fazit demo --lang en --out <tmp>` | Passed. Copied the printed report to `site/demo/en/index.html`. |
| `git diff --check` | Passed. |

- Chromium compared 58 before-and-after light-mode screenshot pairs at 1280 px and 360 px. All pairs matched pixel for pixel, including both home pages, both demo reports, the other site pages, the open mobile menus and filtered report views. Both reports opened with the browser offline and JavaScript disabled. [Screen comparison log](../../.shots/lean-audit/screen-comparison.txt)
- The browser recorded the same results for all 120 readiness filter states. It also followed fragments to a filtered finding and status heading and checked that Escape closes the mobile menu and returns focus to its button.
- Chromium printed the town, nonprofit and all-Unknown openDesk reports in both languages on A4 with backgrounds on and off. Poppler rasterised the 12 PDFs at 96 dpi. All 392 page pairs matched pixel for pixel. [Print comparison log](../../.shots/lean-audit/print-comparison.txt)
- Compared 18 report renders across both languages and all three target profiles for the bundled samples and the all-Unknown scan. The bodies matched after the audited wrapper and blank-line cuts. Reports saved 3,432 to 3,471 bytes each.
- Compared both parsed locale dictionaries and checked that the shared validators still reject invalid font and offline markup inputs. The privacy, escaping, offline and D31 test cases remain in the suite.

### Before-and-after screenshots

| Page | 1280 px | 360 px |
| --- | --- | --- |
| English home | [Before](../../.shots/lean-audit/before/home-en-1280.png) · [After](../../.shots/lean-audit/after/home-en-1280.png) | [Before](../../.shots/lean-audit/before/home-en-360.png) · [After](../../.shots/lean-audit/after/home-en-360.png) |
| German home | [Before](../../.shots/lean-audit/before/home-de-1280.png) · [After](../../.shots/lean-audit/after/home-de-1280.png) | [Before](../../.shots/lean-audit/before/home-de-360.png) · [After](../../.shots/lean-audit/after/home-de-360.png) |
| English demo | [Before](../../.shots/lean-audit/before/report-en-1280.png) · [After](../../.shots/lean-audit/after/report-en-1280.png) | [Before](../../.shots/lean-audit/before/report-en-360.png) · [After](../../.shots/lean-audit/after/report-en-360.png) |
| German demo | [Before](../../.shots/lean-audit/before/report-de-1280.png) · [After](../../.shots/lean-audit/after/report-de-1280.png) | [Before](../../.shots/lean-audit/before/report-de-360.png) · [After](../../.shots/lean-audit/after/report-de-360.png) |

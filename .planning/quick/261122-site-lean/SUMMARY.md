# Lean website changes

1. **Privacy.** Both privacy pages now say the site uses no browser storage. Removed the colour-mode row and section, including the `fazit-theme` code reference.
2. **Images.** Re-encoded all eight readiness previews as lossless WebP and verified their decoded pixels against the PNGs. Updated both home pages and gave the preview image high fetch priority. The checker reads VP8L and VP8X dimensions and applies the 150 KB cap to WebP previews. The social card and touch icon use PNG.
3. **Fonts.** Instantiated the Latin Geist Mono font at weight 400 with the pinned fontTools and Brotli scratch tools. It keeps its filename, character map and OFL notices. All 14 site pages preload Latin Figtree.
4. **Screenshots.** Moved the existing working files to the ignored root `.shots/` and removed the obsolete site ignore file. The contributor checklist already lists the CI site check. Deployment exclusions are assigned to the founder.
5. **CSS.** Removed dead selectors, tokens and overridden declarations. Consolidated the mobile navigation rules, the evidence and legal summary styles, the timeline styles and reduced-motion overrides. Moved responsive rules beside their components and kept the breakpoint values required by the design.
6. **First paint.** The blocking script enables motion after registering setup and error recovery. CSS supplies the initial hidden state for headings and reveal targets. Content is visible if the script cannot start or a motion callback fails.
7. **JavaScript.** Shared the one-shot observer logic, dropped the redundant guards for the navigation and named the timing constants. Grid reveal delays follow the rendered column count. The copy control remains optional.
8. **HTML.** Removed the footer switch wrappers, coverage wrappers and unused wrappers on the legal notices. The privacy pages use an article to keep the policy sections together beside the summary on wide screens. Matched the footer wordmark labels to the header labels, aligned the pilot subsection markup and removed the four duplicate social tags. The coverage table retains its explicit roles.
9. **Icons.** Verified page, stylesheet and script references with grep before deleting `visibility.svg`, `warning.svg` and `help.svg`.
10. **Caching.** Both hosting configurations set a one-year immutable cache policy for `/fonts/*` and `/icons/*` and a one-day policy for `/images/*`.
11. **Names and comments.** Standardised on `.tile-icon`, `.note-text` for standalone notes and `.more` for chevron links. Replaced sided positioning and padding with logical properties, shared the pill radius and removed brand references from style comments.

## Verification

- `uv run python site/check_site.py` passed for 16 pages and 516 references, including the byte comparisons for both demo reports.
- `node --check site/site.js`, `uv run ruff check site/check_site.py`, and `uv run ruff format --check site/check_site.py` passed.
- `uv run pytest -q tests/test_repo_basics.py` passed all 9 tests.
- The image checks passed for pixel equality, VP8L and VP8X headers, invalid dimensions, the preview byte cap and both required PNG dimensions.
- Playwright compared 56 full-page screenshots covering both languages, 1280 and 375 px, and both colour schemes. All 48 non-privacy pairs were pixel-identical. The eight privacy pairs reflect the storage copy change. The before, after and first-paint screenshots are in `.shots/261122-site-lean/`.
- The first-contentful-paint checks reproduced the visible heading and tile before the change and confirmed both start hidden after it. Playwright also checked reduced motion, missing JavaScript, failure during motion setup, grid stagger delays, mobile navigation, the coverage reveal and clipboard success and fallback. Firefox passed the WebP, desktop grid and reduced-motion smoke checks.
- Both sample reports opened in offline Chromium with zero HTTP requests. `git diff --check` passed.

## Size in bytes

Home page load totals count uncompressed response bodies requested by Chromium, including the selected preview and the fonts and icons it loads.

| Asset or page load | Before | After |
| --- | ---: | ---: |
| CSS | 32,180 | 29,160 |
| JavaScript | 5,276 | 5,606 |
| Eight readiness images | 970,837 | 301,236 |
| Social card and touch icon | 97,906 | 97,906 |
| Latin Geist Mono | 31,368 | 14,824 |
| English home HTML | 33,987 | 33,390 |
| German home HTML | 36,461 | 35,838 |
| English home, 1280 px light | 268,037 | 150,153 |
| English home, 1280 px dark | 274,042 | 150,787 |
| English home, 375 px light | 234,744 | 152,011 |
| English home, 375 px dark | 241,472 | 152,509 |
| German home, 1280 px light | 273,453 | 157,181 |
| German home, 1280 px dark | 279,356 | 157,173 |
| German home, 375 px light | 242,919 | 157,083 |
| German home, 375 px dark | 248,278 | 157,051 |

## Skipped items

None.

# Timeline dots and content link underlines

## Timeline

The shared timeline uses 11 × 11 CSS px dots. The 1 px rail starts 5 px from the timeline's left edge, so both centres sit 5.5 px from that edge. The dots remain aligned to their titles' cap bands. Their opaque fills make the rail meet each circle at its edge. [Design rules](../../../DESIGN.md#structure)

Playwright captured the English roadmap in WebKit 26.5 at 390 × 844 CSS px with iPhone mobile and touch settings and device scale 3. The baseline was `c2a38f5` on `polish`. The zoomed crops enlarge the original device pixels by 2×.

| Measurement | Before | After |
| --- | ---: | ---: |
| Dot layout box | 11.891 × 11.891 CSS px | 11 × 11 CSS px |
| Horizontal offset in the captured pixels, all three dots | 0.5 device px | 0 device px |
| Painted Next outline | 36 × 35 device px | 33 × 33 device px |

![Zoomed before and after of Now, Next and Later in light mode](../../../.shots/polish6/timeline-zoom-light.png)

[Dark mode zoom](../../../.shots/polish6/timeline-zoom-dark.png) · [Light mode before](../../../.shots/polish6/timeline-before-light.png) · [Light mode after](../../../.shots/polish6/timeline-after-light.png) · [Dark mode before](../../../.shots/polish6/timeline-before-dark.png) · [Dark mode after](../../../.shots/polish6/timeline-after-dark.png)

## Content link underlines

A 1 px gradient in the link's colour expands from the left over 250 ms with `--ease`. The same offset aligns the gradient with the muted resting line on links in running text. Standalone links and card titles put the gradient on the text span so the chevron keeps its gap. The gradient retracts when hover or keyboard focus ends and appears immediately under reduced motion. Print uses the resting decoration. [Links and motion rules](../../../DESIGN.md#links-and-buttons)

The frames show the home page's “See all areas”, the English report's “All blockers” and “The translation guide” within a Roadmap sentence. Chromium captured the transition at device scale 3. The foreground line reached 36.9% at 32 ms, 86.6% at 80 ms and 100% at 250 ms. At 48 ms after pointer leave, it had retracted to 37.2%.

![Chromium frames showing the underline at rest, during hover and after pointer leave](../../../.shots/polish6/hover-underline-frames.png)

Fresh CLI output supplies both published demos. The home download labels now read 425 KB in English and 437 KB in German.

## Verification

The alignment check measured both roadmaps in light and dark at four viewport widths and in iPhone emulation. Each engine checked 60 timeline views at device scales 1, 2 and 3. The limit is 0.1 CSS px for dot centre and width-to-height differences. A run with the original stylesheet rejected the fractional sizes and old radius in all 60 views per engine.

The browser check exercised hover, keyboard focus and retraction on website and report links, including a wrapped report label at 360 px. It verified that the desktop navigation, phone menu and footer keep their resting underline styles on hover. It checked that the underline appears immediately under reduced motion and that print uses the resting decoration.

| Command | Result |
| --- | --- |
| `uv run ruff check .` and `uv run ruff format --check .` | Passed. 50 files formatted. |
| `uv run pytest -q` | 1,040 passed, zero failures. |
| `uv run fazit demo --lang de` and `uv run fazit demo --lang en` | Passed. Both published demos match fresh output byte for byte. |
| `uv run python site/check_site.py` | 24 pages and 969 references checked. |
| `node site/check_alignment.mjs` | 48,592 Chromium measurements and 60,744 WebKit measurements. Zero failures in both engines. |
| `node site/check_spacing.mjs` | 9,524 spacing measurements passed per engine. |
| `node tests/browser/check-scrollbars.mjs` | Passed in both engines. Both demos opened from disk with JavaScript disabled and zero network requests. |
| CI unpacked source distribution | 1,034 passed, six expected checkout-only skips, zero failures on CPython 3.12.16. |

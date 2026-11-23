# Integrate home-cut and align

## Merge resolution

| Conflicted files | Resolution |
| --- | --- |
| `site/index.html`, `site/de/index.html` | Kept the six sections from RR-12b, the compact Mail card and cost tiles, the commands with their prerequisite footnote, and the closing band. Applied the shared symbol and label markup to the hero buttons, preview window controls, evidence, icon facts and standalone links. The hero preview now renders the sample report’s status rows, definitions and Telephony blocker as HTML. Those rows can follow the device’s colours and be measured directly. The two caption links remain, and the preview’s Telephony and All blockers links open their sections in the report. |
| `site/about/index.html`, `site/de/about/index.html` | Kept the RR-12 copy and the status tile’s Roadmap destination. Used the shared markup for the title and circled chevron. |
| `site/integrators/index.html`, `site/de/integrators/index.html` | Kept the link to the next Roadmap step and applied the shared chevron markup to the coverage comparison link. |
| `site/security/index.html`, `site/de/security/index.html` | Kept the safeguards, one offline verification section in the RR-12 position, the RR-12b advice on local folders without synchronisation, and the evidence limits. Centred the safeguard shields and tile icons with their labels and converted the offline test link to the shared markup. |
| `site/style.css` | Combined the compact homepage layout with the shared alignment rules. Kept the CSS for the Mail evidence rows, cost tiles, closing links and Roadmap timeline. Removed rules for the retired home tally and full Mail disclosure, legacy coverage and safeguard pseudo-elements, and per-component offsets for badges, icons and chevrons. |

Both Roadmap pages use the shared navigation, footer and timeline markup. The preview’s eight unused WebP files were removed and the sharing image was recaptured from the updated English demo. Both published demos were regenerated and match fresh CLI output byte for byte.

## Founder and coordinator follow-ups

- Both hero sample report buttons use the shared `.btn-secondary` fill, hover and pressed states.
- Status symbols use Apple’s system colours directly. The website and report use the Increase Contrast palettes when the device requests more contrast and the light Increase Contrast palette for print. Badge labels keep the main text colour over their status tint. The exact values are in `DESIGN.md` and the decision is recorded as D38.
- Both homepages use headings without final full stops.
- The German read-only and open source facts now carry the same claims as the English facts.

## German strings

| Location | Wording |
| --- | --- |
| `Nur Lesezugriff` caption | Keine Änderungen am Mandanten. |
| `Quelloffen` caption | Code und Regeln sind öffentlich. |
| Sample report download | HTML herunterladen, 436 KB |

The hero preview reuses the German sample report’s existing summary and blocker text.

## Test changes

- `site/check_alignment.mjs` covers both Roadmap pages and measures the home status labels and counts, Mail values and provenance, cost tiles, icon facts, closing links and terminal line spacing. A temporary copy with deliberate shifts was rejected for each of those home components.
- `site/check_site.py` compares the hero status rows with the matching report and checks home heading punctuation and the preview links. The six-section and sample cost checks still run.
- `tests/test_report.py` checks the exact shared colours, including Unknown and Increase Contrast, and direct application to the status symbols.

## Verification

| Check | Result |
| --- | --- |
| `uv run ruff check .` and `uv run ruff format --check .` | Passed. |
| `uv run pytest -q` | 979 passed. |
| `uv run fazit demo --lang de` and `uv run fazit demo --lang en` | Passed with temporary output directories. |
| `uv run python site/check_site.py` | Passed for 24 pages and 949 references. |
| `node site/check_alignment.mjs` | Passed 6,800 measurements across 144 page views. The largest offset was 0.30 px against a 0.75 px limit. |
| Browser checks | All 24 site pages and six offline report variants fit without horizontal scrolling at 360, 768 and 1280 px in light and dark. Both published demos loaded with the network and scripting disabled. The two hero secondary buttons matched the Security secondary buttons in all three states. |
| Colour and print | All 948 measured status symbols matched the expected colours. The minimum badge text contrast was 11.58:1. The minimum printed badge symbol contrast was 3.49:1. The town, nonprofit and all-Unknown reports kept the council summary readable on A4 page one in both languages, with backgrounds on and off. |

All nine conflict resolutions are in the working tree. The Git index still records those files as unmerged, pending staging.

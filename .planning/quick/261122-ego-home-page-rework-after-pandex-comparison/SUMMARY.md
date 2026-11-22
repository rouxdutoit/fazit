---
quick_id: 261122-ego
status: complete
date: 2026-11-22
---

# Summary: home page rework after the Pandex comparison

Both home pages (`site/index.html`, `site/de/index.html`) were restructured. No other page changed.

| Plan item | Change |
|---|---|
| 1. Hero | Context line on digital sovereignty; headline "Your Microsoft 365 dependency, with evidence" / "Ihre Abhängigkeit von Microsoft 365, belegt"; the sample report stays the main button; the `git clone` command moved to "How it works". Titles, descriptions and social tags updated. |
| 2. Figures | 15 areas; 52 licence products and 1,343 plan entries (counted from `rules/service_plans.yaml`, matching the 01-08A check); 0 network connections in the current version; 3 target profiles. |
| 3. Why Fazit | New section. States the problem without campaigning; no overall score, no supplier recommendation. |
| 4. One finding | The town sample's Telephony Blocker with its three evidence rows, copied from the generated English and German sample reports, plus the openDesk mapping row and the sample's status tally (4 / 9 / 1 / 1). |
| 5. Coverage | Fourteen areas against `mappings/opendesk.yaml` and `mappings/nextcloud.yaml` (checked 21 November 2026), with a link to the mapping files. Stacks into labelled cards below 600 px; ARIA table roles keep the semantics. |
| 6. Who it is for | Integrators, municipal IT providers, IT leads. |
| 7. Free, always | AGPL, no paid edition (S1), founding pilots until 28 February 2027, matching the pilots page. Replaces "Using Fazit". |
| 8. Scramble | Ported from the handmark site into `site.js`: the hero headline decodes on load and each section label on first view. Skipped for reduced motion or without IntersectionObserver; text stays visible without JavaScript; screen readers get the plain text throughout; CSP unchanged. |

Navigation now links Example, Coverage, How it works and Safeguards.

## Verification

- `uv run python site/check_site.py`: 16 pages, 611 references, no errors.
- `uv run ruff check .`, `uv run ruff format --check .`: pass. `uv run pytest -q`: 585 passed.
- `node --check site/site.js`: pass.
- Checked on localhost:8767 at desktop and 375 px, light and dark, English and German; no horizontal scrolling at 375 px.
- Not done: an automated axe run (loading axe-core from a CDN was blocked in this session) and a manual reduced-motion check.

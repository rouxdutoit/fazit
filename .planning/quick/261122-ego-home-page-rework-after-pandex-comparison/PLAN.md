---
quick_id: 261122-ego
slug: home-page-rework-after-pandex-comparison
date: 2026-11-22
status: complete
---

# Quick task: home page rework after the Pandex comparison

The founder asked for a home page closer to pandex.io in how it presents itself, with a sovereignty angle, and to keep the text-scramble effect from the earlier handmark site.

## Scope

`site/index.html`, `site/de/index.html`, `site/style.css`, `site/site.js`. No other pages change.

## Tasks

1. **Hero.** Context line on digital sovereignty in Germany, Austria and Switzerland; headline "Your Microsoft 365 dependency, with evidence" / "Ihre Abhängigkeit von Microsoft 365, belegt"; sample report as the main button; the `git clone` command moves to "How it works".
2. **Proof figures.** 15 areas; 52 licence products, 1,343 plan entries checked against Microsoft's reference (01-08A summary); 0 network connections in the current version; 3 target profiles.
3. **Why Fazit.** The problem, neutrally: no overall score, no supplier recommendation, the organisation decides.
4. **One finding in full.** The town sample's Telephony Blocker, quoted from the generated sample report with its three evidence rows and the openDesk mapping row.
5. **Coverage table.** Fourteen areas against the openDesk and Nextcloud mappings in `src/fazit/rules/mappings/`, checked 21 November 2026, with a link to the mapping files.
6. **Who it is for.** Integrators, municipal IT providers, IT leads.
7. **Free, always.** AGPL, no paid edition (S1), founding pilots until 28 February 2027 as on the pilots page.
8. **Text scramble.** Port the handmark effect to `site.js`: hero headline on load, section labels on first view. Off for reduced motion, text visible without JavaScript, readable by screen readers throughout, CSP `script-src 'self'` unchanged.

## Done means

- `uv run python site/check_site.py` passes; `uv run ruff check .`, `uv run ruff format --check .` and `uv run pytest -q` pass.
- Both pages checked on localhost:8767 at desktop and phone width, light and dark, with and without reduced motion.
- Every figure and quoted finding matches the code or the generated sample report.

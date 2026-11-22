---
quick_id: 261122-rv4
slug: promises
date: 2026-11-22
status: complete
---

# Quick task: release review batch 4, promises, site, docs and packaging

Fix R-20 to R-29 from `.planning/quick/261122-rev-release-review/FINDINGS.md`. The reviewers' evidence is in `REVIEW-fable-1.md` and `REVIEW-astra-1.md` in the same folder. Do not touch `src/fazit/` or `tests/` except where an item says so; another batch is changing the rules in parallel. Do not touch `.planning/` other than this task's `SUMMARY.md`. The founder has just finished the site design: change wording, headers and scripts only as each item needs, and keep every page visually unchanged.

## Items

1. **R-20 (high).** The report embeds Figtree and Geist Mono as data URIs; nothing is fetched. Make every promise say that: principle 6 in `DECISIONS.md` ("inline CSS and embedded fonts"), the Report section of `AGENTS.md`, both security pages, and anywhere else that says "system fonts" or "Systemschriften". Add decision D29 to `DECISIONS.md` after D28: the report embeds two OFL-licensed fonts as data URIs so it looks the same on every machine; the CSP allows `font-src data:` and nothing else; principle 6 is reworded to match; the founder may switch to system fonts later, which would drop about 69 KB per report.
2. **R-21 (high).** The site CSP must let the sample reports under `/demo/` use their embedded fonts. Add `data:` to `font-src` in both `site/_headers` and `site/.htaccess`, either site-wide or only for `/demo/*` (prefer the narrower rule if both files can express it). If `check_site.py` checks the headers, update it so it requires the new value.
3. **R-22 (high).** Make every present-tense claim true today. Phase 1 builds reports from the bundled samples, or from a scan in the schema plus the organisation's own answers and costs in `inputs.yaml`; measured evidence comes only from samples until import (phase 2) and live counts (phase 3). Fix `README.md`, `README.de.md`, `site/index.html`, `site/de/index.html`, `site/integrators/` (both languages), `publiccode.yml` and any other page that says otherwise: one plain status line near the top of each README and the home pages (in the existing elements, no new visual component), future tense for what does not exist yet, and the roadmap order everywhere as in `.planning/ROADMAP.md` (1.1, 1.2, 1.3, then import). Present the coverage table as the documented capabilities of each target, separate from an organisation's need. Attribute dated product references to the openDesk and Nextcloud profiles only.
4. **R-23 (medium).** One account of how the code is made, everywhere: take the site's current "How it is made" text (founder-approved, commit 36626d5) as the reference and align `README.md`, `README.de.md` and `CONTRIBUTING.md` with it.
5. **R-24 (medium).** Headings on the site must be readable without the scramble effect having run: in print and PDF, in headless renderers, before scrolling, and without JavaScript. Characters are hidden only while an animation is running; `@media print` shows everything. Keep the effect itself (the founder asked for it) and keep `prefers-reduced-motion` and screen-reader behaviour as they are. Verify with headless Chromium: DOM text visible after load without scrolling, and `--print-to-pdf` shows the headings.
6. **R-25 (medium).** Packaging: add `readme`, `authors` (roux, hello@rouxdutoit.com), `[project.urls]` (Homepage https://fazit.dev, Source and Issues on github.com/rouxdutoit/fazit), classifiers (development status matching the README, AGPL, Python 3.12+, OS independent, intended audience, topic), an sdist include list so `site/`, `.planning/`, `.claude/`, `drafts/` and `grants/` stay out, and a licence expression plus `license-files` that cover the bundled OFL fonts and Apache-licensed icons. Remove the `artifacts` line only if the wheel's file list is identical without it. Show the wheel and sdist file lists before and after in the summary. Update `tests/test_repo_basics.py` or `tests/test_installed_package.py` only if they check these fields, and only to require the new, stricter values.
7. **R-26 (medium).** Add `.gitattributes` so byte-sensitive files (LICENSE, the demo reports, rule files, locales, templates, fonts, images) check out unchanged on Windows: `* text=auto eol=lf` plus `binary` for fonts and images, or narrower if that is safer. Check with `git -c core.autocrlf=true` that a checkout keeps the licence hash and the demo bytes.
8. **R-27 (medium).** In `SECURITY.md` and both READMEs (where local processing is promised), one sentence: data stays on the computer only if the scan, inputs and `--out` are on local storage; a network share sends them over the network.
9. **R-28 (low).** Make the home page coverage table match `src/fazit/rules/mappings/opendesk.yaml` and `nextcloud.yaml` (single sign-on for Nextcloud is a community app in the rule data), and add a check to `site/check_site.py` that compares the table's cells and tally with the mapping files so they cannot drift. Remove the 404 pages from `site/sitemap.xml`. Remove the obsolete `interest-cohort` from the Permissions-Policy in both header files. Remove `geist-mono-cyrillic.woff2` and its `@font-face` if no page uses Cyrillic.
10. **R-29 (low).** Add `uv run python site/check_site.py` to "Done means" in `AGENTS.md` and to `CONTRIBUTING.md`, with one line saying that a change to report output needs `site/demo/en` and `site/demo/de` regenerated, and how.

## Done means

```
uv run ruff check .
uv run ruff format --check .
uv run pytest -q
uv run fazit demo --lang de
uv run fazit demo --lang en
uv run python site/check_site.py
uv build
```

Suggest one commit per item. Mark each that changes user-visible wording.

---
quick_id: 261122-rv4
status: complete
date: 2026-11-22
---

# Release review batch 4

## Results and suggested commits

| Item | Result | Wording change | Suggested commit |
| --- | --- | --- | --- |
| R-20 | The offline report promise names embedded fonts. D29 records Figtree, Geist Mono, the report CSP and the approximate size saving from a later move to system fonts. | Yes | `docs: record the embedded report fonts` |
| R-21 | Both hosting configurations allow data-URI fonts under `/demo/*`. The site checker requires the scoped policies. | No | `fix: allow embedded fonts on the demo routes` |
| R-22 | Public copy identifies Phase 1, sample measurements and manual inputs. Planned capabilities follow the roadmap. Product check dates apply to openDesk and Nextcloud. | Yes | `docs: describe current capabilities and the roadmap` |
| R-23 | Both READMEs and the contribution guide follow the founder-approved account of authorship and review. | Yes | `docs: align the account of how Fazit is made` |
| R-24 | Heading text is visible before the first animation frame and in print. The scroll effect, accessible heading names and reduced-motion setting work in Chromium. | No | `fix: keep site headings readable before animation and in print` |
| R-25 | Both archives have the new project metadata and licence notices. The source distribution uses an include list. Removing the artifact rule preserved all 42 entries in the otherwise identical wheel build. | Yes, package metadata | `chore: add package metadata and limit sdist contents` |
| R-26 | An LF checkout policy preserves the licence and demo bytes with `core.autocrlf=true`. PNGs and WOFF2 files are marked binary. | No | `chore: preserve byte-sensitive files on checkout` |
| R-27 | The local-storage promise covers the scan, inputs and output directory and explains network shares. | Yes | `docs: explain the local-storage boundary` |
| R-28 | Both tables show the Nextcloud single sign-on community app. The checker compares cells with the mapping files and tallies with the demo reports. The 404 sitemap entries, obsolete permissions directive and unused font were removed. | Yes | `fix: align site coverage with the rule data` |
| R-29 | The contributor checklists include the site checker and explain how to refresh both demos. | Yes, contributor guidance | `docs: add site checks and demo refresh instructions` |

## Files

- `.gitattributes` sets LF checkout and binary asset attributes.
- `AGENTS.md` documents embedded fonts, the site check and demo refresh.
- `CONTRIBUTING.md` gives the site check, demo refresh and approved development account.
- `DECISIONS.md` records the Phase 1 evidence boundary, the local-storage condition and D29.
- `README.md` and `README.de.md` state current capabilities, planned phases, direct-transfer evidence, local storage and how contributors make and review the code.
- `SECURITY.md` explains local storage, embedded fonts and the provenance of measurements.
- `publiccode.yml` describes Phase 1 and the roadmap in both languages and identifies the project as in development.
- `pyproject.toml` adds the README, author, project URLs, classifiers, SPDX expression, licence files and source distribution include list.
- `tests/test_installed_package.py` checks the combined licence expression and verifies the packaged licence texts, including the existing AGPL hash.
- `site/index.html` and `site/de/index.html` update the current status, roadmap, privacy and audience copy and show the documented replacements and coverage.
- `site/integrators/index.html` and `site/de/integrators/index.html` distinguish the available demo from post-import assessments.
- `site/pilots/index.html` and `site/de/pilots/index.html` describe the assessments as planned after import.
- `site/security/index.html` and `site/de/security/index.html` explain the embedded fonts, local-storage condition and current evidence.
- `site/_headers` and `site/.htaccess` scope the font allowance to the demos and remove `interest-cohort`.
- `site/site.js` prepares each heading inside its first animation frame.
- `site/style.css` shows the original characters in print, defines the community app icon and drops the Cyrillic font rule.
- `site/sitemap.xml` lists indexable routes.
- `site/check_site.py` verifies CSP scope, table entries, sample tallies and sitemap coverage.
- `site/fonts/geist-mono-cyrillic.woff2` was removed after confirming that the site HTML uses no Cyrillic.
- `.planning/quick/261122-rv4-promises/SUMMARY.md` records the checks and commit grouping.

## Verification

- `uv run ruff check .` and `uv run ruff format --check .` passed. Ruff reported 85 files already formatted.
- `uv run pytest -q` passed with **606 tests in 109.43 seconds**.
- `uv run fazit demo --lang de` and `uv run fazit demo --lang en` succeeded. Chromium opened both generated reports at 360 px in an offline browser context. They matched the checked-in demo HTML byte for byte, so regeneration was unnecessary.
- `uv run python site/check_site.py` passed with 16 pages and 501 references. Altered badges, replacements, workload IDs and tallies failed their checks in both languages.
- `uv build` produced the wheel and sdist. The wheel contains the README and all three licence notices. The sdist excludes the site, planning files, Claude configuration, drafts and grants.
- Chromium showed all 13 headings on each homepage before scrolling with normal motion, reduced motion, JavaScript disabled and animation frames paused. Scrolling triggered the effect with its accessible name intact. Print hid the scrambled glyphs, and `--print-to-pdf` retained all 13 headings in each language.
- Chromium loaded both embedded fonts with the demo-only `_headers` policy. Local Apache served one CSP for each tested URL and allowed data-URI fonts only under `/demo/`. [Cloudflare Pages header rules](https://developers.cloudflare.com/pages/configuration/headers/#detach-a-header)
- A Git checkout into a temporary directory with `core.autocrlf=true` matched the licence SHA-256 and both demo files. All 52 checked files matched byte for byte.

## Deviations and open items

- The task protects `.planning/PROJECT.md`, where the historical notes still mention system fonts and give the earlier description of who writes and reviews the code. The current promise is in `DECISIONS.md` and `AGENTS.md`.
- The narrow `_headers` rule uses Cloudflare Pages detach syntax. Production header verification remains in R-36. Platform CI remains in R-34.

## Package file lists

### Wheel before and after

Both wheels contain these 40 files.

```
fazit-0.1.0.dist-info/METADATA
fazit-0.1.0.dist-info/RECORD
fazit-0.1.0.dist-info/WHEEL
fazit-0.1.0.dist-info/entry_points.txt
fazit-0.1.0.dist-info/licenses/LICENSE
fazit/__init__.py
fazit/catalogue.py
fazit/cli.py
fazit/costs.py
fazit/demo/nonprofit/inputs.yaml
fazit/demo/nonprofit/scan.json
fazit/demo/town/inputs.yaml
fazit/demo/town/scan.json
fazit/errors.py
fazit/fonts/OFL.txt
fazit/fonts/figtree-latin.woff2
fazit/fonts/geist-mono-latin.woff2
fazit/i18n.py
fazit/icons/LICENSE
fazit/icons/check-circle.svg
fazit/icons/chevron-right.svg
fazit/icons/help.svg
fazit/icons/report.svg
fazit/icons/warning.svg
fazit/inputs.py
fazit/locales/de.yaml
fazit/locales/en.yaml
fazit/model.py
fazit/output.py
fazit/parsing.py
fazit/report.py
fazit/rules.py
fazit/rules/findings.yaml
fazit/rules/mappings/generic.yaml
fazit/rules/mappings/nextcloud.yaml
fazit/rules/mappings/opendesk.yaml
fazit/rules/risky_file_types.yaml
fazit/rules/service_plans.yaml
fazit/rules/status.yaml
fazit/templates/report.html.j2
```

The final wheel has 42 files including these two additions.

```
fazit-0.1.0.dist-info/licenses/src/fazit/fonts/OFL.txt
fazit-0.1.0.dist-info/licenses/src/fazit/icons/LICENSE
```

### Source distribution before and after

The paths below are relative to `fazit-0.1.0/`. Both source distributions contain these 66 files.

```
.gitignore
AGENTS.md
CONTRIBUTING.md
DECISIONS.md
LICENSE
PKG-INFO
README.de.md
README.md
SECURITY.md
docs/interview-checklist.de.md
docs/interview-checklist.md
inputs.example.yaml
publiccode.yml
pyproject.toml
src/fazit/__init__.py
src/fazit/catalogue.py
src/fazit/cli.py
src/fazit/costs.py
src/fazit/demo/nonprofit/inputs.yaml
src/fazit/demo/nonprofit/scan.json
src/fazit/demo/town/inputs.yaml
src/fazit/demo/town/scan.json
src/fazit/errors.py
src/fazit/fonts/OFL.txt
src/fazit/fonts/figtree-latin.woff2
src/fazit/fonts/geist-mono-latin.woff2
src/fazit/i18n.py
src/fazit/icons/LICENSE
src/fazit/icons/check-circle.svg
src/fazit/icons/chevron-right.svg
src/fazit/icons/help.svg
src/fazit/icons/report.svg
src/fazit/icons/warning.svg
src/fazit/inputs.py
src/fazit/locales/de.yaml
src/fazit/locales/en.yaml
src/fazit/model.py
src/fazit/output.py
src/fazit/parsing.py
src/fazit/report.py
src/fazit/rules.py
src/fazit/rules/findings.yaml
src/fazit/rules/mappings/generic.yaml
src/fazit/rules/mappings/nextcloud.yaml
src/fazit/rules/mappings/opendesk.yaml
src/fazit/rules/risky_file_types.yaml
src/fazit/rules/service_plans.yaml
src/fazit/rules/status.yaml
src/fazit/templates/report.html.j2
tests/conftest.py
tests/fixtures/planted_scan.json
tests/tenants.py
tests/test_cli.py
tests/test_costs.py
tests/test_evidence_cli.py
tests/test_inputs.py
tests/test_installed_package.py
tests/test_locales.py
tests/test_model.py
tests/test_output.py
tests/test_privacy.py
tests/test_repo_basics.py
tests/test_report.py
tests/test_rules.py
tests/test_simulation.py
uv.lock
```

The baseline had 174 files including these 108 additional paths.

```
.claude/CLAUDE.md
.github/workflows/ci.yml
.planning/PROJECT.md
.planning/REQUIREMENTS.md
.planning/ROADMAP.md
.planning/STATE.md
.planning/config.json
.planning/phases/01-demo-and-report/01-01-PLAN.md
.planning/phases/01-demo-and-report/01-01-SUMMARY.md
.planning/phases/01-demo-and-report/01-02-PLAN.md
.planning/phases/01-demo-and-report/01-02-SUMMARY.md
.planning/phases/01-demo-and-report/01-03-PLAN.md
.planning/phases/01-demo-and-report/01-03-SUMMARY.md
.planning/phases/01-demo-and-report/01-04-PLAN.md
.planning/phases/01-demo-and-report/01-04-SUMMARY.md
.planning/phases/01-demo-and-report/01-05-PLAN.md
.planning/phases/01-demo-and-report/01-05-SUMMARY.md
.planning/phases/01-demo-and-report/01-06-PLAN.md
.planning/phases/01-demo-and-report/01-06-SUMMARY.md
.planning/phases/01-demo-and-report/01-07-PLAN.md
.planning/phases/01-demo-and-report/01-07-SUMMARY.md
.planning/phases/01-demo-and-report/01-08-PLAN.md
.planning/phases/01-demo-and-report/01-08A-SUMMARY.md
.planning/phases/01-demo-and-report/01-08B-SUMMARY.md
.planning/phases/01-demo-and-report/01-09-PLAN.md
.planning/phases/01-demo-and-report/01-09-SUMMARY.md
.planning/phases/01-demo-and-report/01-10-PLAN.md
.planning/phases/01-demo-and-report/01-10-SUMMARY.md
.planning/phases/01-demo-and-report/01-11-PLAN.md
.planning/phases/01-demo-and-report/01-11-SUMMARY.md
.planning/phases/01-demo-and-report/01-CONFIRM-2.md
.planning/phases/01-demo-and-report/01-CONFIRM-3.md
.planning/phases/01-demo-and-report/01-CONFIRM.md
.planning/phases/01-demo-and-report/01-CONTEXT.md
.planning/phases/01-demo-and-report/01-FINAL-REVIEW-astra.md
.planning/phases/01-demo-and-report/01-FINAL-REVIEW-fable.md
.planning/phases/01-demo-and-report/01-REVIEWS-2.md
.planning/phases/01-demo-and-report/01-REVIEWS-3.md
.planning/phases/01-demo-and-report/01-REVIEWS.md
.planning/phases/01-demo-and-report/SKELETON.md
.planning/phases/01.1-ai-assistants-and-decision-window/01.1-CONTEXT.md
.planning/quick/261122-ego-home-page-rework-after-pandex-comparison/PLAN.md
.planning/quick/261122-ego-home-page-rework-after-pandex-comparison/SUMMARY.md
.planning/quick/261122-rev-release-review/FINDINGS.md
.planning/quick/261122-rev-release-review/REVIEW-astra-1.md
.planning/quick/261122-rev-release-review/REVIEW-fable-1.md
.planning/quick/261122-rv4-promises/PLAN.md
.planning/quick/261122-sim-simulation-tests/PLAN.md
.planning/quick/261122-sim-simulation-tests/SUMMARY.md
.planning/research/copilot-area.md
HANDOFF.md
site/.gitignore
site/.htaccess
site/.well-known/security.txt
site/404.html
site/_headers
site/apple-touch-icon.png
site/check_site.py
site/de/404.html
site/de/impressum/index.html
site/de/index.html
site/de/integrators/index.html
site/de/pilots/index.html
site/de/privacy/index.html
site/de/security/index.html
site/demo/de/index.html
site/demo/en/index.html
site/favicon.svg
site/fonts/OFL.txt
site/fonts/figtree-latin-ext.woff2
site/fonts/figtree-latin.woff2
site/fonts/geist-mono-cyrillic.woff2
site/fonts/geist-mono-latin-ext.woff2
site/fonts/geist-mono-latin.woff2
site/icons/LICENSE
site/icons/account-balance.svg
site/icons/cancel.svg
site/icons/check-circle.svg
site/icons/code.svg
site/icons/computer.svg
site/icons/contrast.svg
site/icons/handshake.svg
site/icons/help.svg
site/icons/lock.svg
site/icons/person.svg
site/icons/report.svg
site/icons/visibility.svg
site/icons/warning.svg
site/icons/wifi-off.svg
site/images/readiness-de-dark.png
site/images/readiness-de-light.png
site/images/readiness-de-mobile-dark.png
site/images/readiness-de-mobile-light.png
site/images/readiness-en-dark.png
site/images/readiness-en-light.png
site/images/readiness-en-mobile-dark.png
site/images/readiness-en-mobile-light.png
site/impressum/index.html
site/index.html
site/integrators/index.html
site/og.png
site/pilots/index.html
site/privacy/index.html
site/robots.txt
site/security/index.html
site/site.js
site/sitemap.xml
site/style.css
```

## Orchestrator changes on merge

Batch 4 ran in a separate worktree while batch 1 and the founder's site restyling landed on `main`. Claude merged the patch three-way, kept the founder's new tile layout, and carried the wording into it. Claude restored founder copy that was not an overclaim (hero line, meta descriptions as "is built to show", the roadmap tiles after "Now", the privacy lines about a single file and no upload, the first pilots paragraph) and kept principle 2 as a promise with the local-storage condition added, instead of rewording it as an instruction.

## Commit note

Batch 4 landed as one commit, `6008c29`, because the merge left four files unstaged and the first two of three planned commits failed. Its message describes only the wording part. The same commit also holds R-21, R-24 and R-28 (site headers, headings in print, coverage check, sitemap, Cyrillic font) and R-25 and R-26 (package metadata, sdist include list, `.gitattributes`), as described above.

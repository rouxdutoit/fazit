# Fazit release review 3, final (reviewer: Claude Fable 5.2)

Commit `d39df08`, checked in the private clone on 2026-11-22.

## Verdict

**Release as is.** Nothing in the code or the site at this commit is at the level "would embarrass the project in public"; the announcement still waits on two founder actions, the domain and PyPI name (R-35) and the deployed headers and hosting claims (R-36).

Remaining code findings: 0 critical, 0 high, 2 medium, 2 low.

Ran: both Ruff checks, `pytest -q` (688 passed, 109 s), all 12 demos, `site/check_site.py` (18 pages, 618 references), `uv build` and tests from the unpacked sdist, my 5,048 malformed-file cases, 41 judgement variants, some 60 message and path probes, all 18 site routes in Chromium 151 under the declared headers, the home page in Firefox 153 and with reduced motion, print to PDF, and the CI run for this commit (three jobs green, the deep-simulation job still running).

## Round-2 findings, mine

- **F-01 / R-35.** Founder. Still RDAP 404 for `fazit.dev` and PyPI 404 for `fazit`.
- **F-03 / R-36.** Founder. No console error on any route under the declared headers.
- **F-05.** Fixed, with leftovers (low): `PROJECT.md:22-39` still says "Validated: none yet" with every item unchecked, and `ROADMAP.md:39-48` lists 7 unchecked plans beside "11/11". The HANDOFF line and `CLAUDE.md` placeholders are R-40.
- **F-09, F-13.** Founder decisions, unchanged.
- **F-11 / R-39.** Fixed. `DECISIONS.md:49` cites the paper, table and check date.
- **F-15.** Fixed. Clock matrix, prose assertions and duplicates are gone, helpers are shared; the report-test matrix waits for the redesign.
- **F-19.** Fixed with F2-03.
- **F2-01.** Fixed. Firefox and reduced-motion screenshots at 1280 and 390 px show the small arrow only.
- **F2-02.** Fixed. `as_of: 2026-02-30` on line 4 gives "Check the value of `as_of` on line 4"; other constructor errors name the file without a line.
- **F2-03.** Fixed. "Remove the unrecognised field on line 3 of inputs.yaml."; at signs name the field or the line.
- **F2-04.** Fixed. Every item on the list is gone; source went from 3,573 to 3,486 lines. The cost-attribute change introduced F3-01.
- **F2-05.** Fixed. One day, no `immutable`.
- **F2-06.** Fixed. Three jobs finish in about two minutes; the deep run is one job on push.
- **F2-07.** Fixed. Checkout-only tests skip in the sdist, CI runs the unpacked suite, METADATA has no relative link.

## Round-2 findings, the other reviewer's

- **A2-01.** Fixed. Nonprofit with 20 licensed accounts and 1 or 19 assigned seats: four areas Unknown and off the Ready list; the consistent sample still gives Ready. Town with zero assignments or 120 licensed accounts: Licences Unknown.
- **A2-02.** Fixed. One clean account out of 85 no longer removes the Blocker; a partial positive against a supplied No gives Unknown.
- **A2-03.** Fixed. With the rule edited as described, Small apps and Integrations are both Unknown; the consistent control gives Ready.
- **A2-04.** Fixed. Desktop need is Unknown with both facts stated, in both profiles.
- **A2-05, A2-07.** Fixed, as F2-02 and F2-07.
- **A2-06.** Fixed for headings: only the hero waits, and print has all 13. Tiles still fade in on scroll, by design (R-43).
- **A2-08.** Fixed. README, CONTRIBUTING, `PROJECT.md:71` and the site give one account.
- **A-07.** Fixed. A file name with an at sign is printed as "the scan file" or "the inputs file".
- **A-09.** Fixed. 40 of 31 teams at `09:00Z` and `10:00+01:00` is rejected.
- **A-13.** Fixed. With the English label for `sample.directory` removed, the demo prints one sentence and exits 2.

## New findings

| ID | Sev | Area | Where | What is wrong | How I checked | Fix |
|---|---|---|---|---|---|---|
| F3-01 | medium | Messages | `src/fazit/i18n.py:76-80`; `src/fazit/inputs.py:45`, `src/fazit/validation.py:61-64` | A regression from the second lean pass: counts and training days have no upper bound, and the new cent formatter converts the whole amount to text, so a `users` value of 4,300 digits or `training_days_per_person` of 4,400 digits ends in a Python traceback and exit 1 without `--debug`. Both cases passed my fuzzer in rounds 1 and 2. | Inputs fuzzer: 2 of 1,500 cases; `fazit report` reproduces `ValueError: Exceeds the limit (4300 digits)` at `i18n.py:80`. | Cap counts and days in `inputs.py` (nine digits and three would do) so the field error names them. Add both cases to the tests. |
| F3-02 | medium | Site copy | `site/start/index.html:103`, `site/de/start/index.html:103`; `site/pilots/index.html:62` | The new Get started page says import "comes next" and "until then, the founding pilots are the way to assess your own organisation". The pilots page says pilot assessments start once import is available, and the home timeline puts two steps before import. A visitor is sent in a circle. | Extracted the text of the three pages. | "Importing exports follows after the next two steps; pilots begin with it." in both languages. |
| F3-03 | low | Licensing | `site/icons/linkedin.svg`, `site/icons/LICENSE`, `DESIGN.md:35` | The LinkedIn mark is not a Material Symbol but sits under the folder's Apache-2.0 LICENSE, with no source recorded. REUSE is planned (DIST-04). | Read the file and `git log`; the path looks like the Simple Icons glyph. | Record source and licence beside it. |

## Founder actions and decisions

- **R-35.** Claim `fazit.dev` and the PyPI name before any announcement. The repository is public and already names both.
- **R-36.** Before announcing: settle the host (`_headers` is written for Cloudflare Pages, the privacy page names bunny.net), then check live headers and the hosting statements.
- **R-40.** `HANDOFF.md:1` still says "The tool is now called Befund", and `.claude/CLAUDE.md` still has four placeholder sections.
- **R-37, R-38, R-43.** Can stay as they are.
- **Report redesign.** Out of scope; keep the offline and contrast checks when it rewrites `tests/test_report.py`.

Where I differ from the other reviewer on a founder-only question: I would correct the Befund line in `HANDOFF.md` before the announcement, not defer it; it names a product name dropped over a trademark conflict.

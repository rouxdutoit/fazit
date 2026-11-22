# Fazit release review 2 (reviewer: Claude Fable 5.2)

Commit `1099e49`, checked in the private clone on 2026-11-22. The public `main` has moved on again; I looked at it only to see whether F2-01 is still there.

## Verdict

**Release after fixes.** Two issues at the level "would embarrass us in public" remain at this commit: the domain and the PyPI name are still unclaimed (R-35), and the home page draws a giant chevron over its hero in Firefox and for anyone with reduced motion (F2-01, already corrected on the public `main` after this commit, so it only needs to land and be checked).

Remaining: 0 critical, 2 high, 9 medium, 3 low.

Ran: `uv sync`, both Ruff checks, `pytest -q` (693 passed, 124 s), the deep simulation (6 passed, 920 s), both demos, `site/check_site.py`, `uv build`, my 5,048 malformed-file cases from round 1 (no traceback), 26 hand-made scan and input variants for the judgement fixes, path probes, the site in headless Chromium 151 and Firefox 153 under its declared headers, RDAP and PyPI lookups, and the GitHub API for the CI run of this commit.

## My round-1 findings

| ID | Status | Evidence |
|---|---|---|
| F-01 | Not fixed (R-35) | RDAP 404 for `fazit.dev`, PyPI 404 for `fazit`, repo public. `pyproject.toml` now also publishes `Homepage = https://fazit.dev`. |
| F-02 | Fixed | `DECISIONS.md:12,83`, `AGENTS.md:36`, `SECURITY.md:20` and both security pages say embedded fonts; the font test now agrees with the principle. |
| F-03 | Partly fixed | Chromium under the `_headers` rules: no console error on ten routes; `check_site.py` now checks both policies. The hosting half stays open (R-36). |
| F-04 | Fixed | `README.md:7,73`, the audience cards and "Now" say measured figures come from the samples until import. |
| F-05 | Not fixed | `HANDOFF.md:1` still says "now called Befund"; `STATE.md` still 0%; `PROJECT.md:80-81,86` and 64 "Pending" rows unchanged; `CLAUDE.md` placeholders remain. R-30 was listed for batch 4 and not done. The README now links into `.planning/` twice (`README.md:75,95`). |
| F-06 | Fixed for print | Chromium print-to-PDF contains all 13 headings. The effect itself stays (R-43). |
| F-07 | Fixed | `de.yaml:157` "Direkte Übernahme nicht belegt"; path heading names the status; READMEs aligned; test added. |
| F-08 | Fixed | Measured 0 against supplied 271 now gives Unknown with "The measurement and the supplied answer disagree". Covered by an integration test and the simulation. |
| F-09 | Open (R-38) | Unchanged. |
| F-10 | Fixed | `README.md:95`, `CONTRIBUTING.md:44` and the site give one account. `.planning/PROJECT.md:71` still gives the old one and says the founder cannot audit every line, next to the site's "human-reviewed". |
| F-11 | Open (R-39) | `DECISIONS.md:49` unchanged. |
| F-12 | Fixed | Wheel metadata has README, URLs, author, classifiers and three licence files; sdist is 74 files, 283 kB (was 1.7 MB); test checks the licence files. |
| F-13 | Open (R-37) | Unchanged; `cli.py:37-42` now subclasses a Typer internal to fix its usage line. |
| F-14 | Fixed | `rules.py` is 28 lines; `status.py`, `licences.py`, `mappings.py`, `evidence.py`, `validation.py` each have one job; `_evaluate_workload` is 37 lines. Reports are byte-identical. Total source grew from 3,290 to 3,573 lines. |
| F-15 | Not yet (batch 6) | Suite is now 693 tests in 124 s (was 586 in 57 s). |
| F-16 | Fixed | CI run for this commit: all four jobs green, including `windows-latest` and `macos-latest`. publiccode says `development`. |
| F-17 | Fixed | Generated report carries no design comment; test added. |
| F-18 | Fixed | Documented in `README.md:29` and `SECURITY.md:26`; mode tested. |
| F-19 | Partly fixed | `--debug` alone shows help and exits 2, usage says `SCAN_JSON`, unreadable files get the localised sentence, `python -m fazit` works. Positions remain, see F2-03. |
| F-20 | Fixed | `check_site.py` compares the coverage table with the mappings and the tally with the demo; sitemap has 14 routes. |
| F-21 | Fixed | `AGENTS.md:60-65`, `CONTRIBUTING.md:13-16`. |

## New findings

| ID | Sev | Area | Where | What is wrong | How I checked | Fix |
|---|---|---|---|---|---|---|
| F2-01 | high | Site | `site/style.css:1263-1276`; `site/index.html:62`, `site/de/index.html:62` | The arrow in the preview card's title bar is `position: static`, so its absolutely placed chevron attaches to an ancestor. Firefox: a black shape over the card bar and file name, and a smudge on the preview. With reduced motion: a chevron the size of the first screen over the hero text. Chromium default: the chevron fills the card until the image paints. Introduced in `3dab9ac`; 693 tests and the site check passed. | Headless Firefox 153 on the unmodified site; Chromium 151 with `--force-prefers-reduced-motion` at 1280 and 390 px; with `position: relative` it disappears. Public `main` at `0aacfa7` already has `position: relative`. | Land the upstream fix. Before launch, look at both home pages in Firefox and with reduced motion, light and dark. |
| F2-02 | medium | Messages | `src/fazit/parsing.py:293-295` | Values PyYAML rejects while constructing them are reported as "YAML syntax on line 1" wherever they are. `as_of: 2026-02-30` on line 4 gives "Check the YAML syntax on line 1 of inputs.yaml." The wrong line is worse than none, and it is not a syntax error. | Ran it; the quoted form gives the correct "Check the value of as_of". | Check the calendar date on the node, where the line is known; give other constructor errors no line. Add the case to the tests. |
| F2-03 | medium | Messages | `src/fazit/inputs.py:110-117`, `src/fazit/parsing.py:63-73` | R-11 is half done. The likeliest mistake, a misspelt key, still reads "Remove the unrecognised field $[0] from inputs.yaml" or `target_costs.full_exit[0]`; at signs read `$[0][1][0]`. The batch summary says unknown keys are identified by line. | Ran ten cases. | The node walk already knows each key's line: say "line N". |
| F2-04 | medium | Lean | see below | The refactor kept behaviour byte-identical, and that constraint produced the code that now reads most like machine output. | Read every changed module. | Listed below. |
| F2-05 | low | Site | `site/_headers:8-12`, `site/.htaccess:21-23` | Fonts and icons get `max-age` one year with `immutable`, but their names carry no version. `geist-mono-latin.woff2` was already replaced under the same name in `608a410`. | Served the rules; `git log`. | Hash the names or drop `immutable`. |
| F2-06 | low | CI | `.github/workflows/ci.yml:39` | The 300-example simulation runs on every push on four runners: 4 to 16 minutes each, 18 minutes for this commit. The profile is derandomised, so every run repeats the same examples. | GitHub API job timings. | Per push keep the 18-example profile; run the deep one nightly, not derandomised. |
| F2-07 | low | Packaging | `pyproject.toml:40-56` | The sdist ships `tests/`, which fail outside a checkout (`git show` exits 128; others need `site/` and `.github/`). Seven relative README links will be dead on PyPI. | Unpacked the sdist and ran the tests; read METADATA. | Drop tests from the sdist or skip without git; absolute links. |

What still reads like LLM output (F2-04):

- `costs.py:25,34,45,56,72,154` and `report.py:143-153`: an `input_exponent` threaded through three dataclasses and a hand-built Decimal context, only so `data-amount` attributes keep the digits the old code produced. Nobody but tests reads them. Emit cents.
- `parsing.py:201-213`: a hand-written YAML 1.1 float parser with base-60, plus a check kept to mimic a quirk of the code it replaced ("the previous scalar check rejected…").
- `parsing.py:107-138` and `216-246`: a second JSON tokenizer and a second YAML event walk, to add a field name to syntax errors. The line number is enough. `parsing.py` doubled to 295 lines.
- `parsing.py:189-195`: strict scalar spelling is switched on by passing `integer_fields`.
- `i18n.py:36-43`: the message is chosen by appending `_option`, `_field` or `_document` to the code.
- `inputs.py:122-125`: two consecutive `if` blocks with the same failure.
- `model.py:72-85`: the sub-microsecond comparison is still there.
- `status.py:258-264`: the generic engine special-cases one finding id suffix.
- `catalogue.py:215-232`: both locales are loaded and deep-copied on every run to validate labels.

The structure is now what an experienced developer would choose. The volume is not: the fixes and the lean batch together added 283 source lines and 1,571 test lines.

## Open items R-35 to R-43

- **R-35.** Must be done before any announcement. It is the one blocker that still needs an action.
- **R-36.** Agree it can only be verified after deployment, but it is a launch gate. `_headers` now uses Cloudflare Pages syntax (`! Content-Security-Policy`) while the privacy page names bunny.net; settle the host, delete the unused file, and check with `curl -I` before announcing.
- **R-37.** Agree, can stay open.
- **R-38.** Agree, can stay open.
- **R-39.** Disagree in part: fine for the announcement, but verify or delete before the funding application goes in.
- **R-40.** Disagree in part: whether `.planning/` stays public is the founder's call, but the "now called Befund" line and `STATE.md` should be corrected before the announcement. Ten minutes.
- **R-41.** Confirmed, can stay open. An attacker needs write access to an ancestor of `--out`, and gains only the placement of three files with fixed names, mode 0600 and no attacker content. Say in `SECURITY.md` not to use a directory others can write to.
- **R-42.** Confirmed, can stay open. Each file is whole, the run exits 2, and all three are deterministic copies of the same sample.
- **R-43.** Agree, can stay open; print is fixed.

## Ideas

- **I-1.** Agree, 1.2. It is the page decision-makers read and integrators paste.
- **I-2.** Agree, 1.1, ideally before the announcement. It is the only way to use Fazit for a real organisation before import.
- **I-3.** Agree, 2, when pilots start. The cheapest test of "a council IT officer can read and trust it".
- **I-4.** Agree, 2, with licence import. Without it real tenants turn six areas Unknown.
- **I-5.** Agree, 1.1. It belongs with the renewal date and decision window.
- **I-6.** Agree, 4. REUSE can be done now; listing fits the first tagged release.
- **New.** Label stale evidence: mapping checks and answers older than a set age relative to the scan date. Phase 1.3, with the dated criteria mapping. A report rebuilt a year later should not present a 2026 check as current.

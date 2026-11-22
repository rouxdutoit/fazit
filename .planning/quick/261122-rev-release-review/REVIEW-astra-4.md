# Fazit release review 4 · `0ae2be2`

**Hold release because contradictory evidence still produces pilot recommendations and a telephony Blocker.** Site issues are minor, and the founder must verify name ownership and hosting before announcement.

Both Ruff checks, 705 tests, six deep simulations, both demos and the site check (18 pages, 610 references) passed. The wheel built. The unpacked source passed 701 tests with four checkout-only skips. Fresh demos matched both downloads byte-for-byte and opened offline in Chromium and Firefox at 360 px in both themes with embedded fonts and zero HTTP requests. Only the status checksum changed across 12 variants. [Checklist](tmp/r4/checks/checklist.log)

## New findings

- **A4-01 (critical).** Zero internal accounts, zero guests, 20 licensed accounts and 20 assignments yielded five licence-dependent pilots. A headcount of 20 from 0/0 checked also passed. [CLI cases](tmp/r4/checks/licences.log)
- **A4-02 (high).** Removing the times from two snapshots one second apart restored all five pilots. `model.py:68` treats matching calendar dates as the same instant. [CLI comparison](tmp/r4/checks/observations.log)
- **A4-03 (high).** All 85 phone checks failed, yet a measured Yes produced Blocker and transfer need Yes in both languages. There was no assigned add-on, interview confirmation of use or replacement. [CLI results](tmp/r4/checks/zero-observations.log)
- **A4-04 (low).** Both start cards invite readers to use Fazit in their own assessments. Their destination defers this until import. [Extracted copy](tmp/r4/checks/observations.log)
- **A4-05 (low).** Both browsers replayed the wordmark after internal navigation. The referrer policy hides the previous page. [Browser results](tmp/r4/checks/browser.log)

## Round-3 findings

- **A3-01 (fixed).** Twenty assignments with zero licensed accounts withheld five pilots. 125 two-product cases matched independently enumerated allocations.
- **A3-02 (partly fixed).** Denied, missing, partial and mistimed headcounts withheld pilots while preserving positive assignments. See A4-02.
- **A3-03 (fixed).** Use measured in 1/85 gave Blocker without a replacement, Needs work with one, and transfer need Yes. Conflicts gave Unknown.
- **A3-04 (fixed).** PowerShell 6.2.7 parsed each clipboard result as three commands.
- **A3-05 (fixed).** README and homepage timelines place packaging after import in both languages.
- **F3-01 (fixed).** 4,300-digit users and 4,400-digit training days returned one localised field error and exit 2. JSON boundaries passed.
- **F3-02 (fixed).** Both languages distinguish immediate registration from post-import assessments.
- **F3-03 (fixed).** `git show 3510b87` records Simple Icons 10.4.0, CC0 and LinkedIn’s trademark.
- **A2-01 (fixed).** One assignment for 20 licensed accounts withheld all five pilots.
- **A2-02 (fixed).** One negative observation left interview-confirmed telephony use a Blocker.
- **A-20 (partly fixed, low).** Bilingual `publiccode.yml` still places import after 1.3 and packaging in phase 4.
- **F-05 (partly fixed, low).** PROJECT and ROADMAP record completion. STATE reports both 11 plans completed and zero.
- **F2-06 (fixed to plan).** CI specifies one deterministic Ubuntu 3.12 deep run per push. Randomised nightlies remain a proposal.
- **A-14/R-41 (not fixed, medium, deferred).** `git diff` confirmed unchanged pathname-based writes through a replaceable ancestor.
- **A-15/R-42 (not fixed, medium, deferred).** Failing the second replacement left a new demo scan alongside old answers and HTML.

**Code/site totals including documentation** · 1 critical, 2 high, 2 medium, 4 low.

## Founder actions and decisions

- **F-01/R-35 (not fixed on available evidence).** Cached domain and PyPI responses were 404. Current control remains unverified.
- **F-03/A-12/R-36 (partly fixed).** Local headers allowed embedded fonts. Verify production headers, Frankfurt storage, European delivery, IP shortening, three-day deletion and the data-processing agreement.
- **F-09/R-38 (not fixed, accepted).** Generated reports retain Ready.
- **F-13/R-37 (not fixed, accepted).** `uv tree --no-dev` confirms Typer.
- **R-40 (partly fixed).** HANDOFF names Fazit. Tracked Claude placeholders and folder visibility remain open.
- **R-43 (fixed for headings).** Screen and print checks found visible headings. Wordmark motion remains.

# Fazit release review 5, final (reviewer: Claude Fable 5.2)

Commit `acf9be9`, 2026-11-22.

## Verdict

**Release as is.** Nothing in code or site would embarrass the project in public: CI is green on all four jobs, and D31 does what it says. Two medium points should be settled before import is built.

Remaining code and site findings, excluding deferrals R-41 and R-42: 0 critical, 0 high, 2 medium, 4 low.

Ran: both Ruff checks, `pytest -q` (722 passed, also with pure-Python `decimal`), the deep simulation, 12 demos, `site/check_site.py`, `uv build`, 5,048 malformed files, 17 site routes: no problem.

## Round-4 findings

- **F4-01.** Fixed. Eight oversized values give one sentence and exit 2 on both `decimal` implementations; CI is green.
- **A4-01, A4-02, A4-03.** Fixed. Each replay is refused with one sentence naming the field.
- **A4-05.** Fixed. Internal navigation no longer replays the wordmark.
- **A3-05, F-05.** `publiccode.yml` (both languages) and the STATE count are fixed. Not in this clone: `site/integrators/index.html:60` and its German twin.
- **F4-02.** Partly. `SECURITY.md:24` is reworded; `site/security/index.html:121` and its German twin are unchanged; the example still loads (F5-02).
- **F4-03, A4-04.** Not in this clone: `site/de/index.html:144`; line 122 of both start pages.

## D31

22 single violations of its lines are each refused. Of 1,800 random directory and licence scans, all 690 my own oracle calls impossible were refused, no possible one was, and licence pilots appeared exactly when counts reconcile. No scan field reaches the cost comparison.

- **F5-01 · medium · `src/fazit/model.py:517`.** D31 refuses a truthful tenant: 25 assigned of 20 purchased seats ends in exit 2. Microsoft Learn describes that state for volume-licensing customers, who get 90 days to resolve "assigned licenses in excess of the purchased quantity". Drop the rule and show the excess as evidence.
- **F5-02 · medium · `src/fazit/model.py:129-146`.** Evidence is compared only when stamps or periods are identical, and nothing requires one source to use one stamp. 19 internal accounts and no guests, one second before 20 licensed accounts: loads, Directory Ready, eight pilots. Guests checked in 30 of 30 teams against 31 teams, period one day shorter: loads, Teams Ready, where the honest 30 of 31 is Unknown. Ten devices with 20 on Windows, same interview and date: loads. A live collector that stamps each request would switch these checks off and never reconcile licences. Require one collection time and period per collector and source, and compare answers by source and date.

Accepted without effect: no teams with 109 channels, no mailboxes with 504,210 items.

## Founder

- **R-35, R-36.** Open, and needed before any announcement: RDAP 404 and no DNS for `fazit.dev`, PyPI 404 for `fazit`; live headers unchecked.
- **Before phase 2.** The planned exports hold no licensed headcount, so an import-only scan leaves Licences, Power Platform, Telephony, Identity and Security Unknown (nonprofit sample without directory evidence).
- **Disagreement.** If the other reviewer holds the release for scans edited to dodge a comparison, I would not: `SECURITY.md` already says a self-consistent fabrication passes.

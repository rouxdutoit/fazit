---
quick_id: 261123-rv16
slug: monotone-directory
date: 2026-11-23
status: complete
---

# Quick task: Directory Ready from a positive licence check, and two corrections

Round 10 (`.planning/quick/261122-rev-release-review/REVIEW-astra-10.md`, `REVIEW-fable-10.md`). The rv15 plan asked for "no Directory Ready beside a flagged conflict". That is a negative rule, and weaker licence evidence slips past it: on the bundled nonprofit sample, skipping the licence collector and then making the licensed count partial turns Directory from Unknown into Ready (Fable F10-01: 191 such steps in a two-step search). This breaks principle 8. Two other rv15 instructions were also wrong and are corrected here. Each item is a test that fails first.

1. **Positive rule (both reviewers, high).** Directory is Ready only when, in addition to the complete declared population, the licence check has positively passed: a complete licence inventory and a complete licensed count, from the same instant, that reconcile. Anything less (no licence collector, a skipped, denied or partial collector, partial or unknown inventory coverage, a missing, partial, denied or unknown licensed count, a conflict) leaves Directory Unknown with the existing reasons. The rule must be monotone: removing or degrading any evidence, including dropping the licence collector entirely, never makes Directory more ready. The existing test that expects Ready with `licences: null` encodes the defect; change it and say so.
2. **Simulation covers Directory.** `tests/tenants.py` declares a `directory_population` in some generated tenants, consistent with their counts, so `test_worse_collection_never_improves_status` reaches Directory Ready and would have caught F10-01. Add Fable's nonprofit two-step case as an explicit example.
3. **Census bound, corrected (Astra).** Measured internal and guest counts from one census fit within its successful checks, not within the successful checks plus unchecked rows (the rv15 plan said the latter, which was wrong). Unchecked rows only widen the upper bound on the population. Cases: one successful row and one unattempted row cannot yield one member and one guest; the only successful row cannot yield zero members, zero guests and one licensed account. Keep the exhaustive oracle, and every truthful roster must still load.
4. **Date-only scan reference (both, low).** A date-only scan or collection reference names a day that lasts until 24:00 at UTC-12, the latest zone; a date-only evidence day begins at 00:00 at UTC+14. Evidence is valid when its earliest start is not after the reference's latest end. Case: a scan dated only 4 November accepts an interview stamped 20:00-05:00 on 4 November. Update D31 and `docs/scan-format.md`.

## Done means

The "Done means" list in `AGENTS.md`, the deep simulation profile, `uv run python site/check_site.py`, the truthful-tenant property loading every generated truthful scan, and the samples keeping their statuses.

---
quick_id: 261123-rv14
slug: directory
date: 2026-11-23
status: complete
---

# Quick task: apply the declared-population rule to the directory itself

Round 8 (`.planning/quick/261122-rev-release-review/REVIEW-astra-8.md`, `REVIEW-fable-8.md`). rv13's rule (refuse only what the scan declares impossible, infer only from what it declares consistent) holds for licence areas but not yet for the Directory area, and the UTC date rule refuses some truthful scans.

## Items (each a test that fails first)

1. **Directory Ready needs a complete declared population (both reviewers).** An absence in the directory ("there are no guest accounts", no unlicensed accounts) may establish Ready only from a declared, completely covered population. Astra's case: a departmental export checks one member of a tenant with one member and one guest; without a declaration Directory must not be Ready and must not say there are no guests. Fable's: undeclared, no internal accounts, no guests, 20 licensed accounts at one instant must not give Ready. Change the rule data in `status.yaml` if it can express this; otherwise the smallest engine change.
2. **Counts within a declared coverage (Fable F8-01).** Inside a partly checked declaration, a count marked complete, or a count above the declaration's successful checks, is refused (21 rows declared, none checked, 21 failed, 21 internal accounts marked complete).
3. **Inherit the declared total (Astra).** A complete count that omits its own coverage total uses the declared total for the completeness check instead of refusing the scan (two accounts declared once; complete licensed count with two successes and zero failures and no total).
4. **Date-only evidence (Fable, low; 6 of 900 truthful tenants refused).** A date without a time cannot be placed more exactly than the time zones of the world allow. Accept date-only evidence and period ends up to the scan's UTC calendar date plus one day, so no truthful scan is refused and one instant still gives one answer; evidence later than that stays refused. Record the rule in D31.

## Done means

The "Done means" list in `AGENTS.md`, the deep simulation profile, `uv run python site/check_site.py`, and a truthful-tenant property (declared, undeclared and filtered lists, generated independently) in which no scan is refused.

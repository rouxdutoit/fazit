---
created: 2026-11-23
source: release review round 5, F5-02 (Claude Fable 5.2); requirement MODL-05, phase 2
severity: medium
area: scan format
---

# One collection time and period per collector and source

Comparisons between observations are skipped when their stamps or periods differ, and nothing requires one source to use one stamp; mixed dates and periods still load. The planned admin-centre exports carry no licensed headcount, so licence areas stay Unknown after import. Tracked as MODL-05 for phase 2; settle before import is built.

## Done

2026-11-23. The scan loader enforces one stamp and period per collector and source pair. Linked interview counts from the same source and day are comparable. The Phase 2 plan identifies the Microsoft 365 apps Active users export as the headcount source. A model regression verifies that its date-only count can coexist with a directory snapshot and leaves licence reconciliation Unknown.

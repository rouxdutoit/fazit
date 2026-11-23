---
created: 2026-11-23
source: release review round 11, Codex GPT-6.2-Astra
severity: medium
area: scan consistency (D31)
---

# OneDrive Ready from an empty account export with one successful storage check

OneDrive is Ready when an export that confirms zero accounts reports one successful account check for storage. Add the invariant to D31 and the loader: checks of storage in an export cannot exceed the accounts that export confirms.

## Done

2026-11-23. D31 and the loader bound OneDrive storage coverage by the possible account population in the same export. The CLI tests reject excess checks and totals and accept a complete empty export with zero checks.

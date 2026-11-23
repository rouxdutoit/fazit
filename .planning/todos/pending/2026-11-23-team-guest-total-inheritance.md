---
created: 2026-11-23
source: release review round 11, Codex GPT-6.2-Astra
severity: low
area: scan consistency (D31)
---

# A truthful team guest check is refused when its total is omitted

A 31-team guest check with 31 successes and zero failures is refused if its coverage total is omitted. Inherit the team count as the total, as rv14 does for the declared directory population.

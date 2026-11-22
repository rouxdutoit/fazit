---
quick_id: 261122-rv10
slug: consistency
date: 2026-11-22
status: complete
---

# Quick task: reject impossible scans in one place

Round 4 of the release review (`.planning/quick/261122-rev-release-review/REVIEW-astra-4.md`) again found scans whose evidence contradicts itself and still produces pilots or a Blocker: A4-01 (20 licensed accounts in a directory with zero internal accounts and zero guests; a headcount of 20 from 0 of 0 checked), A4-02 (date-only timestamps one second apart treated as the same instant), A4-03 (a measured "telephony in use: yes" when all 85 checks failed). Each round has found the next such case. Stop that with one audit, not three patches.

## Items

1. **Write down the invariants.** List every cross-field invariant a truthful `scan.json` 1.x satisfies: a count fits within its coverage's scanned items and its stated population; a subset fits within its population (licensed accounts within internal accounts plus guests, guests within accounts, teams with guests within teams, and every other pair the catalogue defines); a measured value needs at least one successfully scanned item (a positive boolean or a positive count cannot come from zero scanned); assigned seats within purchased; licence rows within coverage; observation times that must be compared carry a time, not just a date. Put the list in `DECISIONS.md` as decision D31, one line each, so a reader can check them.
2. **Enforce them at load, in one place.** `model.py` (or the validation module) rejects a scan that breaks any invariant, with the existing one-sentence error naming the file and field. Rules and report then never see an impossible scan. Remove special cases in `licences.py`, `evidence.py` and `status.py` that the load-time checks make unnecessary, but keep the reconciliation rule from batch rv9 for scans that are possible but disagree (for example a missing or mistimed headcount).
3. **Times.** Observations compared for the same instant need full timestamps; a date-only value can never establish that two observations are simultaneous. Decide whether date-only timestamps are still accepted at all for measured evidence, and record the decision in D31.
4. **Generator.** `tests/tenants.py` generates only scans that satisfy the invariants, and a new property in `tests/test_simulation.py` generates scans that break exactly one invariant and asserts the load fails with a field error. Reproduce A4-01, A4-02 and A4-03 as explicit cases.
5. **Records.** `publiccode.yml` (both languages) puts the roadmap in the order of `.planning/ROADMAP.md`: report redesign and import (phase 2) next, packaging (phase 2.1), then 1.1 to 1.3. `.planning/STATE.md`'s velocity table shows 11 completed plans, not 0.

## Done means

```
uv run ruff check .
uv run ruff format --check .
uv run pytest -q
uv run pytest -q tests/test_simulation.py --hypothesis-profile=deep
uv run fazit demo --lang de
uv run fazit demo --lang en
uv run python site/check_site.py
```

Both samples must still load. If they break an invariant, fix the sample data, not the invariant, and say what changed. Suggest one commit per item; mark user-visible changes.

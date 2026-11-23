---
quick_id: 261123-rv13
slug: declared-population
date: 2026-11-23
status: proposed
---

# Quick task: decide from declared populations only

Round 7 (`.planning/quick/261122-rev-release-review/REVIEW-astra-7.md`, `REVIEW-fable-7.md`). Five rounds of bound arithmetic each closed one directory case and opened another, and rv12 began refusing truthful scans (36 of 729 filtered scans). Both reviewers trace the remaining cases to one cause: the loader infers that two counts share a population from matching totals, instead of the scan declaring it.

## Principle

Refuse a scan only when it is impossible from what it declares. Infer from a scan only when it is consistent from what it declares. Everything in between stays Unknown, with a reason. This is principle 8 applied to the loader.

## Items

1. **Declared directory population.** `scan.json` 1.x gains (or uses, if one exists) an explicit directory population: one total for internal accounts and guests, from one collector and instant. Bounds between internal accounts, guests and licensed accounts use only that declared total. Matching list sizes never imply a shared population.
2. **Refuse less.** Remove load-time refusals that depend on an inferred population. A scan that is not provably impossible loads.
3. **Infer less.** Licence reconciliation and every pilot or absence that rests on it require the declared population with complete coverage. Without it, the affected areas stay Unknown with the existing reason.
4. **Partial inventories.** Products with a missing SKU or plan GUID in a partial inventory load as unclassified with their seat counts, instead of refusing the scan.
5. **Dated evidence across time zones.** Compare a dated period with the collection instant in one time scale, so one instant gives one answer.
6. **Tests.** The exhaustive directory oracle runs over declared and undeclared populations; a property asserts that no truthful scan (from an independent generator) is refused and that no undeclared population produces Ready.

D31 is updated to match. Samples and demos must still load and render.

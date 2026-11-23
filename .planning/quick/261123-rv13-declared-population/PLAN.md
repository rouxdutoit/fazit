---
quick_id: 261123-rv13
slug: declared-population
date: 2026-11-23
status: complete
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

## Acceptance cases (each a test that fails before the change)

- Astra round 7, critical: Fable's 19-of-20 census with the guest coverage total omitted, 21 licensed accounts and 21 assignments: the four areas stay Unknown (not Ready).
- Astra round 7: 11 internal users plus ten guests in a complete 20-row census is refused only if the scan declares that 20-row population; otherwise it loads and the affected areas stay Unknown.
- Astra round 7, high (regression from rv12): two complete filtered lists of ten internal users and ten guests with eleven licensed accounts load. Generate truthful filtered scans independently (Astra found 36 of 729 refused) and assert none is refused.
- Fable round 7, F7-01: no internal accounts in 19 of 20 rows and 19 guests in 19 of 21 rows with 22 licensed accounts gives no pilot; 20 internal and 20 guests each fully checked with 25 licensed accounts loads unless a shared population is declared.
- Astra round 7: partial inventories with an absent SKU GUID (53 products) or absent plan GUIDs (29) load as unclassified with their seat counts.
- Both: a period ending 2 November collected at 00:30+01:00 and the same instant written as 23:30Z give the same answer.

D31 is updated to match. Samples and demos must still load and render.

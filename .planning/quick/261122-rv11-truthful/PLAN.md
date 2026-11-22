---
quick_id: 261122-rv11
slug: truthful
date: 2026-11-22
status: complete
---

# Quick task: accept every truthful tenant, reject the remaining impossible ones

Round 5 of the release review (`.planning/quick/261122-rev-release-review/REVIEW-astra-5.md`, `REVIEW-fable-5.md`). D31 (batch rv10) now refuses two states a real tenant can be in. That is the worst kind of defect for this tool and comes first. Then close the unambiguous impossible cases. Do not start the structural change F5-02 (one collection time per collector and source); it is recorded for phase 2.

## Items

1. **Truthful tenants must load (both reviewers, medium).**
   - Assigned seats above purchased seats are real (Microsoft documents it for volume-licensing customers after a subscription expires: "assigned licenses in excess of the purchased quantity"). Drop that D31 rule; show the excess as licence evidence with a reason, and let it count as assigned use.
   - Microsoft lists two SKU GUIDs under the part number `MCOPSTN5`. Uniqueness is by GUID; the same part number with two registered GUIDs loads.
   - Update D31 in `DECISIONS.md` accordingly. Test both through the CLI.
2. **Evidence from the future (Astra, high).** Provided evidence, its date and its reporting period, cannot lie after the scan's generation time; an undated interview cannot cover a period that ends after it. Reject with a field error.
3. **Local times (Astra, high).** Measured snapshots carry an explicit UTC offset or `Z`; a clock time without an offset is a field error, because local times repeat at the end of daylight saving time.
4. **Impossible content from zero (Astra, high; Fable).** From the same export and period: storage or items above zero with zero accounts (OneDrive, mail), channels with zero teams. Add these to D31 and the loader.
5. **Coverage arithmetic (Astra, critical A4-01 rest).** The account bound uses the checked rows correctly: with 19 of 20 rows checked, zero internal accounts and 19 guests, at most 20 accounts exist, so 21 licensed accounts is refused.
6. **Generator.** Extend the one-violation property in `tests/test_simulation.py` to items 2 to 5, and add a truthful-tenant property: scans with excess assignments and with duplicate part numbers must load.

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

The sample scans must still load; if their timestamps lack an offset, add `Z` or the right offset and say so. Suggest one commit per item; mark user-visible changes.

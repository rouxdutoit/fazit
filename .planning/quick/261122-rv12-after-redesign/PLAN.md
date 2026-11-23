---
quick_id: 261122-rv12
slug: after-redesign
date: 2026-11-22
status: complete
---

# Quick task: round-6 findings, to run after the report redesign lands

From `.planning/quick/261122-rev-release-review/REVIEW-astra-6.md` and `REVIEW-fable-6.md`. Queued because `src/`, `tests/` and `site/demo` belong to the report redesign until it is on `main`. Rebase on the redesigned code first; line numbers will have moved.

## Items

1. **Account bound from first principles (A4-01 rest, critical per Astra).** Derive the upper bound on accounts from the coverage fields once: internal accounts can be at most the measured internal count plus every row that was not successfully checked (failed or unscanned), and the same for guests; licensed accounts fit within the sum of those upper bounds. Case: 20 rows, 19 failed, zero internal measured, one confirmed guest: at most 20 accounts, so 21 licensed is refused. Fable's variant: no internal accounts and 19 guests counted in the same 19 of 20 rows, with 21 licensed accounts; the unchecked row must not be counted twice. Test it with an exhaustive enumeration over small populations against an independent oracle, not with one more example.
2. **Regression: partial inventory with a shared part number.** A truthful partial `MCOPSTN5` inventory with either optional identifier missing loaded at `acf9be9` and fails at `2e4fae1`. It must load again.
3. **Regression: interview dates across time zones.** An undated interview covering 6 November passes at 00:30 CET and fails at the same instant written as 23:30Z on 5 November. Compare the period end with the scan's own local calendar date (or both in UTC, consistently), so one instant gives one answer.
4. **SharePoint from zero sites.** A complete export with zero sites and positive files or bytes is impossible; add it to D31 and the loader, as for mail, OneDrive and Teams.

5. **Published licence names (F6-01, Fable).** 61 of the 620 products in Microsoft's licensing reference are refused because a part number or plan name does not fit the identifier pattern (for example Windows 10/11 Enterprise E3, Microsoft Intune Suite, Microsoft 365 E3 (no Teams)). Accept every product as Microsoft publishes it: widen the pattern to what the reference contains, or drop an unfit name while keeping the GUID, and test against the full reference table.
6. **German plural (Fable, low).** "Es sind 1 Lizenzplätze" when the excess is one; use the singular for one, in both languages if English has the same issue.

## Done means

The "Done means" list in `AGENTS.md`, the deep simulation profile, and `uv run python site/check_site.py`.

# Fazit release review 8, confirmation (reviewer: Claude Fable 5.2)

Commit `a906333`.

## Verdict

**Release as is.** The declared population closes every round-7 case: licence pilots appear only from a declared, completely checked population, and no truthful scan I built is refused for its directory or licence evidence. Two gaps remain in Directory readiness; neither is reachable from the samples.

Remaining code findings, excluding R-41 and R-42: 0 critical, 0 high, 3 medium, 2 low.

Clean in the checkout: both Ruff checks, `pytest -q` (1,002 passed), deep simulation (28 passed), 12 demos, `site/check_site.py` (24 pages, 972 references). The unpacked sdist has only the known palette failure, fixed in `e606ce5`, where public CI is green.

## Round-7 items

- **F7-02.** Fixed in `f348f4d`.
- **A4-01 and F7-01.** Fixed. Astra's census without a guest total stays Unknown at 20 and 21 licensed accounts. 11 internal plus 10 guests is refused when 20 rows are declared and loads undeclared. My totals of 20 and 21 give no pilot. Of 2,500 random scans, the 1,253 impossible under D31 are refused, no possible one is, and licence pilots appear only when declared, complete and reconciled.
- **Filtered lists.** Fixed. Ten internal, ten guests, eleven licensed load.
- **Partial inventories.** Fixed. All 620 products load, seats shown, with the SKU GUID, the plan GUIDs or the part number absent.
- **Dates.** Fixed. Every pair of spellings I tried gives one answer.
- **F5-02.** Deferred as MODL-05 (medium).

## New findings

- **F8-01 · medium · `src/fazit/model.py:514-545`.** A member count is held to the declared total but not to the declared coverage. A declared census of 21 rows with none checked and 21 failed, carrying 21 internal accounts and no guests marked complete, loads with Directory Ready. Refuse a complete count, or one above the successful checks, inside a partly checked declaration.
- **F8-02 · medium · `src/fazit/rules/status.yaml:4-8`.** The plan's property "no undeclared population produces Ready" holds for licence areas only. Undeclared, no internal accounts, no guests and 20 licensed accounts at one instant load with Directory Ready; declared, they are refused. Let Directory Ready need a complete declaration too.
- **Low.** An unpublished code or plan name outside the pattern is still refused.
- **Low.** Dates follow UTC: a scan generated at 00:30 CET refuses evidence dated that local day.

## Founder

R-35: PyPI `fazit` is still unclaimed. R-36: hosting details remain to be confirmed.

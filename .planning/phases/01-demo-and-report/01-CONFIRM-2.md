# Befund second confirmation gate

**Verdict — not ready to make the repository public.** In two fixtures, deleting one row while leaving coverage marked complete changed Telephony from Blocker to Ready.

At HEAD `eb4e925`, I reran `uv run befund report scan.json --inputs inputs.yaml --out out` on copies of the first gate’s fixtures and on variants. Both Ruff checks and all 531 tests passed. The English and German demos opened offline.

- **A02 — resolved.** Three measured integrations with zero supplied gave Needs work. A directory skip with `permission_denied` gave Unknown with the finding present or omitted and named the permission fix. With partial collection and the finding omitted, supplied counts of zero and four gave Unknown and Needs work respectively, both marked incomplete.
- **A03 — resolved.** An empty inventory with `sample.mailbox_usage` and a populated one with `sample.directory` both exited 2 at `licences.source`. With `sample.licences`, Telephony was Unknown. The product count and all 30 licence signals were Unknown with reason `licence_products_missing`. For zero shared mailboxes, mailbox usage exited 2 and the recipient export gave Mail Ready.
- **Unclassified Teams Phone plan — resolved.** The 12-seat `MCOEV` gave Blocker. Replacing its plan with `REVIEW_PLAN` gave Unknown for Telephony and its add-on. The report counted one unclassified plan and requested a catalogue update. Keeping both plans preserved Blocker.
- **H5 — resolved within 01-09.** All 51 `SPE_E3` plan pairs matched the cached Microsoft reference. Restoring `EXCHANGE_S_ENTERPRISE` preserved all 15 statuses, including Teams Ready. Adding an unlisted plan changed only Teams to Unknown on assigned E3 and changed no status on unassigned E3.

## New high findings

For both reproductions, use the town scan and set `telephony.in_use` and `telephony.replacement_available` to `false` under `confirmations`. Run the command above before and after each deletion.

- **High — missing product.** Set licence coverage to complete with `scanned=total=3` and `failed=0`. Delete only the `MCOEV` product. Telephony changes from Blocker to Ready. The report counts two products, claims “3 of 3 scanned” and labels the phone add-on “No” and “Measured”.
- **High — missing plan.** Keep only the 12-seat phone product with complete 1/1 coverage. Change its SKU to `BUSINESS_VOICE_DIRECTROUTING` (`d52db95a-5ecb-46b6-beb0-190ab5cda4a8`) and add `MCOMEETADV` (`3e26ee1f-8a5f-4d52-aee2-b81ce45c8f40`) alongside `MCOEV`. Delete only `MCOEV`. Telephony changes from Blocker to Ready and its add-on reads “No” and “Measured”.

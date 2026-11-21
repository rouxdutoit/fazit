# Befund publication gate

**Verdict — not ready to make the repository public.**

Run `befund report scan.json --inputs inputs.yaml --out out` on fresh `src/befund/demo/town` fixtures at `4e532e4`. For licence cases set both telephony confirmations false. For new measurements copy `generated_at` to `collected_at` and set `missing_reason=null`. All 539 tests passed.

- **Missing product — resolved.** Deleting `MCOEV` from complete 3/3 exited 2 at `licences.coverage` without a report. Omitted counts, understated counts and nonzero failures also exited 2.
- **Missing plan — resolved for matching identifiers.** Deleting `MCOEV` from 12-seat `BUSINESS_VOICE_DIRECTROUTING` changed Blocker to Unknown (`licence_plan_list_incomplete`). Duplicating `MCOMEETADV` preserved Unknown. Removing `EXCHANGE_S_ENTERPRISE` from assigned or unassigned `SPE_E3` also yielded Unknown. [Original fixtures](01-CONFIRM-2.md)

## High findings

- **Wrong organisation.** Pair the untouched town scan with nonprofit inputs. SharePoint becomes Ready for the nonprofit using the town’s 24 sites. Matched files give town Needs work and nonprofit Unknown.
- **Licence identity.** Replace the phone row with null SKU identifiers, zero seats and an empty plan list. Telephony becomes Ready with add-on “No”, “Measured”. With only unassigned E3 (complete 1/1) missing Exchange as above, changing its part number to `MCOEV` restores Ready despite the E3 GUID.
- **Contradictory totals.** Zero every product’s `assigned`. Telephony becomes Ready despite 85 licensed accounts measured simultaneously. Independently, give `teams.teams_with_guests_count` complete 0/0 coverage, zero failures. Teams stays Ready despite 31 inventoried teams.
- **Impossible dates.** Set that guest finding’s period to `2030-12-01/2030-12-31`. Teams stays Ready from a 2026 collection.
- **Collector failure.** Give the `ok` collector `teams_usage` reason `permission_denied`. Teams stays Ready.
- **Conflicting counts.** Measure `integrations.application_count=3` with collector `directory`, source `sample.directory`, three of six scanned. Supply zero dated the same day. Changing only `coverage.kind` from `partial` to `unknown` turns Needs work into Ready.
- **Older answer wins.** Record `small_apps.in_use=true` in a November 2 interview. Supply false dated November 1. The report drops the interview and marks Small applications Ready.
- **Missing list.** Omit `windows_only_software`. Set both `windows_software.*` scan findings to provided zeros, source `inputs_yaml`, `missing_reason=null`. Windows-only software changes from Unknown to Ready.
- **Transfer gap.** Add a partial `telephony` collector (`reason=permission_denied`, `permissions_used=[]`) and complete measured `telephony.in_use=false` from `sample.telephony`. Its mapping says “No”, “Measured” while readiness reports Blocker and cites the denial.
- **Simulated evidence.** Change only `source_kind` to `live`. Teams stays Ready using sample measurements. The simulation banner disappears.

## Phase 2 backlog

- Medium — Unknown-coverage zeros print as exact measured counts alongside the coverage warning.

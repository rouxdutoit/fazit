# Fazit release review 11, final confirmation (reviewer: Claude Fable 5.2)

Commit `9640fe2`.

## Verdict

**Release as is.** F10-01 is fixed at the root: Directory is Ready only after a licence check that passed. Nothing in the code would embarrass the project in public.

Remaining code findings, excluding R-41 and R-42: 0 critical, 0 high, 1 medium, 3 low.

Clean: both Ruff checks, `pytest -q` (1,079 passed), the unpacked sdist (1,073 passed, 6 skipped), deep simulation (31 passed), 12 demos, `site/check_site.py` (24 pages, 969 references), 5,364 malformed files. Public CI is green.

## Round-10 items

- **Directory (F10-01, Astra's high).** Fixed. Any loss of the licence check, a missing collector included, withholds Ready.
- **Census (Astra's medium, my low).** Fixed. The loader and a brute-force roster oracle agree on 2.06 million scans of up to five rows: nothing impossible loads, nothing possible is refused. The oracle finds 144 impossible two-row scans at `b0b213d`.
- **Dates (both).** Fixed, exact to the microsecond.
- **Unpublished identifiers** (low) and **F5-02** (medium, MODL-05) are unchanged.

## Searches

- **Worse collection.** Chains of up to three degradation steps on the samples and 445 generated tenants: 585,971 evaluations, and no step of the project's own kind improves a status.
- **Low, older.** Outside Directory, a failed check blocks an answer only while its collector is listed as skipped or partial. Mark one finding denied under a collector that says ok, or leave the collector out, and the answer gives Ready (Integrations, Telephony). D31 could refuse the first.
- **Low, new.** The Directory card says the scan lacks “Licensed accounts” while listing that count as measured. The licence inventory is what is missing.
- 2,500 random scans agree with D31; 900 truthful tenants load.

## Founder

R-35: PyPI `fazit` is still unclaimed. R-36: hosting details remain unconfirmed.

---
quick_id: 261122-rv1
slug: judgement
date: 2026-11-22
status: planned
---

# Quick task: release review batch 1, judgement

Fix R-01 to R-09 from `.planning/quick/261122-rev-release-review/FINDINGS.md`. The reviewers' reproductions are in `REVIEW-astra-1.md` and `REVIEW-fable-1.md` in the same folder (look up the source IDs). Read principles 5 and 8 and the M0 section of `DECISIONS.md` first: they define what the rules must do.

## Items

1. **R-01 (critical).** Skipping or denying the directory collector must never improve a status. Reproduce A-01 first as a failing test (nonprofit sample, assigned counts zero, directory skipped). Fix at the source of the derived absence findings, not with a special case for one workload. Keep confirmed positive assignments working. Add the shrunk scan as an `@example` on `test_worse_collection_never_improves_status` in `tests/test_simulation.py`, and widen `tests/tenants.py` so the generator can reach "all assignments zero with licensed accounts from the directory" unaided.
2. **R-02 (critical).** When a complete measurement and a complete answer disagree, in either direction, the finding is a conflict: both values and sources are shown, the area is not Ready, no pilot is suggested, and the reason sentence does not credit either source. A partial measured lower bound keeps its current treatment (it can confirm a problem). `tests/test_rules.py` around line 789 currently expects Ready for 0 measured against 7 supplied; that test encodes the defect. Change it to the correct expectation and say so in the summary. Add the conflict case to the simulation generator.
3. **R-03 (high).** Telephony: assigned Teams Phone licences with `telephony.in_use: false` (or measured non-use) must not produce Blocker together with transfer need No. Unused assigned seats point to a licence review (Needs work, with a reason saying so); the no-replacement Blocker needs evidence of use. Cover used, unused and unanswered. Change `tests/test_evidence_cli.py` around line 808 accordingly and say why.
4. **R-04 (high).** Look up disputes by finding ID across workloads, so the desktop OS mapping cannot print a definite No from a count the report marks as disputed. A positive Windows-only count can establish a dependency; ruling one out needs a specific complete answer.
5. **R-05 (high).** In `inputs.yaml`, integer fields (counts, months, whole training days) accept only plain decimal spellings. `030`, `0o30`, `0x1e`, `1_000` and sexagesimal `1:30` are rejected with one sentence that names the file and the field. Check every YAML 1.1 implicit resolver PyYAML applies to scalars in `inputs.yaml` (booleans such as `yes`/`on` for boolean answers too) and decide each explicitly. Test the padded value against the final report total.
6. **R-06 (medium).** A complete, empty licence inventory from a collector that ran (coverage complete, 0 of 0) is a measured product count of zero. Keep "missing list" for absent or incomplete evidence; a contradicting directory count is a conflict.
7. **R-07 (medium).** Reject or flag impossible subsets: a subset count above its population from the same source and period, also when optional coverage counters are omitted; more licence products than the reported scanned count. Follow the existing pattern (load-time error with file and field, or conflict) that fits each case, and say which.
8. **R-08 (medium).** A headline card for a zero with unknown coverage must not look like an exact organisation-wide zero; qualify it the way a partial zero is already qualified.
9. **R-09 (medium).** Validate at load time that every label a rule file references exists in both locales, and report a broken one through the existing localised error path with the rule file and field. No traceback without `--debug`.

## Rules

- Judgement lives in data (`rules/*.yaml`) where it can; code changes only where the engine cannot express the rule.
- Each fix comes with the test that would have caught it. Never weaken a test to pass; where an existing test encodes a defect (items 2 and 3), change it and say so.
- New user-facing strings go into both locales; German is formal, administrative and written as German.
- If the report HTML changes, regenerate `site/demo/en/index.html` and `site/demo/de/index.html` (town sample, opendesk profile; see `check_site.py`) and list what changed visibly.
- Suggest one commit per item (or per pair where they cannot be separated), each marked if it changes user-visible behaviour or wording.

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

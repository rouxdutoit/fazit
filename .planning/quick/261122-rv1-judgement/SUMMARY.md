---
quick_id: 261122-rv1
status: complete
date: 2026-11-22
---

# Judgement review

## Results

- **R-01.** Reproduced both failures on the nonprofit sample before changing the engine. With every assignment at zero, skipping or denying the directory check now keeps the affected areas Unknown. Confirmed positive assignments still appear as measured. The simulation includes the reduced nonprofit case and generates all-zero assignments independently.
- **R-02.** Unequal complete measurements and complete answers appear together with their sources and a neutral conflict reason. The disputed finding cannot determine readiness or put its area on the pilot list. A partial measured minimum can still establish a problem. The integration test that previously expected Ready for zero measured and seven supplied now expects Unknown. The simulation generates disagreements in both directions.
- **R-03.** The telephony blocker requires evidence of use and confirmation that a replacement is unavailable. Confirmed non-use with assigned Teams Phone seats yields Needs work and asks for a licence review. Unanswered use stays Unknown. The transfer tests now expect licence review with confirmed non-use and Unknown for disputed use. The old blocker assertions inferred use from assigned seats.
- **R-04.** The desktop mapping resolves disputes by finding ID across workloads. An undisputed positive count of Windows-only applications without web versions can establish a dependency even with some application answers outstanding. A definite No requires a complete answer about applications, devices and peripherals. A disputed count can keep the desktop need Unknown.
- **R-05.** Integer spellings use decimal digits without signs, leading zeros, prefixes or separators. Boolean answers use true or false, with the existing YAML case variants. Null spellings still leave fields unanswered. ISO calendar dates remain valid, full timestamps are rejected, and decimal amounts and fractional training days use quotes. Non-finite numbers, merge keys, YAML value markers, anchors and aliases are rejected. Ordinary text follows the field schema. In both languages the town report totals EUR 527,800 for the partial exit with `users: 30`. With `users: 030` the command names the inputs file and field in one sentence and writes no report.
- **R-06.** A completed empty licence inventory shows zero measured products. Incomplete empty inventories still report a missing list. A positive directory count conflicts with verified zero assignments, and an unavailable directory cross-check leaves readiness open.
- **R-07.** The scan loader rejects a subset above its population for the same source and period, even when coverage counters are omitted. Counts also have to fit their own stated scope. The loader rejects licence rows above the reported scanned count or total and still requires an exact row count for complete inventory coverage. These errors identify the scan file and field. The directory and licence discrepancy in R-06 is shown in the report as a conflict.
- **R-08.** Headline zeros with unknown coverage now use the same qualifier as partial zeros.
- **R-09.** The catalogue checks workload, finding and unit labels in both locales at load time. A broken reference produces one localised sentence with the rule file and field. The debug path exposes the original error.

## Files changed

- `docs/interview-checklist.de.md` adds the German desktop requirements question.
- `docs/interview-checklist.md` adds the English desktop requirements question.
- `inputs.example.yaml` documents the desktop confirmation and decimal count spellings.
- `site/demo/de/index.html` regenerates the German town report for openDesk with the revised telephony reason, desktop evidence and rule appendix.
- `site/demo/en/index.html` regenerates the English town report for openDesk with the same changes. The inline stylesheet is byte-identical in both languages.
- `src/fazit/catalogue.py` checks referenced labels and units in both locales.
- `src/fazit/demo/nonprofit/scan.json` adds the unanswered desktop finding.
- `src/fazit/demo/town/scan.json` adds the unanswered desktop finding.
- `src/fazit/inputs.py` supplies recognised fields for lexical errors and validates quoted whole training days.
- `src/fazit/locales/de.yaml` adds German desktop, licence reconciliation and validation text.
- `src/fazit/locales/en.yaml` adds the corresponding English text.
- `src/fazit/model.py` checks comparable subset counts and licence coverage bounds.
- `src/fazit/parsing.py` validates input scalar spellings before PyYAML constructs values.
- `src/fazit/report.py` looks up transfer evidence gaps by finding ID and qualifies zeros with incomplete or unknown coverage.
- `src/fazit/rules.py` reconciles licence absence with directory evidence, handles disputed observations and validates the positive count used in mapping rules.
- `src/fazit/rules/findings.yaml` registers the desktop confirmation and the unverified licence reconciliation reason.
- `src/fazit/rules/mappings/generic.yaml` declares the evidence for a Windows desktop requirement.
- `src/fazit/rules/mappings/nextcloud.yaml` declares the desktop confirmation and positive Windows-only count.
- `src/fazit/rules/mappings/opendesk.yaml` declares the same evidence for the openDesk desktop gap.
- `src/fazit/rules/status.yaml` requires usage evidence for a telephony blocker and gives source-neutral count reasons.
- `src/fazit/templates/report.html.j2` shows the conflict message that fits the observations and suppresses the zero-file conclusion on disputed counts.
- `tests/tenants.py` generates unassigned inventories and conflicting counts within valid coverage.
- `tests/test_costs.py` checks the town total and padded-count rejection through both CLI languages.
- `tests/test_evidence_cli.py` covers directory skips, empty inventories, coverage bounds, telephony, desktop disputes and headline zeros.
- `tests/test_inputs.py` checks scalar spellings and verifies the new confirmation is used by the desktop mapping.
- `tests/test_rules.py` checks disputed and partial counts, licence and telephony decisions, and localised rule-label errors.
- `tests/test_simulation.py` adds the reduced examples and checks that generated conflicts withhold Ready.

## Verification

`uv sync`, both Ruff checks and both language demos passed. `uv run pytest -q` passed 665 tests in 80.40 seconds. The deep simulation run passed 6 tests in 255.28 seconds. `uv run python site/check_site.py` checked 16 pages and 501 references and matched both regenerated demos byte for byte. Both reports opened at 360 px in Chromium with IPv4 and IPv6 sockets blocked and made zero HTTP requests.

## Deviations and open work

None within this task.

## Suggested commits

- R-01 and R-06. `fix: reconcile empty and unassigned licence evidence` (visible).
- R-02. `fix: flag disagreements between complete observations` (visible).
- R-03. `fix: require evidence of telephony use for blockers` (visible).
- R-04. `fix: check desktop requirements across workloads` (visible).
- R-05. `fix: reject ambiguous scalar spellings in inputs` (visible).
- R-07. `fix: reject impossible subsets and licence coverage` (visible).
- R-08. `fix: qualify headline zeros with unknown coverage` (visible).
- R-09. `fix: validate rule labels in both locales` (visible).

Regenerate the site demos in each commit that changes the town report or its rule checksums. Include this summary with the last commit.

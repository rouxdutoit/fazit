---
created: 2026-11-23
source: release review round 11, Codex GPT-6.2-Astra (REVIEW-astra-11.md, high) and Claude Fable 5.2 (REVIEW-fable-11.md, low)
severity: high
due: before the first public release on PyPI
area: rules
---

# Losing evidence can turn Unknown into Ready outside Directory

**Problem.** Principle 8 says a skipped or denied collector never improves readiness. Round 11 found it still can, in areas other than Directory:

- Removing only the skipped Directory collector turns Integrations from Unknown to Ready, because a supplied zero in `inputs.yaml` displaces the scan's recorded permission denial.
- Partial checks that lose a positive observation make Integrations, Office files and Telephony Ready.
- Related: blanking the "no replacement" answer turns openDesk Telephony from Blocker to Needs work (marked incomplete).

Fable's round-11 search confirms the first case independently: 24 two-step degradations in which a skipped or partial directory collector is then left out of the scan, and Integrations returns to Ready on the answer. Fable also found that outside Directory a failed check blocks an answer only while its collector is listed as skipped or partial: on the nonprofit sample, marking the integrations finding `permission_denied` while the directory collector says `ok` turns Integrations from Unknown to Ready. The reviewers disagree on one point: Fable treats removing a recorded answer (19 further steps, including the Telephony case above) as outside principle 8, which speaks of collectors; Astra counts it. The founder can decide whether answers fall under the rule.

Astra reports these predate rv16 (`9640fe2`). Reproductions: `tmp/r11/logs/lost-rows.log` and `tmp/r11/logs/other-areas.log` in the review, described in `REVIEW-astra-11.md`.

**General rule to implement.** A supplied value never overrides a recorded denial, skip or failure for the same finding; removing or degrading any evidence never improves any status. A finding that reports a failed check under a collector listed as `ok` is refused by D31, and producers must list every collector they attempted. Implement it once in the evidence precedence (`evidence.py`) and status evaluation (`status.py`), not per area.

**Gate.** A monotonicity search over every one- and two-step degradation (remove a collector, mark it skipped, denied or partial, drop a finding, blank an answer) on both samples and generated tenants finds zero steps that improve a status, in the style of Fable's round-10 search (`REVIEW-fable-10.md`). Add it to `tests/test_simulation.py`.

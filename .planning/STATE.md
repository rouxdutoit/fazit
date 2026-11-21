---
gsd_state_version: '1.0'
status: planning
progress:
  total_phases: 4
  completed_phases: 0
  total_plans: 0
  completed_plans: 0
  percent: 0
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-11-21)

**Core value:** An organisation gets honest, inspectable numbers about its own Microsoft dependency, including "unknown" and "not yet", without any of its data leaving the machine.
**Current focus:** Phase 1: Demo and Report

## Current Position

Phase: 1 of 4 (Demo and Report)
Plan: 0 of TBD in current phase
Status: Ready to plan
Last activity: 2026-11-21 — Roadmap created (4 phases, 58 of 58 v1 requirements mapped)

Progress: [░░░░░░░░░░] 0%

## Performance Metrics

**Velocity:**
- Total plans completed: 0
- Average duration: - min
- Total execution time: 0.0 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| - | - | - | - |

**Recent Trend:**
- Last 5 plans: none yet
- Trend: -

*Updated after each plan completion*

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table. `DECISIONS.md` wins over `HANDOFF.md` on conflict.
Recent decisions affecting current work:

- [Roadmap]: Phases 1 to 4 follow milestones M0 to M3 from `DECISIONS.md`; all four phases are in MVP mode.
- [Roadmap]: DIST-03 (licence, SPDX headers, `CONTRIBUTING.md`, `SECURITY.md`) and DOCS-01 (README in English and German) were pulled forward from M3 into Phase 1 so the first phase is shareable.
- [Roadmap]: Safeguard tests sit with the code they guard: SAFE-04, SAFE-05, SAFE-07 in Phase 1; SAFE-01, SAFE-02, SAFE-03, SAFE-06 in Phase 3.
- [Roadmap]: Rules delivered in Phase 1 bind later phases: report path and `--out` on every command, privacy by default on every data path, both locales for every string, no test needs a tenant.
- [Phase 1]: No Microsoft code. No MSAL, no Graph client, no network code of any kind until Phase 3.

### Pending Todos

None yet.

### Blockers/Concerns

- [Roadmap] `DECISIONS.md` gained entry F1 on 2026-11-21: the tool should produce what an assessment repeats, including "the interview checklist that fills `inputs.yaml`". No v1 requirement covers that checklist. Nearest are COST-05 (Phase 1) and CONV-01 (v2). Decide whether to add a requirement before planning Phase 1.
- [Phase 1] Carries 31 of the 58 requirements. This is deliberate (the demo needs real judgement), but if planning finds it too large, the natural cut is the cost comparison and `inputs.yaml`.
- [Phase 1] No v1 import or collector supplies file-type or device counts (FILE-01 and SRC-02 are v2). The demo's sample data can show findings that a real v1 report shows as Unknown. Decide in the Phase 1 discussion how the demo makes that plain.
- [Phase 1] `m365-exit-scan` is a working name and gets baked into the package and command. Renaming after PyPI publication is costly; decide before Phase 4.
- [Phase 1] MODL-01 calls the schema "documented", but `docs/schema.md` is DOCS-04 in Phase 4. Move DOCS-04 to Phase 1 if the document is wanted from day one.
- [Phase 2] Needs real admin-centre export files to fix the expected columns. None are in the repository yet.
- [Phase 3] A person cannot verify sign-in, and fixtures cannot be recorded, without a test tenant and an app registration. CI still needs neither.
- [Phase 4] The signed Windows build needs a signing certificate or signing service; obtaining one takes time and should start before Phase 4.

## Deferred Items

Items acknowledged and deferred at milestone close, most recent first:

| Category | Item | Status | Deferred At | Milestone |
|----------|------|--------|-------------|-----------|
| *(none)* | | | | |

## Session Continuity

Last session: 2026-11-21 13:14
Stopped at: Roadmap, state and requirement traceability written. Next step is to discuss or plan Phase 1.
Resume file: None

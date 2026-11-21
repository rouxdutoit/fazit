# Phase 1: Demo and Report - Context

**Gathered:** 2026-11-21
**Status:** Ready for planning

<domain>
## Phase Boundary

`demo` and `report` produce the full German or English report from bundled sample data or an existing `scan.json`, with the evidence model, rules, mappings, three cost scenarios and `inputs.yaml`, plus the repository basics a public repo needs on day one. No Microsoft code: no sign-in, no Graph client, no `httpx`, no `msal`. No network access at runtime.

Source of these decisions: `HANDOFF.md` (original spec) and `DECISIONS.md` (agreed changes, which win on conflict). The founder delegated the phase discussion; decisions below are the orchestrator's reading of those two files and are locked for planning.

</domain>

<decisions>
## Implementation Decisions

### Packaging and layout
- **D-01:** Source layout is `src/m365_exit_scan/` following `HANDOFF.md` section 11, minus the Microsoft modules (`auth.py`, `graph.py`, `collectors/`), which arrive in Phase 3.
- **D-02:** `pyproject.toml` uses PEP 621 metadata with the `hatchling` build backend, `requires-python = ">=3.12"`, a console script `m365-exit-scan`, and is managed with `uv` (`uv sync`, `uv run pytest`, `uv run ruff check`). `uv.lock` is committed.
- **D-03:** Runtime dependencies in this phase are exactly `typer`, `jinja2` and `pyyaml`. Dev dependencies are `pytest` and `ruff`. `pyyaml` is new relative to the handoff's list; it is required by the YAML files the handoff itself mandates and is recorded in `DECISIONS.md`. No `pydantic`, no `babel`, no `rich` beyond what `typer` pulls in. `httpx` and `msal` are not added in this phase.
- **D-04:** Data files (templates, locales, rules, sample data) live inside the package and are read with `importlib.resources`, so the installed tool works without the repository.

### Command line
- **D-05:** `demo [--lang de|en] [--sample town|nonprofit] [--profile opendesk|nextcloud|generic] [--out DIR]`. Default sample is `town`, default language `en`, default profile `opendesk`, default output directory `./report`.
- **D-06:** `report SCAN_JSON [--inputs FILE] [--lang de|en] [--profile NAME] [--out DIR]`. Language and profile resolve in this order: command-line flag, then `inputs.yaml`, then the defaults in D-05.
- **D-07:** Both commands write `report-<org-slug>-<YYYY-MM-DD>.html` into the output directory and print the absolute path of that file as the last line of standard output. `demo` also writes a copy of the sample `scan.json` and the matching sample `inputs.yaml` next to the report, so the user can immediately try `report`.
- **D-08:** Errors are one plain sentence naming the file and field, exit code 2 for bad input, no traceback unless `--debug` is passed.

### Evidence model (`scan.json`)
- **D-09:** Top level: `schema_version` (string, starts at `"1.0"`), `tool` (name, version), `generated_at`, `source_kind` (`sample`, `import` or `live`), `organisation` (display name, may be null), `collectors` (list) and `findings` (list). Typed with standard-library dataclasses in `model.py`; loading validates and fails with D-08 messages.
- **D-10:** A collector entry has `id`, `status` (`ok`, `partial`, `skipped`), `reason` (required unless `ok`) and `permissions_used`.
- **D-11:** A finding has `id` (dotted, for example `mail.mailbox_count`), `workload`, `value`, `unit`, `provenance` (`measured`, `provided`, `unknown`), `source`, `collected_at`, `period`, `coverage` and `missing_reason` (required when provenance is `unknown`).
- **D-12:** Workloads in v1: `licences`, `directory`, `mail`, `onedrive`, `sharepoint`, `teams`, `office_files`, `devices`, `windows_software`. Rules and report only read `scan.json` and `inputs.yaml`; nothing else feeds them.
- **D-13:** A loader refuses a `scan.json` whose major schema version it does not know, with a message that states the version found and the version supported.
- **D-14:** Two bundled samples: a fictional 85-person town office and a fictional 20-person non-profit, each with a `scan.json` and an `inputs.yaml`. Each sample deliberately includes one skipped collector, one `unknown` finding and one `provided` value, so the demo shows honest unknowns. All names of organisations and software are invented.
- **D-15:** Values supplied through `inputs.yaml` for things v1 cannot measure (risky file counts, devices, Windows-only software) enter the model as `provided` findings (COST-06).

### Rules and mapping
- **D-16:** `rules/mappings/<profile>.yaml` maps each Microsoft service to its replacement for that profile. `rules/status.yaml` holds ordered status rules. `rules/risky_file_types.yaml` holds the configurable type list grouped by kind (may contain macros, Access database, Publisher, Visio, OneNote) and does not contain `.dotx`.
- **D-17:** A status rule has a workload, a condition on one finding (`exists`, `missing`, `==`, `>`, `>=` against a literal), a status and a reason. Human-readable rule and mapping texts are written inline in both languages (`{en: ..., de: ...}`), and validation rejects a rule file missing either language.
- **D-18:** Per workload the worst matching status wins (Blocker over Needs work over Ready). If any finding a workload's rules require is missing or `unknown`, or its collector was skipped, the workload is `Unknown`. `Unknown` is never upgraded.
- **D-19:** There is no overall score. The readiness section shows a bar split by the number of workloads in each of the four statuses, and a table with status, reason and evidence per workload.
- **D-20:** Rule, mapping and input files are validated on load; an error names the file and the field (RULE-04).

### Costs and manual inputs
- **D-21:** `inputs.yaml` follows `HANDOFF.md` section 7 and adds: per-scenario blocks for `partial_exit` and `full_exit` (retained Microsoft licences per year, hosting per user per month, one-time migration, training, months of parallel running), and a `provided_counts` block for D-15.
- **D-22:** Three five-year scenarios are computed: stay, partial exit, full exit. Arithmetic uses `decimal.Decimal`. A scenario whose formula touches a null input has total `unknown`, and the report names which inputs are missing. Nothing is estimated or defaulted.
- **D-23:** The source tree contains no monetary constants. Sample prices exist only in the sample `inputs.yaml` files, which are marked as invented.
- **D-24:** `inputs.example.yaml` at the repository root carries comments in English and German. `docs/interview-checklist.md` and `docs/interview-checklist.de.md` list the questions whose answers fill `inputs.yaml`.

### Report
- **D-25:** One Jinja2 template, autoescape on, rendering one `.html` file with inline CSS, system font stack, no external resources, no data fetched at view time, and no JavaScript unless a feature cannot be done without it.
- **D-26:** Nine sections in the order given in REPT-02. The header statement depends on `source_kind`: for `sample` it says the report is built from sample data and no Microsoft tenant was contacted; the read-only wording from the handoff is used only for `import` and `live`.
- **D-27:** Light and dark mode through `prefers-color-scheme`, readable at 360 px width, and a print stylesheet that avoids breaking tables and status rows across pages.
- **D-28:** The four statuses each have a text label and a shape or pattern cue, with colours from a blue to orange range that differ in lightness. `Unknown` is neutral grey with a dashed outline. Provenance (`measured`, `provided`, `unknown`) is shown by a text tag on every figure.
- **D-29:** The appendix lists collectors with status and reason, the rules that fired, the full mapping for the chosen profile, the schema version and the tool version.
- **D-30:** The footer shows the project name and the repository URL as plain text taken from one constant, which holds a placeholder until the repository is public.

### Languages
- **D-31:** All fixed report strings come from `locales/en.yaml` and `locales/de.yaml`. German uses the formal "Sie" and the plain register of public administration, written as native German and not as a word-for-word translation. Numbers, dates and currency are formatted per language by a small formatter in the package.
- **D-32:** A test compares the key sets of both locales and fails on any difference.

### Privacy
- **D-33:** `privacy.py` removes person names and email addresses from the model unless `--include-names` is passed. It is applied when a `scan.json` is written and again before rendering. A test fixture `scan.json` containing names and addresses proves both paths.

### Repository basics
- **D-34:** `LICENSE` is the canonical AGPL-3.0 text fetched from gnu.org, not reproduced from memory. Every source file starts with `# SPDX-License-Identifier: AGPL-3.0-or-later`.
- **D-35:** `README.md` and `README.de.md` show the `demo` command first, state that the code is written with AI assistance (Claude and Codex, each reviewing the other) under the direction of a human maintainer, and say plainly that the project is early and that scanning a real tenant is not yet available.
- **D-36:** `CONTRIBUTING.md` asks for a Developer Certificate of Origin sign-off and no contributor agreement. `SECURITY.md` restates the principles and points to the repository's private vulnerability reporting.
- **D-37:** A GitHub Actions workflow runs `ruff` and `pytest` through `uv` on Python 3.12 and the newest stable Python, with no secrets and no network calls in tests.

### Tests required in this phase
- **D-38:** Offline report (SAFE-04), privacy by default (SAFE-05), locale parity (I18N-02), unknown is never ready (RULE-03), invalid rule file error (RULE-04), unknown cost total when an input is missing (COST-03), no monetary constants in `src/` (COST-04), and a smoke test that runs `demo` for both samples in both languages.

### Claude's Discretion
Internal module boundaries within the layout of `HANDOFF.md` section 11, the exact visual design within D-25 to D-28, the wording of sample data, and the wording of user-facing strings within D-31.

</decisions>

<specifics>
## Specific Ideas

- The demo is the project's shop window: it will be shown to integrators and linked from an email to the author of the blog post that prompted the project. It must look calm and trustworthy, like a document a council could print and file.
- The handoff mentions a visual mockup from planning. It is not in the repository; `HANDOFF.md` section 9 is the source of truth.
- The second sample (20-person non-profit) exists because part of the audience runs very small organisations.
- The report must be useful when the answer is "not yet" or "only this department". The suggested-path section should say so when blockers or unknowns dominate.

</specifics>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Specification
- `HANDOFF.md` §2 — the eight non-negotiable principles
- `HANDOFF.md` §7 — `inputs.yaml` shape
- `HANDOFF.md` §8 — rules and mapping as data files
- `HANDOFF.md` §9 — report sections and design rules
- `HANDOFF.md` §10 to §12 — CLI, repository layout, tests that guard the principles

### Agreed changes
- `DECISIONS.md` — D1 to D14 and the milestone order; wins over `HANDOFF.md` on conflict

### Planning
- `.planning/PROJECT.md` — constraints and key decisions
- `.planning/REQUIREMENTS.md` — the 31 requirement IDs mapped to this phase

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
None. The repository holds only documentation and planning files.

### Established Patterns
None yet. This phase sets them: dataclass models, data files inside the package, one error style, tests that guard each principle.

### Integration Points
`scan.json` is the contract later phases write to: `import` in Phase 2 and live collectors in Phase 3 must produce exactly this model.

</code_context>

<deferred>
## Deferred Ideas

- Partner-branded reports — future, after integrators ask for it
- Interactive prompt for the manual inputs — v2 (CONV-01)
- Published `docs/schema.md` — Phase 4 (DOCS-04)
- Signed Windows build and PyPI release — Phase 4

</deferred>

---
*Phase: 01-demo-and-report*
*Context gathered: 2026-11-21*

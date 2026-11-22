# Roadmap: fazit

## Overview

The tool is built judgement first. Phase 1 delivers the whole decision document from bundled sample data: evidence on every finding, per-workload status with honest unknowns, three cost scenarios, in German and English, with no Microsoft code in the repository. That phase is shareable by itself. Phase 2 lets a real organisation feed in its own admin-centre CSV exports, still with no sign-in and no network. Phase 3 adds the only code that talks to Microsoft: `doctor`, browser sign-in, and live licence and directory counts behind host and endpoint allowlists, with tests that prove each trust promise. Phase 4 documents, packages and releases it for `uvx` and as a signed Windows build.

The four phases follow the milestone order M0 to M3 agreed in `DECISIONS.md`.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Demo and Report** - `demo` and `report` produce the full German or English report from sample data, with rules, evidence and costs, and no Microsoft code
- [ ] **Phase 1.1: AI Assistants and Decision Window** (INSERTED) - Copilot and Copilot Studio as the second assessed area, and the renewal date by which a decision is needed
- [ ] **Phase 1.2: Outputs for Integrators** (INSERTED) - CSV export for project plans and `fazit verify` to detect changes to a report
- [ ] **Phase 1.3: Sovereignty Criteria** (INSERTED) - every finding linked to ZenDiS's sovereignty criteria catalogue and the Austrian and Swiss equivalents
- [ ] **Phase 2: Import** - `import` turns admin-centre CSV exports into a real report locally, keeping aggregates only
- [ ] **Phase 3: Doctor, Sign-in and Live Counts** - `doctor` and `scan` with browser sign-in, live licence and directory counts, and enforced host and endpoint allowlists
- [ ] **Phase 4: Documentation, Packaging and Release** - bilingual guides, `uvx` from PyPI, signed Windows build, first tagged release

## Phase Details

### Phase 1: Demo and Report
**Goal**: Anyone can run `demo` and `report` and get an honest, self-contained report in German or English, with per-workload status, evidence on every finding and three cost scenarios, without a Microsoft account, without network access and before any Microsoft code exists
**Mode:** mvp
**Depends on**: Nothing (first phase)
**Requirements**: CLI-01, CLI-02, CLI-06, MODL-01, MODL-02, MODL-03, MODL-04, RULE-01, RULE-02, RULE-03, RULE-04, RULE-05, COST-01, COST-02, COST-03, COST-04, COST-05, COST-06, REPT-01, REPT-02, REPT-03, REPT-04, REPT-05, REPT-06, I18N-01, I18N-02, SAFE-04, SAFE-05, SAFE-07, DIST-03, DOCS-01
**Success Criteria** (what must be TRUE):
  1. With the network switched off, a user runs `demo --lang de` or `demo --lang en`, sees the path of the file that was written, and opens one `.html` file built from the bundled sample data (a fictional 85-person town office and a fictional 20-person non-profit) that shows all nine sections in order in the chosen language, reads well in light and dark mode and at phone width, and prints cleanly to PDF.
  2. Each workload in the report shows Ready, Needs work, Blocker or Unknown as a text label with a plain-language reason and its evidence (source, date, reporting period, coverage); measured, user-provided and unknown values look different, and a workload with missing or skipped data shows Unknown, never Ready.
  3. A user copies `inputs.example.yaml`, fills in some costs, runs `report scan.json --inputs inputs.yaml` with a different `--lang` or `--profile` on a `scan.json` that carries a schema version, and gets a rebuilt report comparing stay, partial exit and full exit over five years; every cost left empty reads "not provided" and every total that depends on it reads unknown.
  4. A user changes a mapping, a status rule or the risky file-type list in a YAML file and sees the change in the next report, whose appendix lists the rules applied and the full mapping; a broken file stops the run with a message that names the file and the field.
  5. Anyone who clones the repository finds the AGPL licence, `CONTRIBUTING.md`, `SECURITY.md` and a README in English and German that shows the `demo` command first and says the code is written with AI assistance, and can run the test suite, locally or in CI and with no tenant, to see it prove that reports load nothing external, contain no person names or email addresses by default, and have the same keys in both locales.
**Plans**: 7 plans

Plans, run one at a time in this order:
- [ ] 01-01-PLAN.md — Walking skeleton and evidence model: `demo` writes one real report; catalogue of fifteen workloads, allowlist loader, two samples, two languages
- [ ] 01-02-PLAN.md — `report` command, writes that stay inside `--out`, proof of privacy and of offline use, visual design
- [ ] 01-03-PLAN.md — Judgement: licence signals, status rules for fifteen workloads with reason and fix on every Unknown, risky file types
- [ ] 01-04-PLAN.md — Mappings by function for three profiles with coverage ladder and check dates, "Cannot be moved", suggested path without a verdict
- [ ] 01-05-PLAN.md — Manual inputs: `inputs.yaml`, provided evidence, example file and interview checklist in two languages
- [ ] 01-06-PLAN.md — Costs: three five-year scenarios in running cost and three blocks, run details, nine sections in every report
- [ ] 01-07-PLAN.md — Repository basics and final proof: licence, CONTRIBUTING, SECURITY, README in two languages, CI, installed package offline, M0 note
**UI hint**: yes

### Phase 1.1: AI Assistants and Decision Window (INSERTED)
**Goal**: The report shows an organisation's dependency on Microsoft's AI assistants and tells it when it has to decide before its licences renew
**Depends on**: Phase 1
**Requirements**: AIAS-01, DECI-01
**Research**: `.planning/research/copilot-area.md` (licence and plan IDs checked against Microsoft's licensing reference, measurable evidence, open alternatives)
**Success Criteria** (what must be TRUE):
  1. "AI assistants (Copilot)" appears as the second area in the report, the site's area list and the coverage table, in both languages.
  2. A paid Copilot or Copilot Studio licence in the licence block is measured evidence; Copilot plans bundled in suites prove nothing on their own; agents and connected data sources come from provided answers; incomplete evidence is never Ready.
  3. Each target profile maps the area with a dated source, and no profile claims more than its documentation says.
  4. With a contract end date and notice period in `inputs.yaml`, the report shows the next renewal and the decision date, marked as provided; without them it says what to supply.
**Plans**: 4 plans
- [ ] 01.1-01-PLAN.md - AI assistants area from answers, status rules and mappings
- [ ] 01.1-02-PLAN.md - Copilot licences as evidence, checked against Microsoft's reference
- [ ] 01.1-03-PLAN.md - decision window from the contract end date and notice period
- [ ] 01.1-04-PLAN.md - publish: sample reports, screenshots, 16 areas on the site and in the READMEs

### Phase 1.2: Outputs for Integrators (INSERTED)
**Goal**: Integrators can move a report's findings into their own project plans, and anyone can check that a report has not been changed since it was written
**Depends on**: Phase 1
**Requirements**: OUTP-01, OUTP-02
**Success Criteria** (what must be TRUE):
  1. `--csv` (or an equivalent output) writes findings, open questions and effort drivers next to the report, with no field that can hold person data, covered by the privacy test.
  2. `fazit verify REPORT` passes on an unchanged report and fails, naming the section, after any edit; it works offline and its help text says it detects changes, not authorship.
**Plans**: TBD

### Phase 1.3: Sovereignty Criteria (INSERTED)
**Goal**: A public body can use the report directly in its sovereignty assessment
**Depends on**: Phase 1.1
**Requirements**: SOVC-01
**Success Criteria** (what must be TRUE):
  1. Each finding names the criterion it informs in ZenDiS's catalogue (version 1.0), with the catalogue's own identifiers, and the appendix lists the mapping with source and date.
  2. Austrian and Swiss criteria are mapped where an official equivalent exists, or the appendix says none was found.
  3. A finding with no matching criterion says so rather than forcing a match.
**Plans**: TBD

### Phase 2: Import
**Goal**: A real organisation's admin-centre CSV exports become a `scan.json` and a report on the user's own machine, with no sign-in, no consent and no network access, and with nothing kept but aggregates
**Mode:** mvp
**Depends on**: Phase 1
**Requirements**: CLI-03, IMPT-01, IMPT-02, IMPT-03, IMPT-04, IMPT-05, DATA-01
**Success Criteria** (what must be TRUE):
  1. With the network switched off and without signing in, a user points `import` at admin-centre exports (mailbox, OneDrive, SharePoint site and Teams usage, and licences) and gets a `scan.json` and a report in German or English, with the report path printed.
  2. The `scan.json` written by `import` holds aggregates only, with no per-user rows, person names or email addresses by default, and each imported figure shows its source file, reporting period and coverage in the report.
  3. When an export uses concealed (anonymised) identifiers, the import still succeeds and the report says the identifiers were concealed.
  4. When one CSV has unrecognised or changed columns, the user sees a message naming that file and the missing columns, the other files are still imported, and the affected workload shows Unknown.
  5. The shared-mailbox count shows Unknown with the reason until the user also imports an Exchange recipient export, after which the count appears.
  6. The report states the tenant's data location and EU Data Boundary status from an export or a provided answer, as a fact without a score.
**Plans**: TBD

### Phase 3: Doctor, Sign-in and Live Counts
**Goal**: An operator can check whether a tenant is ready for a scan, sign in through the browser with the organisation's own app registration, and get measured licence and directory counts, while tests anyone can run prove the tool contacts only two hosts, calls only allow-listed read endpoints and leaves no token behind
**Mode:** mvp
**Depends on**: Phase 2
**Requirements**: CLI-04, CLI-05, AUTH-01, AUTH-02, AUTH-03, AUTH-04, COLL-01, COLL-02, COLL-03, COLL-04, COLL-05, COLL-06, SAFE-01, SAFE-02, SAFE-03, SAFE-06
**Success Criteria** (what must be TRUE):
  1. A user runs `doctor` with their `--client-id` and `--tenant-id` and sees, for consent, roles and sign-in flows, whether a scan can run and the exact fix for each problem found.
  2. A user runs `scan`, signs in through the browser with their organisation's own app registration (or with device code after passing an explicit flag), watches progress while the tool pages through results and waits when Microsoft throttles it, and gets a `scan.json` and a report showing licence SKUs with purchased and assigned counts and counts of users, licensed users, guests and groups, all marked as measured.
  3. When a permission is missing or denied, the scan still finishes, the skipped collector appears in the appendix with the reason, and the affected workload shows Unknown.
  4. The tool refuses any host other than `login.microsoftonline.com` and `graph.microsoft.com`, any redirect to another host and any request not on the read-endpoint allowlist (including `GET /users/{id}/drive`), asks only for read scopes, and leaves no token on disk after a scan.
  5. Anyone can run the test suite without a tenant, locally or in CI, and see tests prove each of those promises: allowed hosts only, read-only scopes, no token-like string on disk after a scan against fixtures, and a collector answering `403` skipped while the report still renders.
**Plans**: TBD

### Phase 4: Documentation, Packaging and Release
**Goal**: Anyone can run a tagged release with one command, including on a Windows machine without Python, and can find what they need to register the app, understand each permission and build on `scan.json`
**Mode:** mvp
**Depends on**: Phase 3
**Requirements**: DIST-01, DIST-02, DOCS-02, DOCS-03, DOCS-04
**Success Criteria** (what must be TRUE):
  1. A user with `uv` installed runs `uvx fazit demo` and gets the report, installed from the tagged release on PyPI.
  2. A user on a Windows machine without Python downloads the self-contained build, sees a valid signature on it, and runs `demo` to get the same report.
  3. An administrator follows the app-registration guide in German or English from nothing to a passing `doctor` run, and the guide says who can grant consent.
  4. A reader finds every scope the tool can request, with the reason for it, in `docs/permissions.md`, and every `scan.json` field in `docs/schema.md`, and both match what the released tool does.
**Plans**: TBD

## Notes on Order and Mapping

- **Order.** Phases 1 to 4 are M0 to M3 from `DECISIONS.md`. No requirement dependency forced a reorder. Phase 3 technically needs only Phase 1; it follows Phase 2 because import comes before any live sign-in (D4).
- **Pulled forward from M3 into Phase 1.** DIST-03 (`LICENSE`, SPDX headers, `CONTRIBUTING.md`, `SECURITY.md`) and DOCS-01 (README in English and German). A public repository needs these on its first day. DIST-03 is one requirement, so `CONTRIBUTING.md` and `SECURITY.md` come with the licence and the headers.
- **Safeguard tests sit with the code they guard.** SAFE-04, SAFE-05 and SAFE-07 are in Phase 1. SAFE-01, SAFE-02, SAFE-03 and SAFE-06 are in Phase 3, where the Graph client and sign-in first exist.
- **Standing rules after Phase 1.** CLI-06, REPT-06, SAFE-05, SAFE-07, I18N-01, I18N-02 and DOCS-01 are delivered in Phase 1 and bind every later phase: each new command prints its report path and accepts `--out`; each new data path is private by default and joins the privacy test; each new string goes into both locales; no test needs a tenant; the README and `SECURITY.md` are kept in step as commands and network code arrive.
- **MODL-01 and DOCS-04.** MODL-01 calls the schema "documented". Phase 1 delivers the versioned schema and the rule that collectors write it while rules and report only read it. The published `docs/schema.md` is DOCS-04 in Phase 4, written once import and live collection have settled the format.
- **File types and devices have no v1 source.** RULE-05 ships in Phase 1 and is exercised by sample data. No v1 import or collector supplies file-type or device counts (FILE-01 and SRC-02 are v2), so a real v1 report shows those workloads as Unknown unless the user supplies counts through `inputs.yaml`, in which case they are shown as provided by the user (COST-06). The demo report must state plainly that it is built from sample data.
- **Final review after all planned work.** Once phases 1.1 to 1.3 are built, Claude Fable 5.2 and Codex GPT-6.2-Astra, both at max, review everything changed since the release review, including security, and check the project against the resolutions of the No AI Slop manifesto (https://www.slopmanifesto.com/). This happens before the PyPI release and the announcement.
- **Download button with the first release.** When phase 4 publishes the PyPI package and the signed Windows build, the "Get Fazit" button (already the main action, pointing to "How it works" until then) leads to a short page with the install command and the Windows file, each with version and size.
- **Languages after v1.** French and Italian (I18N-03) are planned with the Swiss pilot, because both are official languages in Switzerland, part of the stated market. A language is released only after review by a native speaker. Other languages follow the contributor process in `CONTRIBUTING.md` (I18N-04) and are not tied to a phase.

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 1.1 → 1.2 → 1.3 → 2 → 3 → 4

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Demo and Report | 11/11 | Complete | 2026-11-21 |
| 1.1. AI Assistants and Decision Window | 0/4 | Planned | - |
| 1.2. Outputs for Integrators | 0/TBD | Not started | - |
| 1.3. Sovereignty Criteria | 0/TBD | Not started | - |
| 2. Import | 0/TBD | Not started | - |
| 3. Doctor, Sign-in and Live Counts | 0/TBD | Not started | - |
| 4. Documentation, Packaging and Release | 0/TBD | Not started | - |

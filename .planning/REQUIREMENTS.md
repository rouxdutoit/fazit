# Requirements: fazit

**Defined:** 2026-11-21
**Core Value:** An organisation gets honest, inspectable numbers about its own Microsoft dependency, including "unknown" and "not yet", without any of its data leaving the machine.

Sources: `HANDOFF.md` (original spec) and `DECISIONS.md` (agreed changes, which win on conflict).

## v1 Requirements

### Command line

- [x] **CLI-01**: User can run `demo [--lang de|en]` and get a complete report from bundled sample data without a Microsoft account or network access
- [x] **CLI-02**: User can run `report scan.json [--inputs inputs.yaml] [--lang de|en] [--profile NAME]` to rebuild the HTML report with no network access
- [ ] **CLI-03**: User can run `import PATH...` to turn admin-centre CSV exports into a `scan.json` and a report
- [ ] **CLI-04**: User can run `scan` to sign in, collect live data, and get a `scan.json` and a report
- [ ] **CLI-05**: User can run `doctor` to see whether consent, roles and sign-in flows allow a scan, with the exact fix for each problem
- [x] **CLI-06**: Every command that writes a report prints the path of the file it wrote, and accepts `--out DIR`

### Evidence model

- [x] **MODL-01**: `scan.json` has a versioned schema that collectors write and rules and report only read (published documentation is DOCS-04)
- [x] **MODL-02**: Every finding records its source, collection date, reporting period, coverage, and the reason for any missing value
- [x] **MODL-03**: Every value is marked as measured, provided by the user, or unknown, and the report shows the three differently
- [x] **MODL-04**: Bundled sample data describes a fictional 85-person town office and a fictional 20-person non-profit

### Rules and mapping

- [x] **RULE-01**: User can choose a target profile (`opendesk`, `nextcloud`, `generic`) that maps each Microsoft service to its open source replacement, defined in a YAML file
- [x] **RULE-02**: Each workload gets a status of Ready, Needs work, Blocker or Unknown with a human-readable reason, from rules in a YAML file
- [x] **RULE-03**: A workload with missing, partial or skipped evidence is never Ready: it is Unknown unless a problem confirmed by complete evidence gives it a worse status, and it is always marked incomplete with the missing items listed
- [x] **RULE-04**: Rule and mapping files are validated on load, and an invalid file produces an error that names the file and the field
- [x] **RULE-05**: The list of risky file types is configurable, excludes `.dotx`, and macro-enabled types are reported as "may contain macros"

### Costs and manual inputs

- [x] **COST-01**: User can supply organisation name, currency, current costs, target costs, Windows-only software, profile and language through `inputs.yaml`
- [x] **COST-02**: Report compares three five-year scenarios: stay, partial exit, full exit, including one-time migration, training, retained licences and parallel running
- [x] **COST-03**: Any missing cost input is shown as "not provided", and a total that depends on it is shown as unknown
- [x] **COST-04**: The tool contains no hardcoded prices
- [x] **COST-05**: `inputs.example.yaml` ships with comments in English and German
- [x] **COST-06**: An interview checklist in English and German lists the questions whose answers fill `inputs.yaml`, including user-provided counts for things the tool cannot measure in v1 (risky files, Windows-only software, devices)

### Report

- [x] **REPT-01**: Report is one self-contained `.html` file with inline CSS and JS, system fonts, and no external resources
- [x] **REPT-02**: Report contains, in order: header with the read-only statement, what we found, cost comparison, readiness by workload, what moves where, needs attention, suggested path, appendix, footer
- [x] **REPT-03**: Appendix lists permissions used, collectors skipped and why, the rules applied, and the full mapping
- [x] **REPT-04**: Report works in light and dark mode, is readable at phone width, and prints cleanly to PDF
- [x] **REPT-05**: Status is never conveyed by colour alone: each status has a text label and its own symbol (D-80)
- [x] **REPT-06**: Person names and email addresses are absent from the report, `scan.json`, the filename and printed output, because schema 1.x has no field that can hold them and unknown fields are dropped

### Languages

- [x] **I18N-01**: All user-facing report strings come from `locales/de.yaml` and `locales/en.yaml`, with none hardcoded in templates
- [x] **I18N-02**: A test fails if a key exists in one locale and not the other

### Decision support (added 2026-11-22)

- [ ] **AIAS-01**: The report assesses AI assistants (Microsoft 365 Copilot, Copilot Studio) as the second area, after licences: paid add-on licences count as measured evidence, interview answers cover agents built, data sources connected and processes that depend on them, and each target profile maps the area
- [ ] **DECI-01**: User can give the licence contract's end date and notice period in `inputs.yaml`; the report shows the next renewal and the date by which a decision is needed to avoid another term, marked as provided
- [ ] **SOVC-01**: Each finding links to the criterion it informs in ZenDiS's sovereignty criteria catalogue (version 1.0) and, where they apply, the Austrian and Swiss equivalents; the appendix lists the mapping with its source and date
- [ ] **OUTP-01**: User can export findings, open questions and effort drivers as CSV for project plans, under the same privacy rules as `scan.json`
- [ ] **OUTP-02**: `fazit verify REPORT` checks offline whether a report was changed after it was written, using its embedded checksums; it detects changes, it does not prove who ran Fazit
- [ ] **DATA-01**: The report states where the tenant's data is stored (data location and EU Data Boundary status), from an admin-centre export or a provided answer, as a fact without a score

### Import

- [ ] **IMPT-01**: User can import Microsoft 365 admin-centre usage exports for mailboxes, OneDrive, SharePoint sites and Teams, and licence exports
- [ ] **IMPT-02**: Import keeps aggregates only and writes no per-user rows to `scan.json` by default
- [ ] **IMPT-03**: Import recognises concealed (anonymised) identifiers and reports them as such
- [ ] **IMPT-04**: An unrecognised or changed CSV layout produces a clear message naming the file and the missing columns, and the rest of the import continues
- [ ] **IMPT-05**: Shared-mailbox count is Unknown unless an Exchange recipient export is imported

### Sign-in

- [ ] **AUTH-01**: User signs in through the browser (authorisation code with PKCE on a loopback address) using their organisation's own single-tenant app registration, given by `--client-id` and `--tenant-id`
- [ ] **AUTH-02**: User can fall back to device code sign-in with an explicit flag
- [ ] **AUTH-03**: Access and refresh tokens are held in memory only and never written to disk
- [ ] **AUTH-04**: Scopes are requested per collector, all read-only, with none containing `Write`, `ReadWrite` or `Manage`

### Live collection

- [ ] **COLL-01**: `licences` collector reports licence SKUs with purchased and assigned counts
- [ ] **COLL-02**: `directory` collector reports counts of users, licensed users, guests and groups
- [ ] **COLL-03**: A collector whose permission is missing or denied is skipped, listed in the appendix with the reason, and the scan continues
- [ ] **COLL-04**: Graph client pages through results, honours `429` and `Retry-After`, and shows progress
- [ ] **COLL-05**: Graph client refuses any host other than `login.microsoftonline.com` and `graph.microsoft.com`, and does not follow redirects to other hosts
- [ ] **COLL-06**: Graph client refuses any request not on an explicit allowlist of read endpoints, which excludes `GET /users/{id}/drive`

### Safeguard tests

- [ ] **SAFE-01**: A test proves the Graph client raises on any non-allowed host
- [ ] **SAFE-02**: A test proves the requested scopes contain no write or manage scope
- [ ] **SAFE-03**: A test runs a scan against fixtures with a temporary home directory and finds no token-like string on disk
- [x] **SAFE-04**: A test parses generated reports and finds no `src` or `href` that would load an external resource and no external stylesheet
- [x] **SAFE-05**: A test plants names, email addresses and credential-like strings in a `scan.json` and proves none of them reaches the report, the JSON copy, the filename or the printed path
- [ ] **SAFE-06**: A test proves a collector returning `403` is skipped, listed in the appendix, and the report still renders
- [x] **SAFE-07**: CI runs the whole test suite without a live tenant

### Distribution and documentation

- [ ] **DIST-01**: User can run the tool with `uvx fazit demo` from PyPI
- [ ] **DIST-02**: User can run a signed, self-contained Windows build without installing Python
- [x] **DIST-03**: Repository has `LICENSE` (AGPL-3.0-or-later), SPDX headers, `CONTRIBUTING.md` and `SECURITY.md`
- [x] **DOCS-01**: README exists in English and German, shows the `demo` command first, and states that the code is written with AI assistance
- [ ] **DOCS-02**: App-registration guide exists in English and German with the exact steps and who can grant consent
- [ ] **DOCS-03**: `docs/permissions.md` lists every scope and why it is needed
- [ ] **DOCS-04**: `docs/schema.md` documents the `scan.json` format

## v2 Requirements

Deferred. Tracked but not in the current roadmap.

### File inventory

- **FILE-01**: User can count risky file types in customer-nominated SharePoint libraries through a separately granted read permission
- **FILE-02**: A capped or interrupted inventory is labelled partial and can be resumed

### Further sources

- **SRC-01**: User can import exports from on-premises Exchange, Active Directory and Windows file servers
- **SRC-02**: `devices` collector reports Intune managed devices by operating system
- **SRC-03**: `teams` collector reports teams, channels and guest presence from live data

### Convenience

- **CONV-01**: User can answer the manual inputs through an interactive prompt
- **CONV-02**: User can sign in through a project-owned public multi-tenant client ID
- **CONV-03**: Others can contribute rule packs for further target stacks through a documented, checked format
- **CONV-04**: User can opt in to per-person detail with `--include-names`, once a collector exists that can supply it
- **CONV-05**: User can point the tool at their own rule files with `--rules DIR`

### Languages

- **I18N-03**: Report, interview checklist and website in French and Italian for organisations in Switzerland, each reviewed by a native speaker before release (planned with the Swiss pilot)
- **I18N-04**: Further European languages through the documented process in `CONTRIBUTING.md`, each paired with a target profile for that country's open source stack where it differs from openDesk and Nextcloud

## Out of Scope

| Feature | Reason |
|---------|--------|
| Write access or migration execution | The tool's trust rests on being unable to change anything |
| Web dashboard, server, accounts, hosted version | Data must never leave the machine |
| Reading mail bodies or file contents | Counting and sizing only; content analysis is a different trust level |
| Telemetry, analytics, update checks, CDNs | Only Microsoft sign-in and Graph may be contacted |
| Single weighted readiness score | Hides unknowns; a denied collector could raise it |
| Live download of usage reports | Microsoft redirects those calls to a third host; `import` covers them |
| Google Workspace as a source | Second product, different permission model |
| Hardcoded price lists | Prices differ per contract; invented numbers destroy trust |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| CLI-01 | Phase 1 | Complete |
| CLI-02 | Phase 1 | Complete |
| CLI-03 | Phase 2 | Pending |
| CLI-04 | Phase 3 | Pending |
| CLI-05 | Phase 3 | Pending |
| CLI-06 | Phase 1 | Complete |
| MODL-01 | Phase 1 | Complete |
| MODL-02 | Phase 1 | Complete |
| MODL-03 | Phase 1 | Complete |
| MODL-04 | Phase 1 | Complete |
| RULE-01 | Phase 1 | Complete |
| RULE-02 | Phase 1 | Complete |
| RULE-03 | Phase 1 | Complete |
| RULE-04 | Phase 1 | Complete |
| RULE-05 | Phase 1 | Complete |
| COST-01 | Phase 1 | Complete |
| COST-02 | Phase 1 | Complete |
| COST-03 | Phase 1 | Complete |
| COST-04 | Phase 1 | Complete |
| COST-05 | Phase 1 | Complete |
| COST-06 | Phase 1 | Complete |
| REPT-01 | Phase 1 | Complete |
| REPT-02 | Phase 1 | Complete |
| REPT-03 | Phase 1 | Complete |
| REPT-04 | Phase 1 | Complete |
| REPT-05 | Phase 1 | Complete |
| REPT-06 | Phase 1 | Complete |
| I18N-01 | Phase 1 | Complete |
| I18N-02 | Phase 1 | Complete |
| AIAS-01 | Phase 1.1 | Pending |
| DECI-01 | Phase 1.1 | Pending |
| OUTP-01 | Phase 1.2 | Pending |
| OUTP-02 | Phase 1.2 | Pending |
| SOVC-01 | Phase 1.3 | Pending |
| DATA-01 | Phase 2 | Pending |
| IMPT-01 | Phase 2 | Pending |
| IMPT-02 | Phase 2 | Pending |
| IMPT-03 | Phase 2 | Pending |
| IMPT-04 | Phase 2 | Pending |
| IMPT-05 | Phase 2 | Pending |
| AUTH-01 | Phase 3 | Pending |
| AUTH-02 | Phase 3 | Pending |
| AUTH-03 | Phase 3 | Pending |
| AUTH-04 | Phase 3 | Pending |
| COLL-01 | Phase 3 | Pending |
| COLL-02 | Phase 3 | Pending |
| COLL-03 | Phase 3 | Pending |
| COLL-04 | Phase 3 | Pending |
| COLL-05 | Phase 3 | Pending |
| COLL-06 | Phase 3 | Pending |
| SAFE-01 | Phase 3 | Pending |
| SAFE-02 | Phase 3 | Pending |
| SAFE-03 | Phase 3 | Pending |
| SAFE-04 | Phase 1 | Complete |
| SAFE-05 | Phase 1 | Complete |
| SAFE-06 | Phase 3 | Pending |
| SAFE-07 | Phase 1 | Complete |
| DIST-01 | Phase 4 | Pending |
| DIST-02 | Phase 4 | Pending |
| DIST-03 | Phase 1 | Complete |
| DOCS-01 | Phase 1 | Complete |
| DOCS-02 | Phase 4 | Pending |
| DOCS-03 | Phase 4 | Pending |
| DOCS-04 | Phase 4 | Pending |

**Coverage:**
- v1 requirements: 64 total
- Mapped to phases: 64
- Unmapped: 0 ✓
- Phase 1 (Demo and Report): 31
- Phase 1.1 (AI Assistants and Decision Window): 2
- Phase 1.2 (Outputs for Integrators): 2
- Phase 1.3 (Sovereignty Criteria): 1
- Phase 2 (Import): 7
- Phase 3 (Doctor, Sign-in and Live Counts): 16
- Phase 4 (Documentation, Packaging and Release): 5

---
*Requirements defined: 2026-11-21*
*Last updated: 2026-11-22 after adding decision support (phases 1.1 to 1.3, DATA-01 in phase 2)*

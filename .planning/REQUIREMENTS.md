# Requirements: m365-exit-scan

**Defined:** 2026-11-21
**Core Value:** An organisation gets honest, inspectable numbers about its own Microsoft dependency, including "unknown" and "not yet", without any of its data leaving the machine.

Sources: `HANDOFF.md` (original spec) and `DECISIONS.md` (agreed changes, which win on conflict).

## v1 Requirements

### Command line

- [ ] **CLI-01**: User can run `demo [--lang de|en]` and get a complete report from bundled sample data without a Microsoft account or network access
- [ ] **CLI-02**: User can run `report scan.json [--inputs inputs.yaml] [--lang de|en] [--profile NAME]` to rebuild the HTML report with no network access
- [ ] **CLI-03**: User can run `import PATH...` to turn admin-centre CSV exports into a `scan.json` and a report
- [ ] **CLI-04**: User can run `scan` to sign in, collect live data, and get a `scan.json` and a report
- [ ] **CLI-05**: User can run `doctor` to see whether consent, roles and sign-in flows allow a scan, with the exact fix for each problem
- [ ] **CLI-06**: Every command that writes a report prints the path of the file it wrote, and accepts `--out DIR`

### Evidence model

- [ ] **MODL-01**: `scan.json` has a versioned schema that collectors write and rules and report only read (published documentation is DOCS-04)
- [ ] **MODL-02**: Every finding records its source, collection date, reporting period, coverage, and the reason for any missing value
- [ ] **MODL-03**: Every value is marked as measured, provided by the user, or unknown, and the report shows the three differently
- [ ] **MODL-04**: Bundled sample data describes a fictional 85-person town office and a fictional 20-person non-profit

### Rules and mapping

- [ ] **RULE-01**: User can choose a target profile (`opendesk`, `nextcloud`, `generic`) that maps each Microsoft service to its open source replacement, defined in a YAML file
- [ ] **RULE-02**: Each workload gets a status of Ready, Needs work, Blocker or Unknown with a human-readable reason, from rules in a YAML file
- [ ] **RULE-03**: A workload with missing or skipped data is Unknown and never Ready
- [ ] **RULE-04**: Rule and mapping files are validated on load, and an invalid file produces an error that names the file and the field
- [ ] **RULE-05**: The list of risky file types is configurable, excludes `.dotx`, and macro-enabled types are reported as "may contain macros"

### Costs and manual inputs

- [ ] **COST-01**: User can supply organisation name, currency, current costs, target costs, Windows-only software, profile and language through `inputs.yaml`
- [ ] **COST-02**: Report compares three five-year scenarios: stay, partial exit, full exit, including one-time migration, training, retained licences and parallel running
- [ ] **COST-03**: Any missing cost input is shown as "not provided", and a total that depends on it is shown as unknown
- [ ] **COST-04**: The tool contains no hardcoded prices
- [ ] **COST-05**: `inputs.example.yaml` ships with comments in English and German
- [ ] **COST-06**: An interview checklist in English and German lists the questions whose answers fill `inputs.yaml`, including user-provided counts for things the tool cannot measure in v1 (risky files, Windows-only software, devices)

### Report

- [ ] **REPT-01**: Report is one self-contained `.html` file with inline CSS and JS, system fonts, and no external resources
- [ ] **REPT-02**: Report contains, in order: header with the read-only statement, what we found, cost comparison, readiness by workload, what moves where, needs attention, suggested path, appendix, footer
- [ ] **REPT-03**: Appendix lists permissions used, collectors skipped and why, the rules applied, and the full mapping
- [ ] **REPT-04**: Report works in light and dark mode, is readable at phone width, and prints cleanly to PDF
- [ ] **REPT-05**: Status is never conveyed by colour alone: each status has a text label, and status colours differ in lightness
- [ ] **REPT-06**: Person names and email addresses are absent from the report and `scan.json` unless `--include-names` is passed

### Languages

- [ ] **I18N-01**: All user-facing report strings come from `locales/de.yaml` and `locales/en.yaml`, with none hardcoded in templates
- [ ] **I18N-02**: A test fails if a key exists in one locale and not the other

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
- [ ] **SAFE-04**: A test parses generated reports and finds no `src` or `href` that would load an external resource and no external stylesheet
- [ ] **SAFE-05**: A test proves that with default flags no fixture name or email address appears in the report or `scan.json`
- [ ] **SAFE-06**: A test proves a collector returning `403` is skipped, listed in the appendix, and the report still renders
- [ ] **SAFE-07**: CI runs the whole test suite without a live tenant

### Distribution and documentation

- [ ] **DIST-01**: User can run the tool with `uvx m365-exit-scan demo` from PyPI
- [ ] **DIST-02**: User can run a signed, self-contained Windows build without installing Python
- [ ] **DIST-03**: Repository has `LICENSE` (AGPL-3.0-or-later), SPDX headers, `CONTRIBUTING.md` and `SECURITY.md`
- [ ] **DOCS-01**: README exists in English and German, shows the `demo` command first, and states that the code is written with AI assistance
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
| CLI-01 | Phase 1 | Pending |
| CLI-02 | Phase 1 | Pending |
| CLI-03 | Phase 2 | Pending |
| CLI-04 | Phase 3 | Pending |
| CLI-05 | Phase 3 | Pending |
| CLI-06 | Phase 1 | Pending |
| MODL-01 | Phase 1 | Pending |
| MODL-02 | Phase 1 | Pending |
| MODL-03 | Phase 1 | Pending |
| MODL-04 | Phase 1 | Pending |
| RULE-01 | Phase 1 | Pending |
| RULE-02 | Phase 1 | Pending |
| RULE-03 | Phase 1 | Pending |
| RULE-04 | Phase 1 | Pending |
| RULE-05 | Phase 1 | Pending |
| COST-01 | Phase 1 | Pending |
| COST-02 | Phase 1 | Pending |
| COST-03 | Phase 1 | Pending |
| COST-04 | Phase 1 | Pending |
| COST-05 | Phase 1 | Pending |
| COST-06 | Phase 1 | Pending |
| REPT-01 | Phase 1 | Pending |
| REPT-02 | Phase 1 | Pending |
| REPT-03 | Phase 1 | Pending |
| REPT-04 | Phase 1 | Pending |
| REPT-05 | Phase 1 | Pending |
| REPT-06 | Phase 1 | Pending |
| I18N-01 | Phase 1 | Pending |
| I18N-02 | Phase 1 | Pending |
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
| SAFE-04 | Phase 1 | Pending |
| SAFE-05 | Phase 1 | Pending |
| SAFE-06 | Phase 3 | Pending |
| SAFE-07 | Phase 1 | Pending |
| DIST-01 | Phase 4 | Pending |
| DIST-02 | Phase 4 | Pending |
| DIST-03 | Phase 1 | Pending |
| DOCS-01 | Phase 1 | Pending |
| DOCS-02 | Phase 4 | Pending |
| DOCS-03 | Phase 4 | Pending |
| DOCS-04 | Phase 4 | Pending |

**Coverage:**
- v1 requirements: 58 total
- Mapped to phases: 58
- Unmapped: 0 ✓
- Phase 1 (Demo and Report): 31
- Phase 2 (Import): 6
- Phase 3 (Doctor, Sign-in and Live Counts): 16
- Phase 4 (Documentation, Packaging and Release): 5

---
*Requirements defined: 2026-11-21*
*Last updated: 2026-11-21 after roadmap creation*

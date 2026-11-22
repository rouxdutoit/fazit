# Phase 2: Import - Research

**Researched:** 2026-11-22
**Domain:** Local, offline import of Microsoft 365 admin-centre CSV exports into `scan.json` 1.x (Python 3.12+ standard library only)
**Confidence:** MEDIUM overall. HIGH for what Microsoft documents (Graph report CSV headers, admin-centre menu paths, concealment, data-location geographies, the licensing CSV). LOW for what Microsoft does not document (exact admin-centre export bytes, localisation, the licence-summary and Exchange recipient export layouts). Those gaps need real exports before the affected plans run.

<user_constraints>
## User Constraints (from CONTEXT.md)

`02-CONTEXT.md` has no separate "Claude's Discretion" section. Its decisions are locked, and several of them hand the specifics to this research: D-97 (exports and their columns), D-98 (which exports exist), D-101 (exact limits, which go to the plan), D-106 (snapshot stamps and licence reconciliation), D-110 (whether Microsoft's CSV may be committed) and D-112 (whether any export carries the data location). The decisions are copied below verbatim.

### Locked Decisions

#### Baseline

- **D-91:** Plans are written against the code on branch `report-redesign` (scan model `src/fazit/model.py`, D31 checks in `src/fazit/validation.py`, catalogue `src/fazit/rules/findings.yaml`, licence classification `src/fazit/rules/service_plans.yaml` and `src/fazit/licences.py`, report context `src/fazit/report.py`, CLI `src/fazit/cli.py`). No plan starts before that branch is merged into main. Each plan says so in its objective, and its first task checks that `docs/scan-format.md` and the assessed-area catalogue (Licences with `assessed: false`) are on main.
- **D-92:** Phase 2 adds no runtime dependency. CSV parsing uses Python's standard `csv` module. Any new development tool needs a `DECISIONS.md` entry first (D15, AGENTS.md).

#### The command (CLI-03)

- **D-93:** `fazit import PATH... [--inputs inputs.yaml] [--lang en|de] [--profile ...] [--out DIR]`. Each `PATH` is a CSV file or a directory; for a directory, the `.csv` files directly inside it are read (not recursively). Options mean what they mean for `report`, including the language and profile fallback from `inputs.yaml`.
- **D-94:** `import` writes `scan-<YYYY-MM-DD>.json` and `report-<YYYY-MM-DD>-<lang>.html` inside `--out`, through the existing write helpers (atomic replace, no symbolic links, nothing outside `--out`). The date is the scan's `generated_at` date. The report path is printed last (CLI-06). `fazit report scan.json` rebuilds the same report from the written scan.
- **D-95:** Before printing the report path, `import` prints one line per input file: the file as the user gave it, and either the export it was recognised as or why it was not used. Messages exist in both locales (I18N-01). A run where no file is recognised stops with an error sentence and writes nothing. A run with at least one recognised export writes the scan and the report and exits 0, even if other files were refused.
- **D-96:** The clock is passed in: `generated_at` is the run's time with a UTC offset, read once in the CLI layer and handed down, so tests are deterministic (AGENTS.md "Output is deterministic").

#### Recognising exports (IMPT-01, IMPT-04)

- **D-97:** An export is recognised by its header row, never by its file name. Each supported export has a registered column signature (required columns, optional columns, and any known variants Microsoft has shipped). Which exports are supported, their exact column names and their Microsoft Learn sources come from the research; fixture headers must match Microsoft's current documentation and cite the page.
- **D-98:** The v1 export set, subject to the research confirming each one exists and can be downloaded as CSV by an administrator without sign-in from Fazit: mailbox usage, OneDrive usage, SharePoint site usage, Teams usage, licences, Exchange recipients, and whichever export supplies the licensed headcount that MODL-05 requires. The Copilot and Agents usage reports and the Power Platform inventory stay out (D-87).
- **D-99:** A file whose header matches no export, or matches one export with required columns missing, produces one message that names the file and the missing columns of the closest export. That export's collector is recorded as `skipped` with a registered reason, its findings are Unknown with that reason, and every other file is still imported (IMPT-04). Extra, unknown columns are ignored; their names are not printed, because a header cell can hold anything.
- **D-100:** Two files recognised as the same export make that export ambiguous: neither is used, the message names both files, and the export's findings stay Unknown. This keeps one collection time and one reporting period per source (MODL-05).
- **D-101:** Accepted encodings and delimiters: UTF-8 with or without BOM, UTF-16 with BOM, and comma, semicolon or tab delimiters, so a file re-saved by German Excel still imports. Anything else, a file over a fixed size limit, or a malformed CSV is refused with a sentence that names the file. The exact limits come from the plan.

#### Privacy (IMPT-02, IMPT-03)

- **D-102:** Aggregates only, by construction (D19). Per-user rows, user principal names, display names, site URLs and team names are read into memory only to count, sum and detect concealment, and never reach `scan.json`, the report, a file name or printed output. There is no option to keep them in v1. The privacy test (SAFE-05) gains an import case: fixtures planted with names, addresses and credential-like strings produce a scan, report and printed output without any of them.
- **D-103:** Concealed identifiers (the admin-centre privacy setting that replaces names with hashes) are detected per export. The import works the same either way, and the report says, per export, that the identifiers were concealed. Concealment never changes a count.
- **D-104:** The scan does not store input file names, because a file name is free text and could hold a person's name (D19). Each imported export is recorded with its registered source code, its reporting period and refresh date, its row count, whether identifiers were concealed, and the SHA-256 of the file's bytes. The report's evidence names the export (for example "Mailbox usage export, Exchange admin centre") and its period and coverage; the appendix lists each export with its checksum, so the officer can match it to the file that `import` printed. This is how "every figure records its source file" is met without a free-text field. It is a minor schema change (1.x) and gets a `DECISIONS.md` entry and a section in `docs/scan-format.md`.

#### Evidence and consistency (MODL-05, D31)

- **D-105:** Every imported figure is `measured` with a registered `import.*` source, a collector that ran, a reporting period where the export has one, a collection stamp and coverage. Sources are registered in the catalogue next to the `sample.*` ones; the status rules do not change for imported evidence.
- **D-106:** Each collector writes one collection stamp and one reporting period per scan (MODL-05). How snapshot exports without a period (licences, Exchange recipients, the headcount export) get a clock time with a UTC offset, as D31 requires for snapshots and licence inventories, and whether licence reconciliation can be met from the exports an administrator can obtain, comes from the research. Fazit never invents a stamp; where the honest answer is "no shared instant", reconciliation stays Unknown as D31 already prescribes.
- **D-107:** The importer never writes a scan that violates D31: it builds the scan, serialises it, loads it back through the same loader and validation as `report`, and only then writes it (MODL-05). A failure there is a bug and stops with an error, never a written file.
- **D-108:** A supplied export never makes an area look more ready than the evidence allows: deleted rows are excluded, coverage is stated honestly (complete only when the export covers the whole population with no failed rows), and any figure an export does not carry stays Unknown with `not_in_export` (principle 8).
- **D-109:** The shared-mailbox count stays Unknown with `needs_recipient_export` until an Exchange recipient export is imported, then appears as measured (IMPT-05, D9). The mailbox usage and recipient exports keep independent coverage (D31).

#### Licences (IMPT-06)

- **D-110:** The product roster (product names, string IDs, GUIDs and included service plans, free and education products included) is generated from Microsoft's published licensing CSV by a maintainer script that reads a downloaded copy, with the source URL, the download date and the file's SHA-256 recorded in the generated file. Fazit never downloads it at run time. Only the classification (which plan belongs to which area, add-on or bundled) is maintained by hand. A test fails when a generated product has a plan the classification does not cover, so a roster update shows what needs classifying. Whether Microsoft's CSV itself may be committed is decided in the plan from its licence; the generated roster holds identifiers and names only.
- **D-111:** The licence export is matched to products through the roster. A product name the roster does not know, or knows more than once, is kept with its counts and reported as not classified, never guessed.

#### Data location (DATA-01)

- **D-112:** The report states the tenant's data location and its EU Data Boundary status as facts, with their origin (export or provided answer) and date, and never scores them or feeds them into a status. If the research finds no admin-centre export that carries them, they are provided answers in `inputs.yaml` with registered codes (no free text), added to `inputs.example.yaml` and both interview checklists. Unanswered, the report says what to supply.

#### Fixtures and tests

- **D-113:** Fixtures are fictional and realistic: one fictional municipal organisation of about 600 seats (the size the critics asked for), with small committed CSV files whose headers match Microsoft's documentation, plus variants for concealed identifiers, a changed layout, a German Excel re-save and planted personal data. Large populations are generated in memory by tests. `tests/fixtures/import/README.md` cites the Microsoft Learn page for every header and the date it was checked. No real tenant data is ever committed (AGENTS.md).
- **D-114:** Import joins the offline proof: the installed-package test runs `fazit import` on the fixtures with sockets blocked (principle 2, SAFE-07).

#### Pilot validation (VALD-01)

- **D-115:** Phase 2 delivers what a founding pilot needs to run the import unaided: a short guide in English and German (which exports to download from where, the command, how to trace one status and recalculate one cost from the report) and a feedback form. The pilot run itself and the revision of explanations from what pilots report are human steps: the last plan ends in a checkpoint that waits for the founder, and VALD-01 stays open until a pilot has reported. Before the launch, one operator in the 200 to 2,000 range runs the import unaided (launch critique, D).

#### Words and design

- Every new string is in both locales, German written as German (formal Sie, administrative register), and each plan's SUMMARY lists new German strings for native review (DESIGN.md "Copy").
- Report changes follow DESIGN.md and the redesigned report's structure from RR-01 to RR-08. Import adds evidence lines and appendix rows; it does not add a new report section, except the data-location fact (D-112), which goes where the redesign keeps organisation facts.

### Deferred Ideas (OUT OF SCOPE)

- A hand-over section for the data protection officer and staff representatives (report-usefulness B7) is not part of Phase 2's requirements. Data location (DATA-01) is its first fact; the section waits for a requirement.
- Importers for Copilot and Agents usage and the Power Platform inventory (D-87).
- Per-user detail or names on request: no `--include-names` in v1 (D19).
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| CLI-03 | `import PATH...` turns admin-centre CSV exports into a `scan.json` and a report | Code-change map: the new `import` command in `cli.py`, an `importer.py` orchestrator, write through `output.write_files`; D-107 round trip (§8, Plan 02-01) |
| IMPT-01 | Import mailbox, OneDrive, SharePoint site and Teams usage exports, and licence exports | Export reference §1. The four usage exports have documented Graph CSV headers. The licence-summary export is **not documented**, so it waits on a real export (§4, Open Question 1) |
| IMPT-02 | Aggregates only, no per-user rows by default | Aggregators return counts and sums only. The `ExportRecord` holds codes, counts, dates and a hash (§8). Privacy test import case (Plan 02-08) |
| IMPT-03 | Recognise concealed identifiers and report them | Microsoft documents MD5 hashes (§3). Detection rule: 32 hex characters per identifier cell, three-state result |
| IMPT-04 | Unrecognised or changed layout: message naming the file and the missing columns; the rest continues | Recognition by header with case-insensitive matching and a closest-layout message (§2, §8, Plan 02-02) |
| IMPT-05 | Shared-mailbox count Unknown unless an Exchange recipient export is imported | The EAC export layout is undocumented (§5). The mailbox usage page now lists a "Recipient type" column, which is a finding that bears on D9 (Open Question 3) |
| DATA-01 | Data location and EU Data Boundary status as a fact | No export carries them. Provided answers with registered codes (§6) |
| IMPT-06 | Product roster generated from Microsoft's licensing CSV, recorded date, free and education products included; only the classification maintained by hand | CSV facts: 620 products, 15 display names shared by two GUIDs, data-quality defects (§4). Licence terms: do not commit the CSV (§4) |
| VALD-01 | A pilot IT officer traces one status and recalculates one cost unaided; explanations revised | Guide and feedback form plus a final founder checkpoint (Plan 02-08). It stays open after the phase |
| MODL-05 | One collection time and one reporting period per collector and source; the licensed headcount comes from an obtainable export | Usage exports: refresh date plus report period from the file. Snapshot exports: no documented export states a time. Proposed stamp rule and reconciliation outcome in §4.4 |
</phase_requirements>

## Project Constraints (from CLAUDE.md and AGENTS.md)

`.claude/CLAUDE.md` points to `AGENTS.md`, `DECISIONS.md` (principles) and `DESIGN.md`. These directives bind every plan:

- **Never:** write to a tenant; contact any host (Phase 2 code contacts **no host at all**); put a token, a person's name or an email address on disk; load anything external from the report; invent a number. Each has a test, and weakening one is rejected.
- **Code:** Python 3.12+; type hints on every function; frozen dataclasses for data; small modules with one job; functions that fit on a screen; no inheritance trees, metaprogramming or plugin systems; no dead or commented-out code; no `TODO`; comments say why, not what.
- **Dependencies:** runtime `typer`, `jinja2`, `pyyaml`; dev `pytest`, `ruff`, `hypothesis`. A new one needs a `DECISIONS.md` entry first. D-92 adds that Phase 2 adds no runtime dependency.
- **Data holds judgement:** mappings, rules and all user-facing text live in YAML inside the package. The export layouts therefore belong in a YAML rule file, not in Python constants.
- `yaml.safe_load` only; Jinja2 autoescape on; no `eval`, `exec`, shell calls or pickle.
- Files are written only inside `--out`. User errors are one plain sentence naming the file and field, with no traceback unless `--debug`.
- **Deterministic output:** same inputs, same bytes. Dates and clocks are passed in.
- **Words:** every printed message and report string exists in `locales/en.yaml` and `locales/de.yaml`; command help is English only (D18); German is native, formal Sie; DESIGN.md's fixed vocabulary.
- **Tests:** fast, offline, deterministic, with no tenant. Every principle has a failing test. Each bug fix comes with its test.
- **Done means:** `uv run ruff check .`, `uv run ruff format --check .`, `uv run pytest -q`, `uv run fazit demo --lang de`, `uv run fazit demo --lang en`, `uv run python site/check_site.py`. If report output changes, copy the demo HTML to `site/demo/{de,en}/index.html`.
- **Commits:** conventional prefix; `Assisted-by:` for Codex and `Co-Authored-By:` for Claude; never commit real tenant data, `drafts/` or `grants/`.
- **GSD:** changes go through a GSD workflow. Plans follow the RR-06 format (front matter with `estimate`, `must_haves`, `key_links`; `<objective>`, `<context>`, `<tasks>`).

## Summary

The four usage exports in IMPT-01 (mailbox, OneDrive, SharePoint site, Teams team usage) are documented. Microsoft Learn gives each one's admin-centre menu path and an **Export** button, and the matching Microsoft Graph report pages give the exact CSV headers (`Report Refresh Date`, `Is Deleted`, `Storage Used (Byte)`, `Report Period` and so on). Each export states a refresh date and a reporting period of 7, 30, 90 or 180 days, so it can be stored as period-based evidence with a date-only stamp, as D31 already allows. Microsoft does **not** document that the admin-centre **Export** writes byte-for-byte the same header as the Graph CSV. The admin-centre pages describe columns as "Storage used (MB)" and add columns Graph lacks, such as "Recipient type" for mailbox usage and "Geo location" for SharePoint. Header signatures should be registered from the Graph pages (the only verbatim headers Microsoft publishes) and confirmed against one real export per report before release. Matching must be case-insensitive: Microsoft's own Teams page spells the same header "Team type" in one place and "Team Type" in another.

Three exports in D-98 have **no documented layout**: the licence summary on **Billing > Licenses**, the Exchange admin centre **Mailboxes** export, and the **Users > Active users** export. Microsoft Learn describes the pages but not a CSV. The licence-summary export also shows **product display names**, not SKU part numbers or GUIDs, which is why D-110 and D-111 need the roster. 15 display names in Microsoft's CSV belong to two GUIDs each (for example "Microsoft 365 Business Basic", "Visio Plan 2"), so some products will be reported as not classified by design. Microsoft's licensing CSV can be downloaded (620 products, 6,002 rows, SHA-256 `a7a0facf…9b9e5` on 2026-11-22). It sits on download.microsoft.com, whose Terms of Use limit documents to "informational and non-commercial or personal use", so the plan should **not commit it**. Committing only the derived identifier roster is what D-110 already plans.

The hardest question is D-106. **No admin-centre export documented by Microsoft writes a clock time.** Usage exports give a date, and snapshot exports (licences, recipients, user lists) give nothing. Licence reconciliation needs a complete inventory and a complete licensed headcount from the same instant, so it **cannot be met from admin-centre exports**. It stays Unknown (`licence_directory_unverified`), which `licences._directory_cross_check` already produces for period-based or mistimed headcounts. Positive licence assignments still count. The licensed headcount for MODL-05 can come from the documented **Microsoft 365 apps > Active users** usage export (`Assigned Products`, `Is Deleted`, `Report Refresh Date`). Snapshot exports still need *some* stamp to be stored as measured evidence. The honest options are an upper bound ("collected on or before the import date") or a date the operator states. Both need a short D31 amendment, which goes to the founder (Open Question 2). Reconciliation itself arrives with Phase 3's live licence and directory counts.

**Primary recommendation:** Build tracer-first on the mailbox usage export. Use a standard-library CSV reader that decodes by BOM, picks the delimiter under which the header matches a registered layout, and parses values strictly. Register export layouts in `src/fazit/rules/exports.yaml`, and record each export in a new optional `exports` list in `scan.json` 1.1. Treat the licence, recipient and user-list layouts as blocked until a founder-supplied real export header (human step 02-00) and a decision on the snapshot-stamp rule.

## Architectural Responsibility Map

Fazit is a local CLI, so the usual web tiers map onto layers inside one process.

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Read the clock, parse options, print per-file lines and the report path | CLI layer (`cli.py`) | — | D-96: the clock is read once in the CLI; printing is a CLI concern (CLI-06) |
| Read bytes, size limit, SHA-256, BOM and encoding, delimiter, CSV rows | Input layer (`csv_reader.py`, new) | `parsing.py` (pattern of `read_text`) | One job: turn a file into a table or a refusal. No knowledge of Microsoft |
| Recognise an export by header; closest layout and missing columns | Layout registry (`exports.py` plus `rules/exports.yaml`, new) | — | Judgement as data (AGENTS.md); the signatures cite Learn pages |
| Strict cell values (integers, booleans, dates, concealment) | Value parsing (`import_values.py`, new) | `validation.py` limits | Shared by all aggregators; keeps aggregators short |
| Turn rows into counts and sums per export | Aggregators (`aggregates.py`, new) | Catalogue (`findings.yaml`) | One small function per export. Rows never leave memory |
| Assemble collectors, findings, licences and export records; round-trip through the loader | Import orchestrator (`importer.py`, new) | `model.py`, `licences.scan_to_json` | D-107: the same loader as `report` |
| Validate `exports` records and their links to findings (D31 plus the 1.1 addition) | Scan model (`model.py`) | `catalogue.py` | All consistency lives at load time (D31) |
| Product roster lookup by display name; classification | Licences (`licences.py` plus generated `rules/products.yaml`) | Maintainer script (`scripts/`, dev only) | D-110: generated roster, hand-made classification |
| Evidence lines, the appendix export table, the data-location fact | Report context and template (`report.py`, `report.html.j2`) | Locales | Rendering only reads the scan (MODL-01) |
| Data location and EU Data Boundary answers | Inputs (`inputs.py`, `inputs.example.yaml`) | Catalogue codes plus locales | D-112: provided answers with registered codes |

## 1. Export reference (what Microsoft documents)

All pages were checked on **2026-11-22**. The "page updated" dates come from each page's metadata. "Graph headers" are verbatim from the Graph v1.0 report pages, the only place Microsoft publishes exact CSV header strings. Admin-centre metric names are the on-screen labels from the admin-centre article. They are **not** CSV headers.

### 1.1 Mailbox usage

- **Where:** Microsoft 365 admin centre > **Reports** > **Usage** > under Reports select **Exchange** > tab **Email activity** > **View more** > drop-down **Exchange > Mailbox usage**. **Export** writes "an Excel .csv file" that "exports the usage data of all users". [CITED: learn.microsoft.com/…/activity-reports/mailbox-usage, ms.date 2026-04-03]
  - D-104's example label "Mailbox usage export, **Exchange admin centre**" is wrong. The report lives in the **Microsoft 365 admin centre** (Reports > Usage > Exchange). The locale label should say "Mailbox usage export, Microsoft 365 admin centre".
- **Graph headers (v1.0 column list, verbatim):** `Report Refresh Date`, `User Principal Name`, `Display Name`, `Is Deleted`, `Deleted Date`, `Created Date`, `Last Activity Date`, `Item Count`, `Storage Used (Byte)`, `Issue Warning Quota (Byte)`, `Prohibit Send Quota (Byte)`, `Prohibit Send/Receive Quota (Byte)`, `Deleted Item Count`, `Deleted Item Size (Byte)`, `Deleted Item Quota (Byte)`, `Has Archive`, `Report Period`. [CITED: learn.microsoft.com/en-us/graph/api/reportroot-getmailboxusagedetail?view=graph-rest-1.0, ms.date 2024-04-04, updated 2026-06-19]
  - The page's own example header line omits `Deleted Item Quota (Byte)` and `Has Archive`. The beta page includes both. Treat both as optional.
  - Graph lists **no `Recipient Type`** column. The admin-centre table lists **"Recipient type: Either Shared or User"** as its first metric. This bears on D9 and D-109 (Open Question 3).
- **Admin-centre metric names:** Recipient type, User name, Display Name, Deleted, Deleted date, Create date, Last activity date, Item count, Storage used (MB), Deleted Item Count, Deleted Item Size (MB), Issue warning quota (MB), Prohibit send quota (MB), Prohibit send receive quota (MB), Recoverable Item Quota (MB), Report Period, Has Archive. [CITED: mailbox-usage page]. The "(MB)" labels mean the on-screen unit is MB. Whether the export writes `(Byte)` or `(MB)` is **UNVERIFIED** and needs one real export.
- **Deleted rows:** included. "Deleted: The mailbox whose current state is deleted, but was active during some part of the reporting period." Exclude rows where `Is Deleted` is true (D-108). Users deleted more than about 30 days ago disappear from the details table: "Microsoft deletes that user's usage data within 30 days … they don't appear in the User Details table." [CITED: activity-reports overview]
- **Refresh and period:** `Report Refresh Date` on every row; `Report Period` (Graph JSON example `"reportPeriod": "7"`); period options 7, 30, 90, 180 days. Selecting a single day in the UI changes the table to that day ("data for up to 28 days from the current date"). The guide must say: do not select a day.
- **Findings it can honestly measure** (rows with `Is Deleted` false):
  - `mail.mailbox_count` = row count (user and shared mailboxes; room and equipment mailboxes are not in this report, whose recipient type is "Either Shared or User"); coverage `complete`.
  - `mail.storage_bytes` = sum of `Storage Used (Byte)`; coverage `complete`. Archive mailboxes are not counted; the Storage chart note says "doesn't include archive mailboxes", and the evidence text should say so. Recoverable items are a separate column and are not added.
  - `mail.item_count` = sum of `Item Count`; coverage `complete`.
  - `mail.shared_mailbox_count`: **not** from this export under D-109. It stays Unknown `needs_recipient_export`.

### 1.2 OneDrive usage

- **Where:** Microsoft 365 admin centre > **Reports** > **Usage** > **OneDrive** > tab **Usage** > **Export**. [CITED: learn.microsoft.com/…/activity-reports/onedrive-for-business-usage-ww, ms.date 2026-04-24]
- **Graph headers (verbatim):** `Report Refresh Date`, `Site URL`, `Owner Display Name`, `Is Deleted`, `Last Activity Date`, `File Count`, `Active File Count`, `Storage Used (Byte)`, `Storage Allocated (Byte)`, `Owner Principal Name`, `Report Period`. [CITED: …/reportroot-getonedriveusageaccountdetail?view=graph-rest-1.0, updated 2026-06-19]
- **Admin-centre metrics:** URL ("temporarily empty"), Deleted ("It takes at least seven days for accounts to be marked as deleted"), Owner, Owner principal name, Last activity date (UTC), Files, Active files ("Deleted users continue to appear in reports for 180 days"), Storage used (MB), **Site ID** (not in the Graph list).
- **Population caveat, quoted:** "**The report only includes users who have a valid OneDrive license.**" OneDrives of unlicensed or departed users exist and hold data, but they are not in this export.
- **Findings** (rows with `Is Deleted` false):
  - `onedrive.account_count` = rows; **coverage `partial`** (Microsoft documents the omission).
  - `onedrive.storage_bytes` = sum of `Storage Used (Byte)`; coverage `partial`.
  - Both will read as lower bounds ("at least"). Open Question 4 offers the alternative.

### 1.3 SharePoint site usage

- **Where:** Microsoft 365 admin centre > **Reports** > **Usage** > **SharePoint** > tab **Site usage** > **Export**. [CITED: learn.microsoft.com/…/activity-reports/sharepoint-site-usage-ww, ms.date 2026-07-30]
- **Graph headers (verbatim):** `Report Refresh Date`, `Site Id`, `Site URL`, `Owner Display Name`, `Is Deleted`, `Last Activity Date`, `File Count`, `Active File Count`, `Page View Count`, `Visited Page Count`, `Storage Used (Byte)`, `Storage Allocated (Byte)`, `Root Web Template`, `Owner Principal Name`, `Report Period`. [CITED: …/reportroot-getsharepointsiteusagedetail?view=graph-rest-1.0]
- **Admin-centre extras:** Site sensitivity label ID, External sharing, Unmanaged device policy, **Geo location** ("The Geo location of the site"), Anonymous link count, Company link count, Secure link for guest count, Secure link for member count. The drill-down gives "per-site level details for all sites". Microsoft warns that the list can differ from **Sites > Active sites** "because certain site templates and URLs aren't included as Active sites". The URL "doesn't display if Bring Your Own Key (BYOK) or Customer Lockbox is enabled".
- **Findings** (rows with `Is Deleted` false):
  - `sharepoint.site_count` = rows; coverage `complete`.
  - `sharepoint.storage_bytes` = sum of `Storage Used (Byte)`; coverage `complete`.
  - `sharepoint.file_count` = sum of `File Count`; coverage `complete`.
  - Whether OneDrive personal sites appear in this export is **not documented** [ASSUMED: they do not]. The real export should be checked for a `Root Web Template` value of `SPSPERS`.

### 1.4 Teams team usage ("Microsoft Teams team activity")

- **Where:** Microsoft 365 admin centre > **Reports** > **Usage** > **Microsoft Teams** > tab **Team usage** > **Export**. [CITED: learn.microsoft.com/…/activity-reports/microsoft-teams-usage-activity, ms.date 2026-04-03]
- **Graph headers (column list):** `Report Refresh Date`, `Team Name`, `Team Id`, `Team type`, `Last Activity Date`, `Report Period`, `Active users`, `Active Channels`, `Guests`, `Reactions`, `Meetings Organized`, `Post Messages`, `Reply Messages`, `Channel Messages`, `Urgent Messages`, `Mentions`, `Active Shared Channels`, `Active External Users`. The example line on the same page writes `Team Type` and `Active Users`. **The case differs within one Microsoft page, so match headers case-insensitively.** [CITED: …/reportroot-getteamsteamactivitydetail?view=graph-rest-1.0, updated 2025-07-23]
- **What the columns mean:** "Active channels: Valid channels in active teams that have at least one active user in the specified time period." "Active guests: Guests that have at least one panel action in the specified time period." [CITED: Teams team usage page]. The Teams reporting reference: "The Teams reports show data for active users and active channels … if a user … isn't active … data for that user isn't included", and active users in the Teams usage report are counted "only within active Teams". [CITED: learn.microsoft.com/en-us/microsoftteams/teams-analytics-and-reports/teams-reporting-reference, ms.date 2026-08-03]
- **Findings:**
  - `teams.team_count` = distinct `Team Id` rows; **coverage `unknown`**. Microsoft does not document that teams without activity appear in the details table; the chart counts them but the table is undocumented. The result reads as a lower bound.
  - `teams.teams_with_guests_count` = teams with `Guests` > 0; **coverage `unknown`**, because only *active* guests are counted. A positive value confirms the `teams-guests` rule (Needs work). Zero never makes Teams Ready.
  - `teams.channel_count`: **Unknown `not_in_export`**. The export carries active channels only, not the channel count.
  - The guide should ask for the **180-day** period, which lists the most teams.

### 1.5 Licensed headcount (MODL-05): Microsoft 365 apps > Active users

- **Where:** Microsoft 365 admin centre > **Reports** > **Usage** > **Microsoft 365 apps** > tab **Active users** > **Export**. [CITED: learn.microsoft.com/…/activity-reports/active-users-ww, ms.date 2026-05-19]
- **Graph headers (verbatim):** `Report Refresh Date`, `User Principal Name`, `Display Name`, `Is Deleted`, `Deleted Date`, `Has Exchange License`, `Has OneDrive License`, `Has SharePoint License`, `Has Skype For Business License`, `Has Yammer License`, `Has Teams License`, `Exchange Last Activity Date`, `OneDrive Last Activity Date`, `SharePoint Last Activity Date`, `Skype For Business Last Activity Date`, `Yammer Last Activity Date`, `Teams Last Activity Date`, `Exchange License Assign Date`, `OneDrive License Assign Date`, `SharePoint License Assign Date`, `Skype For Business License Assign Date`, `Yammer License Assign Date`, `Teams License Assign Date`, `Assigned Products`. [CITED: …/reportroot-getoffice365activeuserdetail?view=graph-rest-1.0]
  - **No `Report Period` column** is documented for this report.
  - The admin-centre page names Viva Engage where Graph says Yammer. Admin-centre header spelling is **UNVERIFIED**.
- **Finding:**
  - `directory.licensed_user_count` = rows with `Is Deleted` false and a non-empty `Assigned Products`.
  - Collector `directory`, source `import.active_users`.
  - It is a state as of `Report Refresh Date`. Record it with `period` = `<refresh>/<refresh>` (one day) and `collected_at` = the refresh date. [ASSUMED modelling choice; see §4.4]
  - Coverage `unknown` until a real export shows whether every licensed user is listed. Microsoft does not document whether users whose only licence is outside the tracked services appear.
- **Why not "Users > Active users > Export users":** the columns are undocumented and changed recently. A Tech Community thread reports the export "lost some columns and no longer put a delimiter between license values". It is also a snapshot with no stamp. [CITED: techcommunity.microsoft.com/discussions/microsoft-365/m365-user-export-csv-format-changed/4358508; secondary]

### 1.6 Optional: Entra "Download users" and "Download groups" (directory counts)

D-98 does not list these. They are recorded here because they are the only **documented** exports that carry `directory.user_count`, `directory.guest_count` and `directory.group_count`.

- **Download users:** Entra admin centre > Microsoft Entra ID > **Users > All users > Download users**. The documented attributes include `userPrincipalName`, `displayName`, `objectId`, **`userType`**, `accountEnabled`, `usageLocation` and others. A preview adds "Assigned licenses" and "Preferred data location" columns. "Both admin and standard users can download user lists." [CITED: learn.microsoft.com/en-us/entra/identity/users/users-bulk-download, updated 2026-03-25]
- **Download groups:** columns `Object ID`, `Display name`, `Mail`, `Group type`, `Membership type`. [CITED: …/groups-bulk-download, updated 2026-03-25]
- Both are snapshots with no stamp (§4.4).
- **Recommendation:** leave them out of v1 unless the founder adds them. Without them, `directory.user_count`, `guest_count` and `group_count` stay Unknown with `source_not_supplied`.

### 1.7 Findings no supported export carries

| Finding | Reason | Note |
|---|---|---|
| `teams.channel_count` | `not_in_export` | Only active channels are exported |
| `mail.shared_mailbox_count` | `needs_recipient_export` (D-109) | Until an Exchange recipient export is imported |
| `directory.user_count`, `directory.guest_count`, `directory.group_count` | `source_not_supplied` | Unless the Entra downloads (§1.6) are added |
| `telephony.in_use` (measured route) | `source_not_supplied` | Answer route via inputs.yaml remains |
| `office_files.kind.*`, `device_management.*`, `integrations.application_count` (measured routes) | `source_not_supplied` | Answer routes remain |
| Answer-only findings (`*.in_use`, `*_reviewed` …) | `answer_not_provided` in the scan | `evidence.combine` lets inputs.yaml answers replace these at report time |

`not_in_export` belongs only to a finding whose export *was imported* but does not carry the figure. A finding whose export was not supplied gets `source_not_supplied`. Both codes already exist in `codes.reasons` [VERIFIED: src/fazit/rules/findings.yaml:476-498 on report-redesign: `- not_in_export` … `- source_not_supplied` … `- needs_recipient_export` … `- not_recognised`].

### 1.8 Admin-centre export versus the Graph CSV

| Aspect | Graph report CSV (documented) | Admin-centre Export (documented) | Status |
|---|---|---|---|
| Header strings | Verbatim lists above | Not published; on-screen labels differ ("Storage used (MB)") | **UNVERIFIED**; real export needed |
| Extra columns | — | Mailbox "Recipient type"; OneDrive and SharePoint "Site ID"; SharePoint "Geo location", sharing counts | **UNVERIFIED** in the export file |
| Column choice | Fixed | "To add or remove columns from the report, select **Choose columns**" | Unknown whether Export honours the choice. The guide should say "keep the default columns" |
| Encoding, BOM, delimiter | `Content-Type: application/octet-stream`; nothing stated | "an Excel .csv file"; nothing stated | **Undocumented** (§2) |
| Concealment | Applies ("This setting also applies to … Microsoft Graph") | Applies | Documented (§3) |

## 2. Localisation, encoding, BOM and delimiter

- **Localisation of headers:** **not documented.** The German Learn page for mailbox usage is a machine translation (`ms.translationtype: MT`) of the on-screen labels, not of the export ("Empfängertyp", "Verwendeter Speicher (MB)"). It proves nothing about the CSV. [CITED: learn.microsoft.com/de-de/…/mailbox-usage]. No Microsoft page says whether an export made with the admin centre set to German has German headers. Searches for German header strings found nothing.
- **Encoding, BOM, delimiter:** **not documented** for any admin-centre export. For contrast, Microsoft's licensing CSV is UTF-8 **with BOM** (`EF BB BF`), comma, CRLF [VERIFIED: downloaded file, first bytes inspected 2026-11-22]. That shows only how one Microsoft download is encoded.
- **Proposed coping strategy (deterministic, matches D-97, D-99, D-101):**
  1. Register the **English Graph header names** as the canonical signature, compared after Unicode NFC normalisation, whitespace trimming and `casefold()`.
  2. Register additional variants only from an observed real export (header row only). Record in `tests/fixtures/import/README.md` "observed in a test tenant on DATE, admin centre language LANG". D-113 asks fixtures to cite a Learn page; an observed variant has no page to cite, so it needs that recorded observation instead (Open Question 5).
  3. When a file's header contains **none** of any layout's required columns, refuse it with the D-99 sentence plus one hint sentence: "If the admin centre was set to another language, switch it to English and export again." The file is named; header cells are never echoed.
  4. **Value localisation is a second risk.** `Is Deleted` values (`True`/`False` in Graph JSON terms), the recipient types in an EAC export ("Shared mailbox" or "Freigegebenes Postfach"?) and date formats may be localised. Register value variants per layout, as with headers.
- **Windows-1252:** German Excel's plain "CSV (Trennzeichen-getrennt)" saves in the ANSI code page with semicolons; "CSV UTF-8" saves UTF-8 with BOM [ASSUMED from common Excel behaviour; not verified on a Microsoft page this session]. D-101 accepts UTF-8 and UTF-16 only. **Recommendation: keep refusing Windows-1252**, for three reasons:
  - It cannot be validated, because every byte decodes, so mojibake would pass silently.
  - Any non-ASCII name in a cell makes strict UTF-8 decoding fail anyway, so the refusal triggers reliably.
  - The guide's instruction ("use the original download; if you opened it in Excel, save as 'CSV UTF-8 (durch Trennzeichen getrennt)'") is simple.
  The refusal sentence names the file and says how to re-save it.
- **German Excel re-saves damage more than the encoding.** Excel writes the displayed text:
  - Integers above 11 digits in "General" format become scientific notation (`1,07374E+11`), so byte columns lose precision.
  - Dates become `20.11.2026`.
  - D-101's promise "re-saved by German Excel still imports" can hold for delimiter, BOM and `DD.MM.YYYY` dates. It **cannot** hold for scientific-notation numbers, which must be refused, naming the column.

## 3. Concealed identifiers

- **Setting:** Microsoft 365 admin centre > **Settings** > **Org Settings** > tab **Services** > **Reports** > checkbox "**Conceal user, group, and site names in all reports**" (older label "Display concealed user, group, and site names in all reports"). It has been on by default since 1 September 2021 and also applies to Graph, Power BI and the Teams admin centre reports. [CITED: activity-reports overview, updated 2026-11-17; reports-show-anonymous-user-name troubleshooting article, ms.date 2026-04-16]
- **What becomes concealed** (Microsoft's table): "User IDs, Usernames, and User principal names" in user-level reports; "Site IDs and Site URLs" in the OneDrive and SharePoint site usage reports; "Group IDs and Group names" in the Microsoft 365 Groups report; "Team names" in the Teams team usage report. The SharePoint example adds that the "Site URL and Owner display name" were concealed. [CITED: activity-reports overview; TechNet wiki archive 54445, Microsoft-hosted, secondary]
- **Hash format:** "The Global administrator can hide identifiable information (**using MD5 hashes**) such as display name, group name, email, and Microsoft Entra user ID in the report **and its export**." [CITED: teams-reporting-reference]. A Microsoft employee's blog comment says the same: "we use MD5 hashing to anonymize the UPN" (techcommunity, 2022-12-21; secondary). A published example value is `A6968D016DB2256910FD3B85B4B0457B`: 32 upper-case hex characters (office365itpros.com; secondary). Microsoft does not state the case or whether values are salted.
- **Roles:** Global Reader and Usage Summary Reports Reader never see identifiable data (techcommunity post). Reports Reader sees names only when the setting is off. Recommend that the guide names **Reports Reader** with concealment left on: Fazit works the same, and fewer names ever reach the officer's disk.
- **Detection rule (per export, three states, never affects a count):**
  - Identifier columns per layout: mailbox `User Principal Name`; OneDrive `Owner Principal Name` (Site URL is "temporarily empty"); SharePoint `Owner Principal Name` and `Site URL`; Teams `Team Name`; active users `User Principal Name`.
  - Consider only non-empty cells in those columns:
    - every one matches `^[0-9A-Fa-f]{32}$` → `concealed: true`;
    - none matches → `false`;
    - no non-empty cells, or a mix → `null`, shown in the report as "could not be determined".
  - A tri-state is needed because SharePoint URLs are blank under BYOK or Customer Lockbox, and OneDrive URLs are documented as temporarily empty.

## 4. Licences, the product roster and the snapshot stamp

### 4.1 The licence export

- **Billing > Licenses:** Microsoft documents the page and that it "might show an aggregate total of licenses for all subscriptions for the same product name" (one row per product name across subscriptions) [CITED: learn.microsoft.com/…/admin/manage/assign-licenses-to-users, ms.date 2026-02-19]. **No Microsoft Learn page documents a CSV export of the licence summary or its columns.** Searches turned up only community threads. The on-screen identifiers are **product display names** ("Office 365 E3"). The licensing reference: "When managing licenses in the … Microsoft 365 admin center, you see product names that look something like *Office 365 E3*." [CITED: licensing-service-plan-reference]
- **No admin-centre export lists service plans.** Service plans appear in the licensing CSV (per product) and in Graph `subscribedSku.servicePlans`.
- **Documented alternative (not an admin-centre export):** Microsoft Graph PowerShell `Get-MgSubscribedSku`. Its output gives `SkuPartNumber`, `SkuId`, `ConsumedUnits` ("Number of licenses that you've assigned") and `PrepaidUnits.Enabled` ("Number of licenses that you've purchased"), plus `ServicePlans`. It requires `Organization.Read.All`. [CITED: learn.microsoft.com/…/enterprise/view-licenses-and-services-with-microsoft-365-powershell, updated 2026-11-19]. The administrator signs in with Microsoft's module, never with Fazit. This route would give SKU identifiers and plans without the roster lookup, but it is a script, not a download (Open Question 1).

### 4.2 Microsoft's licensing CSV (for D-110)

- **Download URL:** `https://download.microsoft.com/download/e/3/e/e3e9faf2-f28b-490a-9ada-c6089a1fc5b0/Product%20names%20and%20service%20plan%20identifiers%20for%20licensing.csv`. Linked from the Learn page, which says "This information was last updated on August 19, 2026". The HTTP `Last-Modified` header reads Wed, 19 Aug 2026 20:25:33 GMT. [VERIFIED: downloaded 2026-11-22, 1,134,334 bytes, SHA-256 `a7a0facf663be9d1ce880ff570188c8f186b15d192a79482d661822d9ce9b9e5`]
- **Columns (verbatim):** `Product_Display_Name,String_Id,GUID,Service_Plan_Name,Service_Plan_Id,Service_Plans_Included_Friendly_Names`. UTF-8 with BOM, CRLF, one row per (product, service plan). [VERIFIED: file inspected]
- **Counts:** 6,002 rows; 620 product GUIDs; 796 distinct service-plan GUIDs. Free and education products are present (`FLOW_FREE`, `TEAMS_FREE`, "Office 365 A1 for students" …).
- **Duplicates and defects the generator must handle** [VERIFIED: file inspected]:
  - **15 display names map to two GUIDs each**: "Microsoft 365 Business Basic", "Microsoft 365 Apps for Business", "Microsoft 365 Business Standard EEA (no Teams)", "Microsoft 365 F1", "Visio Plan 1", "Visio Plan 2", "Windows 10/11 Enterprise E3", "Microsoft Copilot for Microsoft 365", "Azure Information Protection Plan 1", and 6 Dynamics or GCC products. A licence-export row with one of these names is ambiguous and is kept as not classified (D-111).
  - **3 GUIDs carry two display names** (renames, for example "Power Virtual Agent User License" and "Microsoft Copilot Studio User License", both `VIRTUAL_AGENT_USL`). The roster should keep every display name per GUID, because the admin centre may show either.
  - **One String_Id maps to two GUIDs:** `MCOPSTN5`. D31 already allows this.
  - **8 service-plan GUIDs carry inconsistent names:** `'ATP_ENTERPRISE '` with a trailing space; `'RMS_S_ENTERPRISE)'`; `'Deskless'` and `'DESKLESS'`; a name containing tab characters; `'EXCHANGE_S_FOUNDATION PBI_PREMIUM_EM1_ADDON'`. The generator must normalise (strip, collapse whitespace) and key plans by GUID, choosing one canonical name deterministically.
  - Display names contain non-ASCII characters (`Dynamics 365 Operations – Activity`, with an en dash). Compare names after NFC, NBSP-to-space and casefold, as `catalogue.sku_key` already does for part numbers.
- **Licence terms:** download.microsoft.com content falls under the Microsoft Terms of Use: "use of such Documents from the Services is for informational and non-commercial or personal use only" and "Unless otherwise specified, the Services are for your personal and non-commercial use" [CITED: microsoft.com/en-us/legal/terms-of-use, last updated 2022-02-07]. The same table is published as Learn documentation in the `MicrosoftDocs/entra-docs` repository (`docs/identity/users/licensing-service-plan-reference.md`). That repository's README grants "a license to the Microsoft documentation and other content in this repository under the Creative Commons Attribution 4.0 International Public License", although its `LICENSE` file contains MIT text [VERIFIED: GitHub API and raw files, 2026-11-22].
  - **Recommendation:** do **not** commit Microsoft's CSV. Commit only the generated roster (identifiers and names), with the source URL, download date and SHA-256 (D-110), and an attribution line naming the Learn page.
  - The claim that identifiers and names are factual data, low-risk to republish with attribution, is [ASSUMED]. It is not legal advice; the founder confirms (Open Question 6).
- **Classification size:** the hand-made classification currently names 167 plans in `service_plans.yaml`, with rosters for about 53 products. D-110's coverage test then requires a workload (or explicit `null`) for all **796** plans in the roster, plus an add-on or bundled signal per product and plan pair (6,002 pairs).
  - That is too much hand data for one plan unless the signal is derived. One option: each product gets one default signal (`add_on` for a standalone product, `bundled` for a suite), with per-pair overrides.
  - The derivation rule is a judgement call for the founder (Open Question 7). Budget a separate data plan for it.

### 4.3 Matching export rows to the roster (D-111)

1. Normalise the display name (NFC, NBSP to space, trim, casefold).
2. Look it up in the roster's name index:
   - exactly one GUID → `Product(sku_part_number, sku_guid, purchased, assigned, service_plans=<roster plans>)`;
   - zero or more than one → `Product(None, None, purchased, assigned, ())`. The report already shows it as "Unregistered product N" and reasons `licence_not_classified` (see `_public_product` and `_licence_rows` on report-redesign).
3. Service plans come from Microsoft's product definition (the roster), not from the tenant. The export record for `import.licences` must say so, and `docs/scan-format.md` must state it. Per-user disabled plans do not change what a product includes, so classification by product and plan stays valid. [ASSUMED interpretation; Open Question 8]
4. **Coverage:** `unknown`, until a real export and a Microsoft statement show that the page lists every subscribed SKU, including free, trial and self-service ones. With `unknown`, `licence_findings` keeps positive assignments and leaves inferred absences Unknown (`coverage_unknown`). That is the honest default.

### 4.4 D-106: collection stamps, and whether reconciliation can be met

**What exports carry** [CITED: the pages in §1; absence-based claims are marked]:

| Export | Date in file | Time with offset in file | Period in file |
|---|---|---|---|
| Mailbox, OneDrive, SharePoint, Teams usage | `Report Refresh Date` (documented) | none documented | `Report Period` (documented) |
| Active users | `Report Refresh Date` | none documented | none documented |
| Billing > Licenses export | **no observation** (layout undocumented) | no observation | — |
| EAC Mailboxes export | no observation | no observation | — |
| Entra Download users or groups | none in the documented attributes | none | — |

**Proposed honest rule:**

1. **Period exports.** `collected_at` = `Report Refresh Date`, date only. `period` = `refresh − (N − 1) days / refresh`, where N is the value of `Report Period`, which must be one of 7, 30, 90 or 180 and the same on every row.
   - D31 accepts date-only stamps for period-based measurements, so no rule changes.
   - That the period ends on the refresh date, inclusive, is [ASSUMED]. Microsoft does not document the boundaries, and the town sample uses the same convention (`2026-05-06/2026-11-01`).
   - A refresh date later than the run's date stops that file with a sentence ("the export's refresh date is after the date of this run; check the computer's clock"), because D31 would reject it (`collection_after_scan`).
2. **Active users (state on a date).** `period` = `refresh/refresh`, `collected_at` = refresh date. A date alone never establishes a shared instant (D31), so the licence cross-check returns `licence_directory_unverified`. `_directory_cross_check` already does this for any headcount with a period [VERIFIED: src/fazit/licences.py:295-301: `or accounts.period is not None` / `or not same_collection_time(accounts.collected_at, licences.collected_at)` → `return "licence_directory_unverified"`].
3. **Snapshot exports with no stamp in the file** (licences, recipients, optional Entra downloads). D31 requires a clock time for measured snapshots and the licence inventory [VERIFIED: src/fazit/model.py:564-566: `collected_at=self.timestamp(row["collected_at"], "licences.collected_at", require_time=True)`], and Fazit has no honest time. Two honest options, both needing a short D31 amendment (Open Question 2):
   - **Option U, upper bound (recommended):** `collected_at` = the run's date (from the passed-in `generated_at`), date only. The export record marks it `collected_kind: "no_later_than"`, and the report writes "collected on or before {date}".
     - It is true: the file existed when the import ran.
     - It costs the officer nothing.
     - It is deterministic.
     - As a date it can never establish a shared instant.
     - D31 amendment: "An imported snapshot export that states no collection time records the scan date as the latest possible collection date. Such a stamp is shown as an upper bound and never establishes a shared instant."
   - **Option S, stated date:** the operator states the download date (a new `--exported-on` option, or an inputs.yaml field). It is recorded with `collected_kind: "stated"` and is otherwise treated like U. It changes the locked CLI signature (D-93) or the inputs file, and relies on a person's statement.
4. **Reconciliation outcome:** with any admin-centre exports, inventory and headcount never share a clock instant, so **licence reconciliation cannot be met from admin-centre exports and stays Unknown**, exactly as D31 and D-106 prescribe. Inferred licence absences stay Unknown; positive assignments count. MODL-05's "the licensed headcount … comes from an export the user can obtain" is met by §1.5. Its reconciliation half comes with Phase 3 (live `licences` and `directory` collectors at one instant).
5. **The only Phase 2 route to a real shared instant** is a CSV whose producer writes the time: for example a published PowerShell snippet (`Get-MgSubscribedSku` and a licensed-user count from one run) that adds a `Collected At` column with `Get-Date -Format o`. That is a Fazit-defined format, not an admin-centre download. It requires the Microsoft Graph PowerShell SDK, PowerShell 7 and consent for `Organization.Read.All` and `User.Read.All`. Offer it only if the founder wants reconciliation before Phase 3 (Open Question 1).

**Rejected stamps:**
- The file's modification time: not the data's time, changed by copies and Excel re-saves, and read from the filesystem deep inside, which breaks determinism.
- The run's full time: claims a precise instant the data does not have, and would make every snapshot in one run share an instant, so reconciliation would falsely pass.
- A time parsed from the file name: free text, and D-97 forbids name-based recognition.

## 5. Exchange recipients

- **Recipient types:** the new EAC merged "Mailboxes" and "Shared" into one **Recipients > Mailboxes** list "where you can view shared mailboxes and user mailboxes under one list view". Types: User mailbox, Shared mailbox, Room mailbox, Equipment mailbox, and others. Each "has a unique value in the RecipientTypeDetails property". [CITED: learn.microsoft.com/en-us/exchange/recipients-in-exchange-online/recipients-in-exchange-online, updated 2026-10-27]
- **Valid `RecipientTypeDetails` values** for mailboxes (PowerShell): `DiscoveryMailbox`, `EquipmentMailbox`, `LegacyMailbox`, `LinkedMailbox`, `LinkedRoomMailbox`, `RoomMailbox`, `SchedulingMailbox`, `SharedMailbox`, `TeamMailbox`, `UserMailbox`. `-ResultSize` defaults to **1000** (`unlimited` returns all). [CITED: learn.microsoft.com/en-us/powershell/module/exchange/get-exomailbox, updated 2026-02-27]
- **The EAC export:** **no Microsoft Learn page documents the Mailboxes "Export" (CSV) button, its columns, whether it honours the current filter or search, or a row cap.** Third-party guides mention "Export data to CSV file" or "Export mailboxes" (codetwo.com, secondary). The header row, the recipient-type column name and its values (`SharedMailbox` or "Shared mailbox", and whether German UI localises them) are **UNVERIFIED**.
- **Filtering and truncation risk:** the list view can be filtered (for example to Shared). An export of a filtered view would undercount, and Fazit cannot detect a filter from the file.
  - Coverage stays `unknown` unless Microsoft documents that Export writes every mailbox.
  - `mail.shared_mailbox_count` = rows of type shared, coverage `unknown` (D31: shared mailboxes fit within the recipient export's coverage; mailbox usage keeps its own coverage).
  - A PowerShell route has the 1000-row default cap: any published snippet must use `-ResultSize Unlimited`.
- **Snapshot stamp:** none documented (§4.4).
- **Recommendation:** register the EAC layout only from an observed real export (step 02-00). Until then IMPT-05 is met in its "Unknown" half (`needs_recipient_export`), and the "count appears" half waits on the layout.

## 6. Data location and EU Data Boundary (DATA-01)

- **No export carries them.**
  - The **Data Location Card** is at Microsoft 365 admin centre > **Settings** > **Org settings** > **Organization profile** > **Data location**. It shows three columns per service: **Services**, **Current Geography**, **Committed Geography**. It notes when no EU Data Boundary commitment applies. "Tenant Global Administrators" can see it. [CITED: learn.microsoft.com/…/enterprise/m365-dr-data-location-card, ms.date 2026-10-08]
  - No export or download is described.
  - Per-site "Geo location" appears in the SharePoint site usage table (§1.3), but its values are undocumented and it covers SharePoint only (multi-geo). **Do not use it.**
- **Geographies relevant to DE/AT/CH** (Data Location Card names) [CITED: …/m365-dr-datacenter-locations, updated 2026-10-27]:
  - Local Region Geographies: **Germany** (Berlin, Frankfurt), **Austria** (Vienna), **Switzerland** (Geneva, Zurich).
  - Macro Region Geographies: **European Union/EFTA** ("Macro Region 4", which includes Austria, Germany, Switzerland and Norway among others) and **Europe** ("Macro Region 1").
  - Committed Geography can also read "**No Commitment**".
  - The card "displays simplified Geography names (such as 'France' or 'European Union/EFTA')".
- **EU Data Boundary scope:** "For Microsoft 365, customers with a sign-up location in a country or region in the EU or EFTA are in scope for the EU Data Boundary. However, Customers who have purchased Multi-Geo Capabilities are not in scope." EFTA includes Switzerland. [CITED: learn.microsoft.com/en-us/privacy/eudb/eu-data-boundary-learn, ms.date 2026-07-21]
- **Proposed inputs.yaml block** (registered codes, no free text; `as_of` dates it):

  ```yaml
  # EN: Data Location Card: Settings > Org settings > Organization profile > Data location.
  # DE: Karte "Datenspeicherort": Einstellungen > Organisationseinstellungen > Organisationsprofil > Datenspeicherort.
  data_location:
    # EN: Current Geography shown for Exchange Online.
    current_geography: null      # germany | austria | switzerland | european_union_efta | europe | other
    # EN: Committed Geography shown on the card.
    committed_geography: null    # germany | austria | switzerland | european_union_efta | no_commitment | other
    # EN: true if the card shows an EU Data Boundary commitment, false if it says there is none.
    eu_data_boundary: null
  ```

  - The German menu labels above are [ASSUMED]; check them against the German admin centre.
  - Register the codes as data: a `codes.geographies` list in `findings.yaml` with `geography.<code>` labels in both locales, checked by `load_catalogue`, as source labels are today.
  - The report shows them in the header's `dl.report-meta` (the redesign's place for organisation facts), marked "provided", with the inputs date. Unanswered, it shows the "what to supply" sentence with the inputs.yaml keys.
  - They are never a catalogue finding, because findings feed statuses.

## 7. Coverage semantics for exports

**Rule:** `complete` only when Microsoft documents that the export lists the whole population of the finding, deleted rows are excluded, and no needed cell failed to parse (D31: `scanned = total`, `failed = 0`, or a bare `{"kind": "complete"}`). `partial` when Microsoft documents that the export omits part of the population, or some rows failed. `unknown` when Microsoft does not say whether inactive objects appear.

| Export → finding | Coverage | Why |
|---|---|---|
| Mailbox usage → `mail.mailbox_count`, `storage_bytes`, `item_count` | complete | "exports the usage data of all users", including shared mailboxes. Room and equipment mailboxes are outside the report by definition |
| OneDrive usage → `onedrive.*` | **partial** | "only includes users who have a valid OneDrive license" |
| SharePoint site usage → `sharepoint.*` | complete | "per-site level details for all sites" |
| Teams team usage → `team_count`, `teams_with_guests_count` | **unknown** | Microsoft documents only active users, channels and guests. Whether inactive teams are listed is not documented |
| Active users → `directory.licensed_user_count` | **unknown** until a real export shows it | Inclusion rule undocumented |
| Licence summary → inventory | **unknown** until confirmed | Whether free, trial and self-service SKUs are listed is undocumented |
| EAC mailboxes → `mail.shared_mailbox_count` | **unknown** | Filters may apply; undocumented |

- **Deleted rows:** excluded from every count and sum. Their number goes into the export record (`deleted_rows`) for transparency, not into findings.
- **Period options:** for mailbox, OneDrive and SharePoint the counted columns are current state ("storage currently used"), so the period changes only which *deleted* rows appear, and those are excluded. For Teams, a longer period lists more teams with activity. The guide asks for 180 days.
- **Rows with an empty or unparsable needed numeric cell:** count them as `failed`. Coverage becomes `partial` with `scanned`, `failed` and `total`, and the collector `partial` with `coverage_partial`.
  - A *systematic* defect is a damaged file, not failed observations: scientific notation, a negative sign or a non-digit in any row of a needed numeric column. Refuse the whole file, naming the column.
- **Empty export** (header only): treat as "report not yet available". Microsoft: "Data doesn't exist for all reporting periods right away … typically become available within 24 to 72 hours". Collector `skipped` with a new reason `export_empty`; findings Unknown. Do not record a measured zero.
- **Export with only deleted rows:** a measured zero with complete coverage is consistent with D31 ("Complete coverage of an empty population can establish zero"). Storage and item sums are 0, which `requires_population` demands.

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python `csv` (stdlib) | Python ≥ 3.12 (`requires-python = ">=3.12"`) | Parse rows with a chosen delimiter | D-92 mandates it; handles quoting and embedded newlines |
| `codecs` / `bytes.decode` (stdlib) | stdlib | BOM detection; strict UTF-8 and UTF-16 decoding | No sniffing library is needed with BOM rules |
| `hashlib.sha256` (stdlib) | stdlib | File checksum for the export record (D-104) | Already used for rule-file checksums |
| `unicodedata.normalize` (stdlib) | stdlib | NFC header and name normalisation | Handles composed or decomposed umlauts in headers and names |
| `datetime.date.fromisoformat` (stdlib) | stdlib | Refresh dates | Already used across `model.py` |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `pyyaml` (existing) | as locked | `rules/exports.yaml`, `rules/products.yaml` | Through `parsing.parse_yaml` (safe_load) |
| `hypothesis` (existing dev, pinned 6.170.15) | 6.170.15 | Property tests over generated export tables | Plans 02-03 and 02-02 |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| BOM rules plus "header matches a layout" delimiter choice | `csv.Sniffer` | Sniffer guesses from content, can pick `.` or `:` on numeric data, and is not deterministic enough for refusal messages |
| Refusing Windows-1252 | Decoding cp1252 as a fallback | Silent mojibake; contradicts D-101 |

**Installation:** none. No new package.

## Package Legitimacy Audit

This phase installs **no external packages** (D-92). The roster generator is a maintainer script that uses only the standard library and reads a CSV the maintainer downloads by hand.

| Package | Registry | Age | Downloads | Source Repo | Verdict | Disposition |
|---------|----------|-----|-----------|-------------|---------|-------------|
| — | — | — | — | — | — | No new packages |

**Packages removed due to [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** none

## Architecture Patterns

### System Architecture Diagram

```
 fazit import PATH... --out DIR [--inputs --lang --profile]
          │
          ▼
 CLI: read clock once (generated_at, with offset) ─────────────────────────────┐
          │ expand directories (*.csv directly inside, sorted)                 │
          ▼                                                                    │
 for each file ── csv_reader: stat (regular file?) → size cap → read bytes     │
          │        → SHA-256 → BOM/strict decode → delimiter by header match   │
          │        → csv rows ─── refusal? ──► per-file message (named file)   │
          ▼                                                                    │
 exports.recognise(header) ── no match / missing columns ──► message:          │
          │                    closest layout + missing columns; collector     │
          │                    skipped (export_columns_missing)                │
          ▼                                                                    │
 duplicate layout across files? ── yes ──► both refused; collector skipped     │
          │                                 (export_ambiguous)                 │
          ▼                                                                    │
 aggregates.<layout>(rows) → counts, sums, deleted_rows, concealed (in memory) │
          │   strict values: integers, booleans, ISO or DD.MM.YYYY dates       │
          ▼                                                                    │
 importer.build_scan(evidence, generated_at) ◄─────────────────────────────────┘
          │  collectors (ok, partial, skipped), every catalogue finding
          │  (measured or Unknown + reason), licences via roster, exports records
          ▼
 scan_to_json → load_scan_text (same loader and D31 checks as `report`) ─ fail ─► bug: stop, write nothing
          │
          ▼
 render_report(loaded scan, inputs?) → write_files(out, {scan-DATE.json, report-DATE-LANG.html})
          │
          ▼
 print per-file lines (argument order), then the report path last
```

### Recommended Project Structure

```
src/fazit/
├── csv_reader.py       # bytes → CsvTable | InputError (size, BOM, decode, delimiter, rows, sha256)
├── exports.py          # load rules/exports.yaml → ExportLayout; recognise(header) → Match | Mismatch
├── import_values.py    # strict cell parsers: count, boolean, refresh date, concealment check
├── aggregates.py       # one function per layout: rows → ExportEvidence (findings, record)
├── importer.py         # run(paths, clock, catalogue) → ImportResult (scan text, scan, file lines)
├── rules/exports.yaml  # registered layouts with Learn URL and checked date
├── rules/products.yaml # GENERATED roster (source URL, download date, SHA-256), identifiers only
└── rules/service_plans.yaml  # becomes classification only (plan → workload; product/plan signal)
scripts/
└── generate_product_roster.py  # maintainer-only, stdlib; reads a downloaded CSV path; not in the wheel
tests/fixtures/import/
├── README.md           # each header: Learn URL + checked date (+ observed variants)
├── municipal-600/      # fictional ~600-seat organisation: one CSV per export
├── concealed/  changed-layout/  excel-de/  planted/
```

### Pattern 1: Layouts as data, recognition as one pure function

**What:** each layout in YAML names its `source`, `collector`, `kind` (`period` or `snapshot`), `required` and `optional` columns, `identifiers` (for concealment), `learn_url` and `checked_on`. `recognise()` normalises the header cells and returns the unique layout whose required set is contained in them. Otherwise it returns the closest layout (most required columns present; ties by registry order) and its missing columns.
**When to use:** every file.
**Example:**

```yaml
# src/fazit/rules/exports.yaml (sketch). Values from the Graph page, checked 2026-11-22.
exports:
  - source: import.mailbox_usage
    collector: mailbox_usage
    kind: period
    learn_url: https://learn.microsoft.com/en-us/graph/api/reportroot-getmailboxusagedetail?view=graph-rest-1.0
    checked_on: "2026-11-22"
    required: [Report Refresh Date, User Principal Name, Is Deleted, Item Count, Storage Used (Byte), Report Period]
    optional: [Display Name, Deleted Date, Created Date, Last Activity Date, Issue Warning Quota (Byte),
               Prohibit Send Quota (Byte), Prohibit Send/Receive Quota (Byte), Deleted Item Count,
               Deleted Item Size (Byte), Deleted Item Quota (Byte), Has Archive]
    identifiers: [User Principal Name]
```

A registry test must prove that no layout's required set is a subset of another layout's columns, so a header can never fully match two layouts. Mailbox usage and active users share `Report Refresh Date`, `User Principal Name` and `Is Deleted`; `Item Count` and `Assigned Products` keep them apart.

### Pattern 2: Build, serialise, reload, then write (D-107)

`importer` builds plain dicts, uses `licences.scan_to_json` (which already strips unregistered identifiers), then `model.load_scan_text(text, "scan.json", catalogue)`. The report renders from the **loaded** scan, never the in-memory one, so `report scan.json` reproduces it byte for byte. An `InputError` raised by the reload is a bug: re-raise it (or exit with an internal-error sentence), never write.

### Pattern 3: Clock and order are inputs

`run(paths, generated_at=..., catalogue=...)`; files are sorted inside directories; export records are sorted by source; findings follow catalogue order. The per-file printed lines follow argument order. A test should show that the output scan is identical whatever order the files are given in.

### Anti-Patterns to Avoid

- **Recognising by file name, or echoing header cells.** D-97 and D-99 forbid both. A header cell can contain a name or a script.
- **Using `csv.DictReader` with duplicate headers.** Later columns silently win. Refuse duplicate normalised header names.
- **Opening a FIFO or device from a directory listing.** `open()` blocks on a FIFO. Check `stat().st_mode` with `S_ISREG` before opening, and cap the read at limit + 1 bytes, as `parsing.read_text` does.
- **Clamping values.** A sum above `MAX_STORAGE_BYTES` or a count above `MAX_COUNT` is refused, never clamped [VERIFIED: src/fazit/validation.py:15-16: `MAX_COUNT = 10**12 - 1`, `MAX_STORAGE_BYTES = 2**63 - 1`].
- **Filling `collected_at` with the run's full time.** See §4.4.
- **Adding `exports: []` to every scan.** That changes the demo's scan copy and the site demo for no reason. `scan_to_json` should omit the key when it is empty, and the importer writes `schema_version: "1.1"`.

## 8. Code-change map (branch `report-redesign`)

Facts read this session from `git show report-redesign:<path>` (extracted copy). Re-check with grep at execution time.

**`src/fazit/model.py`**
- Today the top level requires exactly `_SCAN_FIELDS = ("schema_version", "tool", "generated_at", "source_kind", "collectors", "findings", "licences")` [VERIFIED: model.py:26-34] and `SOURCE_KINDS = ("sample", "import", "live")` [VERIFIED: model.py:14].
- Add a frozen `ExportRecord(source: str, sha256: str, refreshed_on: str | None, period: str | None, rows: int, deleted_rows: int, concealed: bool | None, collected_kind: str)`, where `collected_kind` is `"in_export"` or `"no_later_than"` (or `"stated"` under Option S).
- Add `Scan.exports: tuple[ExportRecord, ...] = ()`, placed before `dropped_count`.
- In `_ScanReader.scan()`, read `self.fields(value, "", _SCAN_FIELDS, ("exports",))`, then a new `exports()` method that checks:
  - each source is in `catalogue.source_codes`, starts with `import.`, and is unique;
  - `sha256` matches `[0-9a-f]{64}`;
  - `period` uses `_PERIOD`;
  - counts via `check.count`;
  - `concealed` is a bool or null;
  - a non-empty list requires `source_kind == "import"`.
- Cross-checks after findings and licences:
  - every measured finding or licence inventory with an `import.*` source has a record with the same source;
  - its `period` equals the record's `period`, and its `collected_at` equals `refreshed_on` (period exports) or the snapshot rule.
- Relax `require_time` in `finding()` (today `require_time=provenance == "measured" and period is None` [VERIFIED: model.py:380]) and in `licences()` (today `require_time=True` [VERIFIED: model.py:564-566]) **only** when the source's record has `collected_kind` other than `"in_export"`. This is the D31 amendment (Option U or S).
- `same_collection_time` needs no change: a date-only stamp has no `tzinfo`, so it returns False [VERIFIED: model.py:65-69].

**`src/fazit/licences.py`**
- `scan_to_json` (`asdict` then `del data["dropped_count"]`): also drop `exports` when it is empty.
- Add roster loading from the generated `rules/products.yaml` and a name index `{normalised display name: (part_number, guid)}` that excludes ambiguous names.
- `_directory_cross_check` stays as is; it yields `licence_directory_unverified` for import headcounts.

**`src/fazit/rules/findings.yaml` (catalogue)**
- `codes.sources`: add `import.mailbox_usage`, `import.onedrive_usage`, `import.sharepoint_site_usage`, `import.teams_usage`, `import.active_users`, `import.exchange_recipients`.
- `codes.licence_sources`: add `import.licences`.
- `measured_by` per finding: for example `mail.mailbox_count: {mailbox_usage: [sample.mailbox_usage, import.mailbox_usage]}` and `directory.licensed_user_count: {directory: [sample.directory, import.active_users]}`.
- `codes.reasons`: add `export_columns_missing`, `export_ambiguous` and `export_empty`. Optionally add `export_layout_unknown` if not reusing `not_recognised`. Note that `not_recognised` already exists and means "This version does not recognise the reason", a different meaning, so **do not reuse it** for layouts.
- `codes.geographies` (D-112). The catalogue loader's fixed key set in `_parse_catalogue` must accept it.
- The existing collectors cover every export; no new collector is needed [VERIFIED: findings.yaml:450-459: `licences, directory, mailbox_usage, onedrive_usage, sharepoint_site_usage, teams_usage, exchange_recipients, office_files, telephony`].
- `load_catalogue` already forces a `source.<code>` label in both locales for every source code.

**Locales (`en.yaml`, `de.yaml`)**
- `source.import.*` labels: "Mailbox usage export, Microsoft 365 admin centre" / "Export der Postfachnutzung, Microsoft 365 Admin Center" (draft German; native review).
- `reason.export_*` with `label` and `fix`.
- `cli.import_*` lines for the per-file messages:
  - recognised as X, with SHA-256;
  - not a CSV Fazit can read;
  - missing columns `{columns}` of `{export}`;
  - same export as `{other}`;
  - empty;
  - file too large;
  - encoding refused, with the re-save hint;
  - language hint;
  - no file recognised (stop).
- New `errors.*` codes for reader failures.
- `appendix.exports_*` for the exports table.
- `geography.*` labels; the data-location strings for the header; "on or before" wording.

**`src/fazit/cli.py`**
- `@app.command(name="import")`, since `import` is a keyword.
- `def import_exports(ctx, paths: list[Path], inputs, lang, out, profile)`.
- Read the clock once: `datetime.now().astimezone().isoformat(timespec="seconds")`.
- Call `importer.run(...)`, then `render_report(...)` with `scan_file_name="scan.json"`.
- Write through `write_files(out, {f"scan-{date}.json": text, report_file_name(...): html})`.
- Print the lines with `escape_controls` (as `_printed_path` does), then the report path last.
- Reuse `_exit_with_error`. Apply the language and profile fallback from inputs as `report()` does.
- A path containing `@` should print a neutral placeholder, as `error_sentence` does today with `private_input_file`.

**`src/fazit/report.py` and `templates/report.html.j2`**
- `_prepare_report` context gains `exports=scan.exports` and `upper_bound_sources={r.source for r in scan.exports if r.collected_kind != "in_export"}`.
- The `finding_date` macro prints "on or before" for those sources.
- The appendix gets an "Imported exports" table: label, refresh date, period, rows (deleted excluded), identifiers concealed (yes, no, could not be determined), SHA-256 in `<code>`, with `scope` headers.
- `scan_periods` already lists the periods.
- The header `dl.report-meta` gets the data-location entries.
- Follow DESIGN.md: no new section, labels not pills, status never colour alone.
- The demo output must not change. Assert the demo HTML is byte-identical before and after each plan where the import work does not touch shared strings.

**`src/fazit/inputs.py`, `inputs.example.yaml`, `docs/interview-checklist*.md`**
- Add `data_location` to `_INPUT_KEYS`, plus a `FieldNames` entry `("data_location",): ("current_geography", "committed_geography", "eu_data_boundary")`, validated by `choice(..., catalogue geographies)` and `boolean`.
- `test_inputs_example_covers_the_contract` and `test_checklist_matches_inputs_and_catalogue` will need the new keys.

**`docs/scan-format.md` and `DECISIONS.md`**
- Add a section "Imported exports (1.1)". Fix the opening sentence ("Fazit has no import command") once `import` exists.
- New entries: schema 1.1 and the import rules (D-104); the snapshot-stamp amendment to D31 (§4.4); the roster source and licence (D-110).

**Tests**
- `tests/test_import_reader.py`, `test_import_layouts.py`, `test_import_aggregates.py`, `test_import_cli.py`.
- `tests/test_privacy.py`: an import case with `NAME`, `ADDRESS`, `TOKEN` and `SINGLE_TOKENS` planted in UPN, display name, site URL and team name cells; assert with `assert_no_private_text` [VERIFIED: tests/helpers.py:16-19 define `NAME = "Erika Mustermann"`, `ADDRESS = "erika.mustermann@example.invalid"`, `TOKEN = …`, `SINGLE_TOKENS = ("ReviewMarker", "Erika_Mustermann")`].
- `tests/test_installed_package.py`: an import run under `audit_environment` with an empty audit log. Add `rules/exports.yaml` and `rules/products.yaml` to `test_wheel_contains_runtime_data`'s resource tuple.
- `tests/test_model.py`: 1.1 records valid and invalid; 1.0 scans unchanged.
- `tests/tenants.py`: default `exports=()` keeps the generator working; optionally add import-shaped tenants.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| CSV quoting, embedded newlines, quoted delimiters | Manual `split(",")` | `csv.reader(io.StringIO(text, newline=""), delimiter=d, strict=True)` | Excel quotes cells with `;`, newlines and quotes |
| Encoding detection | Byte heuristics or chardet | BOM table + strict `decode` | Deterministic; D-101 lists exactly what is accepted |
| Atomic writing, no symbolic links, stay inside `--out` | New write code | `output.write_files` | Already tested (D-94) |
| Scan validation | Checks in the importer | `model.load_scan_text` round trip | One source of truth for D31 (D-107) |
| Licence identifier privacy in output | New stripping | `licences.scan_to_json` / `_public_product` | Already strips unregistered identifiers |
| Error sentences | f-strings in Python | `InputError` + `locales/*.yaml` `errors.*` + `error_sentence` | I18N-01; one sentence naming file and field |
| Product display name to SKU | A hand list | Generated roster from Microsoft's CSV | D-110; 620 products |

**Key insight:** every hard part of this phase (encodings, quoting, D31, privacy stripping, atomic writes) already has a standard-library or in-repo answer. The importer's own job is small: recognise, count, sum, record.

## Common Pitfalls

### Pitfall 1: Header case and spelling drift
**What goes wrong:** exact string matching refuses a valid export.
**Why it happens:** Microsoft's own Teams page writes "Team type" and "Team Type". Admin-centre and Graph headers may differ, and UI language may change them.
**How to avoid:** NFC, trim and casefold before comparing. Require only the columns that are used. Register observed variants with a recorded observation.
**Warning signs:** a real pilot export refused with "missing columns" that look present.

### Pitfall 2: Excel re-save corrupts numbers and dates
**What goes wrong:** `Storage Used (Byte)` becomes `1,07374E+11`, and dates become `20.11.2026` or `11/20/2026`.
**How to avoid:**
- Integers must match `[0-9]{1,19}`; anything else refuses the file, naming the column.
- Dates: accept `YYYY-MM-DD` and the unambiguous `DD.MM.YYYY`; refuse `M/D/YYYY` and `D/M/YYYY` as ambiguous.
- The guide says: do not open the file in Excel.
**Warning signs:** the semicolon delimiter detected together with failed numerics.

### Pitfall 3: UTF-32 looks like UTF-16
**What goes wrong:** `FF FE 00 00` (UTF-32 LE) starts with the UTF-16 LE BOM `FF FE`.
**How to avoid:** check the UTF-32 BOMs first and refuse them. Decode UTF-16 strictly (`"utf-16"` with BOM present). Refuse NUL characters in decoded text.

### Pitfall 4: Huge cells, huge files, many rows
**What goes wrong:** memory or time blow-up, or Python's int conversion limit (`sys.get_int_max_str_digits()` is 4300) raising inside a parser.
**How to avoid:**
- File cap: proposal 64 MiB, checked by `stat` and by reading limit + 1.
- Row cap: proposal 500,000.
- Keep `csv.field_size_limit()` at its default of 131,072 characters and catch `csv.Error` as malformed.
- Cap digit length before `int()`.
- Check sums against `MAX_STORAGE_BYTES` / `MAX_COUNT`.
- The existing 2 MiB `MAX_FILE_BYTES` [VERIFIED: parsing.py:18] is for JSON and YAML and is too small: a 2,000-seat SharePoint or active-users export in UTF-16 can exceed it.

### Pitfall 5: Formula-prefixed cells
**What goes wrong:** nothing on output, since Fazit writes no CSV, but a `=`, `+`, `-` or `@` cell in a numeric column must not parse as a number.
**How to avoid:** strict digit patterns. Cells starting with `@` are normal in UPN columns and are read only for concealment detection, never written.

### Pitfall 6: A refresh date after the run's date
**What goes wrong:** the D31 loader raises `collection_after_scan`, and under D-107 that would look like a bug.
**Why it happens:** the export's refresh date is a UTC calendar date, while the run's date is local. Near midnight, or with a wrong system clock, they can differ.
**How to avoid:** the importer checks `refresh_date <= generated_at[:10]` per file and refuses that file with a clock sentence before building the scan.

### Pitfall 7: Selecting a single day in the admin centre
**What goes wrong:** the table shows one day's data ("up to 28 days from the current date"). The export may then carry a different or missing period.
**How to avoid:** require `Report Period` ∈ {7, 30, 90, 180}, identical on all rows; otherwise refuse the file. The guide says "choose 180 days, do not click a day in the chart".

### Pitfall 8: Mixed refresh dates or periods within one file
**What goes wrong:** one scan source would carry two stamps (MODL-05).
**How to avoid:** all rows must share one `Report Refresh Date` and one `Report Period`; otherwise refuse.

### Pitfall 9: Snapshot stamp shortcuts
**What goes wrong:** the run's time, the file's modification time or a filename date as `collected_at`. Each is invented or nondeterministic, and the run's time makes reconciliation pass falsely.
**How to avoid:** §4.4 Option U or S, recorded in the export record.

### Pitfall 10: Concealment changing a count
**What goes wrong:** deduplicating by UPN, or treating hash collisions as duplicates.
**How to avoid:** count rows, not identifier values. Teams counts distinct `Team Id` (a GUID, unaffected by concealment). A property test should show that hashing the identifier column of any table leaves every finding unchanged.

### Pitfall 11: The EAC export reflects the current filter
**What goes wrong:** an export of a list filtered to "Shared" (or a search) silently undercounts.
**How to avoid:** coverage `unknown` for the recipient export. The guide says "clear filters before Export". Never derive `mail.mailbox_count` from it (independent coverage, D31).

### Pitfall 12: The demo and site drift
**What goes wrong:** shared code (`scan_to_json`, template macros) changes demo bytes.
**How to avoid:** omit empty `exports`. Each plan runs both demos and `site/check_site.py`, and regenerates `site/demo/*` only when the report output intentionally changes.

### Pitfall 13: Printing a file name that holds a name
**What goes wrong:** D-95 prints the path as given, while D-102 forbids names in printed output.
**How to avoid:** the path is the operator's own argument, so printing it is the CLI-06 pattern. Keep the existing `@` guard (a neutral placeholder for paths containing `@`). The privacy test plants names in cell contents, not in paths.

## Code Examples

Verified patterns (standard library); sketches for the planner, not final code.

### BOM-based decoding (D-101)

```python
# Sketch. Stdlib only. Order matters: UTF-32 BOMs begin with the UTF-16 BOM bytes.
_REFUSED_BOMS = (b"\x00\x00\xfe\xff", b"\xff\xfe\x00\x00")   # UTF-32 BE / LE
def decode_export(data: bytes, file_name: str) -> str:
    if data.startswith(_REFUSED_BOMS):
        raise InputError("export_encoding", file=file_name)
    try:
        if data.startswith(b"\xef\xbb\xbf"):
            text = data[3:].decode("utf-8")
        elif data.startswith((b"\xff\xfe", b"\xfe\xff")):
            text = data.decode("utf-16")          # consumes the BOM, strict
        else:
            text = data.decode("utf-8")           # strict: cp1252 re-saves fail here
    except UnicodeDecodeError:
        raise InputError("export_encoding", file=file_name) from None
    if "\x00" in text:
        raise InputError("export_malformed", file=file_name)
    return text
```

### Delimiter chosen by the header, not by sniffing

```python
# Sketch: the delimiter is the one under which the header matches a registered layout.
def read_table(text: str, file_name: str, layouts: Layouts) -> CsvTable:
    best = None
    for delimiter in (",", ";", "\t"):
        header = next(csv.reader(io.StringIO(text, newline=""), delimiter=delimiter), [])
        result = layouts.recognise(header)          # Match or Mismatch(closest, missing)
        if isinstance(result, Match):
            return _rows(text, delimiter, result, file_name)
        best = result if best is None or result.better_than(best) else best
    raise ExportNotRecognised(file_name, best)      # message: closest export + missing columns
```

### Concealment, three states

```python
_MD5_HEX = re.compile(r"[0-9A-Fa-f]{32}")
def concealed(values: Iterable[str]) -> bool | None:
    present = [v.strip() for v in values if v.strip()]
    if not present:
        return None
    hashed = sum(bool(_MD5_HEX.fullmatch(v)) for v in present)
    return True if hashed == len(present) else False if hashed == 0 else None
```

### Period from the file (§4.4 rule 1)

```python
def report_period(refreshed: date, days: int) -> str:
    if days not in (7, 30, 90, 180):
        raise ...  # refuse: the export does not state a supported period
    return f"{(refreshed - timedelta(days=days - 1)).isoformat()}/{refreshed.isoformat()}"
```

## 9. Plan split (tracer-first, one Codex run each, about 3 tasks and ~150k tokens)

Every plan's objective states D-91 (built on `report-redesign` merged into main), and its first task checks that `docs/scan-format.md` and Licences `assessed: false` are on main.

| # | Plan | Wave | Depends on | Requirements | Tasks (≈3) |
|---|------|------|-----------|--------------|-----------|
| 02-00 | **Human step: capture real export headers** (founder, not Codex) | 0 | — | supports IMPT-01, -05, MODL-05 | From a Microsoft 365 test tenant, with the admin centre in English and then German: export each report (mailbox, OneDrive, SharePoint, Teams team usage, active users, Billing > Licenses, EAC Mailboxes; optionally Entra users and groups). Record **only** the header line, the first bytes (BOM), delimiter, line ending, the format of `Report Refresh Date`, `Is Deleted` and `Report Period` values, the byte-column format, the recipient-type values and the shape of a concealed value. No tenant data |
| 02-01 | **Tracer: mailbox usage end to end** | 1 | — | CLI-03, IMPT-01 (mailbox), IMPT-02, MODL-05 | (1) Schema 1.1 `ExportRecord` and loader checks; catalogue `import.mailbox_usage` and `export_*` reasons; locales; `scan_to_json` omits empty `exports`; DECISIONS entry plus `docs/scan-format.md` section. (2) Minimal `csv_reader` (UTF-8 with or without BOM, comma), `rules/exports.yaml` with the mailbox layout, `exports.recognise`, `aggregates.mailbox_usage`, `importer.run` with the D-107 round trip; fixture plus README citation. (3) `fazit import` command (D-93 to D-96), report source label and appendix exports table, installed-package offline run (D-114), minimal privacy import case |
| 02-02 | **Robust reading and refusals** | 2 | 02-01 | IMPT-03, IMPT-04, CLI-03 | (1) UTF-16 and UTF-32 refusal, `;` and tab via header match, size and row caps, FIFO and regular-file check, malformed CSV, strict integers, ISO and `DD.MM.YYYY` dates, sums against the maxima, single refresh date and period, refresh date after the run. (2) Closest-layout message with missing columns (D-99), language hint, duplicates → `export_ambiguous` (D-100), directory expansion, a run with every file refused writes nothing (D-95), empty export → `export_empty`. (3) Concealment detection in the export record and the report line; fixtures for concealed, changed layout, German Excel (UTF-8 BOM with semicolons; a cp1252 file refused) and planted data |
| 02-03 | **OneDrive, SharePoint, Teams, active users** | 3 | 02-02 | IMPT-01, MODL-05 | (1) Layouts and aggregators for OneDrive (partial), SharePoint (complete), Teams team usage (unknown; `channel_count` → `not_in_export`). (2) Active users → `directory.licensed_user_count` (period `refresh/refresh`); the licence cross-check yields `licence_directory_unverified`; catalogue `measured_by`. (3) Fictional 600-seat municipal fixture set; Hypothesis properties (concealment invariance, partial or unknown coverage never Ready, file order invariance) |
| 02-04 | **Product roster generator (IMPT-06, part 1)** | 2 (parallel to 02-02) | 02-01 | IMPT-06 | (1) DECISIONS entry (roster source and licence; CSV not committed); `scripts/generate_product_roster.py` (stdlib; normalises defects; keeps every display name per GUID; marks ambiguous names). (2) Generated `rules/products.yaml` with URL, download date and SHA-256; `licences.py` loads roster plus classification; `service_plans.yaml` becomes classification only. (3) Coverage test (fails on unclassified plans), with the current 167 plans kept and demo output unchanged |
| 02-05 | **Classification completion (IMPT-06, part 2, data)** | 3 | 02-04, Open Q7 decided | IMPT-06 | Classify the remaining plans (workload or `null`) and product signals by the agreed rule; the coverage test passes; native review of any new notes. Can be split again if the agreed rule leaves too many hand pairs |
| 02-06 | **Licence and recipient exports; snapshot stamp** | 4 | 02-00, 02-03, 02-05, Open Q1, Q2, Q3 decided | IMPT-01 (licences), IMPT-05, MODL-05 | (1) D31 amendment (Option U or S) in DECISIONS, the model's conditional `require_time`, "on or before" in the report. (2) Licence layout from the observed header; roster lookup with ambiguous names → not classified (D-111); purchased and assigned parsing; coverage `unknown` unless confirmed. (3) EAC recipient layout from the observed header with value variants; `mail.shared_mailbox_count` measured, coverage `unknown`; tests showing reconciliation stays Unknown and positive assignments count |
| 02-07 | **Data location (DATA-01)** | 2 (parallel) | 02-01 | DATA-01 | (1) `codes.geographies`, locale labels, catalogue loader key. (2) `inputs.py` `data_location` block, `inputs.example.yaml`, both checklists, contract tests. (3) Report header facts with origin and date, the "what to supply" sentence, both locales, demo regeneration if the header changes |
| 02-08 | **Pilot readiness and proof** | 5 | all | VALD-01, IMPT-02, CLI-03 | (1) Full privacy test over every fixture variant; installed-package test over the full fixture set; `docs/scan-format.md` final. (2) Import guide EN and DE (exports and menu paths, Reports Reader role, 180 days, don't open in Excel, concealment is fine, the command, trace one status, recalculate one cost) and a feedback form EN and DE. (3) Done-means checks, site demo regeneration if needed, **final checkpoint: wait for the founder**; VALD-01 stays open until a pilot reports |

**Ordering notes:**
- 02-01 must not wait for 02-00: the tracer uses the documented Graph headers, and 02-00's findings adjust layouts later in 02-02 and 02-03.
- 02-06 is the only plan blocked by missing Microsoft documentation.
- 02-04 and 02-07 touch no importer code and can run in parallel with 02-02.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `uv` | every Done-means command | ✓ | 0.13.9 | — |
| Python (via uv, project `>=3.12`) | all | ✓ (system 3.14.4 seen; uv manages the project interpreter) | — | — |
| git | commits | ✓ | — | — |
| PowerShell (`pwsh`) | only the optional script route (§4.4 point 5) | ✗ | — | Not needed for the recommended plan |
| Microsoft 365 test tenant | Human step 02-00 (real headers), the pilot | unknown (STATE notes Phase 3 needs one) | — | Without it, 02-06 cannot fix the licence and recipient layouts; usage layouts stay on Graph headers with an UNVERIFIED note |
| Network | none at run time; the maintainer downloads Microsoft's CSV by hand for 02-04 | ✓ for the maintainer | — | — |

**Missing dependencies with no fallback:** a test tenant (or a pilot's real export headers) for the licence and EAC layouts.
**Missing dependencies with fallback:** PowerShell (not needed unless Open Question 1 picks the script route).

## Security Domain

Config: `security_enforcement: true`, ASVS level 1, block on high.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | Phase 2 has no sign-in |
| V3 Session Management | no | — |
| V4 Access Control | no | Local CLI; reads only the paths given |
| V5 Validation, Sanitization and Encoding | **yes** | Strict decoding, the header allowlist (registered layouts), strict value patterns, size and row caps, Jinja2 autoescape, `escape_controls` for printed paths |
| V6 Stored Cryptography | partial | SHA-256 via `hashlib` as an integrity fingerprint only; no secrets |
| V7 Error Handling and Logging | **yes** | One-sentence errors from locales; no traceback without `--debug`; header cells never echoed |
| V8 Data Protection | **yes** | Aggregates only; the schema has no free-text field; `scan_to_json` strips unregistered identifiers; privacy tests |
| V12 Files and Resources | **yes** | Regular-file check (no FIFO or device), read caps, `.csv` directly inside the named directory only, writes through `write_files` (no symlinks, nothing outside `--out`) |
| V14 Configuration | yes | No network code; the installed-package audit hook blocks sockets |

### Known Threat Patterns for a local CSV importer

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| A crafted huge file or cell exhausts memory or CPU | Denial of service | `stat` plus capped read; row cap; csv field limit; digit-length cap before `int()` |
| A FIFO or device in the input directory blocks the run | Denial of service | `S_ISREG` check before `open` |
| A header or cell injects text into terminal output | Tampering | Never echo cells; `escape_controls` on paths |
| Personal data leaks into scan, report or stdout | Information disclosure | The model holds no field for it; privacy test with planted strings (D-102) |
| A doctored export produces a convincing report | Spoofing | D26: the report labels origin; the SHA-256 in the appendix lets an officer match the file; not preventable by design |
| A wrong delimiter or encoding is silently "parsed" | Tampering | Header-match delimiter choice; strict decoding; refuse otherwise |

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Admin-centre **Export** writes the same header strings as the Graph report CSV (`… (Byte)` columns) | §1, §1.8 | Every usage layout refused until variants are registered; byte values in MB would need a unit decision |
| A2 | Admin-centre exports are UTF-8 (with or without BOM) and comma-delimited | §2 | Reader must accept another encoding; D-101 change |
| A3 | Admin-centre export headers are not localised when the UI is German | §2 | German admins' files refused; registered German variants needed |
| A4 | `Is Deleted` values are `True`/`False` in the CSV | §1 | Boolean parser must accept other spellings |
| A5 | `Report Refresh Date` is written as `YYYY-MM-DD` | §4.4 | Date parser and refresh check adjusted |
| A6 | The reporting period ends on the refresh date, inclusive | §4.4 | Period strings shift by one day; D31 ordering still holds |
| A7 | SharePoint site usage excludes OneDrive personal sites | §1.3 | Site count inflated; filter by `Root Web Template` |
| A8 | The active users export lists every user with any licence | §1.5 | Licensed headcount undercounts; coverage kept `unknown` anyway |
| A9 | Service plans taken from the roster may stand in for the tenant's plan list | §4.3 | Licence signals overstated if Microsoft's product definition differs from the tenant's |
| A10 | Republishing identifiers and names from the licensing table with attribution is permitted | §4.2 | Roster must be rebuilt from the CC BY 4.0 Learn markdown instead, or dropped |
| A11 | German Excel "CSV (Trennzeichen-getrennt)" saves Windows-1252 with semicolons | §2 | Guide wording only |
| A12 | The German labels for the Data Location Card menu path | §6 | Guide and inputs comments wording only |
| A13 | Concealed values are unsalted 32-hex MD5 strings in every export | §3 | Detection yields `null` (could not be determined), never a wrong count |

## Open Questions (founder decisions)

1. **Licence export route.**
   - Known: Billing > Licenses shows product display names and can't be relied on for a documented CSV. `Get-MgSubscribedSku` is documented and gives SKU IDs, plans, purchased and assigned.
   - Unclear: the admin-centre export's columns and whether it lists every SKU.
   - Recommendation: v1 supports the admin-centre export once 02-00 observes its header. The PowerShell route waits for evidence that pilots need reconciliation before Phase 3.
2. **Snapshot stamp (D-106):** Option U (upper bound "on or before" the import date; recommended) or Option S (operator-stated date via a new option). Both amend one D31 bullet. Without a decision, licence and recipient exports cannot be stored as measured evidence.
3. **D9 versus the mailbox usage "Recipient type".** The admin-centre mailbox usage article now lists "Recipient type: Either Shared or User". If a real export carries it, the shared-mailbox count could come from the mailbox usage export (period-based, documented report), which D9 and D-109 currently rule out. Recommendation: keep D-109 for Phase 2 and record the observation; revisit with real exports.
4. **OneDrive coverage:** `partial` (recommended; Microsoft says unlicensed users' OneDrives are not in the report) or `complete` for "licensed OneDrive accounts". Partial keeps OneDrive from Ready on import alone.
5. **Observed header variants:** may fixtures and layouts register variants seen in real exports (header row only, recorded with date and UI language) when no Learn page shows them? D-113 says headers must match documentation.
6. **Roster licence:** confirm that committing a generated identifier and name roster with attribution is acceptable, and that Microsoft's CSV is not committed.
7. **Classification rule for 796 plans and 6,002 product–plan pairs:** a default signal per product (`add_on` or `bundled`) with per-pair overrides, or a full hand classification. This decides the size of 02-05.
8. **Plan lists from the roster:** accept roster-derived service plans for imported licence rows (labelled), or leave them empty, which makes every assigned product `licence_plan_list_missing` and every licence signal Unknown.
9. **Entra users and groups downloads:** add them for `directory.user_count`, `guest_count` and `group_count` (documented attributes; snapshot), or leave those Unknown in v1.

## Sources

All checked on **2026-11-22**. Page dates are from each page's metadata.

### Primary (HIGH confidence)
- Exchange mailbox usage report (admin centre). https://learn.microsoft.com/en-us/microsoft-365/admin/activity-reports/mailbox-usage?view=o365-worldwide (ms.date 2026-04-03)
- German machine translation of the same page. https://learn.microsoft.com/de-de/microsoft-365/admin/activity-reports/mailbox-usage?view=o365-worldwide
- OneDrive usage report. https://learn.microsoft.com/en-us/microsoft-365/admin/activity-reports/onedrive-for-business-usage-ww?view=o365-worldwide (ms.date 2026-04-24)
- SharePoint site usage report. https://learn.microsoft.com/en-us/microsoft-365/admin/activity-reports/sharepoint-site-usage-ww?view=o365-worldwide (ms.date 2026-07-30)
- Microsoft Teams team usage report. https://learn.microsoft.com/en-us/microsoft-365/admin/activity-reports/microsoft-teams-usage-activity?view=o365-worldwide (via /microsoftteams/teams-analytics-and-reports/teams-usage-report; ms.date 2026-04-03)
- Microsoft 365 apps active users report. https://learn.microsoft.com/en-us/microsoft-365/admin/activity-reports/active-users-ww?view=o365-worldwide (ms.date 2026-05-19)
- Usage reports overview (roles, concealment setting, deleted users). https://learn.microsoft.com/en-us/microsoft-365/admin/activity-reports/activity-reports?view=o365-worldwide (updated 2026-11-17)
- Graph getMailboxUsageDetail, v1.0 and beta. https://learn.microsoft.com/en-us/graph/api/reportroot-getmailboxusagedetail?view=graph-rest-1.0 · https://learn.microsoft.com/en-us/graph/api/reportroot-getmailboxusagedetail?view=graph-rest-beta
- Graph getOneDriveUsageAccountDetail. https://learn.microsoft.com/en-us/graph/api/reportroot-getonedriveusageaccountdetail?view=graph-rest-1.0
- Graph getSharePointSiteUsageDetail. https://learn.microsoft.com/en-us/graph/api/reportroot-getsharepointsiteusagedetail?view=graph-rest-1.0
- Graph getTeamsTeamActivityDetail. https://learn.microsoft.com/en-us/graph/api/reportroot-getteamsteamactivitydetail?view=graph-rest-1.0
- Graph getOffice365ActiveUserDetail. https://learn.microsoft.com/en-us/graph/api/reportroot-getoffice365activeuserdetail?view=graph-rest-1.0
- Teams analytics and reporting (MD5 concealment; active-only data). https://learn.microsoft.com/en-us/microsoftteams/teams-analytics-and-reports/teams-reporting-reference (ms.date 2026-08-03)
- Reports show anonymous user names (troubleshooting). https://learn.microsoft.com/en-us/office365/troubleshoot/miscellaneous/reports-show-anonymous-user-name (ms.date 2026-04-16)
- Product names and service plan identifiers for licensing. https://learn.microsoft.com/en-us/entra/identity/users/licensing-service-plan-reference ("last updated on August 19, 2026")
- The licensing CSV, downloaded and inspected. https://download.microsoft.com/download/e/3/e/e3e9faf2-f28b-490a-9ada-c6089a1fc5b0/Product%20names%20and%20service%20plan%20identifiers%20for%20licensing.csv
- entra-docs repository README and LICENSE files. https://github.com/MicrosoftDocs/entra-docs
- Microsoft Terms of Use. https://www.microsoft.com/en-us/legal/terms-of-use (last updated 2022-02-07)
- Assign or unassign licences (Licenses page aggregation). https://learn.microsoft.com/en-us/microsoft-365/admin/manage/assign-licenses-to-users?view=o365-worldwide
- Understand subscriptions and licences. https://learn.microsoft.com/en-us/microsoft-365/commerce/licenses/subscriptions-and-licenses?view=o365-worldwide
- View licences and services with PowerShell. https://learn.microsoft.com/en-us/microsoft-365/enterprise/view-licenses-and-services-with-microsoft-365-powershell?view=o365-worldwide (updated 2026-11-19)
- Recipients in Exchange Online. https://learn.microsoft.com/en-us/exchange/recipients-in-exchange-online/recipients-in-exchange-online (updated 2026-10-27)
- Exchange admin centre overview. https://learn.microsoft.com/en-us/exchange/exchange-admin-center
- Get-EXOMailbox. https://learn.microsoft.com/en-us/powershell/module/exchange/get-exomailbox?view=exchange-ps
- Download users (Entra). https://learn.microsoft.com/en-us/entra/identity/users/users-bulk-download
- Download groups (Entra). https://learn.microsoft.com/en-us/entra/identity/users/groups-bulk-download
- Microsoft 365 services data locations. https://learn.microsoft.com/en-us/microsoft-365/enterprise/o365-data-locations?view=o365-worldwide
- Data Location Card. https://learn.microsoft.com/en-us/microsoft-365/enterprise/m365-dr-data-location-card?view=o365-worldwide
- Datacenter locations by geography. https://learn.microsoft.com/en-us/microsoft-365/enterprise/m365-dr-datacenter-locations?view=o365-worldwide
- What is Microsoft 365 data residency. https://learn.microsoft.com/en-us/microsoft-365/enterprise/m365-dr-overview?view=o365-worldwide
- What is the EU Data Boundary. https://learn.microsoft.com/en-us/privacy/eudb/eu-data-boundary-learn (ms.date 2026-07-21)

### Secondary (MEDIUM confidence)
- Microsoft Tech Community, "Privacy changes to Microsoft 365 usage analytics" (2021-08-30), with an employee comment on MD5. https://techcommunity.microsoft.com/blog/microsoft_365blog/privacy-changes-to-microsoft-365-usage-analytics/2694137
- TechNet wiki archive 54445, display concealed data in the SharePoint site usage report. https://learn.microsoft.com/ko-kr/archive/technet-wiki/54445.display-concealed-data-in-sharepoint-site-usage-report

### Tertiary (LOW confidence; for orientation only)
- Concealed value example `A6968D016DB2256910FD3B85B4B0457B`. https://office365itpros.com/2021/09/09/manage-anonymized-user-data-in-microsoft-365-usage-reports/
- Changed columns in the Active users export. https://techcommunity.microsoft.com/discussions/microsoft-365/m365-user-export-csv-format-changed/4358508
- EAC mailbox export button (third-party guide). https://www.codetwo.com/kb/export-exchange-mailboxes-list/

### In-repo (read this session from branch `report-redesign`)
- `src/fazit/model.py`, `validation.py`, `catalogue.py`, `licences.py`, `parsing.py`, `cli.py`, `output.py`, `report.py`, `inputs.py`, `evidence.py`, `i18n.py`, `rules/findings.yaml`, `rules/service_plans.yaml`, `locales/en.yaml`, `templates/report.html.j2`, `docs/scan-format.md`, `tests/test_privacy.py`, `tests/test_installed_package.py`, `tests/helpers.py`, `tests/tenants.py`, `.planning/report-redesign/RR-06-PLAN.md`, `RR-03-PLAN.md`, `UI-SPEC.md`.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH. Standard library only, required by D-92.
- Export layouts (usage reports): MEDIUM. Graph headers are verbatim; the admin-centre export bytes are unverified.
- Export layouts (licences, EAC, Users export): LOW. Undocumented.
- Concealment: HIGH for the setting and MD5; MEDIUM for the exact value shape.
- Data location and EU Data Boundary: HIGH.
- Licensing CSV facts: HIGH (file inspected); licence-terms reading: MEDIUM, not legal advice.
- Architecture and code-change map: HIGH (code read this session; re-check at execution).
- Pitfalls: MEDIUM to HIGH.

**Research date:** 2026-11-22
**Valid until:** 2026-12-22 for the Microsoft pages (they change monthly); re-check the licensing CSV's "last updated" date before generating the roster.

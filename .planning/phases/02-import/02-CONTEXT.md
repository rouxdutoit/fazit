# Phase 2 context: Import

Written on 2026-11-22 by the coordinating Claude session from the project's records, so Phase 2 can be built as soon as the report redesign (RR-01 to RR-08, branch `report-redesign`) is merged into main. Decisions marked **(founder)** were confirmed by the founder; the others follow from the records named after them. These decisions are locked for planning; `01-CONTEXT.md` (D-01 to D-80), `01.1-CONTEXT.md` (D-81 to D-90) and `DECISIONS.md` still apply.

Sources read: `.planning/ROADMAP.md` (Phase 2, notes "Import before extensions" and "Final review"), `.planning/REQUIREMENTS.md`, `DECISIONS.md` (principles, D4, D7, D9, D19, D26, D31), `AGENTS.md`, `DESIGN.md`, `docs/scan-format.md` and `src/fazit/` on branch `report-redesign`, `.planning/research/launch-critique/SYNTHESIS.md`, `.planning/research/report-usefulness/SYNTHESIS.md`.

## Baseline

- **D-91:** Plans are written against the code on branch `report-redesign` (scan model `src/fazit/model.py`, D31 checks in `src/fazit/validation.py`, catalogue `src/fazit/rules/findings.yaml`, licence classification `src/fazit/rules/service_plans.yaml` and `src/fazit/licences.py`, report context `src/fazit/report.py`, CLI `src/fazit/cli.py`). No plan starts before that branch is merged into main. Each plan says so in its objective, and its first task checks that `docs/scan-format.md` and the assessed-area catalogue (Licences with `assessed: false`) are on main.
- **D-92:** Phase 2 adds no runtime dependency. CSV parsing uses Python's standard `csv` module. Any new development tool needs a `DECISIONS.md` entry first (D15, AGENTS.md).

## The command (CLI-03)

- **D-93:** `fazit import PATH... [--inputs inputs.yaml] [--lang en|de] [--profile ...] [--out DIR]`. Each `PATH` is a CSV file or a directory; for a directory, the `.csv` files directly inside it are read (not recursively). Options mean what they mean for `report`, including the language and profile fallback from `inputs.yaml`.
- **D-94:** `import` writes `scan-<YYYY-MM-DD>.json` and `report-<YYYY-MM-DD>-<lang>.html` inside `--out`, through the existing write helpers (atomic replace, no symbolic links, nothing outside `--out`). The date is the scan's `generated_at` date. The report path is printed last (CLI-06). `fazit report scan.json` rebuilds the same report from the written scan.
- **D-95:** Before printing the report path, `import` prints one line per input file: the file as the user gave it, and either the export it was recognised as or why it was not used. Messages exist in both locales (I18N-01). A run where no file is recognised stops with an error sentence and writes nothing. A run with at least one recognised export writes the scan and the report and exits 0, even if other files were refused.
- **D-96:** The clock is passed in: `generated_at` is the run's time with a UTC offset, read once in the CLI layer and handed down, so tests are deterministic (AGENTS.md "Output is deterministic").

## Recognising exports (IMPT-01, IMPT-04)

- **D-97:** An export is recognised by its header row, never by its file name. Each supported export has a registered column signature (required columns, optional columns, and any known variants Microsoft has shipped). Which exports are supported, their exact column names and their Microsoft Learn sources come from the research; fixture headers must match Microsoft's current documentation and cite the page.
- **D-98:** The v1 export set, subject to the research confirming each one exists and can be downloaded as CSV by an administrator without sign-in from Fazit: mailbox usage, OneDrive usage, SharePoint site usage, Teams usage, licences, Exchange recipients, and whichever export supplies the licensed headcount that MODL-05 requires. The Copilot and Agents usage reports and the Power Platform inventory stay out (D-87).
- **D-99:** A file whose header matches no export, or matches one export with required columns missing, produces one message that names the file and the missing columns of the closest export. That export's collector is recorded as `skipped` with a registered reason, its findings are Unknown with that reason, and every other file is still imported (IMPT-04). Extra, unknown columns are ignored; their names are not printed, because a header cell can hold anything.
- **D-100:** Two files recognised as the same export make that export ambiguous: neither is used, the message names both files, and the export's findings stay Unknown. This keeps one collection time and one reporting period per source (MODL-05).
- **D-101:** Accepted encodings and delimiters: UTF-8 with or without BOM, UTF-16 with BOM, and comma, semicolon or tab delimiters, so a file re-saved by German Excel still imports. Anything else, a file over a fixed size limit, or a malformed CSV is refused with a sentence that names the file. The exact limits come from the plan.

## Privacy (IMPT-02, IMPT-03)

- **D-102:** Aggregates only, by construction (D19). Per-user rows, user principal names, display names, site URLs and team names are read into memory only to count, sum and detect concealment, and never reach `scan.json`, the report, a file name or printed output. There is no option to keep them in v1. The privacy test (SAFE-05) gains an import case: fixtures planted with names, addresses and credential-like strings produce a scan, report and printed output without any of them.
- **D-103:** Concealed identifiers (the admin-centre privacy setting that replaces names with hashes) are detected per export. The import works the same either way, and the report says, per export, that the identifiers were concealed. Concealment never changes a count.
- **D-104:** The scan does not store input file names, because a file name is free text and could hold a person's name (D19). Each imported export is recorded with its registered source code, its reporting period and refresh date, its row count, whether identifiers were concealed, and the SHA-256 of the file's bytes. The report's evidence names the export (for example "Mailbox usage export, Microsoft 365 admin centre") and its period and coverage; the appendix lists each export with its checksum, so the officer can match it to the file that `import` printed. This is how "every figure records its source file" is met without a free-text field. It is a minor schema change (1.x) and gets a `DECISIONS.md` entry and a section in `docs/scan-format.md`.

## Evidence and consistency (MODL-05, D31)

- **D-105:** Every imported figure is `measured` with a registered `import.*` source, a collector that ran, a reporting period where the export has one, a collection stamp and coverage. Sources are registered in the catalogue next to the `sample.*` ones; the status rules do not change for imported evidence.
- **D-106:** Each collector writes one collection stamp and one reporting period per scan (MODL-05). How snapshot exports without a period (licences, Exchange recipients, the headcount export) get a clock time with a UTC offset, as D31 requires for snapshots and licence inventories, and whether licence reconciliation can be met from the exports an administrator can obtain, comes from the research. Fazit never invents a stamp; where the honest answer is "no shared instant", reconciliation stays Unknown as D31 already prescribes.
- **D-107:** The importer never writes a scan that violates D31: it builds the scan, serialises it, loads it back through the same loader and validation as `report`, and only then writes it (MODL-05). A failure there is a bug and stops with an error, never a written file.
- **D-108:** A supplied export never makes an area look more ready than the evidence allows: deleted rows are excluded, coverage is stated honestly (complete only when the export covers the whole population with no failed rows), and any figure an export does not carry stays Unknown with `not_in_export` (principle 8).
- **D-109:** The shared-mailbox count stays Unknown with `needs_recipient_export` until an Exchange recipient export is imported, then appears as measured (IMPT-05, D9). The mailbox usage and recipient exports keep independent coverage (D31).

## Licences (IMPT-06)

- **D-110:** The product roster (product names, string IDs, GUIDs and included service plans, free and education products included) is generated from Microsoft's published licensing CSV by a maintainer script that reads a downloaded copy, with the source URL, the download date and the file's SHA-256 recorded in the generated file. Fazit never downloads it at run time. Only the classification (which plan belongs to which area, add-on or bundled) is maintained by hand. A test fails when a generated product has a plan the classification does not cover, so a roster update shows what needs classifying. Whether Microsoft's CSV itself may be committed is decided in the plan from its licence; the generated roster holds identifiers and names only.
- **D-111:** The licence export is matched to products through the roster. A product name the roster does not know, or knows more than once, is kept with its counts and reported as not classified, never guessed.

## Data location (DATA-01)

- **D-112:** The report states the tenant's data location and its EU Data Boundary status as facts, with their origin (export or provided answer) and date, and never scores them or feeds them into a status. If the research finds no admin-centre export that carries them, they are provided answers in `inputs.yaml` with registered codes (no free text), added to `inputs.example.yaml` and both interview checklists. Unanswered, the report says what to supply.

## Fixtures and tests

- **D-113:** Fixtures are fictional and realistic: one fictional municipal organisation of about 600 seats (the size the critics asked for), with small committed CSV files whose headers match Microsoft's documentation, plus variants for concealed identifiers, a changed layout, a German Excel re-save and planted personal data. Large populations are generated in memory by tests. `tests/fixtures/import/README.md` cites the Microsoft Learn page for every header and the date it was checked. No real tenant data is ever committed (AGENTS.md).
- **D-114:** Import joins the offline proof: the installed-package test runs `fazit import` on the fixtures with sockets blocked (principle 2, SAFE-07).

## Pilot validation (VALD-01)

- **D-115:** Phase 2 delivers what a founding pilot needs to run the import unaided: a short guide in English and German (which exports to download from where, the command, how to trace one status and recalculate one cost from the report) and a feedback form. The pilot run itself and the revision of explanations from what pilots report are human steps: the last plan ends in a checkpoint that waits for the founder, and VALD-01 stays open until a pilot has reported. Before the launch, one operator in the 200 to 2,000 range runs the import unaided (launch critique, D).

## Words and design

- Every new string is in both locales, German written as German (formal Sie, administrative register), and each plan's SUMMARY lists new German strings for native review (DESIGN.md "Copy").
- Report changes follow DESIGN.md and the redesigned report's structure from RR-01 to RR-08. Import adds evidence lines and appendix rows; it does not add a new report section, except the data-location fact (D-112), which goes where the redesign keeps organisation facts.

## Decisions after research (2026-11-22)

Research: `02-RESEARCH.md`. Where a decision below and an earlier one disagree, the one below wins.

- **D-116 (founder):** The founder captures real export header rows from a Microsoft 365 tenant (a developer or trial tenant is enough), with the admin centre in English and then in German: the four usage exports, Microsoft 365 apps active users, Billing > Licenses, the Exchange admin centre mailbox list, and the Entra users and groups downloads. Only the header line and the format facts listed in `02-RESEARCH.md` §9 (02-00) are recorded, never tenant data. Usage layouts start from Microsoft's documented Graph headers and are adjusted from the observation; the licence, mailbox-list and Entra layouts are built only from the observation. This amends D-113: a header is cited either to a Microsoft Learn page or to a recorded observation (date, admin-centre language).
- **D-117 (founder):** The Entra admin centre "Download users" and "Download groups" files are supported exports. They measure `directory.user_count`, `directory.guest_count` and `directory.group_count`.
- **D-118:** Snapshot exports that state no collection time (licences, Exchange mailbox list, Entra downloads) record the run's date as the latest possible collection date, shown as "collected on or before {date}". Such a stamp never establishes a shared instant. This needs one D31 amendment in `DECISIONS.md`. No stamp is taken from a file's modification time, its name or the run's clock time. Consequence: licence reconciliation (D31's last bullet) cannot be met from admin-centre exports and stays Unknown in Phase 2; positive assignments still count. It arrives with Phase 3's live counts.
- **D-119:** Period exports record `collected_at` as the `Report Refresh Date` (date only) and the period as the `Report Period` days ending on that date. The active users export records its refresh date as a one-day period. A refresh date after the run's date stops that file with a sentence.
- **D-120:** The licence inventory comes from the Billing > Licenses export, matched to products by display name through the generated roster (D-110, D-111). No PowerShell route in v1. Licence coverage is `unknown` until Microsoft documents that the page lists every subscribed product.
- **D-121:** Service plans for an imported licence row come from Microsoft's product definition in the roster, and the scan format and the report say so. An ambiguous or unknown display name keeps its counts with no identifiers and no plans.
- **D-122:** Microsoft's licensing CSV is not committed. The generated roster (identifiers and names only) is committed with the source URL, the download date, the SHA-256 and an attribution line naming the Learn page.
- **D-123:** Classification: every service plan in the roster gets an explicit area or `null` by hand. A product's add-on or bundled signal is derived by one documented rule, and the existing hand-made product entries in `service_plans.yaml` stay as overrides, so the demo reports do not change.
- **D-124:** D-109 holds: the shared-mailbox count comes only from the Exchange mailbox list. If the real mailbox usage export carries a recipient-type column, 02-00 records that, and it is revisited after Phase 2.
- **D-125:** Coverage per export: mailbox usage and SharePoint site usage `complete`; OneDrive usage `partial` (Microsoft says only licensed OneDrive users are listed); Teams team usage, active users, licences, the Exchange mailbox list and the Entra downloads `unknown` unless the observation and Microsoft's documentation establish more. `teams.channel_count` stays Unknown with `not_in_export`.
- **D-126:** Encoding amends D-101: UTF-8 with or without BOM and UTF-16 with BOM are accepted; Windows-1252 is refused with a sentence that says how to re-save the file as "CSV UTF-8". A German Excel re-save in CSV UTF-8 with semicolons and `DD.MM.YYYY` dates imports; a number in scientific notation is refused, naming the file and the column. Headers are compared after Unicode NFC, trimming and case folding.
- **D-127:** Concealment is recorded per export as concealed, not concealed or could not be determined (32-hex values in the identifier columns, as in `02-RESEARCH.md` §3), and never changes a count.
- **D-128:** An export with a header and no rows is "not yet available": its collector is `skipped` with a new reason, and its findings stay Unknown. An export whose rows are all deleted measures zero with its coverage.
- **D-129:** Data location (DATA-01) is a provided answer in `inputs.yaml` with registered geography codes and an EU Data Boundary yes/no, as proposed in `02-RESEARCH.md` §6. It is shown among the report's organisation facts with its origin and date, is not a catalogue finding, and never feeds a status.
- **D-130:** The pilot guide names the Reports Reader role, the 180-day period, keeping concealment on, downloading without opening the file in Excel, and the menu path of every export.

## Deferred

- A hand-over section for the data protection officer and staff representatives (report-usefulness B7) is not part of Phase 2's requirements. Data location (DATA-01) is its first fact; the section waits for a requirement.
- Importers for Copilot and Agents usage and the Power Platform inventory (D-87).
- Per-user detail or names on request: no `--include-names` in v1 (D19).

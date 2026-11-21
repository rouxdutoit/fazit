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
- **D-01:** Source layout is `src/fazit/` following `HANDOFF.md` section 11, minus the Microsoft modules (`auth.py`, `graph.py`, `collectors/`), which arrive in Phase 3.
- **D-02:** `pyproject.toml` uses PEP 621 metadata with the `hatchling` build backend, `requires-python = ">=3.12"`, a console script `fazit`, and is managed with `uv` (`uv sync`, `uv run pytest`, `uv run ruff check`). `uv.lock` is committed.
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

### Amendments after plan review (2026-11-21)

Two independent reviews of the first plan set (a Claude plan checker and Codex GPT-6.2-Astra at max effort, see `01-REVIEWS.md`) led to these changes. Where an amendment conflicts with an earlier decision, the amendment wins.

- **D-39:** The work of the first plan is split. The report command, privacy, the offline guarantees and the visual design form their own plan after the skeleton. Phase 1 has five plans, run one at a time.
- **D-40 (replaces D-33):** Privacy is by construction, not by redaction. `scan.json` 1.x has no field for person data, no per-person rows and no free text from collectors. Reasons, units, coverage and sources are codes or logical IDs that match a fixed pattern; a source is never a URL. The only free-text field is the organisation's display name. The loader keeps only fields and finding IDs it knows; anything else is dropped, and the appendix lists the dropped names without their values. A string in `scan.json` that contains `@` is an error. There is no `--include-names` flag in v1 and no arbitrary-row renderer. Tests prove that names, addresses and credential-like strings planted in a `scan.json` reach neither the HTML, the JSON copy, the filename nor the printed path.
- **D-41:** A finding catalogue, `rules/findings.yaml`, lists every recognised finding ID with its workload, value type (non-negative integer, byte count, boolean or code), unit and label key. Values are validated against it: a boolean or a string is not a count.
- **D-42:** Each finding names the collector that produced it. Collector IDs are independent of workloads, so two sources (for example mailbox usage and an Exchange recipient export) can feed one workload with separate states.
- **D-43 (clarifies D-18):** Status is decided in this order. First, if a collector the workload needs was skipped, or a finding it needs is missing or unknown, the workload is `Unknown` and the reason names what is missing. Only then does the worst matching rule win, with ties broken by file order. No rule may turn missing evidence into `Needs work` or `Ready`. Problems that are independently confirmed stay visible as notes under an `Unknown` workload. Each workload declares the evidence that establishes `Ready`; a count alone never does. Where `Ready` needs a confirmation only a person can give, it comes from `inputs.yaml` as a provided finding, and the interview checklist asks for it.
- **D-44:** The suggested-path section gives no go or no-go verdict and uses no numeric threshold. It lists blockers, the unknowns to resolve first, and pilot candidates only as far as the evidence supports them.
- **D-45:** Mappings are by function, not by product, and each mapping row carries the URL of the project documentation it was checked against and the date of the check. For openDesk, identity management is Nubus and single sign-on is Keycloak.
- **D-46:** Measured and provided values are never merged or summed. If both exist for one finding, the measured one decides and the provided one is shown beside it, labelled. Partial observations are shown as partial with their coverage and never establish that a risk is absent. Workloads with no collector in v1 (`office_files`, `devices`, `windows_software`) can be assessed from complete provided evidence.
- **D-47:** Every write goes inside the resolved `--out` directory. The tool refuses a destination that is a symbolic link, writes to a temporary file in the same directory and renames it into place. A test plants a link to an outside file and checks that file's bytes survive.
- **D-48:** Inputs are strict. Duplicate keys in JSON or YAML and non-finite numbers are errors that name the file and field. Money values in `inputs.yaml` are quoted strings parsed with `Decimal`, so no digit is lost in parsing. A file that is unreadable, a directory or not UTF-8 produces the same one-sentence error as any other bad input.
- **D-49:** Output is reproducible. The report filename and the scan date come from `scan.generated_at`; rendering reads no clock. A provided answer carries its own `as_of` date or is shown as "date not supplied". A test renders the same inputs under two system dates and compares filenames and bytes.
- **D-50 (fixes the cost model left open in D-21 and D-22):** Scenario blocks sit under `target_costs` and each has a `users` value; the flat keys of `HANDOFF.md` section 7 are not accepted. Hosting is paid from month one for all 60 months. Full current licences are paid during the months of parallel running in both exit scenarios; retained licences are paid for the remaining months. Other IT cost is the same in all three scenarios. An unknown input makes a total unknown only if it is multiplied by something other than zero. A difference against "stay" is unknown whenever "stay" is unknown. Amounts are rounded only for display, and totals are computed from unrounded values.
- **D-51:** Sample data is labelled where the reader sees it: in the header and on each table that shows simulated measurements. Whether prices are invented is tracked separately from where the scan came from, so real prices used with a sample scan are not called invented. The header states what this command did (rendered locally from the named file, contacted no host) and makes no claim about how a `scan.json` from elsewhere was produced. The town sample explains how staff, accounts and guests relate.
- **D-52:** The offline proof is strict. Tests fail on any socket creation, including name lookups, and one test runs the built package installed outside the checkout. The HTML check also covers automatic refresh, external references in CSS and inline style attributes. The README says plainly that installing needs the network once.
- **D-53:** Removed from the plans: the human approval gate for the six packages (settled by D-02, D-03 and `DECISIONS.md` D15 to D17), the arbitrary-row renderer, the 50% threshold, the numeric-literal whitelist and stale-baseline checks, and the licence length and tag checks. The licence is verified by the checksum of the canonical text and by the built package's metadata. Helpers used only by tests live in `tests/`. `--version` stays.
- **D-54:** `--rules DIR` is deferred to Phase 4. Success criterion 4 is proven by editing a rule in a clone and running the documented command. `SECURITY.md` promises private vulnerability reporting only in words that are true before the repository is public.
- **D-55:** Messages use the language given by `--lang` if present, otherwise English. Command help is English (`DECISIONS.md` D18).
- **D-56:** The readiness table shows reporting period and coverage with each piece of evidence. Verify commands use a fresh temporary output directory and assert exit code, file existence and content separately.
- **D-57:** Plans are executed by Codex. They reference plain file paths, not include syntax. The summary of each plan records the final public signatures the next plan depends on.

### Amendments after the competitor and reference teardown (2026-11-21)

A teardown of comparable tools, paid assessment offers and two public evaluations (Zurich's openDesk evaluation and the study for Digitale Verwaltung Schweiz) showed where this design was thin. These additions are data and wording wherever possible.

- **D-58:** Every `Unknown` carries a reason code and a fix. Codes are a fixed list (for example `not_in_export`, `permission_denied`, `not_licensed`, `not_collected_in_this_version`, `answer_not_provided`), and their labels and fix texts are locale strings. A check that did not run is never counted as passed or failed.
- **D-59:** The workload list grows from nine to fifteen: `licences`, `directory`, `mail`, `onedrive`, `sharepoint`, `teams`, `office_files`, `device_management` (replaces `devices`; covers management, not only counts), `windows_software`, `power_platform`, `telephony`, `identity_access`, `security_compliance`, `small_apps` (Forms, Planner, Bookings and similar) and `integrations` (business applications connected to Microsoft 365). Adding a workload must be a data change only.
- **D-60:** Licences are modelled as a list of products with purchased and assigned counts and the service plans each contains. `rules/service_plans.yaml` maps service plan identifiers to workloads with a signal of `bundled` or `add_on`, and each row cites Microsoft's licensing reference page and the date it was checked. A bundled plan proves entitlement, not use: the workload is `Unknown` with the reason "licensed, use not measured". An assigned add-on (for example Teams Phone) is evidence of use and gives at least `Needs work`.
- **D-61:** Each mapping row states how well the target covers the function, on the eight-step ladder used in Zurich's evaluation: in the suite; in the suite with limits; announced; the component vendor's own solution; open source community solution; open source third party; proprietary third party; not available. The report prints the check date beside every mapping, and lists the functions that cannot be moved (for example Teams chat history, VBA macros, SharePoint workflows) under "Needs attention".
- **D-62:** A measured figure's coverage is an object with a kind code and, where known, the numbers scanned, failed and total. Partial coverage is printed as numbers, not hidden.
- **D-63 (extends D-50):** The cost comparison is shown in three blocks, following the Swiss study: direct project cost, productivity loss, and parallel running. Inputs per exit scenario add: application adaptation, external advice, training as days per person times day rate times staff, productivity loss, operations (staff or service) per year, and other recurring cost per year. Every category must be answered with an amount or an explicit zero; an unanswered category is "not provided" and makes the affected block unknown. The three scenarios stay as they are. A "second source" scenario (keep Microsoft 365 and build a fallback) is deferred and noted in `DECISIONS.md`.
- **D-64:** Still nine top-level report sections. Inside them: "Readiness" gains a "Not examined" list (each item with its reason code and fix), "Needs attention" gains "Cannot be moved", and the appendix gains run details (tool version, checksums of the rule files used, input files with their dates and periods). The header and the README say how to check the offline claim: disconnect and run it.
- **D-65:** Four status rules are required content: Teams Phone add-on assigned and no telephony replacement provided is a `Blocker`; premium Power Platform licences assigned is `Needs work`; an unknown number of integrated applications is `Unknown`; macro-capable files present is `Needs work`, with a note that estimating the effort needs a content scan this tool does not do.

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

### Planner interpretations accepted by the orchestrator (2026-11-21)

- Phase 1 has seven plans, not five (D-39).
- One `as_of` date per `inputs.yaml`, applied to every provided finding (D-49).
- An assigned Teams Phone add-on with no answer about a replacement is `Unknown`, with the add-on shown as a note; it is a `Blocker` only when the answer says no replacement is available (D-65 read with D-43).
- Running cost is shown above the three blocks, which hold the cost of the change (D-63).
- `generic` mapping rows cite no project page and say so in the report (D-45, D-61).
- The appendix lists dropped field names only when they are plain lower-case identifiers; others are counted (D-40).
- Service plan identifiers are verified by the executor against Microsoft's page at build time (D-60).
- The installed-package offline test needs `uv` and a prior `uv sync` (D-52).

### Amendments after the second plan review (2026-11-21)

Codex GPT-6.2-Astra re-checked the rewritten plans (`01-REVIEWS-2.md`) and found four blockers and six majors. These amendments resolve them. They win over every earlier decision, over `SKELETON.md` and over the plan text; each affected plan carries a "Corrections after the second review" section that applies them task by task.

- **D-66 (replaces the order in D-43; RULE-03 reworded):** A workload's status is decided in three steps. (1) Problem rules whose own evidence is complete may fire; the worst one that fires sets the status, ties broken by file order. (2) If no problem rule fires and any evidence the workload needs is missing, unknown, partial, or comes from a skipped collector, the status is `Unknown`. (3) Only if every needed piece of evidence is present and complete, and no problem fires, is the status `Ready`. Whenever evidence is incomplete, the workload is marked "incomplete" next to its status, whatever the status is, and the missing items are listed with their reason codes. So a confirmed problem is never hidden behind `Unknown`, and missing evidence is never hidden behind a problem. Required tests: town mail shows the confirmed problem with "incomplete" and the missing recipient export listed; an assigned premium Power Platform add-on with the usage question unanswered is `Needs work`, incomplete; an assigned Teams Phone add-on with the replacement question unanswered is `Unknown`; one Windows-only application confirmed without a web version plus one unanswered entry is `Blocker`, incomplete, showing one confirmed and one unanswered.
- **D-67 (extends D-46 and D-62):** Coverage kinds are `complete`, `partial` and `unknown`. When counts are given they must satisfy `scanned + failed <= total`, and `complete` requires `failed == 0` and `scanned == total`; anything else is an input error naming the finding. Only complete evidence counts towards `Ready` or establishes that a risk is absent. When a finding has both a measured and a provided value, the measured one decides only if its coverage is complete; otherwise the provided one decides and the partial measurement is shown beside it.
- **D-68 (replaces the signal model in D-60):** Licence evidence records, per product, the SKU part number and SKU GUID, purchased and assigned counts, and per service plan the plan name and plan GUID; identifiers match `[A-Za-z0-9_]+` and GUIDs are validated. `rules/service_plans.yaml` classifies a (product, service plan) pair, not a plan alone: a plan inside a suite is `bundled` (entitlement only), and the same plan sold as its own product is `add_on` (evidence of use). Unmapped or ambiguous pairs are `Unknown` with the reason "licence not classified". Audio Conferencing belongs to meetings, not to telephony, and never triggers the telephony rule. Telephony is `Ready` only with a provided confirmation that no telephony runs through Microsoft; absence of an add-on is not evidence. The executor verifies every GUID and name against Microsoft's "Product names and service plan identifiers for licensing" page and records its address and check date in the file.
- **D-69 (tightens D-40):** The report file is named `report-<YYYY-MM-DD>-<lang>.html`, and the JSON and inputs copies follow the same pattern; no organisation name or other free text goes into any filename or into standard output. The only free text the report shows is the organisation's display name and the names of Windows-only software, both supplied by the user, escaped, and rejected if they contain `@`; `SECURITY.md` says so. Reason, source, unit and coverage values must be known codes; an unknown code is an input error, not dropped. Unknown fields and finding IDs are counted in the appendix ("3 fields were ignored"), never named. The privacy test plants names, email addresses and token-like strings in every field and key that is not one of the two free-text fields, and checks the HTML, the JSON copy, all filenames, standard output and standard error.
- **D-70:** Duplicate finding IDs, duplicate collector IDs and duplicate SKUs are input errors, tested in both orders. Licence evidence must name the `licences` collector.
- **D-71 (output safety, extends D-47; part of the review rejected):** All three outputs (report, JSON copy, inputs copy) are written through one function that refuses a destination that is a symbolic link, writes a temporary file in the same directory and renames it into place. Each destination is tested with a planted link to an outside file whose bytes must survive. Rejected with reason: pinning the output directory against replacement while the tool runs. Someone who can swap directories inside the user's own chosen folder already controls the user's files; the defence adds code without protecting anything.
- **D-72:** Each "cannot be moved" entry is a row in the mapping file with its own source and check date, and shows two things separately: what the target cannot do (from the source) and whether this organisation needs it (`yes`, `no` or `unknown`, from a declared finding or provided answer, otherwise `unknown`). A gap never inherits the workload's status. Tests cover needed, not needed and unknown, and no test hardcodes a gap that the data file does not contain.
- **D-73:** The rule-change test copies the rules directory, changes a rule's status in the copy, runs the documented command against it and asserts the resulting status in the report. Run-details checksums are computed from the exact bytes that were parsed, read once.
- **D-74 (replaces the socket patching in D-52):** The offline test runs the installed tool in a subprocess with a Python audit hook (`sys.addaudithook`) that records every `socket.*` audit event, including name and address lookups, to a file before anything else can catch it. The test fails if any event was recorded. A second test proves the hook records a deliberately caught connection attempt.
- **D-75 (sample labels, finishes D-51):** The sample header says the scan measurements are simulated. Provided answers and prices are labelled by their own origin wherever they appear, so a table mixing origins labels each row.
- **D-76 (lean):** The executor ignores the review-disposition ledgers and token estimates inside the plans; they are planning records. Tests that depend only on the scan use `report` without inputs, so later plans that change `demo` do not break them. Catalogue-size assertions compare against the catalogue file instead of repeating numbers.

### Amendments after the third plan gate (2026-11-21)

The round-3 gate (`01-REVIEWS-3.md`) confirmed findings 13 to 15 and 18 to 22 resolved and left three blockers. This closes the plan-review loop; anything further goes to the end-of-phase code review.

- **D-77 (extends D-67):** A partial measurement that finds one or more affected items establishes that they exist; it is a confirmed lower bound, and problem rules that depend on it fire. A partial measurement that finds none establishes nothing. When a provided answer of zero conflicts with a measured positive, the measured lower bound decides, the conflict is shown with both values, and the workload cannot be `Ready`. Test that case.
- **D-78 (extends D-70):** A populated licence block is an input error when the `licences` collector is absent from `collectors` or has status `skipped`.
- **D-79 (resolves finding 16 in part, replaces part of D-69):** Collected data contains no free text at all. `scan.json` 1.x has no organisation name field; the report takes the organisation's display name only from `inputs.yaml`. The privacy test plants names, email addresses and token-like strings in every field and key of `scan.json` with no exemption. In `inputs.yaml` the only free text is the organisation display name and the names of Windows-only software, which the user types about their own organisation; they are shown escaped and rejected if they contain `@`. Rejected with reason: replacing those two user-typed fields with neutral labels by default. The principle protects people whose data the tool collects; it does not second-guess what a user deliberately writes about their own organisation, and a report that cannot name the organisation it describes is worse for its reader. `SECURITY.md` and the README state that everything free-text in a report was typed by the user in `inputs.yaml`.

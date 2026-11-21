# Walking Skeleton — befund

**Phase:** 1
**Generated:** 2026-11-21 (revised the same day after two plan reviews and the reference teardown; decisions D-39 to D-65)

This project is a local command-line tool. It has no database, no server, no routes and no deployment, and none is planned. The skeleton template assumes all four. Each part that does not apply is named below with the reason and with what stands in its place. Nothing was invented to fill a template row.

This file is the contract for the seven plans of Phase 1 (01-01 to 01-07, run one at a time) and for later phases. Plans name the section they build; the tables here are the target state.

## Capability Proven End-to-End

A user runs one command, `uv run befund demo`, with no Microsoft account, and gets one real, self-contained HTML report file built from a bundled `scan.json`, with the absolute path of that file printed as the last line of standard output. The run opens no socket.

The path that proves it: console script, Typer command, sample file read through `importlib.resources`, validation into dataclasses, Jinja2 template with strings from a locale file, one `.html` file on disk.

## Architectural Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Application shape | Local command-line tool. No server, no accounts, no hosted part. | Data must never leave the machine. |
| Language and packaging | Python 3.12 or newer, PEP 621 `pyproject.toml`, `hatchling` pinned to one exact version, managed with `uv`, `uv.lock` committed, `exclude-newer` set to a fixed date (D-02, DECISIONS.md D16, D17). | Small, auditable, no package younger than 14 days. |
| Dependencies | Runtime: `typer`, `jinja2`, `pyyaml`. Development: `pytest`, `ruff`. Nothing else (D-03). | A short list is part of the trust story. |
| Commands | Typer. Console script `befund` points at `befund.cli:main`. Help text is English (D-55). | DECISIONS.md D18. |
| Rendering | One Jinja2 template, autoescape on, no JavaScript, inline CSS, one output file, a restrictive content security policy (D-25). | The report must open offline and print cleanly. |
| Data layer | No database. Inputs are files: `scan.json`, `inputs.yaml`, and YAML data files inside the package. Output is one `.html` file. Frozen dataclasses (D-09). | Nothing is stored between runs. |
| Judgement in data | Workloads, finding ids, status rules, service plans, risky file types, mappings and all words live in YAML inside the package, read with `importlib.resources` (D-04, D-59). | Adding a workload is a data change only. |
| Privacy | By construction (D-40). The loader keeps only the fields and finding ids it knows. There is no redaction module and no flag that shows names. | Redaction protects only the fields someone remembered. |
| Strict input | One module reads and parses files: duplicate keys, non-finite numbers, non-UTF-8 text and directories are errors (D-48). | A silent wrong value is worse than a refused file. |
| Output | Every write goes through one function that stays inside the resolved `--out` directory, refuses a linked destination and renames a temporary file into place (D-47). | A report run must not be usable to overwrite another file. |
| Reproducible | No function reads the clock. File name and scan date come from `scan.generated_at` (D-49). | The same inputs give the same bytes on any day. |
| Sign-in and network | None in this phase. The test suite fails on any socket creation (D-52). | Phase 1 contains no Microsoft code. |
| Deployment target | None. | The tool runs on the user's own machine. |
| Directory layout | `src/befund/` as in HANDOFF.md section 11, without `auth.py`, `graph.py`, `collectors/` and `privacy.py`; with `parsing.py`, `catalogue.py`, `output.py` and `inputs.py` (D-01, D-40). | Modules follow the jobs that exist, not the handoff's list. |
| Error style | One exception type, `InputError`, carrying a code, the file and the field, never the offending value. The command prints one sentence from the locale files, exit code 2, no traceback unless `--debug` (D-08). Messages use `--lang` when given, else English (D-55). | A council IT officer must be able to act on the message. |
| Languages | `locales/en.yaml` and `locales/de.yaml`, identical key sets, a small formatter of our own (D-31). | German and English from the first run. |
| Licence | AGPL-3.0-or-later with SPDX headers (D-34). | Settled by the founder in DECISIONS.md S5. |
| Engineering rules | `AGENTS.md` binds every plan. | One rule set for people and for both models. |

## Stack Touched in Phase 1

- [ ] Project scaffold: `pyproject.toml`, `uv`, `ruff`, `pytest`. Applies as written.
- [ ] Routing: does not apply, there is no server. Its place is taken by the command table: `demo` and `report`.
- [ ] Database: does not apply. Its place is taken by one real read (the bundled `scan.json`, parsed and validated) and one real write (the report file).
- [ ] UI: the report is a document without interactive elements, because D-25 allows no JavaScript. The user's interaction is the command; the file on disk is the response.
- [ ] Deployment: does not apply. The documented local full-stack run is `uv run befund demo --out ./report`.

## Contracts Fixed by the Skeleton

### 1. `scan.json`, schema version `1.0`

Top level (D-09, D-60): `schema_version`, `tool` (`name`, `version`), `generated_at`, `source_kind`, `organisation` (`display_name`, may be null), `collectors`, `findings`, `licences` (an object or null).

Collector (D-10, D-42): `id`, `status`, `reason`, `permissions_used`. Collector ids are independent of workloads.

Finding (D-11, D-42): `id`, `workload`, `value`, `unit`, `provenance`, `collector`, `source`, `collected_at`, `period`, `coverage`, `missing_reason`. All eleven keys are present in every finding; a key with nothing to say holds `null`.

Licences (D-60): `collector`, `source`, `collected_at`, `coverage`, `products`. Each product: `sku`, `purchased`, `assigned`, `service_plans` (a list of plan identifiers).

Coverage (D-62): an object with `kind` (`complete` or `partial`) and, where known, `scanned`, `failed` and `total` (whole numbers of zero or above).

| Field | Rule |
|---|---|
| `source_kind` | `sample`, `import`, `live` |
| collector `status` | `ok`, `partial`, `skipped`; `reason` required unless `ok` |
| `provenance` | `measured`, `provided`, `unknown` |
| measured finding | `value`, `collector` (naming a collector with status `ok` or `partial`), `source`, `collected_at` and `coverage` are set |
| provided finding | `value` and `source` are set; `collector` and `coverage` are null; `collected_at` may be null and is then shown as "date not supplied" (D-49) |
| unknown finding | `value` is null and `missing_reason` is set |
| `id`, `workload`, `unit`, `value` | checked against the catalogue (section 2): the id must be listed, workload and unit must match, and the value must fit the type |
| collector `id`, `source`, `reason`, `missing_reason` | codes: lower-case letters, digits and `_`, parts joined by `.`, at most 64 characters. A source is never a URL. |
| `sku`, service plan identifiers | upper-case letters, digits and `_`, at most 64 characters |
| `permissions_used` | letters, digits and `.`, at most 64 characters each |
| `collected_at`, `generated_at` | ISO 8601 date or date-time |
| `period` | ISO 8601 interval `YYYY-MM-DD/YYYY-MM-DD`, or null |
| `organisation.display_name` | the only free text: one line, at most 120 characters |

Privacy by construction (D-40):

- The loader builds the model from the keys and finding ids it knows. Every other key and every other finding is dropped. Dropped names that are plain lower-case identifiers are listed in the appendix without their values; other dropped names are only counted.
- A string anywhere in the file that contains `@` is an error.
- A known text field that breaks its pattern is an error. Error messages name the file and the field and never repeat the value.
- A reason code that fits the pattern but is not in the list of section 3 is shown as "not recognised by this version"; the code itself is not printed.
- A reader refuses a major version other than 1 and says which version it found and which it supports (D-13). A 1.x file with added keys still loads.
- Duplicate keys and non-finite numbers are errors (D-48).

### 2. Catalogue: workloads and finding ids (`rules/findings.yaml`, D-41, D-59)

Fifteen workloads, in this order: `licences`, `directory`, `mail`, `onedrive`, `sharepoint`, `teams`, `office_files`, `device_management`, `windows_software`, `power_platform`, `telephony`, `identity_access`, `security_compliance`, `small_apps`, `integrations`.

Each finding entry has `id`, `workload`, `type` (`count`, `bytes`, `boolean` or `code`), `unit`, `label` (a locale key), `provided` and `headline` (true when it is one of the headline figures). `provided` is `no`, or `answer` when a person gives the value by id in `inputs.yaml`, or `software_list` and `software_list_without_web_version` for the two counts taken from the list of Windows-only software.

| Workload | Finding id | Type | Unit | Provided | Headline |
|---|---|---|---|---|---|
| licences | `licences.contract_terms_known` | boolean | | yes | |
| directory | `directory.user_count` | count | users | | yes |
| directory | `directory.licensed_user_count` | count | users | | |
| directory | `directory.guest_count` | count | users | | |
| directory | `directory.group_count` | count | groups | | |
| directory | `directory.account_list_reviewed` | boolean | | yes | |
| mail | `mail.mailbox_count` | count | mailboxes | | yes |
| mail | `mail.shared_mailbox_count` | count | mailboxes | | |
| mail | `mail.storage_bytes` | bytes | bytes | | yes |
| mail | `mail.item_count` | count | items | | |
| mail | `mail.other_systems_send_mail` | boolean | | yes | |
| onedrive | `onedrive.account_count` | count | accounts | | |
| onedrive | `onedrive.storage_bytes` | bytes | bytes | | yes |
| onedrive | `onedrive.external_sharing_in_use` | boolean | | yes | |
| sharepoint | `sharepoint.site_count` | count | sites | | yes |
| sharepoint | `sharepoint.storage_bytes` | bytes | bytes | | yes |
| sharepoint | `sharepoint.file_count` | count | files | | |
| sharepoint | `sharepoint.custom_solutions_in_use` | boolean | | yes | |
| teams | `teams.team_count` | count | teams | | yes |
| teams | `teams.channel_count` | count | channels | | |
| teams | `teams.teams_with_guests_count` | count | teams | | |
| teams | `teams.chat_history_must_be_kept` | boolean | | yes | |
| office_files | `office_files.kind.macro`, `.access`, `.publisher`, `.visio`, `.onenote` | count | files | yes | |
| device_management | `device_management.device_count` | count | devices | yes | yes |
| device_management | `device_management.windows_device_count` | count | devices | yes | |
| device_management | `device_management.in_use` | boolean | | yes | |
| windows_software | `windows_software.application_count` | count | applications | software_list | |
| windows_software | `windows_software.without_web_version_count` | count | applications | software_list_without_web_version | |
| power_platform | `power_platform.in_use` | boolean | | yes | |
| telephony | `telephony.replacement_available` | boolean | | yes | |
| identity_access | `identity_access.sso_application_count` | count | applications | yes | |
| identity_access | `identity_access.conditional_access_in_use` | boolean | | yes | |
| security_compliance | `security_compliance.protection_or_retention_in_use` | boolean | | yes | |
| small_apps | `small_apps.in_use` | boolean | | yes | |
| integrations | `integrations.application_count` | count | applications | yes | |

That is 39 ids. Three more ids are derived at report time from the licences block and never appear in a scan: `licences.product_count` (count, unit `products`), and for every workload `{workload}.licence_add_on_assigned` and `{workload}.licence_bundled_assigned` (boolean).

Risky file kinds and their extensions (D-16, configurable in `rules/risky_file_types.yaml`): `macro` (`xlsm`, `xltm`, `xlam`, `docm`, `dotm`, `pptm`, `potm`), `access` (`accdb`, `mdb`), `publisher` (`pub`), `visio` (`vsdx`), `onenote` (`one`). `dotx` is not in the list.

### 3. Reason codes (D-58)

Every Unknown carries a reason code and a fix. Each code has a `label` and a `fix` in both locale files.

`not_in_export`, `permission_denied`, `not_licensed`, `not_collected_in_this_version`, `answer_not_provided`, `source_not_supplied`, `needs_recipient_export`, `collector_skipped`, `not_in_scan`, `licensed_use_not_measured`, `coverage_partial`, `not_established`, `not_recognised`.

The first eight may be written by a collector or an import. The last five are given by the report: `not_in_scan` for an absent measured finding, `licensed_use_not_measured` (D-60), `coverage_partial`, `not_established`, and `not_recognised` for a code this version does not know.

### 4. Status rules (`rules/status.yaml`, D-43, D-65)

One block per workload: `ready` (a list of conditions, all of which must hold, and a reason in English and German) and `rules` (problems, in order; each with an id, one or more conditions that must all hold, a status of `needs_work` or `blocker`, and a reason in English and German). A condition names one finding id, an operator (`exists`, `==`, `>`, `>=`) and, for the last three, a literal.

Evaluation of one workload:

1. Each condition is true, false or open. It is open when its finding is absent or unknown. On a finding with partial coverage, `exists` is true, a `>` or `>=` that holds is true, and everything else is open. A rule is true when all its conditions are true, false when one is false, and open otherwise. The same holds for the `ready` list.
2. If a rule is open, or no rule is true and `ready` is open, the workload is Unknown. The reason names each finding that is missing, with its reason code and fix. Rules that are true stay visible as notes.
3. Otherwise, if a rule is true, the worst status among the true rules wins; ties keep file order.
4. Otherwise, if `ready` is true, the workload is Ready.
5. Otherwise the workload is Unknown with the code `not_established`.

When the workload's `licence_bundled_assigned` is true and a finding a person must provide is missing, the workload's reason code is `licensed_use_not_measured`.

| Workload | Ready when all hold | Problems |
|---|---|---|
| licences | `licences.product_count` exists; `licences.contract_terms_known` == true | `licences-terms-unknown`: `contract_terms_known` == false, needs work |
| directory | `directory.user_count` exists; `directory.guest_count` == 0; `directory.account_list_reviewed` == true | `directory-guests`: `guest_count` > 0, needs work. `directory-accounts-not-reviewed`: `account_list_reviewed` == false, needs work |
| mail | `mail.mailbox_count` exists; `mail.shared_mailbox_count` exists; `mail.other_systems_send_mail` == false | `mail-other-systems`: `other_systems_send_mail` == true, needs work |
| onedrive | `onedrive.account_count` exists; `onedrive.storage_bytes` exists; `onedrive.external_sharing_in_use` == false | `onedrive-external-sharing`: == true, needs work |
| sharepoint | `sharepoint.site_count` exists; `sharepoint.custom_solutions_in_use` == false | `sharepoint-custom-solutions`: == true, needs work |
| teams | `teams.team_count` exists; `teams.teams_with_guests_count` == 0; `teams.chat_history_must_be_kept` == false | `teams-guests`: `teams_with_guests_count` > 0, needs work. `teams-chat-history`: `chat_history_must_be_kept` == true, needs work |
| office_files | each of the five `office_files.kind.*` == 0 | `office-macro`: `kind.macro` > 0, needs work, with the note that estimating the effort needs a content scan this tool does not do (D-65). `office-access`, `office-publisher`, `office-visio`, `office-onenote`: the kind > 0, needs work |
| device_management | `device_management.in_use` == false; `device_management.windows_device_count` == 0; `device_management.licence_add_on_assigned` == false | `devices-managed`: `in_use` == true, needs work. `devices-windows`: `windows_device_count` > 0, needs work. `devices-add-on`: `licence_add_on_assigned` == true, needs work |
| windows_software | `windows_software.application_count` == 0 | `software-no-web-version`: `without_web_version_count` > 0, blocker. `software-present`: `application_count` > 0, needs work |
| power_platform | `power_platform.in_use` == false; `power_platform.licence_add_on_assigned` == false | `power-premium-licences`: `licence_add_on_assigned` == true, needs work (D-65). `power-in-use`: `in_use` == true, needs work |
| telephony | `telephony.licence_add_on_assigned` == false | `telephony-no-replacement`: `licence_add_on_assigned` == true and `telephony.replacement_available` == false, blocker (D-65). `telephony-add-on`: `licence_add_on_assigned` == true, needs work (D-60) |
| identity_access | `identity_access.sso_application_count` == 0; `identity_access.conditional_access_in_use` == false | `identity-sso-applications`: `sso_application_count` > 0, needs work. `identity-conditional-access`: == true, needs work |
| security_compliance | `security_compliance.protection_or_retention_in_use` == false; `security_compliance.licence_add_on_assigned` == false | `security-in-use`: == true, needs work. `security-add-on`: `licence_add_on_assigned` == true, needs work |
| small_apps | `small_apps.in_use` == false | `small-apps-in-use`: == true, needs work |
| integrations | `integrations.application_count` == 0 | `integrations-present`: `application_count` > 0, needs work. An unknown number leaves the workload Unknown (D-65) |

### 5. Service plans (`rules/service_plans.yaml`, D-60)

Each row: `id` (the service plan identifier), `workload`, `signal` (`bundled` or `add_on`), `reference_url`, `checked_on`, an optional `note`. A plan is `add_on` when buying it is a separate decision; it is `bundled` when it comes inside a suite. A product counts only when its `assigned` number is above zero.

Starting identifiers. None of them is trusted: each is checked at build time against Microsoft's page "Product names and service plan identifiers for licensing", and the page address and the date go into the file.

| Workload | Identifiers | Signal |
|---|---|---|
| telephony | `MCOEV`, `MCOPSTN1`, `MCOPSTN2`, `MCOMEETADV` | add_on |
| power_platform | the `FLOW_O365_P` and `POWERAPPS_O365_P` families | bundled |
| power_platform | `BI_AZURE_P2` | add_on |
| identity_access | `AAD_PREMIUM`, `AAD_PREMIUM_P2` | bundled |
| device_management | `INTUNE_A` | bundled |
| security_compliance | `ATP_ENTERPRISE`, `WINDEFATP`, `MIP_S_CLP1` | bundled |
| security_compliance | `EXCHANGE_S_ARCHIVE` | add_on |
| small_apps | the `FORMS_PLAN_E` family, `PROJECTWORKMANAGEMENT`, `MICROSOFTBOOKINGS` | bundled |

### 6. Mappings (`rules/mappings/{profile}.yaml`, D-45, D-61)

Profiles: `opendesk`, `nextcloud`, `generic`. Rows are by function. Each row: `function`, `workload`, `microsoft` and `replacement` (English and German), `coverage` (one step of the ladder), `reference_url`, `checked_on`, an optional `note`.

Ladder: `in_suite`, `in_suite_with_limits`, `announced`, `component_vendor_solution`, `open_source_community`, `open_source_third_party`, `proprietary_third_party`, `not_available`.

Functions and their workloads: `identity_management` (directory), `mail_and_calendar` (mail), `personal_files` (onedrive), `team_files` (sharepoint), `sharepoint_workflows` (sharepoint), `chat` (teams), `video_meetings` (teams), `teams_chat_history` (teams), `office_editing` (office_files), `vba_macros` (office_files), `device_management` (device_management), `desktop_operating_system` (device_management), `windows_applications` (windows_software), `automation_and_low_code` (power_platform), `telephony` (telephony), `single_sign_on` (identity_access), `security_and_compliance` (security_compliance), `forms_tasks_bookings` (small_apps), `application_integrations` (integrations).

Each file also has `product_profile` (true when the rows name products; then every row needs `reference_url` and `checked_on`) and `no_function`, the workloads that are not functions to move (`licences`). Every workload of the catalogue is in a row or in `no_function`. Rows with the coverage `not_available` form the list "Cannot be moved".

### 7. `inputs.yaml` keys (D-21, D-43, D-48, D-49, D-50, D-51, D-63)

```yaml
organisation_name: null        # text, one line
currency: null                 # three-letter code, for example EUR or CHF
language: null                 # de | en
target_profile: null           # opendesk | nextcloud | generic
as_of: null                    # date the answers were given, "2026-11-10"
amounts_are_invented: false    # true only in the two sample files
current_costs:
  microsoft_licences_per_year: null
  other_it_per_year: null
target_costs:
  partial_exit:
    users: null
    retained_microsoft_licences_per_year: null
    hosting_per_user_per_month: null
    operations_per_year: null
    other_recurring_per_year: null
    one_time_migration: null
    application_adaptation: null
    external_advice: null
    training_days_per_person: null
    training_day_rate: null
    training_staff: null
    productivity_loss: null
    parallel_running_months: null
  full_exit: {}                # the same thirteen keys
windows_only_software: null    # a list; an empty list means "none"
#  - name: "..."
#    users: null
#    vendor_has_web_version: null
provided_counts: {}            # keys are the count ids whose "provided" is "answer" in section 2
confirmations: {}              # keys are the boolean ids whose "provided" is "answer" in section 2
```

Amounts are quoted text such as `"8.50"`, read as decimal numbers with no digit lost. A missing key counts as null. A key outside this list, including the flat keys of HANDOFF.md section 7 under `target_costs`, is an error naming the file and the key. Provided answers enter the model as provided findings with the source code `inputs_yaml` and `as_of` as their date.

### 8. Cost model (D-50, D-63)

Five years, 60 months. Letters: M Microsoft licences per year, O other IT per year; per exit scenario U users, R retained licences per year, H hosting per user per month, Op operations per year, Q other recurring cost per year, G one-time migration, A application adaptation, E external advice, d training days per person, r training day rate, s training staff, L productivity loss, P months of parallel running.

| Part | Stay | Partial exit and full exit |
|---|---|---|
| Running cost over five years | M × 5 + O × 5 | R × (60 − P) / 12 + H × U × 60 + Op × 5 + Q × 5 + O × 5 |
| Block 1: direct project cost | 0 | G + A + E + d × r × s |
| Block 2: productivity loss | 0 | L |
| Block 3: parallel running | 0 | M × P / 12 |
| Total | sum | sum |

A product is zero when one factor is known to be zero, even if another factor is unknown. Otherwise an unknown input makes its line, its block and the total unknown. The difference to staying is unknown whenever the total of staying is unknown. Amounts are rounded for display only; totals come from unrounded values.

Worked example, used as the expected values in tests. M = 100000, O = 20000.

| | Partial exit | Full exit |
|---|---|---|
| Inputs | U 30, R 60000, H 8.50, Op 6000, Q 1500, G 15000, A 4000, E 3000, d 2, r 400, s 30, L 9000, P 6 | U 85, R 0, H 8.50, Op 12000, Q 2000, G 40000, A 10000, E 8000, d 2, r 400, s 85, L 25000, P 12 |
| Running cost | 270000 + 15300 + 30000 + 7500 + 100000 = 422800 | 0 + 43350 + 60000 + 10000 + 100000 = 213350 |
| Direct project cost | 15000 + 4000 + 3000 + 24000 = 46000 | 40000 + 10000 + 8000 + 68000 = 126000 |
| Productivity loss | 9000 | 25000 |
| Parallel running | 50000 | 100000 |
| Total | 527800 | 464350 |
| Difference to staying (600000) | -72200 | -135650 |

Two edge cases. Partial exit with P = 0 and M unknown: parallel running is 0, the total is 507800, staying is unknown, the difference is unknown. Partial exit with P = 60 and R unknown: retained licences are 0, parallel running is 500000, the total is 707800.

### 9. Command output and HTML hooks

- Report file name: `report-{org-slug}-{YYYY-MM-DD}.html`, written into the directory given by `--out` (default `./report`). The date is the day in `scan.generated_at`. The slug holds only `a` to `z`, `0` to `9` and `-`.
- The last line of standard output is the absolute path of the report file (D-07, CLI-06).
- `demo` also writes `sample-{sample}-scan.json` and `sample-{sample}-inputs.yaml` next to the report. Files named `report-*` and `sample-*` in the output directory belong to the tool and are replaced on each run.
- A bad input ends the command with one sentence on standard error and exit code 2.
- Nine sections, each with `data-section`, in this order (D-64): `header`, `found`, `costs`, `readiness`, `moves`, `attention`, `path`, `appendix`, `footer`. Sub-sections: `readiness` holds "Not examined"; `attention` holds "Cannot be moved"; `appendix` holds the run details.
- Other attributes the tests rely on: `data-finding`, `data-provenance`, `data-workload`, `data-status`, `data-scenario`, `data-block`, `data-total`, `data-sample`, and `data-subsection` with the values `not-examined`, `cannot-be-moved` and `run-details`.

## Reversibility Ratings

| Decision | Rating | Why |
|---|---|---|
| Shape of `scan.json` (D-09 to D-13, D-40 to D-42, D-60, D-62) | costly now, one-way from the first public release | Phase 2 and Phase 3 write this shape. Once a release is out, files exist on other people's machines. `schema_version` and the D-13 refusal keep a later change a versioned one. Confirm the shape before Phase 4. |
| Package name `befund` and command `befund` | costly now, one-way after publication on PyPI | A rename touches the package directory, every import, the console script and the documents. Decide before Phase 4. |
| Licence AGPL-3.0-or-later | one-way once the repository is public and takes outside contributions | Settled by the founder (DECISIONS.md S5, HANDOFF.md section 3). |

No checkpoint was added for any of the three: Phase 1 publishes nothing.

## Out of Scope (Deferred to Later Slices)

- `import` of admin-centre CSV exports (Phase 2)
- Sign-in, the Graph client, `doctor`, live collectors (Phase 3)
- Published `docs/schema.md`, the app-registration guide, `docs/permissions.md`, PyPI release, signed Windows build, and a `--rules DIR` option (Phase 4, D-54)
- A flag that shows person names: returns when a collector exists that could supply them (DECISIONS.md D19)
- Measured file inventory by extension (v2, FILE-01): this phase takes risky-file counts from `inputs.yaml` only
- A "second source" cost scenario (DECISIONS.md D23)
- An overall score or a go or no-go verdict: excluded for good (DECISIONS.md D1, D20)
- Interactive prompt for the manual inputs (v2, CONV-01); partner-branded reports

## Subsequent Slice Plan

Each later phase adds one vertical slice on top of this skeleton without altering its architectural decisions:

- Phase 2: a user points `import` at admin-centre CSV exports and gets a `scan.json` in this schema and a report, with no sign-in and no network.
- Phase 3: a user runs `doctor` and `scan`, signs in through the browser, and gets measured licence products and directory counts in the same schema.
- Phase 4: a user runs a tagged release with `uvx` or as a signed Windows build, and finds the guides for app registration, permissions and the `scan.json` format.

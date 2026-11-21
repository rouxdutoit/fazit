# HANDOFF: m365-exit-scan

> Working name. Rename freely, but keep it short and typeable.

You are building the first version of a free, open source command-line tool that scans an organisation's Microsoft 365 setup **read-only** and produces a **local, offline HTML report** showing how ready they are to move to an open source stack (openDesk, Nextcloud, LibreOffice, Linux), what it would cost, and what will need work.

Read this whole file before writing code. When something here is unclear or wrong, ask, or record your decision in `DECISIONS.md`.

---

## 1. Why this exists

European public bodies and small organisations are leaving Microsoft (Schleswig-Holstein, Munich, Hamburg's review, small towns moving to openDesk). The software to switch to exists. What's missing is a trustworthy, easy first step: *"What do we actually have, and what would break?"*

Existing answers are consultancy sales calls or vendor-specific tools. This tool is:

- **Open source** (so IT staff can read exactly what it does)
- **Local** (data never leaves the machine that runs it)
- **Read-only** (it cannot change anything in the tenant)
- **Free** (no account, no signup, no server)

The open source scanner is the product's front door. Paid services (migration plans, migration, hosting) may come later, but **this repo must stand fully on its own** and never feel crippled.

## 2. Non-negotiable principles

These are hard rules. Tests should enforce the ones that can be tested.

1. **Read-only.** Request only read permissions. No write scopes, ever.
2. **No data leaves the machine.** The only network calls allowed are to Microsoft sign-in and Microsoft Graph (`login.microsoftonline.com`, `graph.microsoft.com`). No telemetry, no analytics, no update checks, no CDNs.
3. **Tokens stay in memory.** Never write access or refresh tokens to disk.
4. **No content reading in v1.** Count and size things; don't download or open mail bodies or file contents. File *names and extensions* are fine.
5. **Private by default.** Person names and email addresses are excluded from the report unless the user passes `--include-names`. Aggregate counts are the default.
6. **Offline report.** The report is one self-contained `.html` file: inline CSS and JS, no external fonts, scripts or images. It must work with the network off and print cleanly to PDF.
7. **One command.** A non-expert should get from zero to report with one command plus a sign-in.
8. **Honest numbers.** No hardcoded prices. Costs come from user input or clearly labelled config. Unknowns are shown as unknown, not guessed.

## 3. Licence

**AGPL-3.0-or-later** for the code. This lets anyone use, change and share it, and stops someone running a modified version as a closed hosted service. Add `LICENSE`, SPDX headers, and a short `CONTRIBUTING.md`.

## 4. Tech choices

- **Python 3.12+**, packaged with **uv**, runnable as `uvx m365-exit-scan`.
- Auth: **MSAL for Python**, device code flow (works on any machine, no local web server).
- HTTP: `httpx`, calling Graph REST directly. Prefer this over the big Graph SDK to keep dependencies small and auditable.
- Report templating: **Jinja2**, rendering into a single HTML file.
- CLI: **Typer**.
- Tests: **pytest**, using recorded JSON fixtures. CI must never need a live tenant.
- Lint/format: **ruff**.

Keep dependencies minimal. Ask before adding any dependency not listed here.

## 5. Authentication

- Device code flow, delegated permissions. A Global Reader or admin signs in.
- Support two modes:
  - **Bring your own app registration** (`--client-id`, `--tenant-id`): the organisation registers its own app in Entra ID. Document the exact steps in `docs/app-registration.md` (German and English). This is the most trusted path and should be presented first.
  - **Project's public multi-tenant client ID**: convenience option, added later once we register one. Leave a config hook for it.
- Request the smallest read-only scope set that works. Starting list to **verify against current Microsoft Graph docs before implementing** (names and requirements change):
  - `User.Read.All`, `Group.Read.All`, `Organization.Read.All`
  - `Reports.Read.All` (usage reports give counts and storage without reading content)
  - `Sites.Read.All`, `Files.Read.All`
  - `Team.ReadBasic.All`, `Channel.ReadBasic.All`
  - `DeviceManagementManagedDevices.Read.All` (optional; only if Intune is used)
- If a scope is missing or denied, **skip that collector and say so in the report**. Never fail the whole scan.
- Note: Microsoft 365 usage reports may show concealed (anonymised) user identifiers by tenant setting. That's fine and fits principle 5.

## 6. What the scanner collects (v1)

Each collector is an independent module returning a typed result plus a list of warnings.

| Collector | Source (verify) | Collects |
|---|---|---|
| `licences` | `subscribedSkus` | Licence SKUs, purchased vs assigned counts |
| `directory` | users, groups | User count, licensed users, guests, groups |
| `mail` | mailbox usage report | Mailbox count, shared mailboxes, storage, item counts |
| `onedrive` | OneDrive usage report | Accounts, total storage |
| `sharepoint` | sites + site usage report | Site count, storage per site, file counts |
| `teams` | teams + channels | Teams, channels, guest presence |
| `office_files` | drive item listing | Counts of risky file types by extension (see below) |
| `devices` | Intune managed devices | Device count by OS (only if available) |

**Risky file types to count** (names/extensions only, no content):
`.xlsm .xltm .xlam .docm .dotm .dotx .pptm .potm .accdb .mdb .pub .vsdx .one`

Access (`.accdb`, `.mdb`), Publisher (`.pub`) and Visio (`.vsdx`) are usually migration blockers or need special handling; macro-enabled files need conversion. Make the list configurable.

Large tenants: page through Graph results, respect throttling (`429` and `Retry-After`), and show progress. Add a `--max-files` safety limit for the file listing.

## 7. Manual inputs

Some important things can't be seen through Graph. Collect them through an optional `inputs.yaml` (and later an interactive prompt):

```yaml
organisation_name: "Musterstadt Town Office"
currency: EUR
current_costs:
  microsoft_licences_per_year: null   # if null, report shows "unknown"
  other_it_per_year: null
target_costs:
  hosting_per_user_per_month: null
  one_time_migration: null
  training: null
windows_only_software:
  - name: "Case management system"
    users: 6
    vendor_has_web_version: false
target_profile: opendesk   # opendesk | nextcloud | generic
language: de               # de | en
```

Ship `inputs.example.yaml` with comments in English and German.

## 8. Rules and mapping

All judgement lives in **data files, not code**, so non-programmers and consultants can adjust it.

- `rules/mappings/<profile>.yaml`: maps each Microsoft service to its open source replacement for that profile. Example for `opendesk`: Exchange → Open-Xchange, OneDrive/SharePoint → Nextcloud, Teams chat → Element, Teams meetings → Jitsi, Office → Collabora/LibreOffice, Entra ID → Keycloak, Windows → Linux desktop.
- `rules/status.yaml`: rules that assign each area a status of **Ready**, **Needs work** or **Blocker**, with a human-readable reason. Example: any `.accdb` files → `office_files` is at least *Needs work*; Windows-only software with no web version → *Blocker*.
- **Readiness score**: a simple, documented formula (for example, a weighted share of areas that are Ready, with weights in config). Show the formula in the report's appendix. No black boxes.

## 9. The report

One file, `report-<org>-<date>.html`, plus the raw data as `scan.json` (stable, versioned schema documented in `docs/schema.md`, so others can build on it).

Sections, in order:

1. **Header**: organisation, scan date, tool version, and a clear line: *"Read-only scan. Nothing was changed. This file contains no data that left your computer."*
2. **What we found**: users, mailboxes, sites, Teams, storage, devices.
3. **Cost comparison over 5 years**: today vs after switching, including one-time migration and training. Any missing input is shown as "not provided", never invented.
4. **Readiness**: score plus a bar split into Ready / Needs work / Blocker.
5. **What moves where**: table of Microsoft service → replacement → what was found → status and reason.
6. **Needs attention**: the specific risky items (macro files, Access databases, Windows-only software).
7. **Suggested path**: pilot group → convert tricky files → move in waves with both systems running side by side → switch off.
8. **Appendix**: permissions used, collectors skipped and why, the scoring formula, and the full mapping.
9. **Footer**: "Made with m365-exit-scan, free and open source" with the repo URL as plain text (a link is fine, but nothing loads from it).

Design:
- Clean, calm, printable. Works in light and dark mode. Readable at phone width.
- System font stack only (no web fonts, to stay offline).
- Status colours must also differ in lightness and carry a text label; don't rely on colour alone. Prefer blue/orange over red/green.
- A visual reference mockup exists from planning; the section list above is the source of truth.

**Languages:** German and English from day one. All report strings in `locales/de.yaml` and `locales/en.yaml`. No hardcoded user-facing text in templates.

## 10. CLI

```
uvx m365-exit-scan scan  [--client-id ID --tenant-id ID] [--inputs inputs.yaml]
                         [--lang de|en] [--profile opendesk] [--include-names]
                         [--out ./report] [--max-files N]
uvx m365-exit-scan report scan.json [--inputs inputs.yaml] [--lang de|en]
uvx m365-exit-scan demo  [--lang de|en]
```

- `scan`: sign in, collect, write `scan.json` and the HTML report, then print the report path.
- `report`: rebuild the HTML from an existing `scan.json` (e.g. after editing `inputs.yaml` or switching language). No network.
- `demo`: build a full report from bundled sample data for a fictional 85-person town office. **No Microsoft account needed.** This is the most important command for adoption: people must be able to see the value in 30 seconds.

## 11. Repository layout

```
m365-exit-scan/
├── README.md              # English, with link to README.de.md
├── README.de.md
├── LICENSE                # AGPL-3.0-or-later
├── CONTRIBUTING.md
├── SECURITY.md            # how to report issues; restates the principles
├── DECISIONS.md           # running log of design decisions
├── pyproject.toml
├── inputs.example.yaml
├── docs/
│   ├── app-registration.md
│   ├── app-registration.de.md
│   ├── permissions.md     # every scope, and why it's needed
│   └── schema.md          # scan.json format
├── src/m365_exit_scan/
│   ├── cli.py
│   ├── auth.py
│   ├── graph.py           # thin client: paging, throttling, allowed hosts
│   ├── collectors/
│   │   ├── licences.py
│   │   ├── directory.py
│   │   ├── mail.py
│   │   ├── onedrive.py
│   │   ├── sharepoint.py
│   │   ├── teams.py
│   │   ├── office_files.py
│   │   └── devices.py
│   ├── model.py           # typed scan result + schema version
│   ├── rules.py           # mapping, status, readiness score
│   ├── costs.py
│   ├── privacy.py         # name/email redaction
│   ├── report.py
│   ├── templates/report.html.j2
│   ├── locales/{de,en}.yaml
│   ├── rules/
│   │   ├── mappings/{opendesk,nextcloud,generic}.yaml
│   │   └── status.yaml
│   └── demo/sample_scan.json
└── tests/
    ├── fixtures/          # recorded Graph responses, anonymised
    ├── test_collectors.py
    ├── test_rules.py
    ├── test_report.py
    ├── test_privacy.py
    └── test_network_policy.py
```

## 12. Tests that guard the principles

- **Network policy:** `graph.py` refuses any host except the two allowed. Test that it raises on anything else.
- **Read-only:** test that the requested scope list contains no `Write`, `ReadWrite` or `Manage` scopes.
- **No tokens on disk:** run a scan against fixtures with a temp home dir; assert no token-like strings were written anywhere.
- **Offline report:** parse the generated HTML; assert no `http://` or `https://` in any `src` or `href` that would load a resource, and no `<link rel="stylesheet">` to external files.
- **Privacy:** with default flags, assert no fixture email addresses or display names appear in the HTML or `scan.json`.
- **Graceful degradation:** a collector returning `403` is skipped and listed in the appendix; the report still renders.

## 13. Milestones

Work in this order. Each milestone ends with passing tests and a short note in `DECISIONS.md`.

- **M0, skeleton and demo.** Repo layout, CLI, typed model, sample data, full HTML report from `demo` in English and German. No Microsoft code yet. *This milestone alone is shareable.*
- **M1, sign-in and first collectors.** Device code auth, `graph.py` with paging/throttling/host allowlist, `licences`, `directory`, `mail`, `onedrive`.
- **M2, the rest of the collectors.** `sharepoint`, `teams`, `office_files`, `devices`, with graceful skipping.
- **M3, judgement.** Mapping profiles, status rules, readiness score, cost model, `inputs.yaml`, `report` command.
- **M4, release.** Docs (app registration in both languages, permissions, schema), `SECURITY.md`, packaging so `uvx m365-exit-scan demo` works from PyPI, first tagged release.

## 14. Explicitly out of scope for v1

- Any write access or migration execution
- A web dashboard, server, accounts or hosted version
- Reading email or file contents (macro analysis can come later behind an opt-in `--deep` flag)
- Google Workspace (good v2 candidate)
- Telemetry of any kind

## 15. How to work

- Verify Microsoft Graph endpoints, report names and permission names against current official documentation before implementing each collector. Note the doc version or date in code comments.
- Small, focused commits. Clear commit messages.
- Ask before adding dependencies or changing a principle in section 2.
- Write code and docs a council IT officer could read and trust. Plain language beats cleverness.
- When unsure about something user-facing, prefer the honest, boring option.

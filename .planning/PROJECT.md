# m365-exit-scan

> Working name. "M365" is Microsoft's mark; the name may change before the first public release.

## What This Is

A free, open source command-line tool that shows an organisation what it runs on Microsoft 365, what would break if it moved to an open source stack (openDesk, Nextcloud, LibreOffice, Linux), and what that move would cost. It works read-only and locally, and writes one self-contained HTML report in German or English that opens offline. It is used mainly by integrators and municipal IT providers on behalf of organisations with roughly 200 to 2,000 seats in Germany, Austria and Switzerland, and it stays simple enough for a council IT officer to run alone.

## Core Value

An organisation gets honest, inspectable numbers about its own Microsoft dependency, including "unknown" and "not yet", without any of its data leaving the machine.

## Business Context

- **Customer**: Integrators and municipal IT providers who advise organisations considering a move away from Microsoft. The organisations themselves never pay for the tool.
- **Revenue model**: None for the software. Paid assessments and support may be built around it; no scanning feature is ever held back for payment.
- **Success metric**: Organisations for which a real report was produced and used in a decision.
- **Strategy notes**: `DECISIONS.md` (strategy section). Market analysis is kept outside the repository.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] `demo` builds a complete report from bundled sample data, with no Microsoft account, in German and English
- [ ] Every finding carries its evidence: source, date, reporting period, coverage, and the reason for anything missing
- [ ] Status is given per workload (Ready, Needs work, Blocker, Unknown); there is no single weighted score
- [ ] Mappings and status rules live in data files that non-programmers can edit
- [ ] Costs come only from user input; missing inputs leave totals unknown; three scenarios (stay, partial exit, full exit)
- [ ] `report` rebuilds the HTML from an existing `scan.json` with no network access
- [ ] `import` reads admin-centre CSV exports locally and keeps aggregates only
- [ ] Live collection signs in through the browser with a customer-owned app registration, read-only, starting with licence and directory counts
- [ ] `doctor` checks consent, roles and blocked sign-in flows and prints the fix
- [ ] Tests enforce the principles: allowed hosts, allowed endpoints, no tokens on disk, offline report, privacy by default, graceful skipping
- [ ] Runs with one command through `uvx` and as a signed, self-contained Windows build
- [ ] Documentation in German and English: app registration, permissions, `scan.json` schema, security

### Out of Scope

- Any write access or migration execution — the tool's trust rests on being unable to change anything
- A web dashboard, server, accounts or hosted version — data must never leave the machine
- Reading mail bodies or file contents — counting and sizing only in v1
- Telemetry, analytics, update checks, CDNs — the only network destinations are Microsoft sign-in and Microsoft Graph
- A single readiness score — it hides unknowns and can make a denied collector look like readiness
- Live download of Microsoft usage reports — those endpoints redirect to a third host; reports come in through `import`
- Tenant-wide file inventory — deferred until paid assessments show it changes a decision
- Google Workspace as a source — second product
- On-premises Exchange and file servers — later import path, driven by pilots
- A public multi-tenant client ID — bring-your-own registration is the trusted path; a config hook is enough

## Context

**Origin.** `HANDOFF.md` is the original specification. On 2026-11-21 two independent analyses (Claude Fable 5.2 and Codex GPT-6.2-Astra) reviewed it and agreed on "build with changes". Their agreed changes are recorded in `DECISIONS.md`, which wins over `HANDOFF.md` wherever they conflict.

**Why now.** European public bodies and small organisations are reconsidering Microsoft. Schleswig-Holstein moved more than 40,000 mailboxes to open source in 2025. A Swiss study in October 2026 found a quick, full replacement unrealistic and advised each administration to assess its own situation in a structured way. The first step, an honest inventory, is today a paid study or a vendor sales call.

**What already exists.** Google's Apache-licensed Migration Planner scans Microsoft tenants for moves to Google. Plan EU sells a browser-local macro scan. ShareGate and Microsoft's own tools produce inventories for Microsoft-to-Microsoft moves. None produces a neutral decision document aimed at open source targets, in German, that a third party can reproduce. Discovery alone is a commodity; the durable parts are the rule data, the evidence model and trust.

**Facts verified against Microsoft's documentation on 2026-11-21.**
- Usage-report endpoints such as `getMailboxUsageDetail` answer with a `302` to a pre-authenticated URL on another host (`reports.office.com` in Microsoft's example).
- The mailbox usage CSV has no recipient-type column, so shared mailboxes cannot be counted from it.
- `GET /users/{id}/drive` can provision a missing OneDrive for a licensed user. A GET can therefore write.
- Since 1 July 2026 all new Entra tenants block device code flow under security defaults.
- Delegated Graph permissions reach only what the signed-in user can already access.

**Users.** The person running the tool is usually an integrator or an IT provider's engineer on Linux or macOS. The person reading the report is an IT lead or a non-technical decision-maker. The report must work for the second without help from the first.

**How the work is done.** The founder is an AI-assisted coder and says so openly. Claude and Codex both write code here and review each other's work; the README will state this. Because the founder cannot audit every line at the models' level, trust must rest on things anyone can check: small readable modules, tests that enforce each principle, and a minimal dependency list.

**Funding.** A Prototype Fund application (Resilienz track, deadline 30 November 2026) is drafted. If granted, funding runs from June 2027 and covers later work only; nothing in this roadmap depends on it.

## Constraints

- **Read-only**: Request only read permissions and call only allow-listed read endpoints — a GET that provisions resources is excluded
- **Network**: Only `login.microsoftonline.com` and `graph.microsoft.com`, enforced in one transport and by test — the central trust promise
- **Tokens**: In memory only, never on disk — a scan must leave no credentials behind
- **Privacy**: No person names or email addresses in the report or `scan.json` unless `--include-names` is passed
- **Offline report**: One `.html` file with inline CSS and JS, system fonts, no external resources, prints cleanly to PDF
- **Honest numbers**: No hardcoded prices; unknowns are shown as unknown; a skipped collector never improves a status
- **Tech stack**: Python 3.12+, Typer, Jinja2, httpx, MSAL for Python, pytest with recorded fixtures, ruff, packaged for `uvx` — small and auditable; ask before adding any other dependency
- **Languages**: German and English from day one; all user-facing strings in `locales/de.yaml` and `locales/en.yaml`, none hardcoded in templates
- **Licence**: AGPL-3.0-or-later with SPDX headers — keeps the rule data and the tool from being absorbed into a closed product
- **Accessibility of status**: Status colours differ in lightness and always carry a text label; blue and orange rather than red and green
- **CI**: Never needs a live tenant
- **Plain language**: Code and documentation a council IT officer could read and trust

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Primary user is the integrator, not the town IT officer | Officers often lack Python, tenant rights, or run through an IT provider | — Pending |
| Market is Germany, Austria, Switzerland, public and private | German municipalities are mostly not in Microsoft 365; Austrian and Swiss ones are | — Pending |
| Positioning is exit readiness, not exit | Most organisations will not leave soon but must show they could | — Pending |
| Keep AGPL-3.0-or-later | A permissive licence gives away the rule data and neutral name | — Pending |
| No single readiness score; per-workload status with unknowns | A denied collector must never look like readiness | — Pending |
| Evidence on every finding | Lets a third party reproduce and challenge the report | — Pending |
| Judgement (rules, costs, `report`) ships with the demo | The demo needs real judgement and no tenant | — Pending |
| `import` of CSV exports before live sign-in | Removes consent and sign-in friction from the first real scan | — Pending |
| Keep the two-host rule; usage reports through `import` | Microsoft's report endpoints redirect to a third host | — Pending |
| Browser sign-in with PKCE by default, device code as fallback | Device code is blocked by default in new tenants | — Pending |
| Endpoint allowlist in addition to scope checks | A GET can provision a OneDrive | — Pending |
| `.dotx` removed from risky types; macro extensions reported as "may contain macros" | An extension proves neither macros nor business impact | — Pending |
| Tenant-wide file inventory deferred | Needs broad application permissions; value unproven | — Pending |
| Signed self-contained Windows build beside `uvx` | Managed Windows machines often cannot run `uvx` | — Pending |
| AI-assisted development is disclosed | Honesty with users and maintainers; trust rests on tests and readability | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-11-21 after initialization*

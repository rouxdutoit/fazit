<!-- GSD:project-start source:PROJECT.md -->

## Project

**m365-exit-scan**

A free, open source command-line tool that shows an organisation what it runs on Microsoft 365, what would break if it moved to an open source stack (openDesk, Nextcloud, LibreOffice, Linux), and what that move would cost. It works read-only and locally, and writes one self-contained HTML report in German or English that opens offline. It is used mainly by integrators and municipal IT providers on behalf of organisations with roughly 200 to 2,000 seats in Germany, Austria and Switzerland, and it stays simple enough for a council IT officer to run alone.

**Core Value:** An organisation gets honest, inspectable numbers about its own Microsoft dependency, including "unknown" and "not yet", without any of its data leaving the machine.

### Constraints

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

<!-- GSD:project-end -->

<!-- GSD:stack-start source:STACK.md -->

## Technology Stack

Technology stack not yet documented. Will populate after codebase mapping or first phase.
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->

## Conventions

Conventions not yet established. Will populate as patterns emerge during development.
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->

## Architecture

Architecture not yet mapped. Follow existing patterns found in the codebase.
<!-- GSD:architecture-end -->

<!-- GSD:skills-start source:skills/ -->

## Project Skills

No project skills found. Add skills to any of: `.claude/skills/`, `.agents/skills/`, `.cursor/skills/`, `.github/skills/`, or `.codex/skills/` with a `SKILL.md` index file.
<!-- GSD:skills-end -->

<!-- GSD:workflow-start source:GSD defaults -->

## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:
- `/gsd-fast` for a trivial task inline, with no subagents and no PLAN.md
- `/gsd-quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd-debug` for investigation and bug fixing
- `/gsd-execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->

<!-- GSD:profile-start -->

## Developer Profile

> Profile not yet configured. Run `/gsd-profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->

## Engineering standards

Read `AGENTS.md` at the repository root before changing code. It holds the rules both Claude and Codex follow here: what the tool must never do, code and report standards, tests, and what "done" means. Product code on this project is written by Codex (GPT-6.2-Sol, max effort) under Claude's coordination; Claude subagents plan, check and review.

<!-- GSD:project-start source:PROJECT.md -->

## Project

**fazit**

A free, open source command-line tool that shows an organisation what it runs on Microsoft 365, what would break if it moved to an open source stack (openDesk, Nextcloud, LibreOffice, Linux), and what that move would cost. It works read-only and locally, and writes one self-contained HTML report in German or English that opens offline. It is used mainly by integrators and municipal IT providers on behalf of organisations with roughly 200 to 2,000 seats in Germany, Austria and Switzerland, and it stays simple enough for a council IT officer to run alone.

**Core Value:** An organisation gets honest, inspectable numbers about its own Microsoft dependency, including "unknown" and "not yet", without any of its data leaving the machine.

The current project constraints are in [AGENTS.md](../AGENTS.md) and the [principles](../DECISIONS.md#principles).

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

Read [AGENTS.md](../AGENTS.md) before changing code. It covers code, report, test and verification standards. Read [DESIGN.md](../DESIGN.md) before changing the website or the report: its design and copy rules are binding, so work is built to them rather than fixed in review. Claude and Codex assist with writing and reviewing changes under the direction of the human maintainer.

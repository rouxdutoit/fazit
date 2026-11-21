# Working on m365-exit-scan

Instructions for anyone, human or AI, who changes this repository. Short on purpose. If a rule here conflicts with convenience, the rule wins.

## Read first

1. `DECISIONS.md` — what was decided and why. It overrides `HANDOFF.md`.
2. `HANDOFF.md` §2 — the eight principles. They are not negotiable.
3. `.planning/PROJECT.md` — scope, constraints, what is out of scope.

## What this tool must never do

- Write to a tenant, or call an endpoint that is not on the read allowlist.
- Contact any host other than Microsoft sign-in and Microsoft Graph. Phase 1 and 2 code contacts no host at all.
- Put a token, a person's name or an email address on disk by default.
- Load anything external from the report.
- Invent a number. Unknown stays unknown, and a skipped collector never improves a status.

Each of these has a test. A change that weakens one of those tests is rejected.

## Code

- Python 3.12+. Type hints on every function. Frozen dataclasses for data.
- Small modules with one job. Functions that fit on a screen. No inheritance trees, no metaprogramming, no plugin systems, no abstraction added for a future that has not arrived.
- No dead code, no commented-out code, no `TODO` left behind. If something is deferred, it goes in `DECISIONS.md`.
- Comments say why, never what. Names carry the what.
- Dependencies: `typer`, `jinja2`, `pyyaml`; dev: `pytest`, `ruff`. Adding one needs a new entry in `DECISIONS.md` first.
- Data, not code, holds judgement: mappings, status rules, risky file types and all user-facing text live in YAML inside the package.
- `yaml.safe_load` only. Jinja2 with autoescape on. No `eval`, no `exec`, no shell calls, no pickle.
- Files are written only inside the directory the user named with `--out`.
- Errors shown to users are one plain sentence that names the file and the field. No tracebacks unless `--debug`.
- Output is deterministic: the same inputs give the same bytes. Dates and clocks are passed in, not read deep inside functions.

## Report

- One HTML file. Inline CSS, system fonts, no JavaScript unless there is no other way, nothing fetched at view time.
- Semantic HTML: one `h1`, ordered headings, `lang` set, table headers with `scope`, text contrast at WCAG AA in light and dark.
- Status is never colour alone. Every status has a text label; every figure says whether it was measured, provided or is unknown.
- It must print cleanly and read well at 360 px.

## Words

- Plain language a council IT officer can read and trust. No marketing words.
- Every user-facing string exists in `locales/en.yaml` and `locales/de.yaml`. German is written as German: formal "Sie", administrative register, not a word-for-word translation.

## Tests

- Fast, offline, deterministic. No test needs a tenant or the network.
- Every principle has a test that fails when the principle is broken.
- A bug fix comes with the test that would have caught it.

## Done means

```
uv run ruff check .
uv run ruff format --check .
uv run pytest -q
uv run m365-exit-scan demo --lang de
uv run m365-exit-scan demo --lang en
```

All five succeed, and the two reports open with the network off.

## Commits

- One logical change per commit. Imperative subject under 72 characters, with a conventional prefix (`feat`, `fix`, `test`, `docs`, `chore`).
- This project is written with AI assistance and says so. A commit made by a model carries a `Co-Authored-By` trailer naming it. A human maintainer directs the work and is responsible for it.
- Never commit anything under `drafts/` or `grants/`, and never commit real tenant data.

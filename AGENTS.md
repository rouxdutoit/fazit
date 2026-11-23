# Working on fazit

Instructions for anyone, human or AI, who changes this repository. Short on purpose. If a rule here conflicts with convenience, the rule wins.

## Read first

1. [Principles](DECISIONS.md#principles) — the eight rules every change must follow. The rest of `DECISIONS.md` records decisions and overrides `HANDOFF.md`.
2. `.planning/PROJECT.md` — scope and constraints.
3. [DESIGN.md](DESIGN.md) — binding design and copy rules for the website and the report. Build to them from the start.

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
- Dependencies: `typer`, `jinja2`, `pyyaml`; dev: `pytest`, `ruff`, `hypothesis`. Adding one needs a new entry in `DECISIONS.md` first.
- Data, not code, holds judgement: mappings, status rules, risky file types and all user-facing text live in YAML inside the package.
- `yaml.safe_load` only. Jinja2 with autoescape on. No `eval`, no `exec`, no shell calls, no pickle.
- Files are written only inside the directory the user named with `--out`.
- Errors shown to users are one plain sentence that names the file and the field. No tracebacks unless `--debug`.
- Output is deterministic: the same inputs give the same bytes. Dates and clocks are passed in, not read deep inside functions.

## Report

- One HTML file. Inline CSS, embedded fonts, no JavaScript, nothing fetched at view time.
- Semantic HTML: one `h1`, ordered headings, `lang` set, table headers with `scope`, text contrast at WCAG AA in light and dark.
- Status is never colour alone. Every status has a text label; every figure says whether it was measured, provided or is unknown.
- It must print cleanly and read well at 360 px.

## Words

- Plain language a council IT officer can read and trust. No marketing words.
- Every string in the report, and every message the tool prints, exists in `locales/en.yaml` and `locales/de.yaml`. Command and option help is English only (`DECISIONS.md` D18). German is written as German: formal "Sie", administrative register, not a word-for-word translation.

## Tests

- Fast, offline, deterministic. No test needs a tenant or the network.
- Every principle has a test that fails when the principle is broken.
- A bug fix comes with the test that would have caught it.

## Done means

```
uv run ruff check .
uv run ruff format --check .
uv run pytest -q
uv run fazit demo --lang de
uv run fazit demo --lang en
uv run python site/check_site.py
node site/check_alignment.mjs
node site/check_spacing.mjs
node tests/browser/check-scrollbars.mjs
```

Every command succeeds, and the two reports open with the network off. Changes to the website or the report follow [DESIGN.md](DESIGN.md).

The alignment, spacing and scrollbar checks use local Playwright and run in Chromium and WebKit by default, with separate results and the same limits for each engine. Set `PLAYWRIGHT_ENGINE` to `chromium` or `webkit` to run a single engine. Set `PLAYWRIGHT_DIR` to the directory containing the `playwright` package if it differs from `/home/roux/.local/share/playwright-1.62.1/node_modules/`. The spacing check measures the named relations in [DESIGN.md](DESIGN.md#vertical-rhythm) on all pages at 360, 768 and 1280 px and lists any gaps that differ.

If report output changes, copy the HTML from the two demo runs above to `site/demo/de/index.html` and `site/demo/en/index.html`, using the matching language for each file.

## Commits

- One logical change per commit. Imperative subject under 72 characters, with a conventional prefix (`feat`, `fix`, `test`, `docs`, `chore`).
- Credit Codex in an `Assisted-by:` trailer and Claude in a `Co-Authored-By:` trailer. Name the model. A human maintainer directs the work and is responsible for it.
- From the first public release, commits from contributors outside the maintainer team carry a DCO `Signed-off-by:` trailer. See [CONTRIBUTING.md](CONTRIBUTING.md).
- Never commit anything under `drafts/` or `grants/`, and never commit real tenant data.

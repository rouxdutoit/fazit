---
quick_id: 261122-sim
slug: simulation-tests
date: 2026-11-22
status: complete
---

# Quick task: simulation tests over synthetic tenants

The tests prove the principles on the two samples and on hand-picked edge cases. This task adds property-based tests that generate many synthetic tenants and check that the principles hold on every one of them, plus a user-journey test from the built wheel. Hypothesis is allowed by D28 in `DECISIONS.md`, pinned to exactly 6.170.15.

## Scope

New: `tests/test_simulation.py` (and, only if it keeps that file under about 400 lines, one `tests/tenants.py` holding the Hypothesis strategies). Changed: `pyproject.toml` and `uv.lock` (dev dependency `hypothesis==6.170.15`), `tests/conftest.py` (one Hypothesis settings profile), `tests/test_installed_package.py` (malformed inputs from the installed wheel). No change to `src/` unless a generated tenant exposes a real defect; see "If a test finds a bug".

## Tasks

1. **Dependency.** `uv add --dev hypothesis==6.170.15`. `uv lock --check` passes and `exclude-newer` is unchanged. Register one profile in `tests/conftest.py`: `derandomize=True`, `database=None`, `deadline=None`, `print_blob=True`, and a `max_examples` chosen so the whole new file runs in under 20 seconds on this machine.

2. **Strategies.** Generate valid inputs from the package's own data, never from hand-written lists that can drift: registered collectors, workloads, evidence codes and licence product and plan pairs come from `fazit.catalogue`, `fazit.rules` and the rule YAML files. A synthetic tenant varies:
   - each collector's status (every status the schema allows, including skipped and denied);
   - each evidence item's coverage (complete, partial, unknown), counts within and at the edges of the total, zero totals;
   - licence mixes: suites, add-ons, bundled plans, purchased and assigned counts, none at all;
   - `inputs.yaml`: present or absent, each answer present, missing or zero, `as_of` present or absent, `amounts_are_invented` either way, Windows-only software lists, cost inputs including zero, missing and large values;
   - language (`de`, `en`) and profile (every profile in `rules/mappings/`).
   Build tenants through the same writers the tests already use or by writing `scan.json` and `inputs.yaml` into `tmp_path`, and run them through the public path (`fazit report` via Typer's `CliRunner`, or the functions it calls). Reuse existing helpers in `tests/` rather than copying them.

3. **Invariants.** One property test each, every one over the generated tenants:
   - **Nothing is Ready on incomplete evidence.** If any required evidence for a workload is missing, skipped, denied, unknown or partial, that workload's status is not Ready, and the report lists the gap.
   - **A worse collector never improves a status.** Take a generated tenant, degrade one collector (complete to partial, or to skipped or denied) or one evidence item, and assert no workload's status moves towards Ready. Use the status order the rules already define; do not invent one in the test.
   - **No person data in any output.** Plant person names, email addresses and token-like strings in every place the loader must drop (unknown keys, unknown values, extra fields) and assert none of them reaches the HTML, any written file, any file name, stdout or stderr. Names allowed by principle 5 (organisation name and Windows-only application names from `inputs.yaml`) are excluded from the check.
   - **Identical input gives identical output.** Rendering the same tenant twice gives the same bytes. For a few examples, also render in two subprocesses with different `PYTHONHASHSEED` values and compare bytes.
   - **Costs add up.** For each scenario, the total equals the sum of its blocks, and the difference equals the total minus the stay total. Recompute every figure independently in the test from the generated inputs with `fractions.Fraction` and the formulas in `DECISIONS.md` (M0 section), including the rule that an unknown factor leaves a product unknown unless another factor is zero, and that a comparison is unknown when either side is. Check the figures shown in the report match.
   - **Every report renders under the CSP and loads nothing.** The Content-Security-Policy meta is present and unchanged, and the document has no `script`, no external `link`, no `src` or `href` to another origin or protocol-relative URL, no `url()` other than `data:`, no `@import`. Reuse the parser in `tests/test_report.py` if it fits.

4. **User journey from the wheel.** In `tests/test_installed_package.py`, after the existing install-and-run-offline steps, run the installed `fazit report` against malformed input files: missing file, directory instead of file, empty file, invalid JSON, JSON that is not an object, wrong `schema_version`, invalid UTF-8, YAML with a duplicate key, YAML with a wrong type, a negative or non-finite number, deeply nested input, and a `--out` that is a file. Each must exit non-zero with one plain sentence that names the file and, where there is one, the field; no traceback; nothing written; no socket use (the existing audit hook). Reuse the session fixture so the wheel is built once.

## Rules

- Never weaken an existing test. Never relax a check in `src/` to make a generated case pass.
- Tests read like the existing ones: short, typed, no docstrings that repeat the name, no comments that say what.
- Keep the added runtime of the whole suite under 30 seconds.

## If a test finds a bug

Do not hide it with `assume()` or by narrowing a strategy. Fix the defect in `src/` with the smallest change, keep the generated case as an `@example` so it stays covered, and describe it in the summary under "Bugs found" with the shrunk tenant.

## Done means

```
uv run ruff check .
uv run ruff format --check .
uv run pytest -q
uv run fazit demo --lang de
uv run fazit demo --lang en
uv run python site/check_site.py
```

All pass. Report the suite's test count and runtime before and after.

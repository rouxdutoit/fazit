# Plan 01-06 summary

Befund compares staying, partial exit and full exit over five years. The report shows inputs, running costs, direct project costs, productivity loss, parallel running, totals and differences from staying. It names missing inputs by scenario, labels supplied and sample values, and follows `amounts_are_invented` for the invented-price notice. The appendix explains the formulas and records the tool version, rule checksums, scan date and periods, and inputs date. All nine sections render in both languages and all three profiles. Workload evidence expands on screen and appears in print. Unknown evidence shows the translated reason and next step where applicable.

The town demo renders totals of EUR 600,000.00, EUR 527,800.00 and EUR 464,350.00. Partial and full exit differ from staying by EUR −72,200.00 and EUR −135,650.00. The nonprofit demo renders EUR 22,000.00, EUR 29,870.00 and an unknown full-exit total. The partial exit difference is EUR 7,870.00. The missing full-exit input is `target_costs.full_exit.productivity_loss`.

## Public interfaces

- `costs.compute_scenarios(inputs: Inputs) -> tuple[ScenarioResult, ...]` returns results in `SCENARIOS = ("stay", "partial_exit", "full_exit")` order. `YEARS = 5`, `MONTHS = 60`, `MONTHS_PER_YEAR = 12` and `BLOCKS = ("direct_project", "productivity_loss", "parallel_running")`.
- The frozen dataclasses are `costs.CostLine(id: str, amount: Decimal | None, missing: tuple[str, ...])`, `costs.CostGroup(id: str, lines: tuple[CostLine, ...], total: Decimal | None, missing: tuple[str, ...])` and `costs.ScenarioResult(id: str, running: CostGroup, blocks: tuple[CostGroup, ...], total: Decimal | None, missing_inputs: tuple[str, ...], difference_to_stay: Decimal | None)`. Missing paths are deduplicated in formula order.
- `i18n.Formatter(lang: str)` provides `money(amount: Decimal, currency: str) -> str` with half-up display rounding, `number(value: Decimal) -> str` for localized decimal quantities and `period(value: str) -> str` for abbreviated dates. A period spanning two years shows both years.
- `rules.rule_file_checksums(profile: str) -> tuple[tuple[str, str], ...]` reports basenames and SHA-256 digests from `rules_dir() -> Traversable`. The renderer uses the digests captured during parsing.
- `report.render_report(scan: Scan, *, lang: str, profile: str = "opendesk", catalogue: Catalogue | None = None, provided: tuple[Finding, ...] = (), inputs: Inputs | None = None, sample_inputs: bool = False) -> str` returns HTML. `report.report_file_name(generated_at: str, *, lang: str) -> str` returns `report-<YYYY-MM-DD>-<lang>.html`. The nine `SECTION_ORDER` entries are `header`, `found`, `costs`, `readiness`, `moves`, `attention`, `path`, `appendix` and `footer`. The template exposes `data-scenario` with `data-total`, `data-block` for the running costs and three blocks, `data-missing-cost`, and the three `data-subsection` values `not-examined`, `cannot-be-moved` and `run-details`.
- `cli.app` and `cli.main() -> None` expose `befund [--debug] demo [--lang en|de] [--sample town|nonprofit] [--profile opendesk|nextcloud|generic] [--out DIR]` and `befund [--debug] report SCAN_JSON [--inputs FILE] [--lang en|de] [--profile opendesk|nextcloud|generic] [--out DIR]`. The defaults are `en`, `town`, `opendesk` and `./report` where applicable. Report language and profile resolve from flags, the inputs file and defaults. Global `--version` prints the version. Both commands end stdout with the absolute HTML path. Demo also writes dated `scan-<YYYY-MM-DD>-<lang>.json` and `inputs-<YYYY-MM-DD>-<lang>.yaml` copies.

## Dependencies

`uv sync --locked --offline` exited 0. `uv tree --depth 1` reported Befund 0.1.0, Jinja2 3.1.6, PyYAML 6.0.3 and Typer 0.28.0, with pytest 9.2.0 and Ruff 0.17.4 in the development group. Hatchling 1.33.0 is the pinned build backend.

## Verification

- Task 1. `uv run pytest tests/test_costs.py tests/test_locales.py -q && uv run ruff check . && uv run ruff format --check .` exited 0 with 28 tests at the task gate and 35 on the final tree. `uv run pytest tests/test_costs.py -q` passed 17 tests at the gate and 24 on the final tree. The cost tests assert the worked example and the edge totals 507800 and 707800. A default injected into a temporary copy of `costs.py` caused the all-null test to fail as expected. The cost module imports only `inputs` and standard-library modules.
- Task 2. The full automated chain exited 0. `uv run pytest -q` passed 453 tests under the socket guard, `uv run ruff check .` passed, and `uv run ruff format --check .` found 50 files formatted. `uv run befund demo --sample nonprofit --lang en --out "$out"` produced the printed report path in a fresh directory. The file and all three HTML probes for costs, unknown total and run details passed. The tests verified the full sample, language and profile matrix, all five digests and one read per rule file, a changed digest after editing a copied rule, and identical results under two system dates. A separate CLI rebuild with `inputs.example.yaml` showed three unknown totals and omitted the invented-amounts label.
- Final. `uv run befund demo --lang de --out "$out"` and `uv run befund demo --lang en --out "$out"` each exited 0 in separate fresh directories and produced the expected town totals. Chromium loaded only each local HTML file with HTTP and HTTPS blocked and offline emulation active. Both versions fit at 360 and 1200 px in light and dark mode. The A4 PDFs included the collapsed evidence and cost input tables. Locale parity and `git diff --check` passed.

## Deviations and open work

- Prorated amounts combine in exact twelfths before conversion to Decimal. A division by 12 that repeats uses a high-precision Decimal representation because the exact fraction has no finite decimal form. The formatter rounds to cents for display.
- The report uses hashes captured from the same bytes the loaders parsed under D-73. The new `rule_file_checksums(profile)` function provides the standalone manifest.
- The money placement patterns landed in both locale files during Task 1. The existing CLI and locale tests were also updated for the ninth section, shorter periods and the full reproducibility matrix.
- The cost input table uses a native disclosure panel that expands in print alongside the workload evidence. At phone width the three scenario columns stay side by side below each row label.

Plan 01-06 is complete. The changes are in the working tree for the orchestrator.

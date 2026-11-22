---
quick_id: 261122-rv5
status: complete
date: 2026-11-22
---

# Release review batch 5

## Plan results

1. Split mapping, licence, readiness and evidence code out of `rules.py`. Classification, JSON export and report rendering share a cached SKU and service plan index. Renamed the mapping type to `TargetMapping` and removed the scan model's type-only dependency on rules.
2. Split workload evaluation into condition evaluation and rule selection. Separated licence inventory, directory cross-checks and derived findings. Read catalogue rows before checking their references to population counts.
3. Centralised GUID, date, identifier and non-negative integer checks. The scan, inputs, catalogue and rule loaders keep their own field and error policies.
4. Replaced the Decimal cost calculation with exact fractions. Display amounts round to cents, with half cents rounded away from zero. The HTML data attributes keep their existing decimal representation.
5. Centralised language validation, simplified GUID parsing and moved the section order to test data. Removed shared-container tracking from the privacy walk and its synthetic test. YAML float validation checks composed scalars directly and keeps the existing error locations.
6. Kept comments that explain the constraints, including the reason for handling PyYAML constructor errors. The CLI docstrings supply command help.

The line count for `src/fazit/*.py` went from 3,576 to 3,573. `rules.py` went from 971 lines to 28.

## Files

- `src/fazit/catalogue.py` validates catalogue rows with the shared patterns and checks population references after reading the rows.
- `src/fazit/cli.py` uses the shared language check and imports profile names from the mapping module.
- `src/fazit/costs.py` calculates cost lines, subtotals and differences as fractions and carries the input precision for HTML attributes.
- `src/fazit/evidence.py` owns manual finding construction, evidence precedence and conflict checks.
- `src/fazit/i18n.py` validates languages and formats currency from exact cents.
- `src/fazit/inputs.py` parses manual inputs with shared field checks and calendar date validation.
- `src/fazit/licences.py` loads the indexed licence registry, derives findings and filters identifiers for public scan JSON.
- `src/fazit/mappings.py` loads the target profiles and validates the evidence referenced by each mapping.
- `src/fazit/model.py` validates scan fields with shared checks and keeps scan and coverage data.
- `src/fazit/parsing.py` checks floats without a separate YAML load and rejects at signs in parsed inputs.
- `src/fazit/report.py` uses the new modules and formats exact costs for the existing HTML attributes.
- `src/fazit/risky_files.py` loads the risky file type definitions.
- `src/fazit/rules.py` reads and checksums rule files.
- `src/fazit/status.py` loads and evaluates readiness rules.
- `src/fazit/templates/report.html.j2` passes source precision to the cost attribute formatter.
- `src/fazit/validation.py` holds the common patterns and field validators.
- `site/check_site.py` imports mappings and status codes from their new modules.
- `tests/report_expectations.py` holds the expected section order.
- `tests/tenants.py` loads licence and status rules from their new modules.
- `tests/test_cli.py` uses the shared section order and patches the shared date validator for the clock tests.
- `tests/test_evidence_cli.py` imports the relocated service plan loader.
- `tests/test_inputs.py` imports evidence functions and rule loaders from their new modules.
- `tests/test_installed_package.py` uses the shared section order.
- `tests/test_model.py` removes the test for an artificial shared container that the input parsers cannot produce.
- `tests/test_privacy.py` imports the relocated licence registry and scan serializer.
- `tests/test_report.py` uses the shared section order and relocated profile names.
- `tests/test_rules.py` imports the relocated rule loaders and shared section order.
- `tests/test_simulation.py` imports evidence, serialization and status functions from their new modules.
- `.planning/quick/261122-rv5-lean/SUMMARY.md` records the changes and verification.

## Compatibility and deviations

- Fractional timestamp comparisons remain because scan inputs accept fractional seconds, including precision below one microsecond.
- Render-time coverage validation remains because the renderer accepts in-memory scans that bypass the file loader. An existing test covers this path.
- Locale loads still deep-copy cached data so callers can use ordinary dictionaries and lists without mutating other callers' data.
- Decimal serialization remains at the HTML attribute boundary to preserve the bytes of prorated amounts. Cost arithmetic and currency rounding use fractions.
- Review suggestions to remove fonts or change site animation fall outside the byte-identical refactor. Principle 6 also requires embedded fonts.

Report wording and layout matched the baseline. Both checked-in demo pages matched a fresh run and required no regeneration. The JSON and YAML sidecars matched for all 12 variants.

## Verification

- `uv sync`, `uv run ruff check .` and `uv run ruff format --check .` passed.
- `uv run pytest -q` passed 693 tests in 114.67 seconds.
- `uv run pytest -q tests/test_simulation.py --hypothesis-profile=deep` passed 6 tests in 908.30 seconds.
- `uv run fazit demo --lang de` and `uv run fazit demo --lang en` passed. Both reports opened in offline Chromium at 360 px with their embedded fonts and zero network requests.
- `uv run python site/check_site.py` checked 16 pages and 519 references with no errors.
- Before and after SHA-256 values matched for all 12 reports.

```text
town-opendesk-en e970e42009f01f7ab5a48cc353952b3866f5b9e14e93474ce30396a852421e51
town-opendesk-de ed2f7862d3694394a29483b6b2f0c7d9a6398d2318662009062f2b42ab6c58a6
town-nextcloud-en 54a24e3f081da6a0e62be63b07355fe0812dc0cc1456cb2b1248168bf3a07a92
town-nextcloud-de 2f90e20be6eacddcb85dc809cc19df225a4f5690031668ded77ae8540cef2922
town-generic-en 25ad5960dd853273ef1592e0fe690a65b0a3528c9e72921718ecb7a24a431b8e
town-generic-de 362d9689842d2f7c7d36164a153778b7fc49e8ecc6bc962f2ed30de64a68f7b0
nonprofit-opendesk-en 291125a5b8bef05b4c766d315d3530f19c43d182449b7df295069276fae794b8
nonprofit-opendesk-de 627ffe7a08a28e1eaffb67ddcd9cd070d2e87e9957d3801d5da22781aa22e4d7
nonprofit-nextcloud-en 0c1e5ad73dce7f835994d76205499cd32843c0027f95ca3dceb8f22d8d498e41
nonprofit-nextcloud-de 995110214e23deda51a90b616aaccd521abdffdfab24ecb01973c419588d4fa2
nonprofit-generic-en 42a2710a1d849a74181923aa04731e0e124d72f187269be92803b7e68dc485fc
nonprofit-generic-de 384c487592c93779e49fd3605557d3bdd8b60d92abf84a029d297f6a322d004f
```

Additional comparisons matched for repeating prorations, high-precision training inputs, YAML float spellings and sub-microsecond timestamps.

## Open items

None for this task.

## Suggested commits

1. `chore: split mapping, licence, status and evidence modules`
2. `chore: extract rule evaluation and catalogue loading steps`
3. `chore: share validation across input and rule readers`
4. `chore: calculate report costs with exact fractions`
5. `chore: simplify parser, language and section order checks`
6. `docs: clarify compatibility decisions and record verification`

## Orchestrator note

Claude applied the patch to `main` three-way without conflicts and re-ran the checks there: 693 tests, the site check, and the same 12 report hashes. The default simulation run went from about 20 to about 48 seconds. Rendering is not slower (in-process demo renders and the other test files take the same time); Hypothesis derives its derandomised seed from the test source, so the changed imports select different, larger tenants.

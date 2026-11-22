---
quick_id: 261122-sim
status: complete
date: 2026-11-22
---

# Simulation tests over synthetic tenants

## Plan results

1. `pyproject.toml` pins Hypothesis 6.170.15 for development. `uv.lock` records Hypothesis and sortedcontainers with the existing cutoff. `tests/conftest.py` loads the deterministic 18-example profile and removes the temporary constants cache after pytest. `tests/test_repo_basics.py` checks the approved development dependency list and the exact pin. The lockfile check passes.
2. `tests/tenants.py` builds schema-valid synthetic scans and optional answers from the package catalogue, rule data and product rosters. It varies collector state, coverage and counts, licence assignments, manual evidence and costs, language and mapping profile. Permission denial uses the schema's skipped status with the permission-denied reason.
3. `tests/test_simulation.py` checks evidence and reported gaps, collector and evidence degradation, privacy, byte reproducibility, report costs against independent Fraction calculations, and the offline CSP. The reproducibility test also compares two cases across two Python hash seeds. All six properties pass.
4. `tests/test_installed_package.py` runs fourteen malformed-file cases against the same installed wheel. Every case returns one localized sentence naming the file and field. The checks confirm an empty socket audit and an identical workspace snapshot.

## Verification

All six Done means commands pass. The suite went from 586 passed in 51.10 seconds to 606 passed in 78.22 seconds, an increase of 27.12 seconds. The simulation file passed in 19.47 seconds on its own. The site checker passed for 16 pages and 501 references.

The CLI behavior and wording are identical. The fresh German and English reports match the checked-in demo HTML byte for byte. Both open in Chromium with external network access blocked.

## Deviations

The full suite exposed a dependency guard that predated D28. Updating `tests/test_repo_basics.py` brings that guard into line with the plan and preserves its exact allowlist.

The degradation property uses the rule order for assessed statuses and rejects any transition from Unknown to Ready. The retained office-file case has a complete measured macro count of zero, a supplied count of one, and four missing findings. With partial measured coverage, the supplied count confirms a problem and the four gaps remain. That transition from Unknown to Needs work follows the evidence rules.

## Open work

None.

## Suggested commits

- `test: add deterministic simulations for tenant reports` for the dependency, guard, profile, generator and properties.
- `test: check malformed input through the installed wheel` for the installed-wheel cases and this summary.

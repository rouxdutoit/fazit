# Fazit release review 4, confirmation (reviewer: Claude Fable 5.2)

Commit `0ae2be2`, private clone, 2026-11-22.

## Verdict

**Release after one fix.** The licence rule holds and every judgement finding is fixed, but F3-01 is only partly fixed and the public CI on `main` has been red since this commit (F4-01).

Remaining code and site findings: 0 critical, 1 high, 0 medium, 3 low.

Ran: both Ruff checks; `pytest -q` (705 passed on CPython 3.12, 3.14 and 3.15); both demos, equal to `site/demo`; `site/check_site.py` (18 pages, 610 references); `uv build` and a wheel install with a byte-identical report; 5,048 malformed-file cases (0 problems); a run without a network; 17 routes in Chromium under the declared headers (no console error); Firefox; print to PDF; 15 external links.

## Round-3 findings

- **A3-01.** Fixed. Zero licensed accounts with 20 assigned seats: Licences and four dependent areas Unknown, none on the Ready list.
- **A3-02.** Fixed. 20 licensed, one seat, headcount denied or one second apart: the same.
- **A3-03.** Fixed. Use measured in 1 of 85 with replacement No is a Blocker, with need "Yes · Measured"; against a supplied No, Unknown.
- **A3-04.** Fixed. The copy button yields three clean lines in Chromium and Firefox.
- **A3-05.** Partly fixed (low). README, start pages and home timeline match `ROADMAP.md`. `publiccode.yml:18-27,35-47` keeps the old order, "release packages (4)" and "a compatible scan file"; `site/integrators/index.html:60` and its German twin still say the roadmap lists features "planned before local import".
- **F3-01.** Partly fixed, see F4-01. The 4,300-digit `users` and unquoted 4,400-digit days now give one sentence and exit 2.
- **F3-02.** Fixed. Start, pilots and home agree in both languages.
- **F3-03.** Fixed. The path data equals simple-icons 10.4.0, as the licence file says.
- **F-05 leftovers.** Fixed.
- **Licence rule.** Not broken. About 65 hand-built variants (headcount denied, removed, partial, with a period, date-only, one second apart; collectors partial or skipped; empty inventory) and 2,400 random scans: no area was Ready on a licence absence without complete, same-instant, reconciling counts, and no consistent scan was refused.

## New findings

- **F4-01 · high · `src/fazit/inputs.py:45,132,155`.** A quoted `training_days_per_person` has no length bound before `Decimal()`. Where `decimal` falls back to the pure-Python module, as GitHub's hosted Python 3.15.2 behaves, 4,400 digits raise `ValueError` and exit 1. The project's own `test_report_bounds_cost_quantities[huge-decimal-days]` fails in the CI job "ubuntu-latest, 3.x": 1 failed, 704 passed for `0ae2be2`, and the job failed again on both later pushes. Reproduced locally by blocking `_decimal`: the same single failure. On the default build 200,000 decimals are accepted and printed in full. Fix: bound the pattern's digits before converting; tag only on four green jobs. The defect alone is medium; the red default branch makes it high.
- **F4-02 · low · `site/security/index.html:121`, `site/de/security/index.html:121`, `SECURITY.md:24`.** Still "checks the scan and inputs for contradictions", where README and home now say "selected relationships". `device_management.device_count: 10` with `windows_device_count: 20` builds a report, exit 0.
- **F4-03 · low · `site/de/index.html:144`.** "Ihre Messwerte sind simuliert." opens a sentence on a page that addresses the reader as "Sie", so it reads as "your measurements" (extracted page text). Write "Die Messwerte darin sind simuliert."

## Would it embarrass the project in public?

- **Code and site:** only F4-01, the failing CI on `main`.
- **Founder actions:** R-35 is open: RDAP 404 and no DNS for `fazit.dev`, PyPI 404 for `fazit`, while public files name both. R-36 is open: check live headers once the site is on bunny.net. R-40: the HANDOFF line is corrected; the `.claude/CLAUDE.md` placeholders remain.

Public `main` is two commits ahead of this clone; not reviewed.

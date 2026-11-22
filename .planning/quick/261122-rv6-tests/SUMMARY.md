---
quick_id: 261122-rv6
status: complete
date: 2026-11-22
---

# Release review batch 6

## Plan results

1. Reduced the demo matrix from twelve cases to six while covering every pair of sample, language and profile values. All twelve variants have the same stylesheet. Simulation still checks resource elements and attributes, inline styles and the content security policy on generated tenants.
2. Replaced the 26 clock-test renders with one demo and one rebuild on different mocked days. The test checks filenames, the displayed scan date and byte equality. The AST clock check still runs.
3. Consolidated symlink, dangling-link, directory and FIFO checks at the output writer. Kept CLI error localisation and private-path checks and one test that verifies `--debug` re-raises the original error.
4. Replaced prose matches with checks for runnable README examples, published install instructions, document links and trailers. CI must run each command from the AGENTS.md gate and the deep simulation. The CI tests check the Python versions, platforms, read-only permissions and action SHA pins independently of step order.
5. Moved cross-test utilities to `tests/helpers.py` and updated their callers.
6. Named the affected CLI tests after the behaviour they exercise and removed the comment about terminal colours.

## Files

- `tests/helpers.py` provides the shared CLI runner, report parser and selectors, sample paths, README parser, privacy assertions and subprocess socket audit.
- `tests/test_cli.py` reduces the demo and clock matrices, runs documented commands and consolidates output and debug coverage.
- `tests/test_evidence_cli.py` uses the shared readiness selector and CLI runner.
- `tests/test_inputs.py` checks the German checklist for informal address.
- `tests/test_installed_package.py` uses the shared audit, repository root and licence checksum.
- `tests/test_output.py` verifies that unsafe destinations leave the whole batch and link targets intact.
- `tests/test_privacy.py` uses the shared planted data and output assertions.
- `tests/test_repo_basics.py` checks executable documentation, contribution and security links, and CI requirements.
- `tests/test_report.py` imports the relocated helpers. Its test bodies were verified against HEAD after normalising helper names.
- `tests/test_rules.py` uses shared report selectors and the CLI runner and drops repeated debug calls.
- `tests/test_simulation.py` uses shared helpers and leaves the invariant stylesheet check to the report suite.

## Mutation checks

Ran 25 deliberate defects in temporary copies and restored the originals. The relevant tests failed for each defect.

- `test_report_cannot_fetch_resources` detected an external stylesheet and a missing embedded font. This covers the stylesheet assertion removed from simulation.
- `test_demo_writes_the_selected_sample_language_and_profile` detected the wrong sample, an empty input copy, an ignored language and an ignored profile in the retained cases.
- `test_source_does_not_read_the_clock` and `test_demo_and_report_use_the_scan_date_independently_of_the_clock` detected a wall-clock filename. The end-to-end test also detected a wrong displayed scan date.
- `test_batch_rejects_unsafe_destinations_before_writing_any_output` detected following an existing or dangling symlink, accepting directories or FIFOs, and checking destinations after earlier writes. It covers the removed CLI destination cases and the standalone dangling-link test. `test_cli_localises_bad_output_directory` detected success when `--out` named a regular file.
- `test_debug_reraises_the_underlying_input_error` detected a swallowed debug exception. It covers the deleted demo test and the repeated debug calls in the catalogue cases.
- `test_checklist_matches_inputs_and_catalogue` detected informal German address even with formal address elsewhere in the document.
- The retained documentation checks detected an unpublished install command, an unavailable import command, a public vulnerability-reporting link and a missing DCO trailer. The sample provenance test rejected sample evidence labelled as live or imported. The CI checks detected an omitted site command, a missing or bypassed Python version, write permissions at workflow or job level, and an action pinned to a tag. The tests accepted equivalent README prose, changed link labels and extra or reordered CI steps.

## Verification

The default suite went from 693 passed in 125.05 seconds to 671 passed in 106.19 seconds. Python lines under `tests/` went from 7,646 to 7,625 including shared support. Test modules alone went from 7,282 to 7,126. The final default run overlapped the deep simulation.

`uv sync` and all seven plan checks passed. The deep profile passed 6 tests in 880.90 seconds. The site check passed for 16 pages and 516 references.

The two demo reports matched the checked-in HTML byte for byte. Both opened in offline Chromium at 360 px in light and dark mode, with scripts disabled, embedded fonts loaded and zero network requests. The changes are confined to tests and this summary.

## Deviations and open work

The coordination note assigns report parametrisation to the redesign. The German checklist has a direct check for informal pronouns because the locale tests cover package strings. The README tests verify runnable claims and installation examples. The current capability wording in both READMEs was checked by reading it. RV6 is complete.

## Suggested commits

1. `test: reduce repeated demo and stylesheet checks`
2. `test: verify CLI dates with one run per command`
3. `test: consolidate output and debug safeguards`
4. `test: verify README examples and CI requirements`
5. `test: extract shared report and privacy helpers`
6. `test: clarify test names and record verification`

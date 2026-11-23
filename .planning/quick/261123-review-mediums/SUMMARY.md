# Release review medium fixes

Completed the five requested items in order in `open-mediums` on base `b80ad59`. Each item has a Done note in [completed to-dos](../../todos/completed/).

1. **Unidentified licence products.** Every product without a registered identity keeps inferred licence absences and reconciliation incomplete, including products with zero assignments. Confirmed assignments still count. The CLI regression checks both orders of removing the plan list and identifiers from an unassigned STANDARDPACK product.
2. **OneDrive storage coverage.** D31 and the loader bound attempted storage checks and the declared coverage total by the possible account population from the same export. A completely checked empty export can still establish zero accounts and zero storage.
3. **Output directory handles.** Fazit uses directory-relative operations for destination checks, staging, replacement and cleanup where supported. Moving an ancestor during the write leaves operations anchored to the opened directory. Platforms without those operations use the resolved pathname.
4. **Demo refresh recovery.** The existing filenames are retained. A handled replacement failure restores previous contents and removes files created during that refresh. If the filesystem also refuses a restore, Fazit reports the affected file and retains the saved copy when one exists.
5. **Collection stamps and reporting periods.** The loader rejects conflicting metadata within a collector and source pair and accepts equivalent offset timestamps. Independent sources retain their own stamps. Linked interview counts from the same source and calendar date are comparable without a reporting period. The Phase 2 plan uses the Microsoft 365 apps Active users export for dated licensed headcounts. A regression verifies that this evidence leaves reconciliation Unknown and preserves known assignments.

Both published demos were regenerated from the updated catalogue. The site Python SPDX check is registered in `checkout_files`. The source distribution still checks the SPDX identifiers of the files it contains.

## Verification

- `uv run ruff check .` and `uv run ruff format --check .` passed.
- `uv run pytest -q` passed all 1,115 tests.
- The [unpacked source distribution step](../../../.github/workflows/ci.yml) ran as written on Linux with CPython 3.12.16. It passed 1,097 tests with 18 checkout-only skips and zero failures.
- `uv run python site/check_site.py` checked 24 pages and 1,027 references with zero errors.
- `uv run fazit demo --lang de` and `uv run fazit demo --lang en` passed. Chromium and WebKit opened both CLI reports with no network requests.
- `node site/check_alignment.mjs`, `node site/check_spacing.mjs` and `node tests/browser/check-scrollbars.mjs` passed in Chromium and WebKit.
- The focused licence check covered 312 sample, product and profile combinations and found zero status improvements across 1,560 evidence-loss transitions.

The first verification runs hit the shared `/tmp` quota. The passing runs used isolated scratch directories on the workspace disk. The checkout suite used a scratch directory outside the repository so its absolute-path assertions ran under the expected conditions.

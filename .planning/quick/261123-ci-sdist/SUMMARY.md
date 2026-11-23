# Source distribution test fix

The report tests read SVGs through `importlib.resources` from the same package directory as the renderer. The byte-for-byte comparison with `site/icons/` uses the existing checkout-only rule.

## Verification

Ran the Linux Python 3.12 source distribution step from `.github/workflows/ci.yml` before and after the fix, using CPython 3.12.16 and uv 0.13.9. Each run built a fresh sdist, unpacked it in a temporary directory under `/tmp`, synced the locked dependencies, and ran `uv run pytest -q -rs` from the extracted source.

| Test run | Passed | Failed | Skipped |
| --- | ---: | ---: | ---: |
| Unpacked sdist before | 957 | 17 | 4 |
| Unpacked sdist after | 973 | 0 | 5 |
| Checkout after (`uv run pytest -q`) | 978 | 0 | 0 |

All 16 affected report rendering cases passed in the rebuilt sdist. The fifth skip is `test_coverage_symbols_match_the_site`, which passed in the checkout.

Both Ruff checks, both language demos, and `uv run python site/check_site.py` passed. The generated reports matched the checked-in demos byte for byte and opened in offline Chromium with zero HTTP requests.

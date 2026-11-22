# Release review 5 · `acf9be9`

**Hold release.** Impossible headcounts produce pilots. Future evidence can create a current Blocker. Confirmed code findings total **1 critical, 3 high, 3 medium and 0 low**.

## Code

- **Critical · A4-01 partly fixed.** Both original cases exit 2. Checking 19 of 20 rows found zero internal accounts. With 19 guests, at most 20 accounts exist. Raising the licensed headcount from 20 to 21 against 21 assigned seats restored five pilots. `model.py:146` treats checked rows as possible additional internal accounts. Enumeration accepted all 939 feasible cases and 196 impossible ones. [Counts](tmp/r5/logs/populations.log)
- **High · A4-02/A3-02 partly fixed.** Date-only snapshots now exit 2. Berlin’s two 02:30 snapshots on 25 October were an hour apart. Explicit offsets withheld five pilots. Omitting them restored all five and rejected truthful Teams growth. [Bilingual CLI results](tmp/r5/logs/probes.log)
- **High · OneDrive.** A complete export recorded zero accounts. One measured byte from that same export and period changed OneDrive from Unknown to Ready and added a pilot. [CLI comparison](tmp/r5/logs/probes.log)
- **High · Telephony.** A scan generated on 5 November accepted undated interview evidence covering December and issued a Blocker. Dating the interview 5 November correctly rejected it. [CLI comparison](tmp/r5/logs/period.log)
- **Medium · Truthful inventory rejected.** Microsoft lists two SKU GUIDs under `MCOPSTN5`. Each loaded alone. Together they triggered a duplicate error at `model.py:550`. [Microsoft product table](tmp/microsoft-licence-reference.csv)
- **A4-03 and F4-01 fixed.** A measured Yes after 85 failed phone checks produced one field error. Both decimal backends rejected 4,400 whole digits and 200,000 decimal places bilingually. **R-41/A-14 and R-42/A-15 remain open, medium.** Writes still use replaceable ancestor paths. A second replacement failure mixed the demo files. [Decimal checks](tmp/r5/logs/decimal.log) · [Output checks](tmp/r5/logs/deferrals.log)

## Site and records

A4-05 is fixed in Chromium and Firefox. Two low copy issues remain. Both start cards invite assessments before import (A4-04, not fixed). Home and start pages put import before the redesign (A3-05, partly fixed). A-20 and F-05 are fixed in both publiccode descriptions and STATE’s plan count. [Checkout evidence](tmp/r5/logs/site-records.log) · [Browser results](tmp/r5/logs/browser.log)

Fable’s fourth review is absent from this clone. For F4-02, the cited D31 fix rejects excess seats, rows and subsets. Empty inventories and independent mail exports passed. Fable’s original case and F4-03 remain unverified. Only headers and demo checksums changed under `site/`. [Loader checks](tmp/r5/logs/other-invariants.log)

## Founder actions

R-35 remains open pending domain and PyPI ownership checks. R-36 is partly fixed locally. Verify production headers, Frankfurt storage, European delivery, IP shortening, three-day deletion and the data-processing agreement. R-40’s naming fix landed. Folder visibility and Claude placeholders remain open. Typer, Ready and wordmark motion remain accepted decisions (R-37/38/43).

## Verification

Both Ruff checks, 722 tests each on Python 3.12 and 3.14, and 16 deep tests passed. The wheel built. The unpacked source passed 718 with four checkout-only skips. All 12 demos rebuilt byte-for-byte. Costs matched across 18 variants per language. Both downloads matched and opened offline at 360 px in both browsers and themes. The site check passed 18 pages and 610 references.

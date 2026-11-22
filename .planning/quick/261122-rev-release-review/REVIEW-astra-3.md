# Fazit release review 3 · `d39df08`

**Release after fixes.** Recommending pilots with zero licensed accounts and 20 assigned seats, or omitting a confirmed phone dependency without a replacement, would embarrass the project in public.

Both Ruff checks, `pytest -q` (688 passed), six deep simulation tests, both demos, `site/check_site.py` (18 pages, 618 references) and `uv build` passed. Both downloads matched generated HTML. Chromium/Firefox opened both offline at 360 px with embedded fonts and zero HTTP requests. Twelve variants retained text, decisions and costs. [Comparison](tmp/r3/matrix.log)

## Round-2 findings

- A2-01 **Partly fixed.** One seat for 20 licensed people withheld pilots at matching instants, as did 0/85. See A3-02.
- A2-02 **Partly fixed.** Checking one of 85 preserved Blocker. Marking the collector partial changed the interview-confirmed need to Unknown (A3-03).
- A2-03 **Fixed.** Adding the disputed 0/3 integration count to Small apps kept both out of pilots.
- A2-04 **Fixed.** openDesk and Nextcloud showed desktop No, two applications without web versions and a reconciliation request.
- A2-05 **Fixed.** German CLI named `as_of` and line 29.
- A2-06 **Fixed.** All 13 homepage headings visible unscrolled and in print, both languages.
- A2-07 **Fixed.** Unpacked sdist pytest passed 684 with four documented skips.
- A2-08 **Fixed.** Authorship agrees across homepages, READMEs, PROJECT and CONTRIBUTING.
- F2-01 **Fixed.** Firefox/Chromium measured a 14 px chevron at 360/1280 px across both themes and motion settings.
- F2-02 **Fixed.** Quoted/unquoted invalid dates named their line. Constructor errors omitted it.
- F2-03 **Fixed.** Nested typo reported line 3 bilingually.
- F2-04 **Fixed.** Reviewed nine simplifications. The planned microsecond limit rejected a previously valid seven-digit timestamp.
- F2-05 **Fixed.** Both header files dropped `immutable` and cache assets for one day.
- F2-06 **Partly fixed.** CI adopted one deterministic Ubuntu run per push. Fable proposed randomised nightly runs.
- F2-07 **Fixed.** Archive tests passed. All eight wheel README links were absolute.

## Earlier findings

| Astra | Fable |
|---|---|
| A-01 Fixed. Denial kept four areas Unknown. | F-01 Not fixed. R-35. |
| A-02 Fixed. Cross-workload CLI replay passed. | F-02 Fixed. Font policies agree. |
| A-03 Fixed. Unused phone seats gave Needs work. | F-03 Partly fixed. Local policies passed. R-36. |
| A-04 Fixed. Disputed desktop need stayed Unknown. | F-04 Fixed. READMEs identify sample measurements. |
| A-05 Fixed. CLI rejected `030`. | F-05 Partly fixed. R-30 records updated. STATE still lists zero completions under velocity. CLAUDE has placeholders. |
| A-06 Fixed. Nextcloud demos name the SIP subscription. | F-06 Fixed. Print headings visible. |
| A-07 Fixed. Private basename became “the scan file”. | F-07 Fixed. Checked German transfer heading. |
| A-08 Fixed. Zero storage qualified as “in the items checked”. | F-08 Fixed. Disputed zero withheld pilots. |
| A-09 Fixed. Equivalent timestamps rejected 40 of 31 teams. | F-09 Not fixed. Ready retained, R-38. |
| A-10 Fixed. Complete empty inventory measured zero. | F-10 Fixed. Attribution agrees. |
| A-11 Fixed. `.ppsm` triggered Needs work. | F-11 Fixed. S3 (R-39) matches [table 3](https://papers.mxmap-project.org/secassure2026.pdf#page=11). |
| A-12 Fixed locally. Embedded fonts loaded. | F-12 Fixed. Built wheel passed licence checks. |
| A-13 Fixed. Missing source label gave one sentence. | F-13 Not fixed. Typer retained, R-37. |
| A-14 Not fixed. Repeated path lookups, R-41. | F-14 Fixed. Reviewed module split. |
| A-15 Not fixed. Second replacement failure mixed demo files, R-42. | F-15 Fixed. Clock and demo matrices reduced. |
| A-16 Fixed. LF attributes and Windows CI passed. | F-16 Fixed. Windows/macOS jobs passed. |
| A-17 Fixed. Public copy distinguishes sample measurements. | F-17 Fixed. Generated CSS omits design note. |
| A-18 Fixed. Hover contrast exceeded 9:1 on both light surfaces. | F-18 Fixed. Documented 0600 matched output. |
| A-19 Fixed. Bilingual copy specifies local storage. | F-19 Fixed. CLI diagnostic tests passed. |
| A-20 Partly fixed. Start pages reintroduced the ordering error. | F-20 Fixed. Site checker passed. |
| A-21 Fixed. German demo identifies phone add-on. | F-21 Fixed. Both guides require site checks. |

## New findings

| ID | Severity | Area | File and line | What is wrong | How I checked | Concrete fix |
|---|---|---|---|---|---|---|
| A3-01 | Critical | Licences | `src/fazit/licences.py:293` | Impossible per-SKU assignments qualify for pilots. | Nonprofit, contracts reviewed, same instant. Zero licensed accounts, 20 assigned Business Basic seats, five dependent pilots. | Check each user SKU against complete headcounts. [Microsoft](https://learn.microsoft.com/en-us/graph/api/resources/subscribedsku?view=graph-rest-1.0) |
| A3-02 | High | Licences | `src/fazit/licences.py:298` | Nonzero assignments bypass unverified headcounts. | Contracts reviewed, 20 people/one seat. Denying just the headcount or shifting it one second restored five licence-dependent pilots. | Carry denial or an unreconciled snapshot into inferred absences. |
| A3-03 | High | Telephony | `src/fazit/rules/status.yaml:238`, `src/fazit/report.py:260` | Partial coverage hides established use. | Town CLI, use measured in 1/85, replacement No. Telephony disappeared from blockers. | Accept partial Yes in telephony rules and preserve confirmed use in transfer needs. |
| A3-04 | Medium | Windows setup | `site/start/index.html:57` | Copied commands fail in Windows PowerShell 5.1. | PowerShell 6.2.7 rejected both `&&` separators in each clipboard result. [Microsoft](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_pipeline_chain_operators) | Show three separate commands. |
| A3-05 | Low | Roadmap copy | `site/start/index.html:103`, `README.md:75` | Import is called next and packaging placed in phase 4. | Compared both languages with ROADMAP. | Show import after 1.3 and packaging at 2.1. |

Licence and phone defects also reproduced at `1099e49`. [CLI comparisons](tmp/r3/cases.log) · [Browser measurements](tmp/r3/browser.log)

## Founder decisions

R-35 remains open. Both registries returned 404. [RDAP](tmp/r3/rdap.json) · [PyPI](tmp/r3/pypi.json). Confirm control before the phase 2.1 launch. R-36 needs deployed headers and Bunny verification of Frankfurt storage, European delivery, IP shortening, three-day deletion and DPA. R-43 retains the heading animation. The approved redesign follows this review.

On R-40 I would defer the historical “Befund” banner. Fable would correct it before announcement.

Code/site totals include accepted medium deferrals R-41/R-42. **1 critical, 2 high, 3 medium, 1 low.**

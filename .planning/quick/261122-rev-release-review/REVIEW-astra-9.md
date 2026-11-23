# Round 9 · `25c27a1`

**Hold release.** **0 critical, 1 high, 5 medium (3 deferred), 1 low.**

**High · Directory, partly fixed (Astra).** The departmental export gives Unknown. A confirmed guest gives Needs work. Two assignments of one user SKU require two accounts. A complete census at the same instant declares one. Both reports flag the conflict and mark Directory Ready. English says “there are no guest accounts”. Four licence-dependent areas stay Unknown here and with missing headcount. Withhold Directory Ready for this contradiction. [English report](tmp/r9/cases/contradiction-minimal/en/report-2026-11-05-en.html)

**Medium · F8-01 is fixed for individual counts.** One row succeeded and one failed. Fazit accepts one internal account and one guest from that single success, giving Needs work. It accepted 731 impossible partial scans and all 6,435 truthful rosters. [Roster results](tmp/r9/logs/joint.log)

**Medium · Dates.** Fable’s CET case is fixed. A 6 November interview now gives Small applications Ready at 00:00Z on 5 November, before that date exists anywhere. A scan written at 20:05 UTC−05:00 rejects its 20:00 interview when saved with only the local date. [Before and after](tmp/r9/logs/comparison.log)

**Also fixed.** F8-02, Astra’s two-account census with its total declared once, A4-01/F7-01, filtered lists, F5-01, German singular, duplicate-GUID and empty-export checks, 620 complete/partial products, A4-02/03/05, A3-02, F4-01/02, A-20 and F-05.

**Open.** Unregistered nonstandard licence identifiers still fail (F6-01, low). Mixed dates/periods (F5-02/MODL-05), replaceable parent directories (R-41) and interrupted demo writes (R-42) remain deferred.

**Checks.** All nine checks passed, including Chromium and WebKit. Python 3.12 and 3.14 each passed 1,040 tests. Deep simulation passed 31. The unpacked sdist passed 1,034 tests with six checkout-only skips, confirming `e606ce5` fixed F7-02. Twelve demos reproduced byte-for-byte. Both published reports matched and opened offline.

**Founder actions.** Confirm domain control, reserve the PyPI name, verify hosting, retention and the processing agreement, and settle public folder visibility and placeholders. R-37/38/43 remain accepted.

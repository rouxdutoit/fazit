# Round 8 · `a906333`

**Hold release.** **0 critical, 2 high, 4 medium, 1 low**, including the known CI failure and three deferrals.

**High · Directory misses a guest.** A test tenant has two licensed accounts, one member and one guest. A departmental export checks only the member. The licence inventory counts both. Without a declaration, both languages mark the reviewed directory Ready. English says “there are no guest accounts”. Checking both accounts gives Needs work. Power Platform, Telephony, Identity and access, and Security and compliance stay Unknown. Directory stays Ready with zero declared successes, two failures and two same-instant measured successes. It also stays Ready with two assigned seats on one user SKU against one declared account. Require population-wide evidence for the guest absence. [Roster comparison](tmp/r8/logs/roster.log) · [Filtered report](tmp/r8/cases/department-roster/en/report-2026-11-05-en.html) · [Declared scan](tmp/r8/cases/failed-minimal/scan.json)

**Medium · Truthful census refused.** Declare two accounts once. A complete licensed count with two successes and zero failures exits 2 when its total is omitted at `findings[1].coverage`. Repeating the total or omitting all local counters succeeds. Use the declared total in the completeness check at `model.py:347`. [Scan](tmp/r8/cases/inherit-minimal/scan.json) · [CLI comparisons](tmp/r8/logs/minimal.log)

**Round 7.** A4-01, F7-01 and Astra’s filtered-list rejection are fixed as reported. All 729 filtered and 5,264 earlier truthful scans loaded. Licence absence decisions matched all 2,446 two-SKU cases. All 620 reference products kept their seat counts, including partial rows missing SKU or plan GUIDs. F6-01’s future out-of-pattern names still require registration (low). Date-only interviews and dated periods now agree across UTC offsets. [Enumeration](tmp/r8/logs/oracle.log) · [Reference results](tmp/r8/logs/reference.log)

F5-01 (`MCOPSTN5`), the German singular, duplicate GUIDs, empty exports, future interviews, A4-02/A3-02, A4-03’s per-finding checks, F4-01/02, A4-05, A-20 and F-05 remain fixed. F5-02’s mixed dates and periods (MODL-05), R-41’s replaceable parent directories and R-42’s mixed demo files remain deferred (three medium). Missing headcount keeps four areas Unknown. F7-02 is partly fixed. The icon failures cleared. Only the owner-tracked palette test fails in the unpacked sdist, reading `site/style.css` (high).

**Checks.** All seven checkout checks passed, including alignment at 144 views. Python 3.12 and 3.14 each passed 1,002 tests. The 28 deep checks passed. Twelve demos rebuilt identically. The two published reports matched and opened offline in Chromium and Firefox.

**Founder actions.** Round 7 observed the live domain and headers. Confirm domain control and reserve the PyPI name (R-35), verify hosting, retention and the processing agreement (R-36), and settle public folder visibility and placeholders (R-40). R-37/38/43 remain accepted.

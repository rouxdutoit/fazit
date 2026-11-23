# Round 10 · `b0b213d`

**Hold release.** 0 critical, 1 high, 5 medium (3 deferred), 1 low.

**Directory, partly fixed (high, both reviewers).** A one-account census now gives Unknown for two assignments on one product or an explicitly skipped or partial licence collector. With the collector `ok`, changing only `licences.coverage.kind` to `partial` restores Ready in both languages. Omitting the licensed count also restores Ready. Four licence-dependent areas stay Unknown. [CLI results](tmp/r10/logs/compare.log)

**Census, partly fixed (medium, Astra).** One success yielding a member and a guest is refused if the second row failed. It loads if that row was unattempted. All 6,435 truthful rosters loaded, alongside 157 impossible partial scans (previously 731). In one, the only successful row yielded zero members, zero guests and one licensed account. [Enumeration](tmp/r10/logs/joint.log)

**Dates, partly fixed (medium).** Fable’s CET and future-date cases pass. An interview dated 6 November first passes at 10:00Z on 5 November across offsets. Astra’s 20:00 UTC−05 interview still fails when the 20:05 scan stores only its local date. D31 uses the UTC day’s end. [Comparison](tmp/r10/logs/parents.log)

**Still fixed.** Departmental counts give Unknown and confirmed guests give Needs work. Verified fixes include inherited totals, filtered lists, German singular, duplicate GUIDs, empty exports, 620 complete/partial products, F8-01/02, A4-01/02/03/05, A3-02, F4-01/02, F5-01, F7-01/02, A-20 and F-05.

**Open.** Unregistered nonstandard identifiers still fail (F6-01, low). Mixed dates/periods (MODL-05/F5-02), replaceable parent directories (R-41) and interrupted demo writes (R-42) remain deferred.

**Checks.** All nine passed (Chromium and WebKit). Python 3.12/3.14 each passed 1,064 tests. Unpacked sdist passed 1,058 with six checkout-only skips. 31 deep tests passed. 8,343 malformed scans produced field errors. Twelve demos reproduced byte-for-byte. Both published reports matched and opened offline.

**Founder actions.** Confirm domain control and reserve the PyPI name. Verify hosting, retention and the processing agreement. Decide folder visibility and resolve placeholders. R-37/38/43 remain accepted.

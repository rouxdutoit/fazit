# Release review 7 · `5a3bcd0`

**Hold release — 1 critical, 1 high, 5 medium, 0 low** including deferrals.

**A4-01 partly fixed · critical.** Both reviewers’ 20-row examples accept 20 licensed accounts and reject 21. All 5,264 earlier truthful cases loaded. When Fable’s 19-of-20 census omits only the guest coverage total, raising licensed accounts from 20 to 21 with the same 21 assignments turns four areas from Unknown to Ready. The CLI also accepts 11 internal users plus ten guests in a complete 20-row census. [CLI comparison](tmp/r7/logs/constant-inventory.log) · [Enumeration](tmp/r7/logs/accounts.log)

**New regression · high.** Two complete filtered lists contain ten internal users and ten guests respectively. Eleven are licensed. `model.py:500` treats equal list sizes as one population and rejects the scan. The parent commit accepted it. The loader refused 36 of 729 truthful filtered scans. Tie the shared limit to an explicit population. [Comparison](tmp/r7/logs/before.log)

**F6-01 fixed for complete identifiers · medium remains.** All 620 Microsoft products loaded individually and appeared together in both language reports. The CSV corrects two GUIDs misprinted in the web table. Partial inventories still reject 53 products when the SKU GUID is absent and 29 when plan GUIDs are absent. Keep the unclassified products and their seat counts. [Microsoft reference](https://learn.microsoft.com/en-us/entra/identity/users/licensing-service-plan-reference) · [Results](tmp/r7/logs/reference.log)

**Interview dates partly fixed · medium.** Undated periods now use UTC consistently. An interview dated 6 November passes at 00:30 CET and fails at the same scan instant written as 23:30Z on 5 November. [Results](tmp/r7/logs/dates.log)

**Fixed.** Both `MCOPSTN5` products show 25 assigned against 20 purchased (F5-01). One excess seat uses the singular. Partial rows for either product accept one identifier alone. Duplicate GUIDs, future interviews and positive content in empty SharePoint, mail, OneDrive and Teams exports are rejected. A4-02/A3-02 (offsets), A4-03 (failed checks), F4-01 (decimals), F4-02 (security wording), A4-05 (wordmark), A-20 (publiccode) and F-05 (plan count) remain fixed. [Replays](tmp/r7/logs/replay.log)

**Deferred · three medium.** F5-02’s conflicting timestamps, periods and date-only interviews still load (MODL-05). Missing headcount leaves four assessed areas Unknown. R-41’s replaceable ancestor paths and R-42’s mixed demo files remain open.

Both Ruff checks, 978 tests, both demos and the site check passed. Both reports matched the published copies byte-for-byte and opened offline in Chromium and Firefox.

**Founder actions.** R-35 ownership of `fazit.dev` and the PyPI name remains unverified. R-36 still needs production header, hosting, retention and processing-agreement checks. R-40 remains partly fixed (visibility and placeholders). R-37/38/43 remain accepted.

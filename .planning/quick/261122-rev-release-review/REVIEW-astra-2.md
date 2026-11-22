# Fazit release review, round 2

## Verdict

**Release after fixes.** Recommending four pilots with 20 licensed people and one assigned seat would embarrass the project in public, as would dropping a confirmed phone blocker after checking one of 85 accounts.

## Your round-1 findings

Test references below name files under `tests/`. Application paths are relative to `src/fazit/`.

- **A-01 · Fixed.** Replayed the all-zero nonprofit inventory. Denying directory access kept all four areas Unknown. `test_evidence_cli.py:78` and the explicit simulation at `test_simulation.py:218` catch the original defect.
- **A-02 · Partly fixed.** Zero measured integrations against three supplied now gives Unknown, both figures and no pilot. `test_rules.py:792` covers both directions. A dependent workload still selects a pilot in A2-03.
- **A-03 · Fixed.** Twelve assigned but unused phone seats now give Needs work and transfer need No. `test_evidence_cli.py:960` covers used, unused and unanswered. A2-02 concerns partial measurement.
- **A-04 · Fixed.** The disputed software count now gives Unknown for desktop need in both product profiles. `test_evidence_cli.py:1035` and `:1053` cover specific and disputed answers. A2-04 concerns two distinct answers.
- **A-05 · Fixed.** The town CLI rejects `users: 030` at `target_costs.partial_exit.users`. With 30, partial exit costs €527,800. `test_costs.py:409` checks both languages and the total.
- **A-06 · Fixed.** Both Nextcloud demos and site matrices name the Talk Enterprise SIP bridge and gateway. The site checker compares wording to YAML. No independent test requires the subscription fact. [Nextcloud documentation](https://nextcloud-talk.readthedocs.io/en/stable/quick-install/#introduction)
- **A-07 · Partly fixed.** Default demo output concealed an email-named parent. A missing `unavailable@example.invalid.json` still printed the address on stderr. `test_cli.py:150` requires that disclosure. Use a neutral scan or inputs label for identifying filenames.
- **A-08 · Fixed.** A zero mail-storage headline with unknown coverage now says “0.0 B in the items checked”. `test_evidence_cli.py:833` covers three coverage states in both languages.
- **A-09 · Partly fixed.** `test_evidence_cli.py:466` and `:489` reject the original impossible subsets. The CLI accepted 40 of 31 teams at identical instants written `09:00Z` and `10:00+01:00`. Matching spellings failed correctly. Compare instants at `model.py:424`.
- **A-10 · Fixed.** A successful 0/0 inventory with zero licensed users showed measured zero products. `test_evidence_cli.py:294` distinguishes verified empty from incomplete. A2-01 covers inconsistent assignments.
- **A-11 · Fixed.** Counting `hearing.ppsm` now yielded Office files Needs work and removed it from pilots. `test_rules.py:1001` checks the extensions independently. `test_inputs.py:625` checks both interview guides.
- **A-12 · Fixed.** D29 and both security pages describe embedded fonts. Chromium loaded both fonts with the demo policy. `site/check_site.py:391` checks both host configurations. The documentation promise has no direct test. Production verification belongs to R-36.
- **A-13 · Partly fixed.** `test_rules.py:958` and `:984` catch bad workload, finding or unit labels. Deleting just the English source label for `sample.directory` made an ordinary demo print a 63-line traceback at `i18n.py:61`. `test_locales.py:62` catches it only when contributors run tests. Validate sources at catalogue load.
- **A-14 · Not fixed.** Traced the repeated pathname lookups at `output.py:24`, `:33` and `:45`. Existing tests cover destination entries. See R-41.
- **A-15 · Not fixed.** Injected a permission error on the second demo replacement. The new scan survived beside the old answers and HTML. `test_output.py:75` exercises staging failure. See R-42.
- **A-16 · Fixed.** Git’s `core.autocrlf=true` checkout filter preserved the canonical licence hash and both demo hashes. `test_repo_basics.py:60` and the site checker now also run on Windows CI.
- **A-17 · Fixed.** Read both homepages, READMEs and `publiccode.yml`. They distinguish sample measurements from real interviews and identify the two dated profiles. Profile tests cover rendering. Public scope wording has no direct test.
- **A-18 · Fixed.** Chromium’s hovered evidence link measured 5.22:1 on white and 4.79:1 on the light surface. `test_report.py:234` and `:267` cover hover colours and shared site tokens.
- **A-19 · Fixed.** Both READMEs and security pages specify local input and output storage. The wheel’s socket test covers the application. No regression test checks the storage qualification in the copy.
- **A-20 · Fixed.** Compared both READMEs, integrator pages and `publiccode.yml` with the roadmap. All place CSV import after phases 1.1–1.3. No test checks that ordering.
- **A-21 · Fixed.** Fresh German HTML and the homepage now say “Zugewiesene Zusatzlizenz für Telefonie”. Demo byte checks catch drift. No independent assertion checks this wording.

## New findings

| ID | Severity | Area | File and line | What is wrong | How I checked | Concrete fix |
|---|---|---|---|---|---|---|
| A2-01 | Critical | Licence reconciliation | `licences.py:320`, `:322` | Inconsistent complete inventories qualify for pilots. | Nonprofit, same instant, 20 licensed people, one SKU. Raising assignments from zero to one removed the warning and made Power Platform, Telephony, Identity and Security all Ready pilots. Town also suggested Licences with 85 licensed users and three zero-assignment products. Both cases reproduced on the old revision. | For the same scope and date, flag a licensed headcount above the sum of assigned seats. Carry the discrepancy into licence readiness and inferred absences while preserving measured positives. Test both inventories. |
| A2-02 | High | Telephony | `evidence.py:26` | A partial negative reading hides confirmed use without a replacement. | Town interview alone gave Blocker and need Yes. Checking one of 85 accounts found no use there. Both results became Unknown and telephony left the blocker list. The old revision kept Blocker. | For “any use”, preserve a confirmed Yes after a partial negative. Test both directions of partial boolean evidence. |
| A2-03 | High | Editable rules | `status.py:173` | A disputed finding can clear another workload for a pilot. | Added one supported condition, zero integrations, to Small apps. Its row displayed the 0/3 disagreement and still said Ready. The integrations row said Unknown. | Apply disputes by finding ID to every rule that uses it. Test the readiness rows and pilot membership for both workloads. |
| A2-04 | High | Desktop procurement | `report.py:277`, `:286` | A direct answer about required Windows desktops silently disappears from the transfer decision. | In one dated town interview, supplied No alongside two Windows-only apps without web versions. Evidence said No, desktop need said Yes, and neither row flagged the disagreement. | Show both facts together and request reconciliation before giving a definitive answer. Test both product profiles. |
| A2-05 | Medium | CLI diagnostics | `parsing.py:294` | An invalid calendar date directs the operator to the licence header. | Changed `as_of` to `2026-02-30` on line 29 of the example. The German CLI reported line 1. | Use the YAML scalar’s field and source position. Test a multiline file. |
| A2-06 | Medium | Website, R-24 | `site/style.css:818` | The scroll animation again leaves headings blank in full-page screen captures. | Chromium at 360 px, both homepages, hero settled. Twelve of 13 animated headings still had zero opacity before scrolling. Print showed all 13. | Keep original headings visible until their own animation frame. Test an unscrolled capture. |
| A2-07 | Medium | Source distribution | `pyproject.toml:44` | The archive ships tests that require files it omits. | Ran pytest from the unpacked sdist. Three failed and 690 passed. The failures require Git history, `.github/workflows/ci.yml` and `site/style.css`. | Keep checkout-only checks in the repository or package their fixtures. Run the archive’s own suite in CI. |
| A2-08 | Medium | Public attribution, R-23 | `site/index.html:411`, `README.md:95` | The homepage credits Claude and Codex as writers. Both READMEs and the contribution guide assign writing to Codex and checking to Claude. | Compared the English and German homepage text after `f90159a` with `CONTRIBUTING.md:44`. | Align both READMEs and the contribution guide with the founder’s current account. |

**Remaining before announcement.** 1 critical, 5 high, 9 medium, 0 low. This counts the eight table rows plus A-07, A-09, A-13, R-30, R-35, R-36 and R-39. R-41 and R-42 are two additional medium defects accepted for deferral.

**Verification.** At `1099e49` all six repository checks passed, including 693 tests and 516 site references across 16 pages. The deep Hypothesis run passed all six tests in 15m38s. `uv build` produced both archives. Both demo downloads matched the committed HTML and opened offline at 360 px with zero HTTP requests or overflow. All 12 demo hashes matched batch 5. The 1,343 SKU/plan pairs matched the saved Microsoft reference. I inspected the four CI jobs and exercised Linux locally. Windows and macOS runner results were unavailable. R-33’s in-flight test batch and the planned report redesign are outside this review. [CLI cases](tmp/r2/probes.py) · [Seat counts](tmp/r2/seat-count.py) · [Phone coverage](tmp/r2/phone.py) · [Rule variant](tmp/r2/check-data.py) · [Browser checks](tmp/r2/final-site.cjs) · [Archive test results](tmp/r2/archive-tests.log)

**Lean code.** Mostly economical. The licence lookup, mapping loader, shared validators and risky-file catalogue each have a clear job. `status.py:296` and `:361` still pass a dispute through several dictionaries before deciding a status. `cli.py:37` subclasses a command to remove two help-text braces. The simulation mirrors the zero-assignment branch at `test_simulation.py:189` and draws whole registered rosters at `tenants.py:142`. An independent headcount bound would catch A2-01.

## Open items R-35 to R-43

- **R-35 · Disagree with deferral.** The PyPI project and the .dev registry entry for `fazit.dev` both returned 404. Confirm control of both names before announcing them. The responses leave availability unconfirmed. [PyPI](https://pypi.org/pypi/fazit/json) · [.dev registry](https://pubapi.registry.google/rdap/domain/fazit.dev)
- **R-36 · Disagree with deferral.** Before announcement, check live demo response headers and verify Frankfurt storage, European delivery, IP shortening, three-day log deletion and the signed DPA against the Bunny account. The claims appear at `site/privacy/index.html:77`.
- **R-37 · Agree.** Typer is an explicit dependency. Changing CLI frameworks adds little for the first municipal pilot.
- **R-38 · Agree.** Keep Ready for this release. Ask pilots what action they think it authorises before changing the terminology.
- **R-39 · Disagree with deferral.** Table 3 confirms the Microsoft mail counts for DE (793/11,129), AT (1,401/2,092) and CH (1,099/2,110). Cite it and qualify S3’s separate on-premises claim. A domestic mail provider can host a council externally. [Bischof et al., table 3](https://papers.mxmap-project.org/secassure2026.pdf#page=11)
- **R-40 · Agree** to defer folder visibility and the historical HANDOFF banner. R-30 needs correction before announcement because the required reading at `.planning/PROJECT.md:80` still promises `--include-names`, inline JavaScript and system fonts.
- **R-41 · Agree, confirmed.** Redirection requires another writer who controls an ancestor of the chosen output directory. Defer handle-anchored writes for this release.
- **R-42 · Agree, confirmed.** The failure is reported and each demo file stays whole. The ordinary report is a single atomic replacement. Defer recovery of the three-file demo set.
- **R-43 · Agree.** The founder can keep the scramble effect. Fix the visibility defect in A2-06 while keeping the effect.

## Ideas

- **I-1 · Agree · 1.2.** Officers can paste statuses, blockers, questions and all three totals into a council paper. Test the one-page layout with German labels.
- **I-2 · Agree · 1.2.** An inputs-only run with a blank interview starter keeps fictional measurements out of a client’s first report.
- **I-3 · Agree · 2.** Ask each pilot’s IT officer to trace one status and recalculate one cost unaided. Their first imported report will show where the explanation fails.
- **I-4 · Agree · 2.** Generate rosters offline from a dated Microsoft CSV before real imports, including free and education products. Retain human judgement over classification.
- **I-5 · Agree · v2.** Yearly totals support budgeting. Show a break-even month only with explicit cash-flow timing, and let the user supply any yearly price change.
- **I-6 · Agree · 4.** openCode.de improves discovery by public-sector IT. REUSE makes the rights for code, fonts and icons checkable at release.

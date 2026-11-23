---
quick_id: 261122-rev
slug: release-review
date: 2026-11-22
status: complete
---

# Release review: merged findings

Two independent reviews of `82d9d8f`, round 1: Claude Fable 5.2 at max effort (`REVIEW-fable-1.md`, prefix F) and Codex GPT-6.2-Astra at max effort (`REVIEW-astra-1.md`, prefix A). Neither saw the other's work. Claude Opus 5.5 merged them, removed duplicates and added one finding of its own (C). Severity is the higher of the two where both reported an item. Each item names the batch that fixes it, or why it stays open.

## Batch 1: judgement (`261122-rv1-judgement`)

| ID | Sev | Source | Finding |
|---|---|---|---|
| R-01 | critical | A-01 | A skipped or denied directory collector turns four Unknown areas into Ready when every licence assignment is zero. Breaks principle 8. |
| R-02 | critical | A-02, F-08 | A complete measurement silently outranks a disagreeing complete answer in either direction (0 measured against 3 or 271 supplied gives Ready, a pilot suggestion, and a reason that credits the supplied count). |
| R-03 | high | A-03 | Assigned but unused Teams Phone licences give Blocker while the transfer need says No. |
| R-04 | high | A-04 | The desktop OS mapping reads a disputed Windows-only count and prints a definite No; disputes are looked up under the wrong workload. |
| R-05 | high | A-05 | YAML 1.1 reads `users: 030` as octal 24 and silently changes the budget. |
| R-06 | medium | A-10 | A complete, empty licence inventory (0 of 0, collector ok) is discarded and the product count shows Unknown. |
| R-07 | medium | A-09 | Impossible subsets pass: 40 teams with guests out of 31 teams; three licence products beside "1 of 1 scanned". |
| R-08 | medium | A-08 | A zero with unknown coverage appears in the headline cards as an exact organisation-wide zero. |
| R-09 | medium | A-13 | A typo in a rule label gives a 48-line traceback without `--debug`. |

## Batch 2: messages, privacy and CLI (`261122-rv2-messages`)

| ID | Sev | Source | Finding |
|---|---|---|---|
| R-10 | high | A-07 | Printed output contains the absolute path, so a home directory or folder named after a person reaches stdout, against REPT-06. |
| R-11 | medium | C-1, F-19 | Parse-level errors name positions such as `$[0][1]` or end in "at $" and "in fazit". A council IT officer cannot act on them. Name the line (private-safe) or the known field instead. |
| R-12 | low | F-19 | `fazit --debug` alone exits 0 in silence; usage shows `{SCAN_JSON}`; an unreadable scan gets Typer's English box instead of the localised sentence; no `python -m fazit`. |
| R-13 | low | F-18 | Reports are written 0600 regardless of umask, undocumented. |

## Batch 3: report data and wording (`261122-rv3-wording`)

| ID | Sev | Source | Finding |
|---|---|---|---|
| R-14 | high | A-06 | The Nextcloud telephony row and the site matrix omit that the SIP bridge is an Enterprise subscription component. |
| R-15 | medium | F-07 | German "Nicht direkt übertragbar" states a firmer negative than English "Direct transfer unverified"; the README says "cannot be moved"; "kein Hindernis" collides with the Blocker status word. |
| R-16 | low | A-21 | German "Separat zugewiesene Lizenz" describes the assignment, not the add-on. |
| R-17 | medium | A-11 | `.ppsm`, `.ppam`, `.sldm` (and any other macro-enabled Office format) are missing from risky file types and both checklists. |
| R-18 | medium | A-18 | Light-theme link hover falls to 4.43:1, below WCAG AA; the test measures the resting colour only. Applies to the report and, if shared, the site. |
| R-19 | low | F-17 | Every report carries a CSS comment naming apple.com and iOS colours. |

## Batch 4: promises, site, docs and packaging (`261122-rv4-promises`)

| ID | Sev | Source | Finding |
|---|---|---|---|
| R-20 | high | F-02, A-12 | Principle 6, `AGENTS.md` and both security pages promise system fonts; the report embeds two fonts and the test requires them. Fix the words to match the design (embedded fonts, nothing fetched); the founder may instead choose system fonts. |
| R-21 | high | F-03, A-12 | The site CSP `font-src 'self'` blocks the sample report's embedded fonts behind the main button. |
| R-22 | high | F-04, A-17, A-20 | README, site and `publiccode.yml` claim in the present tense assessments from an organisation's own data and an existing scan; measured evidence is sample-only today, and the generic profile has no dated sources. Roadmap copy says CSV import is next. |
| R-23 | medium | F-10 | Three different accounts of who writes the code across README, site and PROJECT. |
| R-24 | medium | F-06 | Site headings stay hidden until a scroll-triggered animation runs: blank headings in print, PDF and headless renderers. |
| R-25 | medium | F-12, A idea | Wheel metadata has no readme, URLs, authors or classifiers; the sdist ships `site/`, `.planning/`, `.claude/`; the licence expression omits the bundled OFL fonts and Apache icons; the `artifacts` line is redundant. |
| R-26 | medium | A-16 | A CRLF checkout on Windows breaks the licence hash and byte-for-byte demo checks. |
| R-27 | medium | A-19 | "Data stays on the computer" assumes local storage; a network share sends it over the network outside Python's socket audit. Say so. |
| R-28 | low | F-20 | The hand-copied site coverage table disagrees with `nextcloud.yaml` on single sign-on and nothing checks it; the sitemap lists 404 pages; `interest-cohort` is obsolete; `geist-mono-cyrillic.woff2` is shipped for a Latin site. |
| R-29 | low | F-21 | `CONTRIBUTING.md` and the "Done means" list omit `site/check_site.py` and how to regenerate `site/demo/`. |
| R-30 | medium | F-05 | `.planning/STATE.md`, `PROJECT.md` and `REQUIREMENTS.md` are stale (0 %, Pending, old name, `--include-names`, inline JS, colours); `.claude/CLAUDE.md` has placeholder sections. |

## Batch 5: structure and lean code (`261122-rv5-lean`)

No behaviour change; both demo reports stay byte-identical.

| ID | Sev | Source | Finding |
|---|---|---|---|
| R-31 | medium | F-14, A simplify | `rules.py` (949 lines) has five jobs; long functions (`_evaluate_workload` 71 lines, `licence_findings` 63, catalogue `_findings` 62); four parallel validation helper sets and patterns defined two or three times; evidence precedence split across modules; licence classification logic built in three places. |
| R-32 | medium | F simplify 2-10, A simplify | `costs.py` Decimal twelfths machinery where `Fraction` suffices; sub-microsecond timestamp comparison; `guid()`; language validated three times; checks that cannot fail; `SECTION_ORDER` used only by tests (both); `i18n` deepcopy; `rules.Mapping` name clash; three idioms for a non-negative integer. |

## Batch 6: tests (`261122-rv6-tests`)

| ID | Sev | Source | Finding |
|---|---|---|---|
| R-33 | medium | F-15, A simplify | Duplicate checks: CSS identical in every report checked 12 times (both), the clock matrix renders 26 reports to prove what the AST test proves, destination checks tested three times, `--debug` twice, `assert "Sie" in text`; tests import private helpers from other test modules. |

## Batch 7: platforms (`261122-rv7-platforms`)

| ID | Sev | Source | Finding |
|---|---|---|---|
| R-34 | medium | F-16 | `publiccode.yml` declares Windows and macOS and `beta`; CI runs Ubuntu only and the README says early development. |

## Open, with reason

| ID | Sev | Source | Why it stays open |
|---|---|---|---|
| R-35 | high | F-01 | `fazit.dev` and the PyPI name are unclaimed. Founder action before any announcement. |
| R-36 | medium | F-03 | The privacy page names bunny.net, which reads neither `_headers` nor `.htaccess`; production headers and the hosting claims (location, deletion, DPA) can only be checked once the site is deployed. Founder. |
| R-37 | medium | F-13 | Replace Typer with argparse (seven of ten installed packages). `AGENTS.md` names Typer; founder decision. |
| R-38 | medium | F-09 | "Ready" can be read as "ready to migrate". Renaming a status is a product decision; founder. |
| R-39 | medium | F-11 | The market figure in S3 is marked as not opened. Verify or remove; founder, since it is a strategy record. |
| R-40 | medium | F-05 | Whether `.planning/` and `.claude/` stay public, and the stale banner in `HANDOFF.md` (not to be edited in this review). Founder. |
| R-41 | medium | A-14 | Output writes look the directory up by name again; another writer controlling an ancestor could redirect them. Needs an attacker with write access to the user's path; handle-anchored writes do not exist on Windows. To be confirmed by both reviewers. |
| R-42 | medium | A-15 | A failure on the second of three demo replacements leaves a mixed set. Demo only; each file is still whole. To be confirmed by both reviewers. |
| R-43 | low | A, F simplify | Remove the heading scramble effect. The founder asked for it; R-24 fixes the defect either way. |

## Outcome after six rounds

Rounds: 1 at `82d9d8f`, 2 at `1099e49`, 3 at `d39df08`, 4 at `0ae2be2`, 5 at `acf9be9`, 6 at `2e4fae1`. Each review is kept as written (`REVIEW-<reviewer>-<round>.md`). Fixes: quick tasks `261122-sim` and `261122-rv1` to `261122-rv11`.

- **Fixed:** R-01 to R-34, all round-2 to round-5 findings, and R-30 and R-39 from the open list.
- **Final verdicts at `2e4fae1`:** Claude Fable 5.2, release as is (0 critical, 0 high, 2 medium, 2 low). Codex GPT-6.2-Astra, hold (1 critical, 0 high, 6 medium including three deferred), over one more case of self-contradicting directory counts (20 rows, 19 failed checks).
- **Agreed by both:** scans edited by hand to avoid a comparison are a phase 2 concern (MODL-05), because today every measured source is a sample source and the report says its measurements are simulated.
- **Queued after the report redesign:** `261122-rv12-after-redesign` (account bound from first principles, two regressions from rv11, SharePoint from zero sites, 61 published licence names refused, a German plural).
- **Still open for the founder:** R-35 (domain and PyPI name), R-36 (production headers and hosting claims), R-37 (Typer), R-38 ("Ready"), R-40 (`.planning/` and `.claude/` visibility, placeholders in `.claude/CLAUDE.md`), R-41 and R-42 (both reviewers agree they can wait), R-43 (wordmark and heading effects).

## Closing note, 2026-11-23

The founder set round 11 as the last review round and decided to ship with its one high open ("ship").

- **Rounds 7 to 11** followed the queued and later batches `261122-rv12` and `261123-rv13` to `261123-rv16`. The main change was to decide from declared populations only (rv13): a scan is refused only when it is impossible from what it declares, and something is inferred only from what it declares consistent. rv16 made Directory Ready depend on a licence check that positively passed.
- **Final verdicts at `9640fe2`:**
  - Claude Fable 5.2: release as is (0 critical, 0 high, 1 medium, 3 low). No improving step among the project's own degradation kinds in about 586,000 evaluations.
  - Codex GPT-6.2-Astra: hold (0 critical, 1 high, 5 medium of which 3 deferred, 2 low). The high: losing evidence can still turn Unknown into Ready outside Directory.
- **Checks at `9640fe2`:** Ruff, 1,079 tests, the unpacked sdist (1,073 passed, 6 checkout-only skips), the deep simulation (31 properties), both demos and the site check pass, and CI is green on all four jobs.
- **Open findings** are planned as to-dos in `.planning/todos/pending/` (twelve files, dated 2026-11-23). The high one, `2026-11-23-evidence-loss-never-improves-status.md`, is due before the first public release on PyPI. Its rule: a supplied value never overrides a recorded denial, skip or failure, and removing evidence never improves a status, gated by a monotonicity search.
- **Accepted by the founder, not planned:** R-37 (Typer), R-38 ("Ready"), R-43 (heading and wordmark effects).

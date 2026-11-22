# Plan set alignment with UI-SPEC revision 4

Shared brief for the agents that align RR-01 to RR-05 with `UI-SPEC.md` revision 4 and write RR-06 and RR-07. One owner per change; a plan that does not own a change must not implement it, only rely on it. Sources: `UI-SPEC.md` (revision 4), `.planning/research/report-usefulness/SYNTHESIS.md` (sections A and C, 13 founder decisions), `.planning/research/launch-critique/SYNTHESIS.md` (C1 to C9, A3).

## Rules for every plan

- **Base: current `main`** (172f278 or later). Since the plans were written (base 709bd17), `0ae2be2`, `6e36d71` and `acf9be9` landed: D31 load-time scan checks in `model.py` (counts within coverage and population, Windows devices within devices, and more), licence reconciliation as one rule, value bounds, and special cases removed from `status.py`. Re-check every symbol, file, line reference, test name, baseline count (`[HEAD=… EXPECT=…]`) and grep against it. Never cite a symbol you have not found with grep today.
- **Small:** at most three tasks per plan and one executor run (Codex GPT-6.2-Sol). Keep the existing plan format: frontmatter (`files_modified`, `must_haves`, `estimate`), Goal, context, `<tasks>` with `read_first`, `action`, `verify`/`automated`, `acceptance`, `done`, threat register.
- **`DESIGN.md` is in `read_first` of every task.**
- **German:** every new or changed German string is a draft and goes into the native-review table in that plan's SUMMARY. Never "z. B."-style abbreviations; formal "Sie"; status names exactly Bereit, Handlungsbedarf, Hindernis, Unbekannt.
- **Principles:** no score, verdict, proposed resolution, effort estimate or supplier recommendation; Unknown never improves a status; no person names; no script in the report.
- **Run order (unchanged):** RR-01, RR-06, RR-07, RR-02, RR-03, RR-04, RR-05.

## Who owns what

| Change (spec rev 4 section) | Owner | Notes for the others |
|---|---|---|
| All new and changed copy of spec §8 rev 4 in both locales: `summary.define.*`, `summary.scope_*`, `summary.not_examined` value "All open points", `summary.blockers` "What blocks this move", `costs.total_label`, `costs.stay_basis`, `costs.comparison_unknown`, `costs.stay_assumption`, `costs.break_even`, `costs.break_even_none`, `costs.vat_note`, `costs.profile_note`, productivity-loss labels, `path.even_if_staying`, `path.for_move`, `appendix.not_looked*`, nav order; ban-list test adds verdict, recommendation, Urteil, Empfehlung, empfohlen | RR-01 (Task 3) | Others use the keys, never add copy. Copy for RR-06 and RR-07's own new rules and labels stays in RR-06 and RR-07. |
| `next_step` gains `kind: clarify / decide / replace`, required by the loader, set per sentence from the action it names | RR-01 (Task 2) | RR-06 adds `next_step` and `kind` for every rule it adds or rewords. |
| Licences without status, five categories, D-81 amendment | RR-01 (as today) | — |
| Coverage table of the plan set (end of RR-01) | RR-01 | Update it to rev 4 and to this map, including RR-06 and RR-07 rows. |
| Desktop inference removed: Windows desktop need stays Unknown unless answered (C6); Windows-software rule reworded so no Needs work reason says "blocks"/"Hindernis"; test that no Needs work reason does | RR-06 | — |
| Deeper Ready rules for Teams and SharePoint (C2); `.xls` and legacy macro formats among risky file types (C4); interview fields for SharePoint workflows and VBA (C5 answers); Windows-subtotal check for provided answers if D31 does not already cover it (C3: check `inputs.py` and `model.py` first and drop what is done) | RR-06 | — |
| "Simulated" label and fictional inventory heading in sample runs (A3); `docs/scan-format.md` with one minimal example (C9) | RR-06, or a new RR-08 if RR-06 would exceed three tasks | If split, RR-08 runs directly after RR-06. |
| Target-aware readiness: the evaluator receives the profile; a needed function the profile leaves out changes status as the plan defines, never to Blocker on an undocumented transfer alone (C1) | RR-07 | Spec §9: rule evaluation changes only through RR-06 and RR-07. |
| Mapping review: openDesk XWiki, CryptPad, Notes; specific citations per row; "Direct transfer undocumented" where only the method is undocumented; each mapping file marked unreviewed until the named operator review (C5) | RR-07 | Facts and sources go into the plan text, checked with dates, so the executor needs no network. |
| Scope statement data (spec 1.2 item 3): counts per coverage label for the chosen profile, needed functions outside it, the Unknown-need count; absent for a profile without dated sources | RR-07 (report context and tests) | RR-03 renders it in the summary. |
| Area cards, evidence disclosure, filters (spec 2) | RR-02 | — |
| Readiness bar stays in `readiness`, above the filters, as their visual; `data-segment` read from `readiness` (§9 item 4) | RR-02 | RR-03 no longer moves the bar. |
| Card target line: a needed transfer gap first, before the two-function cap | RR-02 | Uses RR-07's data if present; the gap list exists today. |
| Not-examined index: RR-02 leaves today's markup at the end of `readiness` untouched | RR-02 | RR-04 moves it. |
| `SECTION_ORDER` = header, summary, path, readiness, costs, moves, attention, found, appendix, footer | RR-03 (Task 1) | `path` keeps today's content until RR-04. |
| Summary per spec 1.2 rev 4: count line "Of {n}" from the catalogue; status definitions `dl`; no bar or other part-of-whole picture; scope statement (renders RR-07's data); blockers with conditional "All blockers"; unknowns before the costs with "All open points"; three tiles (`tiles-3`, totals in whole units, difference as main line, Stay basis, Comparison unknown); Stay assumption and break-even lines | RR-03 | Goal and must-haves lose "can we move" and any "verdict" wording. |
| Costs per spec 3 rev 4: scale from known totals; no bar on a row with an unknown total; break-even (3.3: `operations_per_year` of the scenario, exact Decimal, whole units, `break_even_none`, absent when operations unknown; town full move EUR 39,130); intro line, `profile_note`, `vat_note`, productivity-loss label | RR-03 | — |
| An all-Unknown test fixture (every area Unknown) used for summary tests and page-one checks | RR-03 | RR-05 uses it for the PDF check. |
| "What to do next" (spec 4.1): open points moved from `readiness`, grouped by the evidence requested, with areas, owner role and key or fix; `clarify`/`decide` steps under "Worth doing even if you stay"; `replace` steps under "Needed for a move"; status timeline, pilot sentences and stock `ol.steps` removed; §9 item 12 hooks | RR-04 | — |
| Navigation in section order (Summary, Next steps, Areas, Costs, Replacements, Closer look, Appendix) | RR-04 | — |
| Coverage symbol `circle` for `in_suite` in `site/icons/` and `src/fazit/icons/` (Material Symbols Rounded, filled, `viewBox="0 -960 960 960"`, path `M480-80q-83 0-156-31.5T197-197q-54-54-85.5-127T80-480q0-83 31.5-156T197-763q54-54 127-85.5T480-880q83 0 156 31.5T763-763q54 54 85.5 127T880-480q0 83-31.5 156T763-197q-54 54-127 85.5T480-80Z`, same file layout and licence as the existing icons) | RR-04 | RR-05's design check asserts no coverage symbol equals a status symbol. |
| Appendix part "What Fazit does not look at" | RR-04 | — |
| Print: `break-before: page` on `path`, costs, appendix; page one = header + summary; phone order | RR-04 | — |
| Real-PDF check that page one fits A4 for town, non-profit and all-Unknown in both languages; design checks; screenshots; decisions | RR-05 | — |
| Landing screenshot: the home card shows the redesigned report's best first screen, matching it in light and dark, desktop and phone, EN and DE, with updated alt text | RR-05 (keep) | The first screen now has the count line and definitions, no bar. |
| Decisions to record: departures from D-19, D-26, D-64; Licences without status amending D21 and RULE-02; page one for the council, pulling OUTP-03 into the redesign (ROADMAP and REQUIREMENTS note) | RR-05 (Task 3) | — |
| Founder action before RR-02: one council clerk or Kämmerer reads page one | RR-05 lists it as a follow-up | Not a build criterion. |

## Interfaces between plans

- **Scope statement (RR-07 → RR-03).** The report context gains `scope_statement`: `None` when the profile has no dated project sources (for example `generic`); otherwise an object with `profile` (display name), `total` (functions Fazit checks for this profile), `by_coverage` (ordered list of coverage id and count, only ids present, in the profile's coverage order), `needed` (list of function label and the id of its transfer-gap element, need Yes), and `unknown_need` (count of functions outside the profile whose need is Unknown). RR-07 builds and tests the data; RR-03 renders it with RR-01's `summary.scope_*` keys. The counts equal the replacements table.
- **Next-step kind (RR-01 → RR-04).** `StatusRule.next_step` carries `kind`; the report context exposes it per row so RR-04 can split "Worth doing even if you stay" (`clarify`, `decide`) from "Needed for a move" (`replace`).
- **Open points (RR-04).** Grouping key is the evidence requested: the finding id or input key that closes the item, or the collector for a missing export. RR-04 defines the helper; RR-03's summary links to `#not-examined`.
- **Break-even (RR-03).** One helper in the cost code computes the break-even operations amount from the existing model without changing it; tiles and the costs section use the same helper.

## Revision 4.1 (Apple-lens review), owners

| Change | Owner |
|---|---|
| Summary item 1 is one `dl.status-summary`: per status the count and its definition on one row (replaces the separate count line and definitions list); scope statement moves after "What is still unknown", before the tiles; "Confirmed blockers: {shown} of {total}" only when rows are cut off | RR-03 |
| Every card in `.areas`: area name as the anchor at `--fs-headline`, status (symbol and word) at `--fs-body` under it; §6.2 exception 6 widened | RR-02 |
| "Worth doing even if you stay": `clarify`/`decide` steps first, then the open points under the subheading "Evidence still needed" (`readiness.missing`) carrying `id="not-examined"` | RR-04 |
| Copy: German `readiness.evidence_summary` uses "erhoben, bereitgestellt"; `filter.search_hint` shortened; `costs.stay_assumption` "Staying assumes no price change."; `found.title` "What Fazit recorded" | RR-01 |

# Cross-check (Fable on Astra)

Answer to the [cross-check instructions](CROSS-BRIEF.md) with [REVIEW-astra.md](REVIEW-astra.md) as input.

Checked against the repository on 2026-11-22. I rendered both samples in memory for all three profiles and recalculated the town's costs by hand. Not checked: the external legal links and the OpenProject importer claim.

## 1. Agree

- **Statuses are identical across profiles.** Reproduced: all 15 area statuses match under openDesk, Nextcloud and generic, for both samples. `evaluate` receives no mapping (`src/fazit/report.py`, `_evidence_context`). Only the transfer gaps change (8, 6 and 4 rows). I missed this; it limits what "target-aware" can mean on the first screen today.
- **Check-circle conflict.** Confirmed. `status_label` uses `check-circle` for Ready (`src/fazit/templates/report.html.j2`, line 82). `UI-SPEC.md` 6.2 assigns `check-circle` to `in_suite`. `DESIGN.md` "Symbols" forbids reusing a status symbol. I wrongly wrote that coverage symbols "are not status symbols". My scope statement must not use it either.
- **Desktop contradiction.** Confirmed. The sample lists `device_management.windows_desktops_required` under "Not examined" and shows the same gap with `data-need="yes"` (`site/demo/en/index.html`, lines 4066 and 4857). The cause is `need_if_positive` in `_mapping_gaps` (`src/fazit/report.py`, lines 262 to 273). My "needs 5 of 8" count rested on this inference. With it removed the town reads 4 needed, 3 Unknown.
- **Break-even of EUR 39,130.** Confirmed. Full move totals EUR 464,350; the gap to EUR 600,000 is 135,650; divided by five years it is 27,130 on top of 12,000 (`src/fazit/demo/town/inputs.yaml`; `src/fazit/costs.py`, operations × `YEARS`).
- **"All blockers" link can point nowhere.** Spec 1.2 item 3 links to `#status-blocker`; spec 2.1 omits empty groups. The link must be absent with zero blockers.
- **Second wireframe for the unfavourable case.** The non-profit sample has `productivity_loss: null` for the full move (`src/fazit/demo/nonprofit/inputs.yaml`, line 41). Same point as my all-Unknown test; Astra's is more concrete.
- **Three totals, not two differences.** OUTP-03 names "the three scenario totals" (`.planning/REQUIREMENTS.md`). Spec 1.2 item 4 shows differences only. I missed that the spec fails its own later requirement.
- **Known total shown when the comparison is Unknown.** `tests/test_costs.py` has a known partial total of 507,800 with Stay unknown. The spec handles this in the tile; the chart rule should follow.
- **Licences needs an explicit amendment.** RR-01 removes Licences as an assessed area. D21 says fifteen areas (`DECISIONS.md`) and RULE-02 is marked complete. I flagged the stale counts, not the decision. It is a founder decision.
- **Chat history is the third Teams mapping** (`src/fazit/rules/mappings/opendesk.yaml`), so the two-function cap hides the gap. Same as my 2.3 change; agreed from both sides.
- **Shared-mailbox count has no manual route** (`src/fazit/rules/findings.yaml`, `provided: "no"`). An open-points row must say "needs phase 2 import", not name an input key. My "key per row" rule needs this exception.
- **Stock path removed; open evidence in decided areas listed.** Both reviews, and `SYNTHESIS.md` C7.
- **Effort: drivers only. No named Microsoft hosting scenario.** Both reviews.

## 2. Disagree

- **The memo proposes the decision.** Astra's note 1 has the page suggest that members "commission a telephony continuity option". That is Fazit drafting the motion. D20 allows "what must be resolved first", not what to resolve (`DECISIONS.md` D20). Astra says to leave the motion to the organisation and then writes one. Instead: state the blocker, its evidence and the open question. No proposed resolution.
- **Leading with one "affected service".** Spec section 1 rewritten around a single service works only when there is a blocker. One of 31 rules produces one (`src/fazit/rules/status.yaml`, `telephony-no-replacement`). The non-profit sample has none. Most first runs will be mostly Unknown. Instead: lead with the count line and status definitions, then blockers or the zero-blocker sentence, then unknowns.
- **Risk register "Do".** Astra keeps it with likelihood and ownership left to the client. Then it is an open-points list with a different name. The word "risk" promises a rating Fazit cannot give (principle 8). Owner columns invite person names into a Fazit file (principle 5, D19). Instead: open-points list with roles; the client adds names in its own system.
- **Sequencing with acceptance tests ranked third.** Fazit holds no dependency data. Astra's own example concedes the counts do not identify the applications. Acceptance tests written by Fazit are invented project content, and they sit in the paid conversation (F1). Instead: do later, after the operator review (`SYNTHESIS.md` D); export the finding and the question, not the test.
- **Privacy and consultation extracts in 1.2 as "Do".** Separate printable extracts are extra outputs to name, test and translate. The consultation sheet's questions (logging, access, retention) concern the target, about which Fazit knows nothing. Instead: one short hand-over section of facts in the report, phase 2 with DATA-01, plus an explicit "Fazit did not examine" line.
- **Draft tender rows with acceptance tests.** Same objection. A "proposed acceptance test" in a Fazit file will be pasted into a Leistungsbeschreibung. Instead: quantity schedule and function list in generic wording, labelled as not a specification.
- **Totals on page one without the Stay assumption.** Astra puts three totals first and moves the differences away. The totals are worse than the differences if the reader does not know Stay is today's bill times five (`DECISIONS.md`, cost formulas). Instead: totals, each with origin, plus one line stating the Stay assumption.
- **"Must before build" on every row.** Astra marks sections 0 to 11 all must. Several (extracts, reader validation wording, copy-and-paste tests) can follow. The founder needs a short must list.
- **Break-even input left unspecified.** Astra varied operations. RR-01 says only "break-even input beside each move's difference". Choosing which input to vary is a judgement; an unlabelled choice steers the reader. Instead: the spec names one rule (for example the largest recurring input the user supplied) and the tile states which input was varied.
- **Copied extract as an acceptance test.** Copy and paste out of an HTML file loses structure in ways no CSS controls (principle 6: no script). Instead: test the printed first page; treat paste as best effort.

Astra did not object to the readiness bar. I still hold that a filled proportion bar reads as a score (D1). Founder decision.

## 3. Add

- **RR-06 and RR-07 do not exist as files.** `RR-01-PLAN.md` assigns them the desktop inference (C6), target-aware readiness (C1), deeper Ready rules and the mapping review. Only RR-01 to RR-05 are in `.planning/report-redesign/`. The fixes both reviews rely on are unplanned in detail.
- **The spec forbids what RR-07 requires.** Spec 9 keeps status rules unchanged; RR-07 changes the engine so the profile affects status. Until then the summary must not imply the statuses depend on the chosen target.
- **The scope statement depends on the profile and on RR-06.** Rendered counts: 8 gaps (openDesk), 6 (Nextcloud), 4 (generic); the non-profit sample shows zero "needed". The statement needs a wireframe per profile and a zero case.
- **Area count after Licences.** The count line needs a rule: derive "Of n areas" from the assessed catalogue, never a literal.
- **Two reviews, no reader.** Neither review tested page one on a council member or Kämmerer. VALD-01 covers the IT lead only (`.planning/REQUIREMENTS.md`). One reading by a real clerk before RR-02 is cheap.
- **Legal references.** Both reviews cite paragraphs. None may enter report copy without a qualified check; the report should name procedures, not sections.

## 4. Final top five

**Changes to `UI-SPEC.md` before the build**

1. Reconcile spec with plans and decisions: no "verdict" (section 0), Licences and the area count, D21 and RULE-02 amended, generated path, RR-06 and RR-07 written.
2. Make page one a contract: first printed A4 page with status definitions, blockers or the zero-blocker sentence, unknowns, three totals with origin and the Stay assumption, dates, sample note. Two wireframes: the town, and an incomplete case.
3. Fix symbols and scores: a different symbol or text only for coverage; founder decides on the readiness bar; honesty list bans any proportion readable as overall readiness.
4. Open points become one list directly after the summary: includes gaps in decided areas, each with the input key or "needs import", role later.
5. Cards and tiles tell the truth at a glance: needed-but-uncovered function shown before the two-function cap; desktop need stays Unknown unless answered; known total shown when the comparison is Unknown; tile names the break-even input.

**What Fazit should produce**

1. One-page summary as the report's first printed page (OUTP-03 pulled into the redesign). Facts and open questions, no proposed motion.
2. Open-points list with keys and roles, plus the blank interview starter (OUTP-04).
3. Scope statement: what the chosen target covers, covers with limits, and leaves out, with the organisation's need. Counts and names only; after RR-06.
4. "Worth doing even if you stay" group in next steps (S4), driven by a `kind` tag on each next step.
5. Finance aids: break-even on a named input now; per-year table, VAT flag and internal staff time after 2.1.

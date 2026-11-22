# Report usefulness: what both reviewers found

On 2026-11-22, Claude Fable 5.2 and Codex GPT-6.2-Astra (max effort) each answered the same [brief](BRIEF.md) independently: is Fazit's report the most useful document for the people who decide on and carry out a move off Microsoft 365, and what should Fazit produce around it? Each then read the other's answer ([cross-check brief](CROSS-BRIEF.md)). Sources: [REVIEW-fable.md](REVIEW-fable.md), [REVIEW-astra.md](REVIEW-astra.md), [CROSS-fable.md](CROSS-fable.md), [CROSS-astra.md](CROSS-astra.md).

Tags: **both** means both raised it in their reviews; **both after cross-check** means one raised it and the other agreed; a single name means only that reviewer holds it. Items are ranked by value to clients.

## The short answer

The report is not yet the most useful document. It serves the IT lead and finance fairly well and the council badly. Three findings carry most of what follows:

1. **The council reads paper.** It gets a printed attachment to a Beschlussvorlage. The spec designs the first screen at 1280 × 800 and has no rule for the first printed page (both).
2. **The spec still promises a verdict** ("puts the verdict first", UI-SPEC §0; "can we move", §1). D20 forbids one. The honest first question is "what would a move take, what stops it, what is still open, what does it cost" (both).
3. **The report mixes a working file and a record.** The IT lead improves it run by run; the council files a dated copy. Open work is spread over five places, and the stock "how a move proceeds" steps appear even with an open blocker (both).

One report can carry the shared evidence. Page one is for the council. The working sections are for the IT lead and the integrator. Procurement, finance, the data protection officer and the staff representatives get factual extracts or rows from the same findings, never their own narrative and never legal judgements (both).

Facts confirmed in the repository during the review: readiness statuses are identical under all three target profiles (`src/fazit/report.py` passes no profile to the evaluator); UI-SPEC §6.2 reuses Ready's `check-circle` symbol for in-suite coverage; the sample both lists Windows desktop need as Unknown and shows it as needed (inferred in `src/fazit/report.py`, `_mapping_gaps`); RR-06 and RR-07, which RR-01 relies on, are named in the run order but not yet written.

## A. Changes to the redesign spec before the build

All are "must before build" unless marked "can follow".

1. **§0 and §1: findings, not a verdict.** Replace "puts the verdict first" with "puts the findings first", here and in the goals of RR-01 and RR-03. Restate the cold reader's questions as "what would a move take, what stops it, what is still open, what does it cost". *Both.* Disagreement: Astra wants page one to lead with "the affected service and the next decision" (for the town, telephony). Fable answers that only one of 31 rules can produce a Blocker, most first runs will be mostly Unknown, and proposing what the council should commission is drafting the motion. **Take Fable's line:** blockers when present, otherwise the zero-blocker sentence with its incomplete-evidence qualifier, then the open question. Never a proposed resolution.

2. **§7 and §11.2: the first printed A4 page is a contract.** Pull OUTP-03 into the redesign. `break-before: page` on the areas, so header and summary fill page one in both languages for both samples. Page one carries: status definitions, blockers or the zero-blocker sentence, open questions, the three totals with origin and the Stay assumption, evidence and answer dates, and the sample or invented-price note. Test on a real PDF. *Both.* Pasted text: Astra wants a paste test; Fable says HTML paste cannot be controlled without script. **Test print; treat paste as best effort.**

3. **§1.2 item 4 and §3: three totals, not two differences.** OUTP-03 names "the three scenario totals"; the spec shows only differences from staying. Each total shows its origin. One line states that Stay is today's bill times five. A known total stays visible when the comparison is Unknown, and the chart draws no bar comparison for an incomplete total. Tiles round to whole euros; the table keeps cents. *Both after cross-check.* Break-even: the spec must name which input is varied and the tile must say it (Fable). Example: the town's full move breaks even at EUR 39,130 a year in operations, against EUR 12,000 entered (Astra, confirmed by Fable).

4. **§1.2 item 6, §2.4 and §4: one open-points list, straight after the summary.** It replaces the stock "How a move typically proceeds" steps and the scattered "Not examined", "Evidence still needed" and "Unknowns to resolve first". It includes gaps inside decided areas (mail is Needs work while its shared-mailbox count is Unknown). Each row names what closes it: an `inputs.yaml` key, an export, or "needs phase 2 import" where no manual route exists. Each row carries the owner role RR-01 already writes into `next_step`. Group by the evidence requested, so one missing export is one row. *Both.* Fable also moves the summary's unknowns above the cost tiles, because an unknown changes how far to trust them. *Fable.*

5. **§6.2: coverage must not use a status symbol.** `check-circle` is Ready's symbol (`report.html.j2`, `status_label`); the spec assigns it to in-suite coverage, which `DESIGN.md` "Symbols" forbids. Use text or a distinct Material Symbol. *Astra; Fable confirmed.*

6. **§1.2, §2.3 and §4: say what the target covers, and for which needs.** Add a scope statement to the summary: of the functions Fazit checks for this profile, how many the target covers, covers with limits, and leaves out, and which of those left out this organisation needs, by name (Fable). Astra agreed in cross-check, with guards: keep each profile's own categories (Nextcloud has a community component; the generic profile has no product dates); keep documented coverage, local need and evidence of transfer as three separate labels; never a fraction, percentage or bar. On cards, put a needed gap before the two-function cap (town: chat history is the third Teams mapping). *Both after cross-check.* It depends on RR-06 removing the desktop inference: the town then reads 4 needed, 1 not needed, 3 Unknown, not 5 needed.

7. **§1.2 item 1 and §8: definitions and scoped blockers.** Print a one-line definition of each status beside the count line, on screen and on page one. Scope the blocker heading to this move ("Confirmed blockers for this move"), and stop Needs-work reasons saying "blocks" (the Windows-software rule). Show "All blockers" only when a Blocker group exists. *Both* (the link: *Astra*). Ban "verdict", "Urteil", "Empfehlung" in copy (*Fable*).

8. **Reconcile spec and plans before freezing tests.** Derive "Of n areas" from the assessed catalogue, since RR-01 removes Licences as an assessed area. Update categories, wireframe counts and the generated path. RR-03 still tests difference tiles and RR-04 still specifies stock steps. Write RR-06 and RR-07. Spec §9 keeps status rules unchanged, which RR-07 must break to make readiness target-aware; until it lands, nothing may imply that statuses depend on the chosen target. Label the mapping profile and the cost assumptions separately: the town's totals are the same under all three profiles. *Both.*

9. **§10 and §11: design for the unfavourable report.** Add wireframes for a report with no blocker, incomplete evidence and an unknown cost (the non-profit sample lacks the full-move productivity-loss input), and for a first run with almost everything Unknown. Check page one and the 360 px opening for both. *Both.*

10. **§1.2 item 2: the readiness bar.** Fable: a filled, segmented bar reads as progress towards 100 % and weights every area the same, so drop it from the summary. Astra: D1 allows an unweighted distribution, but move it below the opening finding. *Both agree it must not be the first thing seen.* Founder decision C3.

11. **§2.3: classify each next step** (can follow, but cheapest now). Tag each `next_step` as clarify, decide or replace when RR-01 writes the 31 sentences, so the native German pass happens once. Clarify and decide steps feed "Worth doing even if you stay". *Fable;* Astra agreed but insists each step is classified on its actual action, not by rule.

12. **§3: costs print as a unit** (can follow). The cost section's caption carries organisation, dates and price origin. Label productivity loss as an internal estimate, not a payment. State VAT as "not stated" until an input exists. *Fable; Astra agreed on the printable section.*

13. **§11: one real reader before RR-02** (can follow). Give page one, unexplained, to a council clerk or Kämmerer and ask what it supports and what is open. Give the full file to an IT officer at 200 to 2,000 seats to trace one status and recalculate one cost (VALD-01). *Both;* Fable wants it before RR-02, Astra in phase 2 pilots.

14. **Smaller items** (can follow). Filters below or after the first card, not three controls before it (*Fable*). A short "What Fazit did not look at" list: file contents, mail, per-person data, department level, target settings (*Fable*). Legal references name procedures, not paragraphs, unless a qualified person has checked them (*Fable*).

## B. New roadmap items

| Rank | Item | Who it serves | Phase | Source |
|---|---|---|---|---|
| 1 | **One-page council summary** as the report's first printed page (OUTP-03). Facts and open questions; no proposed motion. Renewal and notice dates join in 1.1. | Council, head of administration | Redesign (pulled from 1.2) | Both |
| 2 | **Open-points list and blank interview starter** (OUTP-04). The list in the report; the blank starter so the first client meeting does not carry the fictional town. | IT lead, integrator | List: redesign. Starter: 1.2, or phase 2 if the first real runs need it | Both |
| 3 | **Neutral project and procurement CSV**: findings, open points, quantities with unit, source, date and coverage, functions in generic wording, need (yes, no, unknown), owner role. First line says it is not a specification. Columns OpenProject can map; a version-tested OpenProject file only after a pilot import. Widens OUTP-01. | Integrator, procurement | 1.2 | Both. Astra adds acceptance tests per row; Fable says Fazit-written tests will be pasted into a tender. Leave them out. |
| 4 | **Scope statement** in the summary (A6). | Council, procurement | Redesign, after RR-06 and RR-07 | Fable; Astra agreed |
| 5 | **"Worth doing even if you stay"**: clarify and decide steps grouped in the open-points list, with the contract window from 1.1. Makes "not yet" a useful result (S4). | IT lead, council of an organisation that stays | Redesign (tag), content grows in 2 and 1.1 | Both |
| 6 | **Finance aids.** Break-even on a named input now. A per-year table, a VAT flag and an input for internal staff time later. | Finance | Break-even: redesign. The rest: founder decision C6 | Both on break-even; split on the rest |
| 7 | **Hand-over facts for the data protection officer and staff representatives**: affected functions, training days, people trained, parallel months, guests and sharing, data location (DATA-01), and the questions only the operator can answer (logging, access, retention). No view on whether a DSFA or agreement is required. | DPO, works council or Personalrat | 2 | Both. Fable: one short section in the report. Astra: printable extracts. Start with the section. |
| 8 | **Protect the issued copy.** A rerun with the same scan date and language overwrites the report. Document one `--out` folder per issued revision, and pair it with `fazit verify`. | IT lead, council file | 1.2 | Astra |
| 9 | **Comparison across two runs.** Compare scope, profile, coverage and rule versions first; tell new evidence apart from completed work. | Integrator, programme board | New phase after repeat pilots | Both |
| 10 | **Sequencing by dependency.** Astra ranks it third; Fable says Fazit holds no dependency data. Write it as rule data only after the named operator review. | Integrator | 1.2 or later | Split |

**Do not do** (both): effort ranges derived from the inventory (export effort drivers instead; the estimate is the integrator's paid work); a risk register with named owners and ratings (the open-points list with roles replaces it); a named "sovereign Microsoft cloud" profile (Fazit would have to state another vendor's coverage and prices).

## C. Decisions for the founder

The founder decided all twelve on 2026-11-22, after this synthesis was first written.

| # | Decision | Outcome |
|---|---|---|
| 1 | Hold the build until the spec is amended | **Hold.** Amend UI-SPEC.md first; write RR-06 and RR-07 before RR-02. |
| 2 | Who page one is for | **The council.** Page one has the same content on screen and in print. The working sections are for the IT lead and the integrator. |
| 3 | The readiness bar | **Count line only in the summary.** No bar, pie or other part-of-whole chart there; a share of areas reads as "how ready are we". The bar stays only as the visual for the area filters. |
| 4 | Scope statement on the first screen | **Add it, after RR-06 and RR-07.** Counts with names, never a fraction, percentage or bar. The operator review of the mapping files becomes a gate before the redesign ships. |
| 5 | Licences without a status | **Inventory only.** Amend D21 and RULE-02; derive the area count from the assessed catalogue. |
| 6 | Finance timing | **Staged.** Break-even now, in the redesign; VAT flag and internal staff time after 2.1; per-year cash flows stay in v2 (CONV-06). |
| 7 | Where cost figures came from | **Fixed source categories per cost input** (organisation's accounts, supplier quote, estimate). No free text. Timing not decided; proposed: with the VAT and staff-time inputs after 2.1, not in the redesign. |
| 8 | Blocker rules | **Fix the wording now.** Scope the heading to this move; Needs-work reasons stop saying "blocks". New Blocker rules only with the operator review. |
| 9 | A fourth scenario (D23) | **Keep D5's three.** No sovereign-cloud profile; revisit only if pilots ask to price another option. |
| 10 | Effort | **Effort drivers now.** The report says Fazit gives no effort estimate. Later, an optional input for the integrator's own rates, which Fazit multiplies. |
| 11 | Outputs for specialists | **Facts plus ready questions for the operator** (logging, access, retention). Never DSFA, tender or agreement templates. |
| 13 | The status name "Blocker" (raised after the review: the word felt negative) | **Keep "Blocker" / "Hindernis".** Plain words for a council; the negative feel is answered by scoping ("What blocks this move"), a next step on every card and the "Worth doing even if you stay" group, not by a softer label. |
| 12 | OpenProject | **One plain CSV in 1.2** with column names OpenProject can map, opening in LibreOffice Calc and Excel. A tested OpenProject import only after a pilot import works unaided. |

Still to do outside this folder: amend D21 and RULE-02 (`DECISIONS.md`, `.planning/REQUIREMENTS.md`); add OUTP-03 to the redesign in `.planning/ROADMAP.md`; bring RR-01 to RR-05 in line with the amended spec, and write RR-06 and RR-07.

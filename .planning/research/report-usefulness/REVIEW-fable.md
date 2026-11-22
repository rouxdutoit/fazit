# Is Fazit's report the most useful document for a move off Microsoft 365?

Reviewer: Claude Fable 5.2, 2026-11-22. Read-only review. "Sample" means `site/demo/en/index.html` (Stadtverwaltung Musterstadt, openDesk profile). "Spec" means `.planning/report-redesign/UI-SPEC.md`, revision 3. Legal references name the procedure a reader works in; the exact paragraph differs by Land and country and needs a check by someone qualified before it appears in any Fazit copy.

Three findings carry most of what follows:

- **The sample holds a fact that neither it nor the spec puts first.** Of the 19 mapped functions, 6 are "In the suite", 5 "In the suite with limits" and 8 "Not available" (sample, "What moves where"). Of the 8, the organisation needs 5, does not need 1, and 2 are Unknown (sample, "Direct transfer unverified"). This tells a reader what a move would and would not replace. The area count ("1 Blocker, 9 Needs work") does not.
- **The council never opens an HTML file.** It reads a printed attachment to a paper. The spec designs the first screen at 1280 × 800 (spec 11.2) and has no criterion for the first printed page.
- **The report mixes two documents.** One is a working file the IT lead improves run by run. The other is a dated record that goes into a file. The spec treats it as one.

## 1. The report, persona by persona

### 1. The council or committee

- **Decision or action:** A resolution (Beschluss) on a paper (Beschlussvorlage) that the administration writes. Usually it is not "move" but "commission a detailed study", "run a pilot", or "do not renew for a full term". The paper has fixed parts: facts, options, financial effect, proposed resolution. Fazit can feed the first three. D20 rules out the fourth (`DECISIONS.md` D20).
- **What the sample gives them:** "Readiness by area" gives the status counts. "Five-year cost comparison" gives three totals. "Suggested path" names the one blocker. All of it sits behind an inventory and a licence table with product codes such as `SPE_E3`.
- **What is missing:**
  - The scope statement above: what the target replaces, what it replaces with limits, what stays outside it. Fazit has this today.
  - Whose numbers these are. Every cost is "Provided", and the provider may be the firm that would sell the project. D26 says a report depends on its producers (`DECISIONS.md` D26). The report should state who supplied the answers, as an organisation or role, never a person.
  - The decision date. Phase 1.1 supplies it (DECI-01, `.planning/REQUIREMENTS.md`).
  - What staying costs beyond flat licences. Today "Stay" is five times this year's bill (`DECISIONS.md`, cost formulas). A user-supplied yearly price change is CONV-06, deferred to v2.
  - A plain definition of each status. The launch critique found "Ready" is read as "ready to move" (`SYNTHESIS.md` B7). The plans now add a definition (RR-01, truths); it must be on the printed first page, not only beside a screen legend.
- **Cut or move:** Licence products, evidence tables, collection methods, rule checksums. All belong after the summary. The spec already moves them.
- **Order:** First printed page. See the paragraph at the end of this section.

### 2. The IT lead who runs Fazit

- **Decision or action:** Two jobs. First, get the report complete enough to show anyone: run exports, hold interviews, fill `inputs.yaml`, rebuild. Second, brief the head of administration. VALD-01 expects this person to trace one status and recalculate one cost unaided (`.planning/REQUIREMENTS.md`).
- **What the sample gives them:** "Evidence behind the figures" (source, date, coverage per finding). "Not examined" (five open items). "How the costs are calculated" and "Readiness rules" in the appendix.
- **What is missing:**
  - One list of everything still to supply, with the key to fill. The sample says "enter it in the inputs file" without naming the key in the visible text (sample, "Not examined", third item). The interview checklist already pairs each question with its key and the role to ask (`docs/interview-checklist.md`, for example "Has procurement reviewed…"). The report should print the same pairing for open items only.
  - Open evidence inside decided areas. The critique found "Unknowns to resolve first" omits it (`SYNTHESIS.md` C7); the spec's summary item 6 fixes this.
  - A statement of what Fazit did not look at by design: file contents, mail, per-person data, department level. The sample says it in pieces (macro reason; pilot sentence in "Suggested path"). One short list in the appendix would stop the reader assuming more.
- **Cut or move:** "How a move typically proceeds" is four stock sentences that appear even with an open blocker (`SYNTHESIS.md` C7). The plans replace it with a generated path (RR-01 coverage table, C7).
- **Order:** The screen report is this reader's. The first screen should serve the briefing job; the completion list belongs directly after the summary's unknowns, not in the appendix.

### 3. The integrator's project lead

- **Decision or action:** Write an offer and a project plan: scope, work packages, order, open points, assumptions. Later, show progress.
- **What the sample gives them:** "What moves where" (function to replacement). "Needs attention" (file types, three Windows applications with user counts, eight transfer gaps with the organisation's need). Quantities in "What we found".
- **What is missing:**
  - Findings as rows they can sort and import. Phase 1.2 plans this (OUTP-01).
  - A next step per rule. The spec adds it (2.3); 31 sentences in `status.yaml`.
  - Dependencies between areas. Fazit holds none today. They are general knowledge (identity before mail and files; mail relay before mailbox cut-over), so they can be rule data, with the same review need the critique set for mappings (`SYNTHESIS.md` D).
  - A blank starter without the fictional town's inventory. Planned as OUTP-04.
  - Effort. Fazit has no effort data and no basis for any (no effort field in `src/fazit/rules/`). What it has is effort drivers: counts that scale work. OUTP-01 already uses that word.
- **Cut or move:** Nothing; this reader reads everything. The category filter is for them and for the IT lead, not for the council.
- **Order:** The area cards, replacements and closer-look sections, plus a separate CSV.

### 4. The data protection officer

- **Decision or action:** Three things. A view on whether the new systems need a Datenschutz-Folgenabschätzung (GDPR Art. 35). Updates to the record of processing (Art. 30) and new processor contracts (Art. 28). The exit itself: return and deletion of data at the old processor, and retention duties that Microsoft features fulfil today.
- **What the sample gives them:** Very little. "Security and compliance: Unknown". Twelve guests. No external OneDrive sharing. "Teams chat history must be kept: No". The header's local-processing sentences. Nothing on where data sits today.
- **What is missing:**
  - Data location and EU Data Boundary status. Planned for phase 2 (DATA-01).
  - The list of systems that would process personal data after the move. The mapping already names them for the chosen profile (Nubus, OX App Suite, Nextcloud Files, Element, Jitsi, Collabora, Keycloak, OpenProject; sample, "What moves where"). A deduplicated list is a few lines of code.
  - Which retention and protection features are in use. This is one yes/no answer today (`docs/interview-checklist.md`, "Security and compliance"). It needs two or three more specific answers (retention labels, litigation hold, sensitivity labels). All interview data; no new permission.
  - A statement about the report itself: it holds no person names, addresses or content (`DECISIONS.md` principles 4 and 5). One caveat: it prints application names with user counts ("Kieselbogen Kasse · 9"). In a small office that can point at people. Say so in the checklist.
- **Cut or move:** Nothing needs cutting. Their facts are scattered over four sections.
- **Order:** A short hand-over section after "Next steps" (see 2, idea 6). Fazit must not draft the DSFA or state whether one is required. That is a legal judgement.

### 5. The works council or Personalrat

- **Decision or action:** Co-determination before new technical systems that can monitor behaviour or performance are introduced, and on training. In private bodies BetrVG § 87 (1) 6; in public bodies the Bund or Land Personalvertretungsgesetz. The outcome is usually a Dienstvereinbarung per system or for the whole suite.
- **What the sample gives them:** Training days, people to train and months of parallel running, but only as rows in "Cost inputs". Windows-only applications with user counts.
- **What is missing:**
  - The same list of introduced systems as for the data protection officer. Each is a separate item for co-determination.
  - Training and parallel running stated as facts about staff, not only as cost lines. The inputs exist.
  - What changes at the workplace: whether desktops stay on Windows. The sample has the answer as Unknown ("Windows desktops required…"), which is the right honest state, and it matters most to this reader.
- **Cut or move:** Nothing.
- **Order:** The same hand-over section. Fazit knows nothing about logging or monitoring settings in the target and must say so.

### 6. Procurement

- **Decision or action:** Choose the procedure (in-house award, framework call-off, or tender under UVgO or GWB/VgV depending on value), then write the specification (Leistungsbeschreibung). A specification must describe functions and quantities and must normally be product-neutral. Check the notice period of the running contract.
- **What the sample gives them:** A usable quantity base: 91 mailboxes, 312.4 GB, 24 sites, 481.5 GB, 31 teams, 92 devices, licence counts (sample, "What we found"). "Licence terms reviewed: Yes".
- **What is missing:**
  - The quantities as one schedule, with date, source and coverage, exportable. Fazit has it all.
  - Functions in neutral words. The `generic` profile exists for this (`src/fazit/rules/mappings/generic.yaml`). A report built with the openDesk profile names products in every row, which a tender text cannot copy.
  - Per function, whether the organisation needs it: Yes, No, Unknown. The transfer-gap list has this for the 8 uncovered functions only. For the other 11 it is implicit.
  - Contract end and notice period: phase 1.1.
- **Cut or move:** Nothing.
- **Order:** A separate file (see 2, idea 3). Label it as a quantity schedule and function list, not a specification. Nineteen functions do not make a complete requirements list.

### 7. Finance

- **Decision or action:** Budget entries per year, and a Wirtschaftlichkeitsuntersuchung (BHO § 7 for federal bodies; the Land budget rules and municipal Haushaltsverordnungen ask the same for measures of financial weight). That needs options including "do nothing", costs per budget year, the split between one-off and running costs, and stated assumptions.
- **What the sample gives them:** The best-served reader today. "Cost inputs", "Costs by scenario" with four blocks and subtotals, "Difference from staying", formulas in the appendix. Every amount carries its origin.
- **What is missing:**
  - Years. One five-year total cannot be entered in a budget. CONV-06 (by year, break-even month, yearly price change) is v2. A plain per-year table needs one assumption Fazit does not hold: when project costs fall. Ask for a start month, or state "year 1" as the assumption.
  - Whether amounts include VAT. Most municipal core budgets cannot deduct input tax. One yes/no input, shown in the table caption.
  - Which lines hit the budget and which do not. "Productivity loss" is an internal estimate, not a payment. The three blocks of D22 already separate it; the label should say it.
  - Internal staff time for the project. There is no input for it (`docs/interview-checklist.md`, "Partial exit" lists 13 questions, none on own staff). It is usually the largest hidden cost.
  - Break-even input. The plans add it (RR-01 coverage table, C8).
- **Cut or move:** Two-decimal cents on six-figure sums ("EUR 135,650.00") cost attention in tiles. Keep cents in the table.
- **Order:** The cost section, complete enough to print alone. `break-before: page` on costs is already in the spec (section 7).

### Can one report serve all seven?

No. One report can serve three: the IT lead, the integrator's project lead and, through its first printed page, the decision-maker. Finance is served by the cost section if it prints as a unit. Procurement and project planning need rows, not prose: a separate CSV. The data protection officer and staff representation need one short hand-over section that collects facts already in the report; they do not need their own document from Fazit, and Fazit must not write their assessments.

The first **screen** is for the person who briefs the decision-maker: the IT lead or the integrator. `PROJECT.md` ("Users") says the reader is "an IT lead or a non-technical decision-maker"; in practice the second receives paper. The first **printed page** is for the council. They must be designed as two views of the same summary, and the spec designs only the first.

## 2. What Fazit should produce: ranked ideas

| # | Idea | Value | Honesty risk | Data | Format | Phase | Verdict |
|---|---|---|---|---|---|---|---|
| 1 | **Scope statement** (own): what the target covers, covers with limits, does not cover; of the uncovered, what this organisation needs | High: council, IT lead, procurement | Low. Counts of mapping rows with their documented basis. Risk: mapping quality (`SYNTHESIS.md` C5) | Has it | Summary, first screen | Redesign | **Do.** It answers "what would a move replace" without a verdict. |
| 2 | **One-page decision memo** as the report's first printed page (seed; OUTP-03) | High: council, head of administration | Medium. A "memo" drifts towards a proposal. Keep it to facts, options and unknowns | Has it; decision date in 1.1 | Print layout of the summary, not a second file | Redesign (pull OUTP-03 forward from 1.2) | **Do.** Costs one print rule now, a rebuild later. |
| 3 | **Quantity schedule and function list** (seed "requirements list", narrowed) | High: procurement, integrator | Medium. Must not be called a specification; must use generic wording | Has it; "needed" per function only partly | CSV beside the report | 1.2 | **Do later.** Rows for a tender annex; drop the word "requirements". |
| 4 | **Open-points list with roles** (seed "risk register", replaced) | High: IT lead, integrator | Low if roles only. A register with likelihood and impact would be invented | Has reasons, fixes, keys; roles are in the checklist text, not in data | Section after the summary's unknowns; same rows in the CSV | Redesign for the list; roles in 1.2 | **Do.** It is the working half of the report. |
| 5 | **No-regret actions** (seed) | High: council and IT lead of an organisation that stays; S4 | Low if derived: every next step that only clarifies or inventories is no-regret by construction | Needs a `kind` tag on each `next_step` | A group in "Next steps" | Redesign (the tag), or 1.2 | **Do.** It makes "not yet" a useful result. |
| 6 | **Hand-over facts for data protection and staff representation** (own) | Medium: DPO, Personalrat | Medium. Must list facts and say what Fazit cannot see; no word on whether a DSFA or agreement is required | Has systems list, training, parallel months, guests, sharing; data location in 2 | One short section | 2 (with DATA-01) | **Do later.** Cheap, and it is where two veto holders first meet the project. |
| 7 | **Costs per budget year** (own; CONV-06 in part) | High: finance | Low with a stated timing assumption or a start-month input | Has all but timing and VAT flag | Second table in costs | New phase after 2.1, before 1.1 | **Do later.** The five-year total is not a budget figure. |
| 8 | **Progress across runs** (seed) | Medium: integrator (repeat work), council at second reading | Low. Pure comparison. Risk: a count going up reads as a score | Needs the earlier `scan.json` and `inputs.yaml`; demo already writes both | `fazit report --previous`, a "Changed since" block | After 2.1 | **Do later.** Only real once organisations have two runs. |
| 9 | **Sequencing by dependency** (seed) | Medium: integrator | Medium. General knowledge presented as this organisation's plan | Needs new rule data and an operator's review | Order of the open-points list; a column in the CSV | 1.2 or later | **Do later.** Wait for the named operator review. |
| 10 | **Work packages for OpenProject** (seed) | Low to medium: integrator | Low | Has it once the CSV exists | The 1.2 CSV with columns OpenProject can map | 1.2 | **Do later**, as columns, not a format. Check OpenProject's current import routes first. |
| 11 | **"Stay on a sovereign Microsoft cloud" scenario** (seed; D23) | Medium: finance, council | High as a profile: it needs claims about another vendor's product. Low as a fourth, user-named cost column | Has none; all from inputs | Extra cost scenario | After launch | **Founder decision.** See section 4. |
| 12 | **Effort ranges from the inventory** (seed) | High if true: integrator, finance | High. No data in the repository supports a range; any figure is invented | Does not have it | — | — | **Do not do.** Publish effort drivers; let the integrator price them. |
| 13 | **Risk register with owners** (seed, as written) | Medium | High: owners are persons (principle 5); ratings are invented | Does not have it | — | — | **Do not do.** Idea 4 replaces it. |

### Notes on the top five

**1. Scope statement.** The sample's mapping table has 19 rows; the coverage labels are 6, 5 and 8. The transfer-gap list adds the organisation's need for each of the 8. So the summary can say, with links: "openDesk replaces 6 of 19 functions, 5 with limits. 8 are outside it; this organisation needs 5 of them, 2 are Unknown." Then the 5 by name: device management, the desktop operating system, Windows-only applications, Power Platform, telephony. This is the first fact a council needs: the move is a suite replacement plus five separate projects. It also makes the report target-aware on the first screen, which the critique found missing (`SYNTHESIS.md` C1). Two guards. It is a count of documented functions, so the line must say "of the 19 functions Fazit checks". And the `generic` profile has no project documentation (`DECISIONS.md`, M0 note), so its statement reads differently or is absent. It must never be shown as a fraction bar or percentage.

**2. First printed page.** OUTP-03 already requires a summary that "can be pasted into a council paper". The spec's summary has the right parts but no page budget. Add one acceptance criterion: header plus summary fill exactly the first A4 page, and the areas start on page 2. The page needs four things the screen can leave to links: the status definitions in one line each; evidence date and "inputs as of"; who supplied the answers; and the sample or invented-price note. No second file: a separate memo would need its own checksum, name and tests, and two documents drift.

**3. Quantity schedule and function list.** Rows: area, function in generic words, quantity, unit, provenance, source, date, coverage, needed by the organisation, coverage in the chosen profile, open question. It fits OUTP-01 as written. The honest limit goes in the file's first line and the CLI message: these are the functions Fazit checks, not all the organisation needs. For a tender the user should build with `--profile generic`; the CSV should say which profile produced it.

**4. Open-points list with roles.** Today open work is spread over reasons, "Evidence still needed", "Not examined", missing cost inputs and "Suggested path". One list, one row per open item: what is open, why it matters (the area and what it blocks), who typically answers (role), and the `inputs.yaml` key or export that closes it. The roles exist in prose in `docs/interview-checklist.md`; move them into `findings.yaml` so checklist and report cannot disagree. The spec's "Everything not examined" index (2.4) is most of this already; it lacks the role and the key, and it sits at the end of the areas.

**5. No-regret actions.** Tag each of the 31 `next_step` sentences as `clarify` (find out, count, review), `decide` (the organisation must choose) or `replace` (work that only makes sense if moving). The first two kinds are worth doing whatever the council decides. "Next steps" then has a group: "Worth doing even if you stay". This is S4 in the report (`DECISIONS.md` S4: useful when the answer is "not yet"). It is not a recommendation to move or to stay, and it names no supplier. The tag is rule data, so it gets the same review as the sentences.

## 3. Changes to the redesign spec before it is built

**Does the first screen answer the right question for the right reader?** Partly. The reader is right if it is the IT lead or integrator. The question is half wrong. Spec 1 says a cold reader asks "can we move, what stops us, what does it cost" and that the first screen answers the first two. "Can we move" is the verdict D20 forbids, and the count line plus bar is the nearest thing to an answer the screen offers. The honest first question is "what would a move take, and what is still open". The header title already says this ("What leaving Microsoft 365 would take", spec 8).

| Spec § | Change | Reason | When |
|---|---|---|---|
| 0 | Replace "puts the verdict first" with "puts the findings first". The same phrase is in the Goal of RR-01 and RR-03. | D20: "No overall verdict". A spec that calls its summary a verdict will be built and tested as one. **Wrong, not missing.** | Must |
| 0, 1.2, 2.2, 10, 11 | "Of 15 areas", "All · 15", six categories with `contracts_costs`, and the wireframe counts are stale. RR-01 removes Licences as an assessed area and keeps five categories. | Spec and plans disagree; the spec is the contract (`DESIGN.md` is built to, not reviewed in). | Must |
| 1 | Reword the cold reader's questions: "what would a move take, what stops it, what is still open, what does it cost". | Personas 1 and 2; D20. | Must |
| 1.1 | Add to the meta row: "Answers supplied by" (organisation or role, optional input, shown as "not stated" when empty). | Persona 1; D26. Needs a founder decision on the field (section 4). | Can follow |
| 1.2 item 1 | Print a one-line definition of each status under the count line, at least in print. | `SYNTHESIS.md` B7; RR-01 adds the copy, the spec does not place it. | Must |
| 1.2 item 2 | Reconsider the readiness bar in the summary. A filled, segmented, pill-shaped bar is read as progress towards 100 %, and segment width weights "guest accounts need a decision" the same as "replace device management". Options: drop it; or keep it only in the areas section as the filter's visual. | Persona 1. D1 bans a score; spec 9 bans a percentage; a proportion bar is both in picture form. **Arguably wrong.** Founder decision (section 4). | Must decide |
| 1.2 new item, after the count line | Scope statement (idea 1): three counts with the coverage symbols in `--fg`, then the uncovered functions the organisation needs as `dl.rows`, each linked to its gap. Coverage symbols are not status symbols, so `DESIGN.md` "Symbols" holds. | Personas 1, 2, 6; `SYNTHESIS.md` C1. | Must |
| 1.2 item 3 | The blocker list will usually be empty or one row: only one of 31 rules can produce a Blocker (`src/fazit/rules/status.yaml`, `telephony-no-replacement`; `SYNTHESIS.md` C2). The Windows-software rule says an application "blocks a move away from Windows desktops" yet has status `needs_work`. The spec keeps both sentences (2.3). A summary headed "What blocks the move" that omits an item whose own reason says "blocks" will be read as an error. Either the heading's scope is stated ("Confirmed blockers for the Microsoft 365 move"), or the rule text stops using "blocks". | Persona 1 and 3. **Wrong in combination.** RR-06 may already touch this rule; check. | Must |
| 1.2 item 4 | Tiles: round to whole currency units in the tile; cents stay in the table. Add the break-even line the plans already carry (RR-01 coverage, C8) to the spec text. Under each tile, name the origin as today, and when prices are invented make "invented prices" the tile's detail line, not small print. | Persona 7; `SYNTHESIS.md` C8. A tile is the most quoted number in the report. | Must (spec and plans must agree) |
| 1.2 item 4 | State that "Stay" assumes today's prices for five years, in the tile detail or directly under the tiles. | Persona 7 and 1. The first objection finance raises (`REQUIREMENTS.md`, CONV-06 rationale). | Must |
| 1.2 item 6 | Each unknown row shows the role who answers and the input key, once roles are data. Until then, the key. | Persona 2; idea 4. | Can follow (key: must) |
| 1.2 | Order within the summary: count line and definitions; scope statement; blockers; unknowns; then costs and decision window. Unknowns move above the cost tiles. | An unknown changes how far to trust the tiles. Spec 1 itself says "costs and unknowns follow directly"; unknowns first is the honest order. | Must |
| 2.1 | No change to grouping. Note that with Licences gone, D-81's "Copilot follows Licences" wording needs the amendment RR-01 already records. | Consistency. | Must |
| 2.2 | Keep the filters, but they are for personas 2 and 3 only. Do not let them push the first card below the fold: put the hint line after the cards or in the empty state. | "One thing to look at first per screen" (`DESIGN.md`, Structure). Two pill tracks and a hint are three things before the first card. | Can follow |
| 2.3 | `next_step` gains `kind: clarify | decide | replace` and, later, a role. Add to `StatusRule` now so the 31 sentences are written and reviewed once. | Idea 5; the German native pass (spec 8) should happen once. | Must (the field); display can follow |
| 2.3 | Target line: when the area's functions include one "Not available" that the organisation needs, say so on the card, before the two-function cap cuts it. Order mapped functions worst coverage first. | Persona 3. A Ready-looking target line that hides a gap repeats the critique's C1. | Must |
| 2.4 | The not-examined index becomes the open-points list: add the input key or export per row, and move a link to it into the nav (it is the IT lead's main working list). | Persona 2; idea 4. | Can follow |
| 3 | Add under the chart: the Stay assumption, and whether amounts include VAT ("not stated" until an input exists). Label productivity loss as an internal estimate, not a payment. | Persona 7. | Can follow (labels need locale strings; cheap to add now) |
| 3.2 | The cost section must print as a self-contained unit: its caption carries organisation, dates and price origin, because finance will detach it. | Persona 7. | Can follow |
| 4, "Suggested path" | The spec keeps `ol.steps` (the stock sequence); the plans replace it with a generated path (RR-01 coverage, C7). Update the spec. Add the no-regret group here. | `SYNTHESIS.md` C7; idea 5. **Spec is behind the plans.** | Must |
| 4, "found" | Add to the appendix or "found": one list "What Fazit did not look at" (file contents, mail, per-person data, department level, target-system settings). | Personas 2, 4, 5. | Can follow |
| 5 | Seven nav links in German at 1280 px is tight ("Nächste Schritte"); fine. Add no link for personas; add "Open points" only if 2.4 changes. | — | Can follow |
| 7 | New print rules: `break-before: page` on `readiness`, so header plus summary are page 1; the summary must fit one A4 page in both languages for both samples; status definitions, both dates, the supplier of the answers and the sample note are on that page. | Persona 1; OUTP-03. Spec 7 breaks before `costs` and `appendix` only. | Must |
| 7 | Print the evidence disclosures open only from page 2 on (already so). Consider `--summary-only` print later; not now. | — | — |
| 8 | Add copy: status definitions; scope statement; Stay assumption; "Worth doing even if you stay" / a German equivalent written natively; "Answers supplied by". Ban list gains "verdict" / "Urteil", "Empfehlung". | Above. | Must |
| 9 | Honesty list gains: no proportion that can be read as overall readiness; the scope statement is counts, never a fraction bar. | D1, D20. | Must |
| 10 | Redraw both wireframes with the new summary order and without Licences. | Above. | Must |
| 11.2 | Replace with two criteria. Screen, 1280 × 800: title, count line, scope statement and the first blocker row or the zero-blocker sentence. Print: page 1 as above, checked on a real PDF in both languages. | Personas 1 and 2. | Must |
| 11.3 | "Counts appear once in the summary" stays; add that the scope counts appear once and link to "What replaces what". | — | Must |

One caution on scale. The sample has about 90 seats; the target is 200 to 2,000 (`SYNTHESIS.md` C9 asks for a 600-seat sample). The summary caps (3 blockers, 4 unknowns) were set on a sample with one of each. On a first real run before interviews, most areas will be Unknown or incomplete. Test the first screen and the first printed page on an all-Unknown report (OUTP-04's blank starter) before build is called done. That is the report most IT leads will see first.

## 4. Decisions for the founder

1. **Who the first screen is for.** Options: the decision-maker; the IT lead or integrator who briefs them. Recommendation: the briefer on screen, the decision-maker on the first printed page; write both into the spec.
2. **The readiness bar in the summary.** Options: keep; drop; keep only beside the filters. Recommendation: drop it from the summary. Cost: the first screen loses its only graphic. Gain: nothing on it can be read as a score (D1).
3. **Founder decision: a scope statement on the first screen.** It adds three counts by coverage level. It is not a score or verdict, but it is a new headline number. Options: add; keep coverage only in "What replaces what". Recommendation: add, as counts with names, never as a fraction or bar. Cost: the mapping files become first-screen content, so the operator review (`SYNTHESIS.md` D) moves from "before launch" to "before the redesign ships". Gain: the report says what a move replaces.
4. **Pull OUTP-03 (one-page summary) into the redesign.** Options: now, as print rules; in 1.2 as planned. Recommendation: now; building the summary twice costs more.
5. **Founder decision: name who supplied the answers.** Principle 5 allows the organisation name only. Options: add an optional "answers supplied by" organisation or role; leave provenance as "Provided" alone. Recommendation: add it, validated like the organisation name, with the checklist warning against person names. Cost: one more free-text field to guard in the privacy test. Gain: the council sees whose cost figures it is reading (D26).
6. **Blocker scope.** Options: keep one Blocker rule and scope the heading; promote further rules to Blocker (for example a Windows-only application with no web version when the target profile includes the desktop); drop "blocks" from Needs-work reasons. Recommendation: fix the wording now, and decide promotions with the operator review, not alone.
7. **Founder decision: D23, a further scenario.** Options: (a) keep deferred; (b) a fourth cost column the user names and fills ("other option"), with no mapping and no status; (c) a "sovereign Microsoft cloud" profile. Recommendation: (b) after the launch; never (c). Cost of (b): the comparison widens to four columns at 360 px and in every cost test. Gain: finance can show the option its own rules ask about. (c) would make Fazit state another vendor's coverage and prices, which principle 8 and the supplier-neutral rule cannot carry.
8. **Costs per year and VAT flag before 1.1.** Options: keep CONV-06 in v2; add a plain per-year table and a VAT input after 2.1. Recommendation: after 2.1 and before 1.1; finance is the reader closest to served, and this closes the gap.
9. **Effort.** Options: effort ranges; effort drivers only. Recommendation: drivers only, and say in the report that Fazit states no effort. This also protects F1: the estimate is the paid conversation (`DECISIONS.md` F1).
10. **Scope of 1.2's CSV.** Options: findings only (as planned); findings plus quantity schedule and function list in generic wording. Recommendation: the wider scope, in one file with a `type` column, named so nobody mistakes it for a specification.
11. **Internal staff time as a cost input.** Options: add `internal_project_days` and a day rate per move scenario; leave it inside "productivity loss". Recommendation: add it with the per-year work; it changes the cost model and its tests, so not during the redesign (spec 9 keeps the cost model untouched).
12. **Hold or build.** Options: build the redesign as specified and amend later; amend the spec first. Recommendation: amend first. The "must" rows above change the summary's content and order, the print contract and one field on all 31 next steps; each is cheap in the spec and costly after RR-02 and RR-03.

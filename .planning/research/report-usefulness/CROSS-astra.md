# Cross-check: Codex GPT-6.2-Astra (max effort) on Fable's review, 2026-11-22

Answer to the [cross-check instructions](CROSS-BRIEF.md) with [REVIEW-fable.md](REVIEW-fable.md) as input.

## Agree

- I missed the value of the openDesk coverage count. Of 19 mapped functions, six are in the suite, five have limits and eight carry a gap. That gives readers a reason to inspect particular functions. (`site/demo/en/index.html:4080`)
- Put open evidence in one working list. Mail already has a confirmed sending dependency while its shared-mailbox count remains Unknown. Both facts matter to the IT lead. (`site/demo/en/index.html:2889`)
- Give finance a cost section it can print separately. The evidence date, answer date, price origin and five-year flat-price assumption need to travel with the figures. (`site/demo/en/index.html:294`, `DECISIONS.md`, cost formulas)
- Surface the staff assumptions outside the cost table. The town’s partial-move example assumes 30 people in training and six months of parallel running. Staff representatives can challenge both. (`src/fazit/demo/town/inputs.yaml:24`)
- Export quantities and units as effort drivers. Mailboxes and storage volumes help an integrator price discovery. The inventory supplies no handling rate from which to calculate project days. (`.planning/REQUIREMENTS.md`, OUTP-01)
- Test the opening page with every measurement Unknown, in German and English. That represents the first interview the planned blank starter must support. (`.planning/REQUIREMENTS.md`, OUTP-04)

## Disagree

- **Five separate projects.** The demo’s five Yes answers include a Windows desktop requirement inferred from two applications without web versions. A remote Windows host remains possible. Removing that inference alone gives four Yes, one No and three Unknown. Report the dated limitation and local need separately. Let the client define the projects. (`src/fazit/report.py:238`, `site/demo/en/index.html:4857`)
- **Three coverage labels for every target.** Nextcloud’s single sign-on mapping uses a community component. The generic profile describes types of solution and has no product check dates. Preserve each profile’s actual categories. Ask the buyer which functions are required. (`src/fazit/mappings.py:14`, `src/fazit/rules/mappings/nextcloud.yaml:158`, `src/fazit/rules/mappings/generic.yaml:4`)
- **Paper as the council’s only route.** The project explicitly serves an unaided non-technical reader. Give screen and paper the same opening finding. A page break alone cannot satisfy OUTP-03, which requires each area’s status, open questions, first blockers and all three scenario totals in a pasteable page. (`.planning/PROJECT.md:70`, `.planning/REQUIREMENTS.md:64`)
- **The bar and the symbols.** D1 permits an unweighted distribution of area statuses. Move the bar below the opening finding because it competes for attention. There is a direct design breach elsewhere. Section 6.2 assigns Ready’s check-circle to suite coverage. Use coverage text or a distinct Material Symbol. (`DECISIONS.md`, D1 and D20, `DESIGN.md:36`, `.planning/report-redesign/UI-SPEC.md:205`)
- **A named supplier for all answers.** The sample labels monetary inputs as invented and totals as calculated. Different roles supply different inputs. The organisation-name validator accepts ordinary personal names. Use fixed source categories for material costs and a suggested role for each action. Leave named assignments with the client. (`src/fazit/templates/report.html.j2:121`, `src/fazit/inputs.py:108`, `DECISIONS.md`, principle 5 and D26)
- **Mapped products as systems being introduced.** A component list establishes neither deployment nor processing arrangements. Give data protection and staff representatives the relevant functions, then ask which components will operate, what they will log and who will have access. (`src/fazit/rules/mappings/opendesk.yaml:159`, `.planning/REQUIREMENTS.md`, DATA-01)
- **Automatic stay actions and low-risk progress tracking.** Listing mail senders helps an organisation that renews. Designing a replacement route assumes a move. Classify the actual action. Across runs, distinguish new evidence from completed work and compare scope, profile, coverage and rule versions before describing progress. (`.planning/report-redesign/RR-01-PLAN.md:178`, `DECISIONS.md`, D1, D2 and S4)
- **Annual budgets and a fourth scenario.** A start month and VAT flag leave payment timing unresolved. Keep annual cash flows in CONV-06 and show a five-year break-even input where calculable. D23 defers a fallback for selected workloads while Microsoft 365 stays in use. A sovereign-cloud offer is a different option. Keep D5’s three scenarios. (`.planning/REQUIREMENTS.md:138`, `DECISIONS.md`, D5, D22 and D23)

## Add

- **Identify what the costs price.** I checked the same town inputs against all three profiles. Each gives an invented full-move total of EUR 464,350. The CLI can override the profile independently of the costs. Label the mapping profile and the cost assumptions separately wherever they appear together. (`src/fazit/cli.py:155`, `src/fazit/report.py:218`, `src/fazit/costs.py:154`)
- **Protect the issued copy.** Revised answers for the same scan date and language replace the report in the same output directory. Use a separate `--out` directory for each issued revision and retain its inputs. Phase 1.2 verification detects edits to a report. (`src/fazit/report.py:39`, `src/fazit/output.py:43`, `.planning/REQUIREMENTS.md`, OUTP-02)
- **Count requests a person can close.** The missing recipient export appears as both a missing source and a missing mailbox count. Conversely, the index omits the open workflow and VBA transfer questions. Group by the evidence requested and link every affected finding. (`site/demo/en/index.html:4055`, `site/demo/en/index.html:4785`)
- **Reconcile the build instructions themselves.** RR-01 assigns work to RR-06 and RR-07, whose plan files are absent in this checkout. RR-03 still tests difference tiles and RR-04 still specifies stock steps. Align those tasks and tests with the revised spec. Record the inventory-only Licences decision against D21 and derive the assessed count from the catalogue. (`.planning/report-redesign/RR-01-PLAN.md:285`, `.planning/report-redesign/RR-03-PLAN.md:143`, `.planning/report-redesign/RR-04-PLAN.md:147`, `DECISIONS.md`, D21)

## Final top five

**Changes to `.planning/report-redesign/UI-SPEC.md` before build**

1. **§§0–1.** Lead with the affected service and decision. The town has no telephone replacement. Whether its proposed 30-person move includes telephony remains open. (`src/fazit/demo/town/inputs.yaml:15`)
2. **§§1–2, 4, 6.** Show documented target coverage, local need and evidence of transfer separately. Put a locally needed gap before the two-function card limit. Define Ready beside the area statuses.
3. **§§1–4.** Replace the stock sequence with one evidence list. Give each item a suggested role, an available input or source, and the evidence that would close it. Include gaps inside decided areas.
4. **§§1, 3, 8.** Show all three five-year totals or Unknown, scenario scope and price origin. Preserve a known scenario total when Stay is Unknown. Keep differences and break-even workings beside the assumptions.
5. **§§7, 10–11.** Test the first A4 page and pasted text in both languages. Require area statuses, dates and sample labels to survive. Check the same opening at 360 px with incomplete and wholly Unknown evidence.

**What Fazit should produce**

1. **A one-page council brief** with the affected decision, scoped blockers, open questions and three totals. Add the renewal and notice dates in phase 1.1. (`.planning/REQUIREMENTS.md`, OUTP-03 and DECI-01)
2. **An evidence request list and blank interview starter** that let IT collect missing facts even when the organisation intends to renew. Use the recipient-export route once phase 2 supplies it. (`.planning/REQUIREMENTS.md`, OUTP-04 and IMPT-05)
3. **A supplier-neutral project and procurement CSV** with functions, quantities, units, evidence references, client-confirmed prerequisites and completion checks. It gives the buyer and integrator rows they can reuse. (`.planning/REQUIREMENTS.md`, OUTP-01)
4. **A printable finance comparison** showing which assumption would change the result. In the invented town example, annual full-move operating costs of EUR 39,130 bring the five-year total level with staying, with all other inputs fixed. (`src/fazit/demo/town/inputs.yaml:29`, `src/fazit/costs.py:93`)
5. **A factual handover for data protection and staff representatives** with affected functions, training assumptions, sourced location facts when available, and deployment questions for the operator. (`docs/interview-checklist.md:34`, `.planning/REQUIREMENTS.md`, DATA-01)
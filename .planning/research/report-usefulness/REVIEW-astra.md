# Review: Codex GPT-6.2-Astra (max effort), 2026-11-22

Independent answer to [BRIEF.md](BRIEF.md). Links point into the repository at the time of review.

## 1. The report, persona by persona

**1. Council, committee or management board**

- **Decision or action** — Prepare a *Beschlussvorlage* for the body with authority to act. The immediate decision may be to fund an investigation, retain a service during a partial move, or return with better evidence. Each is a decision a council can take without committing to a migration. [Example of council competence, GO NRW §41](https://recht.nrw.de/lrgv/gesetz/01112025-gemeindeordnung-fuer-das-land-nordrhein-westfalen-go-nrw-bekanntmachung-der/)
- **Current sample** — *What we found* opens with 91 internal accounts and 91 mailboxes. Much later, *Suggested path* supplies the fact worth putting on the agenda. The fictional town says it uses Microsoft telephony and has no replacement. *Five-year cost comparison* prices a partial move for 30 people, but the report cannot say whether those people depend on that phone service. [EN demo, opening][opening] · [EN demo, Telephony][phone] · [Town inputs, partial move][towncost] · [EN demo, pilot scope][pilot]
- **Missing** — Put the affected decision, the evidence behind it and the question to return with on one page. For this town, ask the service lead how calls would continue and whether telephony falls within the proposed partial move. Show the three five-year totals with their origin. Add the notice deadline when phase 1.1 supplies it. Leave the wording of the motion and spending authority to the organisation. [REQUIREMENTS, OUTP-03][memo] · [Phase 1.1, D-90][window]
- **Cut or move** — Move the licence table, storage tiles and instructions for checking offline operation behind the brief. A count of Ready areas deserves less prominence than the service whose withdrawal members are being asked to consider. [EN demo, header and inventory][opening] · [EN demo, Readiness by area][statuses]
- **Order** — First screen and first printed A4 page. A clerk should be able to paste that page into the council paper with its scope, dates and fictional-data warning intact.

**2. IT lead running Fazit**

- **Decision or action** — Establish which findings the IT service can defend, obtain the missing evidence and reproduce the report for a colleague.
- **Current sample** — *Readiness by area* shows Mail as Needs work because other systems send mail through Microsoft. It also marks the evidence incomplete because the shared-mailbox count is unknown. *Appendix — Collection methods* identifies the skipped Exchange recipient export. *Suggested path — Unknowns to resolve first* lists only Security and compliance. An officer following that list could reasonably think the mail question was settled. [EN demo, Mail][mail] · [EN demo, Collection methods][collect] · [EN demo, Suggested path][path]
- **Missing** — Give the officer a single list of outstanding questions, including gaps inside decided areas. For each, name the source, the responsible role, the field it resolves and how to check the next report. Today the officer can investigate shared mailboxes separately. The catalogue has no manual answer field for that count. Phase 2 supplies the recipient-export route. Phase 3 adds live licence and directory counts. [findings.yaml, shared-mailbox count][shared] · [ROADMAP, phase 2][import] · [ROADMAP, phase 3][live]
- **Cut or move** — Show the deciding evidence beside the finding. Put product codes and full service-plan rosters in the inventory reference. Preserve conflicting observations, dates, reporting periods and partial coverage when shortening the visible card. [DECISIONS, evidence precedence][precedence] · [UI-SPEC §2.3][cards]
- **Order** — Outstanding actions immediately after the council page, each linked to the relevant area. Give the officer a direct route from there to the collection record.

**3. Integrator’s project lead**

- **Decision or action** — Agree the scope of discovery or a pilot, identify prerequisites, and give the client a work package with an observable completion condition.
- **Current sample** — *Needs attention* gives the lead three named Windows-only applications, two without a web version. There is a consequential inconsistency. *Not examined* says the need for Windows desktops is unknown, while *Direct transfer unverified* says desktops are needed. The renderer can infer that answer from applications without web versions. A remote Windows host is still a possibility. This distinction could change the scope of a desktop procurement. [EN demo, Windows-only software][software] · [EN demo, Not examined][unexamined] · [EN demo, desktop transfer gap][desktopgap] · [report.py, desktop inference][desktoplogic]
- **Missing** — Each proposed task needs a triggering finding, a suggested role, the decision it precedes and what the client would accept as evidence. Here the task is to establish how the two applications can run and what peripherals they require. Device counts and file types are interview or inventory inputs in v1. The number of affected staff, the department for a pilot and the work involved require local investigation. Phase 1.2 can export the task and its evidence. [Interview checklist, Windows software][interviewapps] · [ROADMAP, v1 source limits][sources] · [REQUIREMENTS, OUTP-01][export]
- **Cut or move** — Remove the stock progression from pilot to switching off the old system. It appears even when a blocker is open and the report expressly lacks department-level evidence. [EN demo, Suggested path][pilot]
- **Order** — A short list of prerequisites in the HTML. The editable work breakdown belongs in the optional project export, where the client can assign people and dates.

**4. Data protection officer**

- **Decision or action** — Advise the controller on the proposed processing and, where it is likely to pose a high risk, on a *Datenschutz-Folgenabschätzung* under GDPR Article 35. The controller owns that assessment. Swiss municipal readers need their applicable cantonal framework. [GDPR, Article 35](https://eur-lex.europa.eu/legal-content/EN/TXT/PDF/?uri=CELEX%3A32016R0679) · [Swiss FDPIC, supervisory responsibilities](https://www.edoeb.admin.ch/en/tasks-data-protection)
- **Current sample** — *Readiness by area — Security and compliance* shows a bundled entitlement and an unanswered question about protection or retention. *Needs attention* records a supplied answer that Teams chat history need not be kept. *Appendix — Collection methods* says this sample run used no Microsoft permissions. These facts concern three different things: a licence, an organisational answer and Fazit’s own operation. [EN demo, Security and compliance][security] · [EN demo, chat-history need][chatgap] · [EN demo, Collection methods][collect]
- **Missing** — Provide a printable evidence extract distinguishing what Fazit retained, what the source exports may contain, and what processing the proposed service would perform. Phase 2 can add the stated tenant data location and EU Data Boundary status, with source. Purpose, recipients, support access, retention, transfers and safeguards for the proposed deployment need answers from the controller and operator. Phase 1.3 can identify which sovereignty criterion a fact informs. The DPO still needs the underlying contracts and processing design. [REQUIREMENTS, DATA-01 and IMPT-02][data] · [ROADMAP, phase 1.3][sovereignty]
- **Cut or move** — Leave move prices and product replacement lists out of the DPO extract. Keep the distinction between a supplied retention answer and a policy the records lead has checked.
- **Order** — An evidence annex reachable from the affected area or action. Bring a privacy question onto the first page only when it bears on the decision before members.

**5. Works council or Personalrat**

- **Decision or action** — Prepare consultation about changes to staff systems, monitoring capabilities and working arrangements. For a German *Betriebsrat*, a *Betriebsvereinbarung* may address matters under BetrVG §87(1) no. 6. A municipal *Personalrat* works under the applicable Land legislation and may negotiate a *Dienstvereinbarung*. The introduction of IT alone does not settle which provision applies. [BetrVG §87](https://www.gesetze-im-internet.de/betrvg/__87.html) · [LPVG NRW, §§1 and 72](https://recht.nrw.de/lrgv/gesetz/14062023-personalvertretungsgesetz-fuer-das-land-nordrhein-westfalen/)
- **Current sample** — *What we found* identifies 92 devices as a fictional interview answer. *Five-year cost comparison — Cost inputs* includes training days and people to be trained. These give representatives a starting point for discussing workload. Neither figure describes who can inspect staff activity in the proposed system. [EN demo, device figure][devices] · [Town inputs, training assumptions][towncost]
- **Missing** — A consultation sheet should ask which functions will change, what events the new service logs, who can inspect them, how long they are retained, and how training time will be protected. In phase 1.1, paid Copilot licences and supplied answers about agents can identify a topic for consultation. They cannot establish how any employee used AI. Phase 1.2 can produce the questions using role labels and leave unanswered questions open. [Phase 1.1 context, D-82 to D-87][ai] · [DECISIONS, D19][privacy]
- **Cut or move** — Omit storage volumes, licence identifiers and the comparative cost of suppliers from the consultation sheet. Retain the training assumptions that representatives can challenge.
- **Order** — A short extract available before the client defines the pilot and its logging settings. Record the agreement in the organisation’s own procedure.

**6. Procurement**

- **Decision or action** — Prepare a sufficiently precise, functional *Leistungsbeschreibung*. German examples are GWB §121 and VgV §31, or UVgO §23 where applicable below threshold. Austria’s BVergG §104 also provides for functional specifications. The purchasing authority determines the applicable procedure and the award criteria. [GWB §121](https://www.gesetze-im-internet.de/gwb/__121.html) · [VgV §31](https://www.gesetze-im-internet.de/vgv_2016/__31.html) · [Official UVgO text](https://www.fib-bund.de/Inhalt/Vergabe/Recht/UVgO_BAnzAT_07.02.2017-B1.pdf) · [Austrian BVergG §104](https://www.ris.bka.gv.at/Dokumente/Bundesnormen/NOR40206805/NOR40206805.pdf)
- **Current sample** — *What moves where* maps functions to named components. *Direct transfer unverified* separates a documented limitation from the client’s need. For example, the openDesk mapping has no documented route for importing historic Teams chats, while the town says it does not require those chats. Making chat import mandatory in a tender based on this report would create a requirement the client has disclaimed. [EN demo, What moves where][moves] · [EN demo, chat-history need][chatgap]
- **Missing** — A supplier-neutral working list with the required outcome, source finding, applicable volume, open question and proposed acceptance test. One candidate from the mail finding is that a representative business application can send an authorised test notification through the proposed service. The buyer must confirm the need, service level and test. Phase 1.2 can draft rows. Phase 1.3 can add applicable criterion identifiers and dates. [EN demo, Mail][mail] · [Generic mapping, functions][generic] · [ROADMAP, phase 1.3][sovereignty]
- **Cut or move** — Keep product names and documentation dates in the technical evidence. Do not copy a replacement name, an undocumented transfer or an Unknown into a mandatory tender clause.
- **Order** — A separate optional worksheet after the buyer has confirmed scope. Link each row back to the evidence used to draft it.

**7. Finance and the Kämmerei**

- **Decision or action** — Prepare the *Haushaltsanmeldung* and the applicable *Wirtschaftlichkeitsuntersuchung*. BHO §7 is the German federal provision. Municipal finance follows the relevant budget rules, for example NRW’s investment comparison where §13 applies. [BHO §7](https://www.gesetze-im-internet.de/bho/__7.html) · [KomHVO NRW §13](https://recht.nrw.de/lrgv/rechtsverordnung/01012026-kommunalhaushaltsverordnung-nordrhein-westfalen-komhvo-nrw/)
- **Current sample** — *Five-year cost comparison* gives EUR 600,000 to stay, EUR 527,800 for a partial move and EUR 464,350 for a full move, all from invented inputs. *Appendix — How the costs are calculated* explains running costs, direct project costs, lost working time and parallel running. Finance can reproduce the comparison. It still needs to know which amounts would draw on which year’s budget. [EN demo, scenario totals][totals] · [DECISIONS, cost formulas][costmodel]
- **Missing** — Show the scope of each scenario, the assumptions that change the comparison, and which figures finance should obtain from a quote or the organisation’s accounts. Distinguish valued staff time from additional expenditure. Annual cash flows, escalation and a payback date require timing and rate assumptions. The current inputs support a five-year sensitivity calculation. The requirements defer the annual model. [Interview checklist, costs][interviewcost] · [REQUIREMENTS, CONV-06][annual]
- **Cut or move** — Replace the two prominent differences from staying with the three totals on the council page. Keep the differences, workings and exact missing inputs in the cost section.
- **Order** — One compact comparison on page one. Finance should be able to reach the assumptions and full table directly from it.

**One report can carry the common evidence.** Write its first screen for the committee chair deciding what to authorise next, and its working sections for the accountable IT lead. The integrator can use the same findings to start the project. Give procurement, finance and the two consultation functions extracts from that record. Seven separately maintained narratives would let the same fact acquire seven different meanings. This serves both the stated primary operator and the reader who must understand the report unaided. [PROJECT, users and success metric][project] · [DECISIONS, S2 and S4][strategy]

## 2. What Fazit should produce: ranked ideas

| Rank and output | Client value | Honesty risk and data needed | Format and phase | Verdict |
|---|---|---|---|---|
| **1. One-page decision memo** | **High** — committee and IT lead | **Low** if the action is scoped. Findings, gaps and costs exist. The client must supply the scope of a proposed move and decide the motion. | Opening HTML section that copies and prints on one A4 page. Design before phase 2, add dates in 1.1, meet OUTP-03 in 1.2. [OUTP-03][memo] | **Do.** It gives the sponsor something to put on the agenda. |
| **2. Evidence requests and a blank interview start** | **High** — IT lead and integrator | **Low.** Gap codes, sources and interview questions exist. A clean start must leave every unsupplied measurement Unknown. | Short HTML action list. Phase 2 supplies real export routes. Phase 1.2 adds the interview-only CLI entry and optional CSV. [OUTP-04][blank] · [Interview checklist][checklist] | **Do.** It makes the first client meeting productive without carrying the fictional town into it. |
| **3. Sequencing by dependency, with acceptance tests** | **High** — integrator | **Medium.** Findings can trigger conditional prerequisites. Actual application connections, criticality, pilot membership and test results need client confirmation. | HTML next steps and CSV rows in 1.2. Record the prerequisite and expected evidence together. [ROADMAP, phase 1.2][outputs] · [EN demo, pilot scope][pilot] | **Do.** A conditional sequence tells the lead which work a discovery task can unlock. |
| **4. Risk and action register with owner roles** | **High** — project lead and sponsor | **Medium.** Rules can identify an observed issue or possible consequence. The client must accept ownership, assess likelihood and decide whether a risk is tolerable. | Optional local CSV in 1.2. Include evidence ID, suggested role, action and closure evidence. [OUTP-01][export] · [DECISIONS, D19][privacy] | **Do.** It gives a finding a route to resolution while keeping personal assignments in the client’s system. |
| **5. Finance assumptions and a break-even input** | **High** — finance and committee | **Low** for one specified variable with all other material inputs known. The formulas exist. Quotes and credible ranges come from the client. | Cost section for phase 2, with a reusable assumptions extract in 1.2. [Cost formulas][costmodel] · [RR-01, launch-critique coverage][rrcoverage] | **Do.** It identifies a price or cost estimate worth checking before members rely on a difference. |
| **6. Actions worth taking if the organisation stays** | **High** — IT lead and management | **Low** when triggered by actual gaps. Contract terms, mail senders and retention answers are useful under either decision. | Short part of next steps for phase 2. Add the contract window in 1.1. [DECISIONS, S4][strategy] · [Interview checklist, workload questions][questions] | **Do.** A decision to renew still leaves concrete work the organisation benefits from doing. |
| **7. Draft tender requirements** | **High** — procurement | **Medium to high.** Generic functions and some local needs exist. Mandatory scope, service levels and award weightings need the buyer. | Optional neutral CSV. Pilot in 1.2, add criterion references in 1.3. [Generic mapping][generic] · [SOVC-01][sovreq] | **Do later.** Test the draft with a buyer before calling any row suitable for a tender. |
| **8. Privacy and staff-consultation extracts** | **High** — DPO and Personalrat | **Medium.** Source facts and supplied answers can travel. Target logging, access, retention and agreements require local evidence. | Printable selections from the report or project export in 1.2, using phase 2 location facts and 1.1 AI answers where available. [DATA-01][data] · [AIAS-01][ai] | **Do.** The two functions can start their own procedures from traceable facts and clearly addressed questions. |
| **9. OpenProject work packages** | **Medium** — integrator using OpenProject | **Medium.** Fazit can generate task subjects and evidence references. Import compatibility depends on the installed version. OpenProject’s CSV importer documentation currently identifies it as a development-branch feature. | Neutral CSV in 1.2. Add an optional, version-tested file after a client import trial. The client controls import. [OUTP-01][export] · [OpenProject importer](https://www.openproject.org/docs/user-guide/work-packages/importing/) | **Do later.** A verified file format would save re-entry. A generic CSV alone does not establish compatibility. |
| **10. Comparison across two runs** | **Medium** — IT lead and programme board | **High** if coverage, scope, period, profile or rules changed. Two local scans, their inputs and rule versions are needed. More evidence can reveal a problem that was always there. | Opt-in offline CLI comparison in a **new phase** after repeat pilots. Compare coded records and inputs behind the reports. [EN demo, Run details][run] · [OUTP-02][verify] | **Do later.** Show changed evidence and comparability first. `fazit verify` answers the separate question of whether one report changed. |
| **11. Effort ranges derived from inventory** | **High** — integrator and finance | **High.** Counts and volumes exist or can be supplied. Handling times, complexity, throughput and rework rates do not follow from them. | Export effort drivers in 1.2. Consider arithmetic on client-supplied pilot rates in a **new phase**. [OUTP-01][export] · [Risky file types, macro rule][riskfiles] | **Do not do** as an inventory-derived estimate. A range without a local basis gives two invented numbers. |
| **12. A “sovereign Microsoft cloud” scenario** | **Medium** — procurement and management | **High.** Contract terms, operating control, deployment, price and the client’s criteria would all need evidence. D23’s fallback for selected services is a different proposition. | Use factual location fields in 2 and criterion references in 1.3. A fourth scenario would need a **new phase**. [DECISIONS, D5 and D23][scen] · [DATA-01][data] | **Do not do** as a named default. A hosting label cannot establish sovereignty or price a contract. |

**1. The memo needs a decision small enough to take.** For the town, members could commission a telephony continuity option and ask IT to return with evidence of which services the 30-person proposal includes. State what would come back and which role would bring it. Include a compact status-by-area index and all three totals elsewhere on the page. That meets the council-paper requirement and lets the chair read the first paragraph aloud without turning it into a mandate to migrate. [Town inputs, scenario scope][towncost] · [EN demo, Telephony][phone] · [OUTP-03][memo]

**2. Make each missing answer obtainable.** A useful mail row would tell the Exchange administrator that the mailbox usage report has no recipient type. Today, the finding stays Unknown in Fazit. With phase 2, a recipient export can establish the count. A different row should ask the records lead whether Microsoft retention is in use and point to the existing confirmation field. One calls for a particular export, the other for an organisational answer. Both need an as-of date. [DECISIONS, D9][d9] · [findings.yaml, security confirmation][retention] · [Interview checklist, dating answers][checklist]

**3. Sequence the test the evidence supports.** The town reports four applications using Microsoft single sign-on and three connected to Microsoft 365. Those figures do not identify the applications or establish whether the sets overlap. A defensible prerequisite is to confirm which applications are in the proposed wave, then demonstrate sign-in for each before changing that wave’s identity service. The project lead records the outcome. Unrelated workloads need no invented predecessor. [Town inputs, application counts][townapps] · [status.yaml, identity and access][identity]

**4. Give a risk an explicit way to close.** Custom SharePoint solutions are in use in the town. Whether an approval workflow must survive is still open. A register entry can describe the possible loss of an approval step, suggest the process owner, and ask for either confirmation that no such workflow is needed or a successful trial of the agreed process. Keep *suggested role* distinct from *accepted owner*. Recording a new risk or obtaining an answer should never count as completing migration work. [EN demo, SharePoint][sp] · [EN demo, workflow transfer gap][workflow]

**5. Give finance a number it can challenge.** In the fictional full-move case, annual operations are entered at EUR 12,000. I recalculated the model with only that input changed. At **EUR 39,130 per year**, the five-year total reaches EUR 600,000, equal to staying. The additional EUR 27,130 per year over five years accounts for the entire EUR 135,650 difference. That gives finance a specific assumption to price. It supplies neither a market rate nor a payback month. If a material input is missing, the comparison stays Unknown. [Town inputs, full-move operations][townfull] · [costs.py, annual operations][costops] · [EN demo, scenario totals][totals]

The delivery order matters. Use the redesign to establish what goes on the page. Phase 2 makes it usable with real exports. Phase 2.1 packages and launches it. The numbered extensions follow launch. The optional files above can all come from the same findings and stay inside the user’s output directory. [ROADMAP, execution order][order] · [AGENTS, output and report rules][agents]

## 3. Changes to the redesign spec before it is built

**The first screen addresses the right reader but asks too broad a question.** Revision 3 asks whether the organisation can move. At 1280 × 800, its acceptance test requires a title, counts, a bar and one blocker. A build can pass while the chair still cannot say what to authorise. Make the first thing the chair sees a scoped consequence and the next decision it informs. The counts can still help the IT lead navigate. [UI-SPEC §1][spec1] · [UI-SPEC §11][spec11] · [DECISIONS, D20][verdict]

| Spec section | Timing | Change and reason |
|---|---|---|
| **§0. Intent** | **Must before build** | Replace the promise of a verdict with a testable purpose. A reader can identify one decision, what is known about it and what evidence would change it. Use one common report for the chair and IT lead. Make the project export a reuse of that evidence. This defines what goes above the fold and honours D20. [UI-SPEC §0][spec0] · [PROJECT, users][project] |
| **§1. Page order and first screen** | **Must before build** | Lead with the affected service, the consequence and the role that can resolve it. Follow with a material open question, the three scenario totals and their origin. Place the per-area index below. Keep the shortlist caps and show how many entries were omitted. With zero blockers, qualify the result when evidence is incomplete. If only Needs work remains, show an actionable finding. Add the supplied notice window in 1.1. Two difference tiles alone do not meet OUTP-03. [UI-SPEC §1.2][summary] · [OUTP-03][memo] · [REVIEW-astra, items 2 and 5][astra] |
| **§2. Areas** | **Must before build** | Keep the cards, keyboard filters and evidence disclosures. Above each disclosure put the deciding fact, the practical next action and any unresolved evidence. Put a locally relevant transfer gap ahead of the first two catalogue mappings. Chat history, for example, is the *third* Teams mapping. Use a visible definition of Ready limited to the checks performed. The current Teams rule already checks guest presence and the retention answer as well as the count. It establishes no transfer test. [UI-SPEC §§2.1–2.3][cards] · [openDesk mapping, Teams][mapteams] · [status.yaml, Teams][teamsrule] · [RR-02, card requirements][rr2] |
| **§3. Costs** | **Must before build** | Put the three totals and their scope ahead of the chart. Show the known total even if the comparison is Unknown, and name the missing input on the side that lacks it. The existing test has a known EUR 507,800 partial move and an unknown Stay total. For incomplete scenarios, show known blocks in text and reserve whole-scenario bar comparisons for known totals. Finance should never have to interpret a short bar to discover that a cost is missing. [UI-SPEC §3][spec3] · [test_costs.py, unknown Stay baseline][costtest] · [RR-03, summary and chart][rr3] |
| **§4. Every current section** | **Must before build** | Move *Suggested path* immediately after the brief and turn it into actions supported by findings. Blocker, Unknown and Ready describe evidence states. They are unsuitable as successive project stages. Include work the client can do while staying. Keep inventory and rule details as references. In *What moves where*, give documented coverage, local need and evidence of transfer distinct labels. This protects the project lead and buyer from the same mistaken inference. [UI-SPEC §4][spec4] · [EN demo, Suggested path][path] · [RR-04, remaining sections][rr4] |
| **§5. Navigation** | **Must before build** | Provide direct links to actions, costs and recorded evidence from the brief. The seven proposed links omit the inventory where the IT lead finds licence evidence. Show *All blockers* only when it has a destination. The spec omits empty status groups while the summary calls for a link to the Blocker group. Preserve the skip link, keyboard focus and fragment access through filters. [UI-SPEC §§1.2, 2.1 and 5][spec5] · [REVIEW-fable, navigation and inventory][fable] |
| **§6. Tokens and components** | **Must before build** | Fix an actual conflict with DESIGN.md. The spec assigns the check-circle to in-suite coverage. The current template uses that same symbol for Ready. Monochrome still leaves the shapes identical in print. Use a distinct rounded Material Symbol from the shared set, or simply the coverage text. Keep controls monochrome and reserve all four status symbols and colours for status. [UI-SPEC §6.2][spec6] · [Report template, status symbols][symbols] · [DESIGN, Symbols][designsym] |
| **§7. Phone and print** | **Must before build** | Make A4 page one independently usable with organisation, scope, origin, decision, material uncertainty and all three totals or Unknown. Start detailed evidence on a later page. Full-document printing should still expand evidence regardless of screen filters. On a 360 px phone, put the scoped finding before navigation controls and secondary figures. Test German wrapping and a copied extract as well as the complete PDF. [UI-SPEC §7][spec7] · [REVIEW-astra, print acceptance][astraprint] · [AGENTS, report requirements][agents] |
| **§8. Copy** | **Must before build** | Name the affected move wherever the current blocker heading implies the whole organisation. Put *simulated* next to a fictional measurement that could be copied and *invented* beside example costs. Preserve independent labels when genuine client answers accompany a sample scan. Keep Ready, Needs work, Blocker and Unknown, and the four binding German labels. Have a native German reviewer check the actions and the council page in context. [UI-SPEC §8][spec8] · [Launch critique, A3 and B7][launch] · [DECISIONS, independent origins][precedence] · [DESIGN, Copy][designcopy] |
| **§9. What must not change** | **Must before build** | Reconcile revision 3 with the working plans before freezing tests. I reproduced identical statuses for all fifteen areas under openDesk, Nextcloud and generic. The evaluator receives no profile. RR-01 already assigns target-aware rules, stronger Ready checks, licence treatment and simulated labels to the amended plan set. Specify which client answer and target evidence may change a status. An undocumented transfer alone cannot establish a Blocker. Preserve offline rendering, privacy, partial coverage and rule precedence in every case. [UI-SPEC §9][spec9] · [report.py, status evaluation][evaluation] · [RR-01, amended scope][rrcoverage] |
| **§10. Wireframes** | **Must before build** | Redraw the town’s first screen and A4 page with the phone-service decision visible. Draw a second version with no confirmed blocker, incomplete evidence and an unknown cost. The non-profit sample already lacks the full-move productivity-loss input. Give that case the same design attention as the favourable fictional price difference. Derive the area count from the assessed catalogue. [UI-SPEC §10][spec10] · [Non-profit inputs, missing cost][nonprofit] · [RR-01, assessed areas][rr1] |
| **§11. Acceptance criteria** | **Must before build** | Add tests for the copied brief retaining its origin, an incomplete Needs work area reaching the action list, missing evidence never improving status, and a scoped blocker leaving unrelated work undecided. Retain the bilingual, offline, keyboard, contrast and full-PDF checks. Distinguish release criteria for a usable document from visual similarity to the site. [UI-SPEC §11][spec11] · [RR-05, checks and handover][rr5] · [DESIGN, Structure][designstructure] |
| **§11. Reader validation** | **Can follow in phase 2 pilots** | Give the chair the first page without an explanation. Ask what decision it supports and what is still open. Give the IT officer the whole file and ask them to trace one status and recalculate one cost unaided. Ask the integrator to turn one finding into a task with a completion test. Use an organisation in the 200–2,000-seat range. The repository already calls for the IT exercise and distinguishes sample testing from real-organisation validation. [REQUIREMENTS, VALD-01][valid] · [Launch critique, founder actions][launchpilot] · [PROJECT, validation status][projectval] |

I read both current HTML files in a local text renderer and matched both to reports generated in memory. I used the saved desktop and phone views for visual context. The read-only environment prevented a fresh graphical browser render, so viewport and A4 fit remain checks for the build. [English demo][opening] · [German demo][deopening]

## 4. Decisions for the founder

- **Founder decision:** Choose the first reader of the HTML: committee chair, technical operator or seven equal audiences. Choose the chair for page one and the IT lead for the evidence. This gives the council a usable paper at the cost of moving inventory off the opening screen. [PROJECT, users][project]
- **Founder decision:** Retain a readiness status for Licences under D21, or ratify RR-01’s inventory-only treatment. Choose inventory only and amend D21 and RULE-02 explicitly. This removes a misleading Ready while preserving licence evidence. It changes the pre-Copilot denominator from 15 to 14 and breaks direct comparison with earlier tallies. [DECISIONS, D21][verdict] · [RULE-02][rulereq] · [RR-01, assessed areas][rr1]
- **Founder decision:** Let specialists receive factual extracts, or maintain jurisdiction-specific tender, assessment and agreement templates. Choose extracts. Public bodies retain control of their legal wording, and the project avoids a recurring legal maintenance burden.
- **Founder decision:** Fund one neutral project export or promise OpenProject compatibility at launch. Choose the neutral export in phase 1.2 and fund a version-specific format when a pilot demonstrates an unaided import. That saves re-entry without making one project system a product dependency. [ROADMAP, phase 1.2][outputs] · [OpenProject importer](https://www.openproject.org/docs/user-guide/work-packages/importing/)
- **Founder decision:** Publish default effort bands or invest in locally calibrated estimates. Publish drivers now. Revisit ranges when pilots can supply units, observed rates and variation. Clients forgo an instant duration and gain an estimate they can defend. [OUTP-01][export] · [DECISIONS, honest figures][principles]
- **Founder decision:** Keep three scenarios, add a second-source fallback, or add a named Microsoft hosting variant. Keep three. Revisit the fallback if pilots repeatedly need to price continuity for a particular service. A fourth option would broaden the comparison and require its own evidenced scope, operating model and costs. [DECISIONS, D5 and D23][scen]

[opening]: ../../../site/demo/en/index.html#L288
[deopening]: ../../../site/demo/de/index.html#L288
[devices]: ../../../site/demo/en/index.html#L378
[statuses]: ../../../site/demo/en/index.html#L2713
[phone]: ../../../site/demo/en/index.html#L3662
[mail]: ../../../site/demo/en/index.html#L2889
[sp]: ../../../site/demo/en/index.html#L3072
[security]: ../../../site/demo/en/index.html#L3845
[unexamined]: ../../../site/demo/en/index.html#L4055
[moves]: ../../../site/demo/en/index.html#L4080
[software]: ../../../site/demo/en/index.html#L4680
[workflow]: ../../../site/demo/en/index.html#L4785
[chatgap]: ../../../site/demo/en/index.html#L4802
[desktopgap]: ../../../site/demo/en/index.html#L4857
[path]: ../../../site/demo/en/index.html#L4937
[pilot]: ../../../site/demo/en/index.html#L4997
[collect]: ../../../site/demo/en/index.html#L5005
[run]: ../../../site/demo/en/index.html#L5916
[totals]: ../../../site/demo/en/index.html#L2683
[towncost]: ../../../src/fazit/demo/town/inputs.yaml#L14
[townfull]: ../../../src/fazit/demo/town/inputs.yaml#L29
[townapps]: ../../../src/fazit/demo/town/inputs.yaml#L53
[nonprofit]: ../../../src/fazit/demo/nonprofit/inputs.yaml#L41
[shared]: ../../../src/fazit/rules/findings.yaml#L89
[retention]: ../../../src/fazit/rules/findings.yaml#L324
[identity]: ../../../src/fazit/rules/status.yaml#L260
[teamsrule]: ../../../src/fazit/rules/status.yaml#L87
[riskfiles]: ../../../src/fazit/rules/risky_file_types.yaml#L3
[mapteams]: ../../../src/fazit/rules/mappings/opendesk.yaml#L51
[generic]: ../../../src/fazit/rules/mappings/generic.yaml#L4
[desktoplogic]: ../../../src/fazit/report.py#L262
[evaluation]: ../../../src/fazit/report.py#L292
[costops]: ../../../src/fazit/costs.py#L93
[costtest]: ../../../tests/test_costs.py#L108
[symbols]: ../../../src/fazit/templates/report.html.j2#L82
[interviewcost]: ../../../docs/interview-checklist.md#L15
[interviewapps]: ../../../docs/interview-checklist.md#L58
[questions]: ../../../docs/interview-checklist.md#L67
[checklist]: ../../../docs/interview-checklist.md#L3
[project]: ../../../.planning/PROJECT.md#L70
[projectval]: ../../../.planning/PROJECT.md#L22
[strategy]: ../../../DECISIONS.md#L48
[principles]: ../../../DECISIONS.md#L5
[precedence]: ../../../DECISIONS.md#L20
[costmodel]: ../../../DECISIONS.md#L30
[d9]: ../../../DECISIONS.md#L63
[privacy]: ../../../DECISIONS.md#L73
[verdict]: ../../../DECISIONS.md#L74
[scen]: ../../../DECISIONS.md#L77
[agents]: ../../../AGENTS.md#L28
[designstructure]: ../../../DESIGN.md#L22
[designsym]: ../../../DESIGN.md#L31
[designcopy]: ../../../DESIGN.md#L51
[rulereq]: ../../../.planning/REQUIREMENTS.md#L28
[sovreq]: ../../../.planning/REQUIREMENTS.md#L61
[export]: ../../../.planning/REQUIREMENTS.md#L62
[verify]: ../../../.planning/REQUIREMENTS.md#L63
[memo]: ../../../.planning/REQUIREMENTS.md#L64
[blank]: ../../../.planning/REQUIREMENTS.md#L65
[data]: ../../../.planning/REQUIREMENTS.md#L66
[valid]: ../../../.planning/REQUIREMENTS.md#L76
[annual]: ../../../.planning/REQUIREMENTS.md#L138
[window]: ../../../.planning/phases/01.1-ai-assistants-and-decision-window/01.1-CONTEXT.md#L17
[ai]: ../../../.planning/phases/01.1-ai-assistants-and-decision-window/01.1-CONTEXT.md#L7
[outputs]: ../../../.planning/ROADMAP.md#L67
[sovereignty]: ../../../.planning/ROADMAP.md#L76
[import]: ../../../.planning/ROADMAP.md#L86
[live]: ../../../.planning/ROADMAP.md#L114
[sources]: ../../../.planning/ROADMAP.md#L144
[order]: ../../../.planning/ROADMAP.md#L154
[launch]: ../../../.planning/research/launch-critique/SYNTHESIS.md#L9
[launchpilot]: ../../../.planning/research/launch-critique/SYNTHESIS.md#L41
[spec0]: ../../../.planning/report-redesign/UI-SPEC.md#L7
[spec1]: ../../../.planning/report-redesign/UI-SPEC.md#L13
[summary]: ../../../.planning/report-redesign/UI-SPEC.md#L25
[cards]: ../../../.planning/report-redesign/UI-SPEC.md#L93
[spec3]: ../../../.planning/report-redesign/UI-SPEC.md#L130
[spec4]: ../../../.planning/report-redesign/UI-SPEC.md#L149
[spec5]: ../../../.planning/report-redesign/UI-SPEC.md#L167
[spec6]: ../../../.planning/report-redesign/UI-SPEC.md#L205
[spec7]: ../../../.planning/report-redesign/UI-SPEC.md#L216
[spec8]: ../../../.planning/report-redesign/UI-SPEC.md#L228
[spec9]: ../../../.planning/report-redesign/UI-SPEC.md#L271
[spec10]: ../../../.planning/report-redesign/UI-SPEC.md#L295
[spec11]: ../../../.planning/report-redesign/UI-SPEC.md#L334
[rr1]: ../../../.planning/report-redesign/RR-01-PLAN.md#L39
[rrcoverage]: ../../../.planning/report-redesign/RR-01-PLAN.md#L302
[rr2]: ../../../.planning/report-redesign/RR-02-PLAN.md#L32
[rr3]: ../../../.planning/report-redesign/RR-03-PLAN.md#L29
[rr4]: ../../../.planning/report-redesign/RR-04-PLAN.md#L139
[rr5]: ../../../.planning/report-redesign/RR-05-PLAN.md#L35
[fable]: ../../../.planning/report-redesign/REVIEW-fable.md#L45
[astra]: ../../../.planning/report-redesign/REVIEW-astra.md#L7
[astraprint]: ../../../.planning/report-redesign/REVIEW-astra.md#L26
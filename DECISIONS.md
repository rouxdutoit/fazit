# Decisions

Running log of design decisions, newest first. `HANDOFF.md` is the original spec; where an entry here conflicts with it, this file wins.

## Principles

1. **Read-only.** Request read permissions and use an explicit allowlist of read endpoints. Exclude requests that can change the tenant, even if they use `GET`.
2. **Local processing.** Assessment data stays on the computer, provided its input and output files are on local storage (a network share sends them over the network). Live collection may contact only `login.microsoftonline.com` and `graph.microsoft.com`. Import usage reports offline. Omit telemetry, analytics, update checks and CDNs.
3. **Tokens in memory.** Keep access and refresh tokens in memory.
4. **Metadata only.** Collect counts, sizes and coded evidence. Leave mail bodies and file contents unopened.
5. **Privacy by construction.** Exclude collected person names and email addresses. The v1 CLI omits `--include-names`. Reports may show the organisation name and Windows-only application names entered in `inputs.yaml`.
6. **Offline report.** Produce one self-contained HTML file with inline CSS and embedded fonts. Omit JavaScript and external resources. The report opens and prints with the network disconnected.
7. **One command.** After setup, one command produces a report. Live collection uses browser sign-in with PKCE by default, with device code as a fallback.
8. **Honest figures.** Use supplied costs and clearly labelled example amounts. Show missing evidence as unknown. A skipped or denied collector never improves readiness.

## 2026-11-23 — Report area filters on phones

**D45. Keep the status filters in one row.**

The founder chose a capsule track with a 2 px inset around same-height segments. When the full labels exceed the available width, the segments share it equally and show the status symbols and counts. The status words remain in the radio labels and in their titles. The category picker gives browser-managed text its normal line height and room for descenders. [Design rules](DESIGN.md#links-and-buttons)

## 2026-11-23 — Section spacing and sample report navigation

**D44. Use a responsive section gap throughout the site and report.**

The founder set 40 px below 768 px, 56 px from 768 px and 64 px from 1080 px. The gap applies on both sides of a section divider and above the footer. The screen rules include the legal pages and both sample reports. Print keeps its compact spacing. This updates D41. [Design rules](DESIGN.md#vertical-rhythm)

The founder also asked for a single, centred download beneath the home preview, more padding in the shared command block and an unbroken outline on future timeline dots. Only the sample report produced by `fazit demo` links from the wordmark to the website in the report's language. Organisation reports link to their own content.

## 2026-11-23 — Linked card chevrons

**D43. Use the plain trailing chevron on linked cards.**

Linked card titles use the same trailing chevron as standalone links and report card titles. It takes the title's text colour and follows the shared gap and baseline rules. The whole card is the link. This updates D30 and D42. [Design rules](DESIGN.md#links-and-buttons)

## 2026-11-23 — Button heights and chevrons

**D42. Use 44 px standard buttons and align chevrons with lowercase text.**

The founder chose the phone menu's 44 px button height for standard buttons on the site and report. The desktop bar pill is 28 px high and has a hit area at least 44 px high. The chevron follows the dimensions measured on Apple's Continuity link and takes its stroke weight from Figtree. Linked card titles keep their neutral circle around the trailing chevron. [Design rules](DESIGN.md#links-and-buttons) · [Apple's Continuity link](https://www.apple.com/macbook-air/)

## 2026-11-23 — Badge contrast and vertical rhythm

**D41. Use tinted status labels in dark mode and share one spacing rhythm.**

The founder specified that in dark mode the symbol and badge label both use Apple's status colour. Light mode keeps the main text colour for badge labels to meet WCAG AA. The founder also asked for uniform spacing across the site and report. The screen gaps use the same named relations in both, verified in Chromium in English and German. [Contrast measurements and spacing values](DESIGN.md#colour)

## 2026-11-23 — Website language links

**D40. Use the Material Symbols Outlined translate icon for the website language links.**

The founder specified Outlined at the standard weight and grade for the footer and phone menu.

## 2026-11-23 — System colours and the report phone menu

**D39. Adopt Apple's June 2025 palette and use the website's phone menu in the report.**

- Increased contrast follows the screen theme. Print uses the default light palette. This updates D38. [System colour values](DESIGN.md#colour)
- At the website's phone menu breakpoint, the report uses the same top-right menu control and full-width panel for its section index. The report uses a native disclosure and marks the section linked by the current fragment. This updates D37.

## 2026-11-23 — Status colours

**D38. Use the status colours at full strength.**

The founder confirmed that D30 uses Apple's system colours directly in both themes. The site and report use the corresponding Increase Contrast colours when requested by the device. Print uses the light Increase Contrast palette for legibility on paper.

## 2026-11-23 — Report navigation and section layout

**D37. Use the sticky top bar and the website's section grid.**

The founder reverted RR-09 item 1. The section links stay in the sticky bar. A compact “On this page” disclosure holds the links when the inline row would overflow on phones. The website's section grid places headings to the left and content to the right from 880 px. At narrower widths each heading sits above its content. This updates the phone behaviour in D33.

## 2026-11-22 — Report polish

**D36. Area cards use badges for status and incomplete evidence.**

The founder chose the area name as the anchor on both the website and the report. A quiet badge gives the status as a symbol and word. A second badge marks incomplete evidence when needed. Both sit at the top right on wide screens and below the area name on phones. The capsules are labels with no interaction. Pill-shaped controls remain pressable. This updates the card hierarchy in D33 and the structure rule in DESIGN.md.

## 2026-11-22 — Report redesign

**D33. The report leads with the findings.**

- The section order is header, summary, path (What to do next), readiness, costs, moves, attention, found, appendix and footer. This changes REPT-02 and the report structure in D-19, D-26 and D-64 of the Phase 1 context. Run details carry the local and offline notes.
- Each assessed area has a card headed by its area name, with its status on the next line. The report sorts a display copy into Blocker, Needs work, Unknown and Ready, in catalogue order within each group. The rule engine keeps its `STATUSES` order. Copilot follows the D-81 amendment in `.planning/phases/01.1-ai-assistants-and-decision-window/01.1-CONTEXT.md`.
- Status counts appear in the summary and on the status filter. The founder removed the readiness bar from the entire report. Radio inputs and CSS filter the area cards on screen. Counts, statuses, the summary and printed pages cover every assessed area.
- Catalogue data supplies the categories. Rule data supplies each action and its kind (`clarify`, `decide` or `replace`). What to do next puts actions and evidence requests worth doing even if the organisation stays before the actions needed for a move. Actions based on findings replace the stock steps and timeline.
- The summary shows three five-year totals in whole currency units, the Stay assumption and the annual target operations cost at which each move would cost the same as staying, where calculable. It uses the existing cost model. Known totals set one scale for the chart. An unknown total has a marker in place of a bar.
- The report shares the site's tokens and components, with six exceptions. (1) The report embeds both fonts and leaves script-dependent styles and icon masks to the site. (2) Symbols are inline SVG. (3) The report bar uses a `div`. D37 records the phone behaviour. (4) Link hover uses `--accent-hover`. (5) Coverage labels stay visible beside their symbols. (6) In grouped cards the area name is the anchor, the status is body size, Ready cards are compact and the evidence lists live in disclosures.
- The filled circle marks in-suite coverage on the site and in the report. Coverage symbols and status symbols have distinct paths. `site/icons/` holds every symbol the report inlines. The site checker and report tests enforce the design rules.

**D34. Licences is recorded inventory.**

The licence evidence stays in the recorded inventory. Status, cards and categories apply to the assessed catalogue, which gives the area count. It contains 14 assessed areas before Phase 1.1. This amends D21 and RULE-02.

**D35. Page one is for the council.**

- The header and summary have the same content on screen and on paper. They give the organisation, evidence and answer dates, the sample or invented-price note where applicable, each status with its count and definition, the first blockers or the zero-blocker statement with its evidence caveat, the open questions and the three totals with their origin. The council receives findings and open questions for its own decision.
- A4 PDFs verify page one for both samples and an all-Unknown report in English and German, with backgrounds on and off. Pasting into a council paper is best effort. This moves OUTP-03 from Phase 1.2 into the report redesign.

## 2026-11-22 — Target profiles

**D32. Readiness depends on the target profile.**

The evaluator reads the chosen profile's transfer gaps. A needed function that the profile leaves out or has no documented way to transfer makes its area at least Needs work. Only a workload rule can set Blocker. An Unknown need keeps its area from Ready. The target rules live in `src/fazit/rules/status.yaml`. New Blocker rules wait for the operator review.

## 2026-11-22 — Scan consistency

**D31. Validate the relationships between fields in `scan.json` 1.x at load time.**

- A successful collector has no failure reason. A partial or skipped collector has a registered reason. Measured findings and licence inventories refer to a collector that ran and a source registered for that evidence.
- A measured finding carries a value, collection date or time, and coverage. Its missing reason is empty.
- A provided finding carries a value and an interview source. Its collector, coverage and missing reason are empty.
- An unknown finding has a registered reason and an empty value.
- Each collector ID and finding ID appears at most once.
- A scan that includes evidence from a sample source declares its source kind as sample.
- Successful and failed checks together fit within the stated population. Complete coverage with counts records the entire population with zero failures.
- A count of scanned items fits within the stated successful count and within the total less known failures. Mail items, SharePoint files, Teams channels and bytes can accumulate multiple units per checked row.
- A measured value requires at least one possible successful check. Complete coverage of an empty population can establish zero or No.
- A subset fits within the upper bounds of its population when the catalogue links their counts and the observations share a source and reporting period or, without a period, a collection instant. A linked coverage total also limits successful checks after deducting known failures.
- The optional `directory_population` declares one scope and total for internal, guest and licensed account counts from the directory collector at a given instant. A measured count from that snapshot inherits the declared total for coverage checks when it omits its own. Its value and successful checks fit within the declaration's successful checks. When the declaration records failures only, the total less those failures bounds successful checks. A declaration marked partial or recording fewer successful checks than its total rules out a complete count. Internal and guest counts together fit within the declared total, and licensed accounts fit within their combined upper bound. For an incomplete count, its upper bound is the observed count plus the rows without a successful check, including failed checks. If the successful count is absent, the measurement establishes at least one successful check and at least one per observed account. Directory counts outside a matching declaration have independent scopes, even if their coverage totals match.
- Directory can be Ready only when complete internal and guest counts come from a complete declared population at the same instant. A confirmed guest still establishes a finding when the population is unverified.
- Teams with guests fit within the team count. Their stated coverage total equals the known team population and is at least the observed team count when the population is incomplete.
- Windows devices fit within all devices, and Windows-only applications without a web version fit within all Windows-only applications, when the observations are comparable.
- The mailbox usage and Exchange recipient exports have independent coverage. Shared mailboxes fit within the stated coverage of the recipient export.
- Within the same export and reporting period, an empty mailbox population rules out positive storage and item counts. An empty OneDrive account population rules out positive storage. An empty SharePoint site population rules out positive file and storage totals. An empty team population rules out positive channel counts.
- Assigned seats may exceed purchased seats. The excess appears in the licence evidence and the assigned seats still count towards use. [Microsoft 365 subscription guidance](https://learn.microsoft.com/en-us/microsoft-365/commerce/subscriptions/what-if-my-subscription-expires?view=o365-worldwide)
- Product GUIDs appear at most once after normalisation. Registered products may share a part number, as the two products with part number `MCOPSTN5` do. An incomplete inventory may omit either identifier. A product with one identifier remains unclassified. [Microsoft licence reference](https://learn.microsoft.com/en-us/entra/identity/users/licensing-service-plan-reference)
- Published product and service plan identifiers outside the code pattern require a matching GUID from the licence reference. An incomplete inventory can retain a published identifier without its GUID as unclassified evidence with the recorded seat counts. Published aliases for a registered SKU resolve to its registered product.
- Licence rows fit within successful checks and the total less known failures. Complete licence coverage records one row per product, including the empty inventory.
- A date-only collection stamp or reporting period end can be up to one day after the scan's UTC calendar date. A period end with a collection stamp must also fall within one day of the collection's UTC calendar date or earlier. A date-only reference supplies its stated calendar date. Clock times are compared as instants.
- Measured snapshots and the licence inventory carry a clock time. Every clock time includes a UTC offset or `Z`. Date-only collection stamps are accepted for period-based measurements and for provided or unknown evidence. A date alone never establishes a shared instant.
- Licence reconciliation requires a complete inventory, a complete directory population declaration and a complete measured licensed headcount from the same instant. The headcount must be at least the largest user-SKU assignment count and at most the sum of assigned user seats. When these checks leave assignments unverified, inferred licence absences stay unknown and positive assignments stay recorded.
- Counts supplied together in one `inputs.yaml` follow the same subset rule: a subset count fits within its population when both are given.

## 2026-11-21 — M0 complete (demo and report)

Fazit builds the nine-section report in German and English with all three target profiles. It accepts bundled samples or a compatible `scan.json` and the organisation's answers and costs in `inputs.yaml`. All measured figures in this milestone come from sample data. These commands run locally with no Microsoft account and contact no host.

- One `as_of` date applies to all answers in `inputs.yaml`. An omitted date is labelled as such. `amounts_are_invented` labels costs independently of the scan and of the origin of the answers.
- The catalogue uses `provided` values `no`, `answer`, `software_list` and `software_list_without_web_version`. The last two derive counts from the Windows-only software list. A positive lower bound can establish a problem when some application answers are still missing.
- The scan format contains no free text. The loader validates registered codes, rejects `@` and counts discarded fields and findings without exposing their keys. The display name and Windows-only application names are taken from `inputs.yaml`. JSON files omit SPDX headers because JSON has no comment syntax.
- Coverage is `complete`, `partial` or `unknown`. Counts must fit within the total. Complete counts cover the total with zero failures. Complete measurements take precedence over manual answers. A complete manual answer can replace a partial measurement for evaluation, with both shown. A positive measured lower bound takes precedence over a supplied zero and is shown as a conflict.
- Status rules use `exists`, `==`, `>` and `>=`. There is no `missing` operator. A confirmed problem can set a status while required evidence remains incomplete. Missing, skipped, unknown or partial required evidence is listed with reasons and next steps, and precludes Ready. A partial count can confirm a positive finding. Telephony needs a manual confirmation that Microsoft telephony is out of use before it can be Ready.
- Licence evidence gives the SKU part number and GUID, the plan name and GUID, and purchased and assigned counts. The associated `licences` collector must be present and able to supply evidence. The samples use real product and service plan identifiers checked against Microsoft's licensing reference, with simulated counts. Classification uses the product and plan pair to distinguish an assigned add-on from entitlement bundled with a suite. Audio Conferencing is a meetings signal. The derived finding forms are `licences.product_count`, `<workload>.licence_add_on_assigned` and `<workload>.licence_bundled_assigned`.
- Mappings use `no_function` for workloads with no function to transfer. The generic profile has no project documentation citations or check dates. Each transfer gap shows the documented limitation and the organisation's need separately. The need remains unknown without a specific complete answer. Checksums in the appendix use the bytes that were parsed, with one read per rule file.
- The report is `report-<YYYY-MM-DD>-<lang>.html`. The demo also writes `scan-<YYYY-MM-DD>-<lang>.json` and `inputs-<YYYY-MM-DD>-<lang>.yaml`. The date is taken from the scan. Each write stays inside the resolved `--out` directory, refuses symbolic links at the destination and replaces an existing regular file of the same name atomically.
- The wheel includes the report template, locales, rule files and both sets of sample files. The installed-package test checks these files, the licence and the offline console entry point. Its subprocess audit hook records and blocks socket operations, including attempts caught by the caller.

Costs use five years and the following formulas. Both exit scenarios use their own inputs and the same ongoing other IT cost as staying.

- Stay running cost = 5 × (annual Microsoft licences + annual other IT). The three change blocks are zero.
- Exit running cost = annual retained Microsoft licences × (60 − parallel months) ÷ 12 + monthly hosting per person × users × 60 + 5 × (annual operations + annual other recurring costs + annual other IT).
- Direct project cost = migration + application adaptation + external advice + training days per person × day rate × people trained.
- Productivity loss = the supplied total for lost working time.
- Parallel running = annual current Microsoft licences × parallel months ÷ 12.
- Scenario total = running cost + direct project cost + productivity loss + parallel running. Difference from staying = scenario total − stay total.

An unknown factor leaves a cost unknown unless another factor in that product is zero. A comparison stays unknown when either total is unknown. The calculation reconciles prorated lines in exact twelfths before division. Repeating amounts use high-precision Decimal values and are rounded to cents only for display.

## 2026-11-21: outcome of the Claude vs Codex analysis

Two independent analyses (Claude Fable 5.2 and Codex GPT-6.2-Astra at max effort) and one rebuttal each. The working documents are kept outside the repository. Both sides ended at "build with changes" and agree on everything below.

### Strategy

- **S1. The scanner is free and complete, and earns nothing by itself.** Any income comes from paid assessments and support built around it, sold mainly through integrators. No scanning feature is ever held back for payment.
- **S2. Primary user is the integrator or municipal IT provider**, not the town IT officer. The tool must stay simple enough for the officer.
- **S3. Market is Germany, Austria and Switzerland, public and private.** Microsoft 365 is the mail provider of 793 of 11,129 German municipalities, 1,401 of 2,092 Austrian and 1,099 of 2,110 Swiss (Bischof et al., "Email Provider Dependencies and Email Security in Municipalities Across Germany, Austria, and Switzerland", SecAssure 2026, table 3: <https://papers.mxmap-project.org/secassure2026.pdf>; checked on 2026-11-22). 87 % of German municipalities use domestic mail providers, hosted or their own.
- **S4. Positioning is exit readiness.** The report must be useful when the answer is "not yet" or "only this department".
- **S5. Licence stays AGPL-3.0-or-later.** Codex proposed Apache-2.0 and withdrew it.

### Changes to the handoff

- **D1. No single weighted readiness score.** Status is given per workload, with explicit unknowns. A skipped or denied collector must never make an organisation look more ready. (Replaces the readiness score in handoff section 8 and report section 4.)
- **D2. Every finding carries its evidence:** source, date, reporting period, coverage, and the reason for anything missing. Values are marked as measured, provided by the user, or unknown.
- **D3. Judgement before Microsoft code.** Rules, mappings, costs, `inputs.yaml` and the `report` command ship with the demo. (Handoff M3 moves ahead of M1.)
- **D4. New `import` command before any live sign-in.** Administrators export usage reports from the admin centre; the tool processes the CSV files locally and keeps aggregates only.
- **D5. Cost comparison shows three scenarios:** stay, partial exit, full exit, including retained licences and parallel running. A missing material input leaves the total unknown.
- **D6. Sign-in default is the browser flow with PKCE**, with a customer-owned single-tenant app registration. Device code is a fallback only. Since 1 July 2026 new Entra tenants block device code under security defaults.
- **D7. The two-host rule stays.** Microsoft's usage-report endpoints redirect to a third host (`reports.office.com` in Microsoft's example), so those reports come in through `import` (D4), not live collection. Live collection starts with licence and directory counts.
- **D8. "Read-only" is enforced by an endpoint allowlist**, not only by scope names. `GET /users/{id}/drive` is excluded because it can create a missing OneDrive.
- **D9. No shared-mailbox count from Graph usage reports.** The CSV has no recipient-type column. Shown as unknown unless an Exchange recipient export is imported.
- **D10. Permissions are requested per feature**, least privilege first. Admin consent for these delegated scopes can come from an Application Administrator or Cloud Application Administrator; the operator separately needs a reporting role.
- **D11. A `doctor` command** checks consent, roles and blocked sign-in flows and prints the fix.
- **D12. `.dotx` leaves the risky-file list**; it cannot contain macros. An `.xlsm` extension is reported as "may contain macros", never as a confirmed blocker.
- **D13. Tenant-wide file inventory is deferred** until paid assessments show it changes a decision. If built, it runs on customer-nominated libraries with a separately granted read permission, and capped scans are labelled partial.
- **D14. Distribution is `uvx` plus a signed, self-contained Windows build.**
- **D15. `pyyaml` is added to the dependency list.** The handoff mandates YAML files for rules, locales and inputs but does not list a YAML parser. No other dependency is added without a new entry here.
- **D16. `hatchling` is the build backend, pinned to an exact version.** It is needed to build the package and is not a runtime dependency.
- **D17. No package release younger than 14 days is installed.** `pyproject.toml` sets uv's `exclude-newer` to a fixed date, moved forward deliberately. A release that is a few days old has not been looked at by anyone yet.
- **D18. Command-line help is English only.** Everything in the report and every message the tool prints exists in German and English. Help text for commands and options stays in English, because the language is not known until the arguments have been parsed.
- **D19. Privacy is by construction, and there is no `--include-names` in v1.** `scan.json` 1.x has no field that can hold a person's name or address, collectors write codes and counts only, and the loader drops anything it does not know. The handoff's opt-in flag returns when a collector exists that could supply names. This replaces redaction, which only protects the fields someone remembered to list.
- **D20. No overall verdict.** The report gives status per area and says what must be resolved first. It does not say "go" or "no go", and it uses no numeric threshold.
- **D21. Fifteen areas are assessed, not nine.** (amended by D34) Public evaluations found their real gaps outside mail and files: telephony, Power Platform, identity, device management, security and compliance, small apps such as Forms and Planner, and integrations with business applications. Licence data shows which of these an organisation pays for, without reading any content.
- **D22. Costs are shown in three blocks:** direct project cost, productivity loss, and parallel running. Comparing licences with hosting alone understates the cost of leaving.
- **D23. A "second source" scenario is deferred.** Keeping Microsoft 365 and building a fallback for chosen areas is a real option for many organisations. It is not in v1.
- **D24 (replaced by D25). The tool was briefly called Fazit.** German for "conclusion" or "bottom line"; it reads naturally to the audience and in the formal register. Package, command and module are `fazit` (free on PyPI and npm on 2026-11-21). The working name `m365-exit-scan` is dropped because "M365" is Microsoft's trademark. A TMview search on 2026-11-21 found no live FAZIT word mark for software (class 9) or IT services (class 42) in the EU, Germany or Switzerland; expired German marks in those classes and live marks in unrelated classes exist. TMview is not an official register, so a formal clearance search is still needed before the first public release. The GitHub handle `fazit` is taken; the repository lives under the maintainer's account.
- **D25 (replaced by D27). The tool was briefly called Befund.** German for "finding", as in an auditor's or doctor's findings: the report is exactly that, and "ohne Befund" (nothing found) fits a tool that reports honest unknowns. Chosen by the founders on 2026-11-21 over Fazit. Package, command and module are `befund`, free on PyPI and npm; befund.dev appeared unregistered; the GitHub handle `befund` is taken, so the repository is `rouxdutoit/befund`. A TMview search on 2026-11-21 found no live mark for the plain word in class 9 or 42, but a crowded medical field around it: BEFUNDO (EU application, class 9, filed 2026-10-08), Befundomat (German registration, classes 9, 42, 44), and pending German applications befundHilfe (class 42) and B BefundWerk (class 9). A formal clearance search by a trademark attorney is needed before the first public release; the risk is higher than it was for Fazit.
- **D27. The tool is called Fazit, finally.** After Befund, a trademark search on 2026-11-21 found the EU application BEFUNDO (019433396, class 9, "downloadable computer software for the management of data", filed 2026-10-08, opposition period to 2027-01-15), one letter from Befund and older than our use. Fazit has no live mark in class 9 or 42 in the EU, Germany, Austria or Switzerland (TMview, 2026-11-21); the only German FAZIT mark in those classes has expired. Package, command and module are `fazit`; the repository is `rouxdutoit/fazit`. The search is not a formal clearance; a trademark attorney's opinion is still advisable before the PyPI release and the announcement.
- **D26. A report depends on the people and tools that produced its evidence.** Fazit checks the scan and inputs for contradictions and labels where each figure came from. An internally consistent fabrication can pass these checks and produce a report. The appendix records the scan's stated origin, producer and version.
- **D28. `hypothesis` is added as a test dependency, pinned to 6.170.15.** The two samples prove the rules on two tenants only. Property-based tests generate many synthetic tenants (coverage, provenance, collector status, licence mix, inputs, language) and check that the principles hold on all of them, and Hypothesis shrinks a failure to the smallest tenant that breaks one. Tests run derandomised with no example database, so a run is repeatable and leaves nothing on disk. 6.170.15 was uploaded on 2026-11-06 and is within `exclude-newer` (D17). Its one dependency is `sortedcontainers`. It is a development dependency only and is not in the wheel.
- **D29. Embed the report fonts.** The report embeds Figtree and Geist Mono, both licensed under the SIL Open Font License, as data URIs so its typography looks the same on every machine. Its content security policy allows only `font-src data:` for fonts. Principle 6 now specifies embedded fonts. The founder may switch to system fonts later, which would save about 69 KB per report.
- **D30. Controls are monochrome; colour means status.** Founder's decision on 2026-11-22, after trying apple.com's link blue, Apple green and a deeper green in light mode. Buttons, links and symbols take the text colour: near-black on white in light mode (`#1d1d1f`, hover `#424245`), Fazit's pale green on near-black in dark mode (`#c4f7d0`, hover `#e1fbe7`, with a glow). The only colours are Apple's system colours for the four statuses, so colour always means status. Links in running text carry a thin static underline in the secondary text colour, because colour no longer marks them (WCAG 1.4.1); standalone links keep their chevron, cards their circled chevron, and the footer has no underlines. Orange was ruled out because it is the Blocker colour.

### Milestone order

1. **M0:** demo, evidence model, rules, costs, `inputs.yaml`, `report`. German and English.
2. **M1:** `import` of admin-centre CSV exports.
3. **M2:** `doctor`, browser sign-in, live licence and directory counts, endpoint and host allowlists.
4. **M3:** documentation, packaging, signed Windows build, first tagged release.
5. **Later, driven by paid pilots:** selected-library file inventory, on-premises Exchange and file-server import.

### Decided by the founder, 2026-11-21

- **F1. Yes to the services business.** The founder wants a business in which customers pay for focused time, with everything around that time automated as far as it will go. Consequence for the tool: whatever an assessment repeats (inventory, cost comparison, the report itself, the interview checklist that fills `inputs.yaml`) should be produced by the tool, so that paid time goes to the conversation and the recommendation.

### Verified on primary pages on 2026-11-21

- Usage-report redirect and CSV columns: <https://learn.microsoft.com/en-us/graph/api/reportroot-getmailboxusagedetail?view=graph-rest-1.0>
- OneDrive provisioning on GET: <https://learn.microsoft.com/en-us/graph/api/drive-get?view=graph-rest-1.0>
- Device code blocked for new tenants: <https://learn.microsoft.com/en-us/entra/fundamentals/security-defaults>
- Existing tools: <https://github.com/google/migration-planner>, <https://plan-eu.eu/en/macro-scan/>

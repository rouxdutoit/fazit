# Decisions

Running log of design decisions, newest first. `HANDOFF.md` is the original spec; where an entry here conflicts with it, this file wins.

## Principles

1. **Read-only.** Request read permissions and use an explicit allowlist of read endpoints. Exclude requests that can change the tenant, even if they use `GET`.
2. **Local processing.** Assessment data stays on the computer. Live collection may contact only `login.microsoftonline.com` and `graph.microsoft.com`. Import usage reports offline. Omit telemetry, analytics, update checks and CDNs.
3. **Tokens in memory.** Keep access and refresh tokens in memory.
4. **Metadata only.** Collect counts, sizes and coded evidence. Leave mail bodies and file contents unopened.
5. **Privacy by construction.** Exclude collected person names and email addresses. The v1 CLI omits `--include-names`. Reports may show the organisation name and Windows-only application names entered in `inputs.yaml`.
6. **Offline report.** Produce one self-contained HTML file with inline CSS and system fonts. Omit JavaScript and external resources. The report opens and prints with the network disconnected.
7. **One command.** After setup, one command produces a report. Live collection uses browser sign-in with PKCE by default, with device code as a fallback.
8. **Honest figures.** Use supplied costs and clearly labelled example amounts. Show missing evidence as unknown. A skipped or denied collector never improves readiness.

## 2026-11-21 — M0 complete (demo and report)

Befund builds the nine-section report in German and English from either bundled sample or an existing scan, with all three target profiles. These commands run locally with no Microsoft account and contact no host.

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
- **S3. Market is Germany, Austria and Switzerland, public and private.** One study counts Microsoft 365 as mail provider for 793 of 11,129 German municipalities, 1,401 of 2,092 Austrian and 1,099 of 2,110 Swiss (cited by Codex from the MX-map study, April 2026; not yet opened by Claude). German towns are mostly on on-premises systems.
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
- **D21. Fifteen areas are assessed, not nine.** Public evaluations found their real gaps outside mail and files: telephony, Power Platform, identity, device management, security and compliance, small apps such as Forms and Planner, and integrations with business applications. Licence data shows which of these an organisation pays for, without reading any content.
- **D22. Costs are shown in three blocks:** direct project cost, productivity loss, and parallel running. Comparing licences with hosting alone understates the cost of leaving.
- **D23. A "second source" scenario is deferred.** Keeping Microsoft 365 and building a fallback for chosen areas is a real option for many organisations. It is not in v1.
- **D24 (replaced by D25). The tool was briefly called Fazit.** German for "conclusion" or "bottom line"; it reads naturally to the audience and in the formal register. Package, command and module are `fazit` (free on PyPI and npm on 2026-11-21). The working name `m365-exit-scan` is dropped because "M365" is Microsoft's trademark. A TMview search on 2026-11-21 found no live FAZIT word mark for software (class 9) or IT services (class 42) in the EU, Germany or Switzerland; expired German marks in those classes and live marks in unrelated classes exist. TMview is not an official register, so a formal clearance search is still needed before the first public release. The GitHub handle `fazit` is taken; the repository lives under the maintainer's account.
- **D25. The tool is called Befund.** German for "finding", as in an auditor's or doctor's findings: the report is exactly that, and "ohne Befund" (nothing found) fits a tool that reports honest unknowns. Chosen by the founders on 2026-11-21 over Fazit. Package, command and module are `befund`, free on PyPI and npm; befund.dev appeared unregistered; the GitHub handle `befund` is taken, so the repository is `rouxdutoit/befund`. A TMview search on 2026-11-21 found no live mark for the plain word in class 9 or 42, but a crowded medical field around it: BEFUNDO (EU application, class 9, filed 2026-10-08), Befundomat (German registration, classes 9, 42, 44), and pending German applications befundHilfe (class 42) and B BefundWerk (class 9). A formal clearance search by a trademark attorney is needed before the first public release; the risk is higher than it was for Fazit.

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

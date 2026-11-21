# Decisions

Running log of design decisions, newest first. `HANDOFF.md` is the original spec; where an entry here conflicts with it, this file wins.

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

### Milestone order

1. **M0:** demo, evidence model, rules, costs, `inputs.yaml`, `report`. German and English.
2. **M1:** `import` of admin-centre CSV exports.
3. **M2:** `doctor`, browser sign-in, live licence and directory counts, endpoint and host allowlists.
4. **M3:** documentation, packaging, signed Windows build, first tagged release.
5. **Later, driven by paid pilots:** selected-library file inventory, on-premises Exchange and file-server import.

### Open, for the founder

- Whether you want a business in which every paying customer buys your time and the scanner earns nothing.
- The funded scope in the Prototype Fund application (deadline 30 November 2026, 15:00 CET).
- The project name. "M365" is Microsoft's mark; descriptive use is normally acceptable.

### Verified on primary pages on 2026-11-21

- Usage-report redirect and CSV columns: <https://learn.microsoft.com/en-us/graph/api/reportroot-getmailboxusagedetail?view=graph-rest-1.0>
- OneDrive provisioning on GET: <https://learn.microsoft.com/en-us/graph/api/drive-get?view=graph-rest-1.0>
- Device code blocked for new tenants: <https://learn.microsoft.com/en-us/entra/fundamentals/security-defaults>
- Existing tools: <https://github.com/google/migration-planner>, <https://plan-eu.eu/en/macro-scan/>

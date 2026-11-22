# Research: new area "AI assistants (Copilot)"

All pages accessed on **2026-11-22** unless stated. "LSPR" means Microsoft's [licensing service plan reference](https://learn.microsoft.com/en-us/entra/identity/users/licensing-service-plan-reference) (HTML updated 2026-11-19). Its [CSV](https://download.microsoft.com/download/e/3/e/e3e9faf2-f28b-490a-9ada-c6089a1fc5b0/Product%20names%20and%20service%20plan%20identifiers%20for%20licensing.csv) was last modified 2026-08-19 and is **older than the HTML**; where they differ, the HTML is quoted and the difference noted.

## 1. Licensing

Microsoft has renamed the product. "Microsoft Copilot" is an add-on to eligible suites, or included in Microsoft 365 E7. "Microsoft Copilot Business" is an add-on for tenants with up to 300 users ([licence options](https://learn.microsoft.com/en-us/copilot/plan/copilot-license-options)). E7 "adds Microsoft Copilot, the Microsoft Entra Suite, and Microsoft Agent 365"; E3 and E5 get Copilot only as an add-on ([E3/E5/E7 comparison](https://learn.microsoft.com/en-us/copilot/plan/compare-copilot-e3-e5-e7)).

### 1.1 Copilot service plans (from LSPR)

| Plan name | Plan GUID | Meaning |
|---|---|---|
| M365_COPILOT_APPS | a62f8878-de10-42f3-b68f-6149a25ceb97 | Copilot in productivity apps |
| M365_COPILOT_TEAMS | b95945de-b3bd-46db-8437-f2beb6ea2347 | Copilot in Teams |
| M365_COPILOT_BUSINESS_CHAT | 3f30311c-6b1e-48a4-ab79-725b469da960 | Graph-grounded chat |
| M365_COPILOT_INTELLIGENT_SEARCH | 931e4a88-a67f-48b5-814f-16a5f1e6028d | Intelligent search |
| M365_COPILOT_SHAREPOINT | 0aedf20c-091d-420b-aadf-30c042609612 | Copilot for SharePoint |
| M365_COPILOT_CONNECTORS | 89f1c4c8-0878-40f7-804d-869c9128ab5d | Power Platform connectors in Copilot |
| GRAPH_CONNECTORS_COPILOT | 82d30987-df9b-4486-b146-198b21d164c7 | Graph connectors in Copilot |
| COPILOT_STUDIO_IN_COPILOT_FOR_M365 | fe6c28b3-d468-44ea-bbd0-a10a5167435c | Copilot Studio inside Copilot |
| Bing_Chat_Enterprise | 0d0c0d31-fae7-41f2-b909-eaf4d7f26dba | "Commercial data protection for Microsoft Copilot" (Copilot Chat) |
| VIRTUAL_AGENT_BASE_MESSAGES | 7b0640f1-63cc-4f83-b8c6-0a4d78b8b988 | Copilot Studio messages (capacity) |
| CDS_VIRTUAL_AGENT_BASE_MESSAGES | 5dd1819f-0de7-487f-985b-c450a4c9cc1d | Dataverse for Copilot Studio |
| FLOW_VIRTUAL_AGENT_BASE_MESSAGES | 4b9ec373-ed29-4192-8a47-c9ab9048b079 | Power Automate for Copilot Studio |
| VIRTUAL_AGENT_USL | 1263586c-59a4-4ad0-85e1-d50bc7149501 | Copilot Studio user licence |
| CDS_VIRTUAL_AGENT_USL | cb867b3c-7f38-4d0d-99ce-e29cd69812c8 | Dataverse, user licence |
| FLOW_VIRTUAL_AGENT_USL | 82f141c9-2e87-4f43-8cb2-12d2701dc6b3 | Power Automate, user licence |
| CCIBOTS_PRIVPREV_VIRAL | ce312d15-8fdf-44c0-9974-a25a177125ee | Copilot Studio viral trial |
| Microsoft_Copilot_for_Sales | a2194428-ead1-4fc1-bb81-ab8675125f42 | Copilot for Sales |
| Microsoft_Copilot_for_Sales_PowerAutomate | 0c1c2af2-6c51-43c7-9c55-fa487ac147ff | Copilot for Sales flows |
| financecopilot_trial | 5a6d0425-3ef2-4e42-8372-76709c9effe0 | Copilot for Finance (preview) |
| AGENT_365 | d0ce5ebb-9db0-491f-b780-8973a1d815fe | Agent 365 |

Already in `service_plans.yaml`: `Bing_Chat_Enterprise` (workload null) and `POWER_VIRTUAL_AGENTS_O365_F1/P1/P2/P3` (power_platform; the "Copilot Studio for Teams" plan bundled in suites, per [Copilot Studio access](https://learn.microsoft.com/en-us/microsoft-copilot-studio/requirements-licensing-subscriptions)).

### 1.2 Products (SKUs) and add-on versus bundled

| Product | SKU part number | SKU GUID | Copilot plans | Proposed class |
|---|---|---|---|---|
| Copilot for Microsoft 365 | Microsoft_365_Copilot | 639dec6b-bb19-468b-871c-c5c441c4b0cb | the eight M365_COPILOT_*/GRAPH/STUDIO plans | **add-on** |
| Microsoft Copilot for Microsoft 365 | M365_Copilot | a809996b-059e-42e2-9866-db24b99a9782 | same eight, plus MCOMEETADV | **add-on** |
| Microsoft 365 Copilot (Education Faculty) | Microsoft_365_Copilot_EDU | ad9c22b3-52d7-4e7e-973c-88121ea96436 | same eight | **add-on** |
| Microsoft 365 Copilot for Sales | Microsoft_Copilot_for_Sales | 15f2e9fc-b782-4f73-bf51-81d8b7fff6f4 | eight + Sales plans + Workplace Analytics | **add-on** |
| Microsoft Sales Copilot | Microsoft_Viva_Sales | 3227bcb2-8448-4f81-b3c2-8c2074e15a2a | Microsoft_Viva_Sales_PremiumTrial (8ba1ff15-7bf6-4620-b65c-ecedb6942766), Microsoft_Viva_Sales_PowerAutomate (a933a62f-c3fb-48e5-a0b7-ac92b94b4420) | **add-on** |
| Microsoft 365 Copilot for Finance (Preview) | Microsoft_Copilot_for_Finance_trial | 7792674b-fa0c-4af5-b2a1-a15239f933b6 | financecopilot_trial + COPILOT_STUDIO_IN_COPILOT_FOR_M365 | add-on (trial) |
| Microsoft Copilot Studio (Copilot Credit pack) | Power_Virtual_Agents | 75564b9c-51e8-431c-b8fe-d472d5a545c8 | the three *_BASE_MESSAGES plans | **add-on, tenant capacity** |
| Microsoft Copilot Studio User License | VIRTUAL_AGENT_USL | 4b74a65c-8b4a-4fc8-9f6b-5177ed11ddfa | the three *_USL plans | add-on (free, needs pack) |
| Microsoft Copilot Studio Viral Trial | CCIBOTS_PRIVPREV_VIRAL | 606b54a9-78d8-4298-ad8b-df6ef4481c80 | CCIBOTS_PRIVPREV_VIRAL | trial (self sign-up) |
| Power Virtual Agent (legacy) | VIRTUAL_AGENT_BASE | e4e55366-9635-46f4-a907-fc8c3b5ec81f | VIRTUAL_AGENT_BASE (f6934f16-83d3-4f3b-ad27-c6e9c187b260) | add-on, legacy |
| Agent 365 | AGENT_365 | 796a6fb4-740b-4d36-bf56-9c12ca7fa069 | AGENT_365 plus eleven "…_FOR_AGENTS"/DEFENDER_FOR_AI plans | add-on (agent governance) |
| Microsoft 365 E7 | MICROSOFT_365_E7 | 9a18296a-025f-4e37-9ffa-30bf8d1ce775 | all eight Copilot plans + AGENT_365 | **bundled** in a suite |
| E3, E5, Business, Office 365 E1/E3, F3 suites | e.g. SPE_E3, SPE_E5, SPB, ENTERPRISEPACK | (in LSPR) | Bing_Chat_Enterprise only | **bundled** |

Notes:

- **CSV/HTML drift.** In the August CSV, `Microsoft_365_Copilot` lacks M365_COPILOT_SHAREPOINT and COPILOT_STUDIO_IN_COPILOT_FOR_M365, and `M365_Copilot` lacks SharePoint, Studio and MCOMEETADV. The November HTML includes them. The product classification should key on the SKU, not on the exact plan list.
- **Copilot Chat cannot be proven from licence data.** Bing_Chat_Enterprise appears in 37 suite rows of the HTML, but 13 label it "RETIRED" (for example SPE_E3, Microsoft_365_E5_(no_Teams)) while siblings such as Microsoft_365_E3 do not. Microsoft says Copilot Chat (Basic) is "the standalone baseline experience included with eligible Microsoft 365 licenses" ([Copilot overview](https://learn.microsoft.com/en-us/copilot/plan/copilot-overview)). Treat it as available to everyone, and measure use from the usage report.
- **Not in LSPR (unverified):** "Microsoft Copilot Business" SKU identifiers; Copilot Studio pay-as-you-go (billed through an Azure subscription, so invisible to licence data, per [Copilot Studio licensing](https://learn.microsoft.com/en-us/microsoft-copilot-studio/billing-licensing)); any "Copilot for Service" SKU; Security Copilot (no per-user plan; listed as "Included for eligible customers" in E5 and E7).
- Only add-ons prove deliberate purchase. E7 is a suite, but buying E7 is itself a deliberate Copilot decision; see open questions.

## 2. Measurable evidence without reading content

| Source | Where | Periods | Columns (exact) | Per user? | Export |
|---|---|---|---|---|---|
| [Microsoft Copilot usage report](https://learn.microsoft.com/en-us/microsoft-365/admin/activity-reports/microsoft-365-copilot-usage) (licensed users) | M365 admin centre › Reports › Usage › Microsoft Copilot › Copilot | 7, 28, 90, 180 days | User name; Display name; Prompts submitted (any app); Copilot Chat (work) prompts submitted; Copilot Chat (web) prompts submitted; Active Days; Last activity date (UTC); Last activity date of Teams/Word/Excel/PowerPoint/Outlook/OneNote/Loop Copilot (UTC); … of Copilot Chat (work)/(web) (UTC); … of Microsoft 365 App (UTC); … of Microsoft Edge (UTC) | Yes; names hidden by default | **Export** to CSV |
| [Copilot Chat usage report](https://learn.microsoft.com/en-us/microsoft-365/admin/activity-reports/microsoft-copilot-usage) (unlicensed users only) | … › Microsoft Copilot › Copilot Chat | 7, 28, 90, 180 days | Username; Display name; Prompts submitted; Active days; Last activity date (UTC); Last activity date of Teams/Outlook/m365.cloud.microsoft/chat/Microsoft Copilot (app)/Edge/Word/Excel/PowerPoint/OneNote (UTC) | Yes; hidden by default | Export to CSV |
| [Agents usage report (preview)](https://learn.microsoft.com/en-us/microsoft-365/admin/activity-reports/microsoft-365-copilot-agents-new) | … › Microsoft Copilot › Agents | 7, 30 days | Agent table: Agent ID; Agent name; Creator type (Your Users / Your org / Microsoft / Third-party); Active users (licensed); Active users (unlicensed); Responses sent to users; Last activity date (UTC). User table: Username; Display name; Number of agents used; Agent responses received; Last activity date (UTC) | Agent table is per agent; user tables per user | Export not explicitly described on the page (**unverified**) |
| Graph `getMicrosoft365CopilotUsageUserDetail` ([beta](https://learn.microsoft.com/en-us/graph/api/reportroot-getmicrosoft365copilotusageuserdetail?view=graph-rest-beta)); successors under `/copilot` incl. `getMicrosoft365CopilotUserCountSummary` ([report root](https://learn.microsoft.com/en-us/microsoft-365-copilot/extensibility/api/admin-settings/reports/resources/copilotreportroot)) | Graph, `Reports.Read.All` | D7–D180 | CSV: Report Refresh Date, Report Period, User Principal Name, Display Name, Last Activity Date, Microsoft Teams/Word/Excel/PowerPoint/Outlook/OneNote/Loop Copilot Last Activity Date, Copilot Chat Last Activity Date | Yes | CSV redirects to `reports.office.com`; JSON returns `200` from Graph |
| [Power Platform inventory](https://learn.microsoft.com/en-us/power-platform/admin/power-platform-inventory) | PPAC › Manage › Inventory, or › Copilot Studio | current state | Item name, Item type (`microsoft.copilotstudio/agents`), Item ID, Location, Created on, Created by (object ID), environment, connectors ([schema](https://learn.microsoft.com/en-us/power-platform/admin/inventory-schema)) | Per resource; owner/creator IDs | **Download** to CSV (entire inventory) |

Observations:

- The Copilot usage report includes every user licensed in the past 180 days, even with no activity, so it yields **enabled** and **active** counts. Fazit should keep only counts: rows, rows with a last-activity date inside the period, and the sum of prompts. Names and agent names are discarded (principle 5). Agent names would be free text, so we keep only the count of agents by Creator type.
- Inventory needs Global admin, Power Platform admin, Dynamics 365 admin, Global reader, or AI admin/reader. Classic chatbots are excluded and appear under Copilot Studio › Classic chatbots. The CSV column headers are not listed on the page (**unverified**); a real export is needed before writing an importer.
- Microsoft says Purview audit data "isn't intended to be used as the basis for Copilot usage reporting". Do not use it.
- JSON output from Graph stays on `graph.microsoft.com` (example shows `200 OK`), unlike CSV. This could let a later live collector respect D7. **Unverified in a real tenant.**

## 3. Interview questions (provided answers)

1. Do staff use any Microsoft AI assistant at work, including the free Copilot Chat in Edge, Teams or Outlook? (`copilot.in_use`)
2. Has the organisation built agents in Copilot Studio, Agent Builder or SharePoint agents that colleagues use? Roughly how many? (`copilot.org_agents_in_use`, `copilot.agent_count`)
3. Do those agents use connectors, Graph/Copilot connectors, Dataverse or external data sources? (`copilot.agent_connectors_in_use`)
4. Is Copilot Studio paid through a Copilot Credit pack or pay-as-you-go on Azure? (supports `copilot.studio_capacity_purchased`)
5. Is Copilot, or any agent, part of a process that must keep running (citizen-facing chat, case handling, help desk)? (`copilot.business_critical`)
6. Are there DLP policies on the "Microsoft Copilot, Copilot Chat, and Copilot Cowork" location, or sensitivity labels that exclude content? ([Purview DLP for Copilot](https://learn.microsoft.com/en-us/purview/dlp-microsoft365-copilot-location-learn-about)) (`copilot.policies_in_use`)
7. Are there shared prompt libraries or templates staff depend on? (`copilot.prompt_library_in_use`)
8. Has a replacement assistant been chosen and tested? (`copilot.replacement_available`)

## 4. Open alternatives (project documentation only)

| Profile | Function | Coverage | Basis |
|---|---|---|---|
| **Nextcloud** | Chat assistant | in_suite_with_limits | Assistant app (AGPL-3.0 per GitHub) gives "Chat with AI"; needs a backend: local `llm2` or remote `integration_openai` (OpenAI-compatible, also Ollama/LocalAI) ([AI overview, Nextcloud 35](https://docs.nextcloud.com/server/stable/admin_manual/ai/overview.html)). `llm2`: GPU ≥8 GB VRAM or 10–20 CPU cores, ≥12 GB RAM; "It is currently not possible to scale this app"; about 1,000 requests/hour theoretical; advises against critical use ([llm2](https://docs.nextcloud.com/server/stable/admin_manual/ai/app_llm2.html)). |
| Nextcloud | AI in documents and mail | in_suite_with_limits | Smart picker, Mail thread summaries, document generation in Nextcloud Office through an LLM provider (overview page). |
| Nextcloud | Answers grounded in organisation files | in_suite_with_limits | Context Chat indexes users' files; no files over 100 MB, no password-protected files, no multi-tenant, does not enforce `files_accesscontrol` ([Context Chat](https://docs.nextcloud.com/server/stable/admin_manual/ai/app_context_chat.html)). |
| Nextcloud | Meeting transcription and summaries | in_suite_with_limits | Talk transcription via `stt_whisper2`, subtitles via `live_transcription`, chat summaries (overview page). |
| Nextcloud | Custom agents with connectors | not_available | `context_agent` exists, but no documented builder for organisation-made agents with business connectors. |
| **openDesk** | AI in documents | in_suite_with_limits | AI wiring for Collabora Online and Notes only; operator supplies "an external, OpenAI-API-compatible AI endpoint", model and key; empty endpoint (default) "disables AI everywhere"; no AI backend shipped ([openDesk AI](https://docs.opendesk.eu/operations/ai/)). Edition and stability not stated. |
| openDesk | Chat assistant | not_available | Not documented. Nextcloud Assistant is not mentioned. |
| openDesk | Grounded answers, meeting AI, custom agents | not_available | Not documented. An "agentic AI" prototype by ZenDiS was reported by a secondary source ([borncity, 2026-10-10](https://borncity.com/news/opendesk-zendis-zeigt-agentische-ki-und-offline-betrieb-fuer-behoerden/)); no primary ZenDiS page found, so it does **not** qualify as `announced` (**unverified**). An MCP page is linked from the AI page but returned 404. |
| Generic | Chat, grounded answers | open_source_community | Self-hosted serving such as Ollama (MIT), vLLM (Apache-2.0), LocalAI (MIT) (licences per GitHub API). Open WebUI reports no standard SPDX licence; check before recommending. |
| Generic | AI in office documents | open_source_third_party | LibreOffice ships "no AI of any kind in the default installation"; optional extensions connect to local models ([TDF, 2026-09-03](https://blog.documentfoundation.org/blog/2026/09/03/yes-no-ai-is-now-a-feature/)). Collabora Online 26.04 added an AI Assistant tab, Calc/Impress AI tools and AI deck generation ([release notes](https://www.collaboraonline.com/collabora-online-26-04-release-notes/)); default-off and provider types not stated there (**unverified**). |
| Generic | Custom agents | open_source_community | Separate redevelopment on an open agent framework. |

## 5. Cost model inputs

List prices, Germany, net of VAT (documentation only; Fazit never uses them):

| Item | Price | Source |
|---|---|---|
| Microsoft 365 Copilot (enterprise) | 26,00 €/user/month, annual billing; 27,30 € paid monthly | [microsoft.com/de-de enterprise](https://www.microsoft.com/de-de/microsoft-365-copilot/enterprise) |
| Microsoft 365 Copilot Business | 18,20 €/user/month annual (promo 15,60 € first year, 2026-07-01 to 2026-12-31); 21,84 € monthly | [microsoft.com/de-de pricing](https://www.microsoft.com/de-de/microsoft-365-copilot/pricing) |
| Copilot Studio Copilot Credit pack | 173,30 €/pack/month for 25,000 credits; VAT not stated | [Copilot Studio page](https://www.microsoft.com/de-de/microsoft-copilot/microsoft-copilot-studio) |
| Copilot Studio pay-as-you-go | no EUR rate shown (**unverified**) | same |
| Microsoft 365 E7 | no price shown (**unverified**) | enterprise page |

Microsoft also notes usage-based billing for "select advanced AI features" (Cowork, Code, Autopilot) on top of licences. These costs do not show in licence data.

Cost lines a move needs. All can use existing `inputs.yaml` blocks; no new formula is needed:

| Line | Existing block |
|---|---|
| Copilot add-on licences (stay) and any kept during transition | annual Microsoft licences / retained licences / parallel running |
| Replacement assistant subscription or support (e.g. Nextcloud/openDesk support with AI) | annual other recurring costs |
| Inference: own GPU servers (≥8 GB VRAM per `llm2`) or an API priced per token | monthly hosting per person, or annual other recurring costs |
| Model operations (updates, evaluation, monitoring) | annual operations |
| Rework of each agent, connector and prompt library | application adaptation |
| Redesign of Copilot DLP and label rules | external advice |
| Training on the new assistant | training days |
| Lost time while assistants differ in quality | productivity loss |

## 6. Proposal

### 6.1 Findings (`workload: copilot`, label `workload.copilot`, placed after `licences`)

| ID | Type | Source | Phase | Headline |
|---|---|---|---|---|
| `copilot.licence_add_on_assigned` | boolean | derived from licences (existing pattern) | now | yes |
| `copilot.licence_bundled_assigned` | boolean | derived from licences | now | no |
| `copilot.studio_capacity_purchased` | boolean | licences: purchased units of `Power_Virtual_Agents` > 0 (tenant pack, not assigned to users); `provided: answer` for pay-as-you-go | now | no |
| `copilot.licensed_user_count` | count, users | licences: assigned units of add-on SKUs | now | yes |
| `copilot.active_user_count` | count, users | import: Copilot usage report (rows with last activity in period) | 2 | yes |
| `copilot.chat_active_user_count` | count, users | import: Copilot Chat usage report | 2 | no |
| `copilot.agent_count` | count, agents | import: agents report (Creator type Your org + Your Users) or PPAC inventory rows of type `microsoft.copilotstudio/agents`; `provided: answer` | 2 | no |
| `copilot.in_use` | boolean | answer | now | no |
| `copilot.org_agents_in_use` | boolean | answer (measured later from `agent_count`) | now | no |
| `copilot.agent_connectors_in_use` | boolean | answer | now | no |
| `copilot.policies_in_use` | boolean | answer | now | no |
| `copilot.prompt_library_in_use` | boolean | answer | now | no |
| `copilot.business_critical` | boolean | answer | now | no |
| `copilot.replacement_available` | boolean | answer | now | no |

Service plan changes: add the plans in 1.1 with `workload: copilot`; add the add-on SKUs in 1.2 with those plans under `add_on`; list them under `bundled` in E7. Move `Bing_Chat_Enterprise` from `no_workload` to `bundled` under `copilot`, or leave it unclassified given the "RETIRED" inconsistency (open question). Keep `POWER_VIRTUAL_AGENTS_O365_*` in `power_platform` unless the founder prefers to move them.

### 6.2 Status rules (status.yaml style)

```yaml
copilot:
  ready:
    evidence:
      - {finding: copilot.licence_add_on_assigned, op: '==', value: false}
      - {finding: copilot.studio_capacity_purchased, op: '==', value: false}
      - {finding: copilot.in_use, op: '==', value: false, provenance: provided}
      - {finding: copilot.org_agents_in_use, op: '==', value: false}
  rules:
    - id: copilot-critical-no-replacement
      when:
        - {finding: copilot.business_critical, op: '==', value: true, provenance: provided}
        - {finding: copilot.replacement_available, op: '==', value: false, provenance: provided}
      status: blocker
    - id: copilot-add-on            # needs_work
      when: [{finding: copilot.licence_add_on_assigned, op: '==', value: true}]
    - id: copilot-studio-capacity   # needs_work
      when: [{finding: copilot.studio_capacity_purchased, op: '==', value: true}]
    - id: copilot-agents            # needs_work
      when: [{finding: copilot.agent_count, op: '>', value: 0}]
    - id: copilot-agents-answer     # needs_work
      when: [{finding: copilot.org_agents_in_use, op: '==', value: true}]
    - id: copilot-connectors        # needs_work
      when: [{finding: copilot.agent_connectors_in_use, op: '==', value: true}]
    - id: copilot-in-use            # needs_work
      when: [{finding: copilot.in_use, op: '==', value: true}]
    - id: copilot-critical-with-replacement   # needs_work
      when:
        - {finding: copilot.business_critical, op: '==', value: true, provenance: provided}
        - {finding: copilot.replacement_available, op: '==', value: true, provenance: provided}
```

Unknown follows from the engine: any missing Ready evidence keeps the area Unknown. Bundled Copilot Chat alone never sets a status, because every suite carries it; `copilot.in_use` decides.

### 6.3 Mapping rows

| function | Microsoft | openDesk | Nextcloud | Generic | need_finding |
|---|---|---|---|---|---|
| `ai_chat_assistant` | Copilot Chat | not_available | in_suite_with_limits | open_source_community | `copilot.in_use` |
| `ai_in_documents` | Copilot in Word, Excel, PowerPoint, Outlook | in_suite_with_limits | in_suite_with_limits | open_source_third_party | `copilot.licence_add_on_assigned` |
| `ai_grounded_search` | Graph-grounded chat and search | not_available | in_suite_with_limits | open_source_community | `copilot.licence_add_on_assigned` |
| `ai_meeting_notes` | Teams recap and transcription | not_available | in_suite_with_limits | open_source_community | `copilot.in_use` |
| `custom_agents` | Copilot Studio agents and connectors | not_available | not_available | open_source_community | `copilot.org_agents_in_use` |

Reference URLs and notes are those in section 4; generic rows carry none, as today.

## 7. Open questions

1. Should E7 count as deliberate Copilot use (treat its Copilot plans as add-on) or as bundled?
2. Is `Bing_Chat_Enterprise` worth classifying given 13 "RETIRED" labels, or is Copilot Chat measured only by report and interview?
3. Need a real export of the agents report and the PPAC inventory CSV to confirm headers before building importers.
4. Copilot Business SKU identifiers are missing from LSPR; recheck at the next LSPR update.
5. Does the founder want a separate `inputs.yaml` cost line for inference, or reuse hosting and recurring costs?
6. Should the `copilot` area require a provided `copilot.in_use == false` before Ready even when no add-on exists (proposed: yes, like telephony)?

# Brief: is Fazit's report the most useful document for a move off Microsoft 365?

You are an independent reviewer. Another reviewer gets the same brief and works without seeing your answer. Read the repository (the current directory) read-only. Do not edit any file. Write your answer in English, plain Markdown, no preamble.

## Context

Fazit (AGPL-3.0, Python 3.12) is a free, local, read-only command-line tool. It writes one self-contained offline HTML report, in German or English, on what moving an organisation off Microsoft 365 would take. The target is openDesk, Nextcloud or a product-neutral profile. Its audience is public bodies and integrators in Germany, Austria and Switzerland, with 200 to 2,000 seats. The main user is an integrator or municipal IT provider; a council IT officer must still be able to run it alone.

Today the report is built from bundled fictional samples plus the organisation's answers and costs in `inputs.yaml`. Import of admin-centre CSV exports (phase 2) and packaging with a signed Windows build (phase 2.1) come next; the public launch follows. Phases 1.1 (Copilot area and decision window), 1.2 (CSV export and `fazit verify`) and 1.3 (links to sovereignty criteria) follow import.

A report redesign has a finished spec (`.planning/report-redesign/UI-SPEC.md`, revision 3). It puts the conclusion first: a status count, what blocks the move, cost tiles, what is still unknown, then one card per area. Its build is on hold until this review is in, because what the report contains may need to be designed differently. The design aim is Apple's structure: conclusion first, one thing to look at first per screen.

## Rules you must respect

- `DECISIONS.md`, section "Principles", and decisions D1 to D27: local, read-only, offline; no telemetry or network calls; metadata only; no person names; honest Unknowns (a missing input never improves a status); **no overall score, verdict or supplier recommendation**.
- `DESIGN.md` is binding for anything visual: monochrome controls; colour only for the four statuses (Ready, Needs work, Blocker, Unknown; German: Bereit, Handlungsbedarf, Hindernis, Unbekannt); Material Symbols; no JavaScript in the report.
- You may challenge a principle or decision. If you do, mark it clearly as **"Founder decision:"** and say what it would cost and gain. Do not quietly design around a principle.
- Fazit cannot read file contents, mail bodies or person data, and today measures only counts from admin-centre reports. Do not propose features that need data it cannot have without saying so, and say which phase could supply it.

## Read first

- `site/demo/en/index.html`: the current sample report (fictional town, about 90 seats). Open it as the reader would. `site/demo/de/index.html` is the German version.
- `.planning/report-redesign/UI-SPEC.md`, with its reviews `REVIEW-fable.md` and `REVIEW-astra.md` in the same folder.
- `.planning/report-redesign/RR-0*-PLAN.md`: the five build plans. Another agent is amending them right now; read them as work in progress.
- `.planning/research/launch-critique/SYNTHESIS.md`: what a sceptical launch audience said.
- `DECISIONS.md`, `DESIGN.md`, `AGENTS.md`, `.planning/PROJECT.md`, `.planning/ROADMAP.md`, `.planning/REQUIREMENTS.md`.
- `docs/interview-checklist.md` and `src/fazit/rules/` (findings, status rules, mappings, risky file types, service plans).
- Skim `src/fazit/` only as needed to check what the tool can compute.

## Questions

### 1. The report, persona by persona

For each persona below, answer in this order:

- **Decision or action:** what they need this document for, in one or two sentences. Name the real procedure where one exists (for example a council resolution, a Datenschutz-Folgenabschätzung under GDPR Art. 35, a Dienstvereinbarung under BetrVG § 87 (1) 6 or the Personalvertretungsgesetz, a tender under GWB/VgV or UVgO, a Haushalt or Wirtschaftlichkeitsuntersuchung under BHO § 7).
- **What the current sample report gives them**, with the section name.
- **What is missing** that they need and Fazit could honestly supply (now or in a named phase).
- **What should be cut or moved** because it costs them attention.
- **Order:** where their part should appear in the report, or whether it belongs in a separate output.

Personas:

1. The council or committee that decides (Gemeinderat, Ausschuss, Geschäftsleitung).
2. The IT lead who runs Fazit.
3. The integrator's project lead who executes the move.
4. The data protection officer.
5. The works council or Personalrat (co-determination when new IT systems are introduced).
6. Procurement (public tenders need a specification).
7. Finance (Kämmerei, budget, Wirtschaftlichkeit).

Then say in a short paragraph whether one report can serve all seven, or whether the report should serve one or two readers and other outputs serve the rest. Say which reader the first screen is for.

### 2. What Fazit should produce: ranked ideas

Rank ideas for what Fazit should produce to carry a client from "should we?" to "here is the project". Judge this seed list; do not assume any item is good. Add your own.

- a one-page decision memo;
- a draft requirements list for a tender;
- a risk register with owners;
- work packages importable into OpenProject (part of openDesk);
- effort ranges derived from the inventory, with stated assumptions;
- sequencing by dependency;
- no-regret actions for organisations that stay for now;
- progress tracking across repeated runs (comparing two reports);
- a "stay on a sovereign Microsoft cloud" scenario (decision D23 deferred a second-source scenario).

For each idea give: **value to clients** (high, medium, low, with the persona it serves); **honesty risk** (can it be done without inventing numbers or crossing into a verdict or supplier recommendation?); **data it needs** and whether Fazit has it; **format** (section in the report, separate file, or CLI output; mind the offline, no-JavaScript, metadata-only rules); **phase** it fits (1.1, 1.2, 1.3, 2, 2.1, 3, 4, or a new phase); **verdict** (do, do later, or do not do) with one sentence why. Put the ranked table first, then notes on the top five.

### 3. Changes to the redesign spec before it is built

Go through `UI-SPEC.md` by section (0 to 11). For each change, give the section, the change, the reason (which persona or which finding above), and whether it is **must before build** or **can follow**. Keep within `DESIGN.md`. Flag anything in the spec that the persona review shows to be wrong, not just missing. Say if the spec's first screen answers the right question for the right reader.

### 4. Decisions for the founder

List the decisions only the founder can make, each with the options and your recommendation in one line.

## Output

Use the four headings above. Short sentences, plain words, British spelling. Cite the file and section (or line) for each claim about the repository. Quotes from the repository at most 15 words each. No praise, no filler. Aim for depth over length; about 3,000 to 5,000 words.

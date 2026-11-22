# Fazit before Show HN: what the thread will say

Basis: repository at HEAD on 2026-11-22 (108 commits, first commit 2026-11-21 13:00). Read: the seven site pages named in the brief, README.md, SECURITY.md, CONTRIBUTING.md, DECISIONS.md, AGENTS.md, HANDOFF.md, .planning/ROADMAP.md, PROJECT.md, STATE.md, the release-review findings, pyproject.toml, ci.yml, site.js, _headers, cli.py, status.yaml, the mapping files, test names. I ran `fazit demo` once into the scratchpad (0.7 s, output byte-identical to site/demo/en/index.html). I did not run the test suite, did not open the live site or the GitHub repository, and did not read the German pages.

## 1. Top comments

Ranked by damage to the thread.

### 1. "It does not read Microsoft 365"

> "So this is a Show HN for an M365 exit scanner that cannot scan M365. It renders a Jinja template from a bundled JSON file. Come back when it does the thing in the title."

- Trigger: README.md:73 "Import and live collection are not available yet."; cli.py has only `demo` and `report`.
- Fair: yes. This is the comment that gets upvoted to the top, and it also touches the Show HN rule that the work must be something people can try for its stated purpose.
- Smallest change: timing. Do not post until `import` (Phase 2) produces a report from a real admin-centre export. If posting anyway, the title must say what exists: "Show HN: Fazit – an evidence model and report format for M365 exit assessments (no collection yet)", and the first line of the hero must say "sample data only".

### 2. "Two days old, 57,000 lines, 'human-reviewed'"

> "First commit yesterday at 1pm, 108 commits, 56k lines added, 20 commits in a single hour. Nobody reviewed this. 'Signs off every change' means `git commit -s`."

- Trigger: `git log` (2026-11-21 13:00 to 2026-11-22 15:00); site/index.html:400 "signs off every change and is responsible for it".
- Fair: yes. Worse, the project's own tracked file contradicts the site: .planning/PROJECT.md:71 "the founder cannot audit every line at the models' level".
- Smallest change: copy. Replace the "Owned by" tile with the PROJECT.md sentence, which is the honest and stronger one: "The maintainer directs the work and cannot audit every line. Trust rests on what you can check: small modules, tests, three dependencies." Delete "signs off every change" and "human-reviewed" everywhere (README.md:95, CONTRIBUTING.md, site).

### 3. "The model line-up is an advert"

> "'Claude Opus 5.5 Max, Codex 6.2 Sol Max, reviewed by Fable 5.2 Max'. This reads like a GPU spec sheet. LLMs reviewing LLMs is not review. And then it links an anti-slop manifesto."

- Trigger: site/index.html:392-405 "Written with … Max … Reviewed by … Max"; "No AI Slop manifesto".
- Fair: mostly. Disclosure is right; listing models as a quality credential with a "Max" badge is not disclosure, it is a claim, and the manifesto link dares the thread to find slop.
- Smallest change: cut the section to one sentence in the footer area and README: "Fazit is written with AI coding tools (Claude, Codex) under one human maintainer. Model reviews are in the repository." Remove "Max", "at maximum effort", and the manifesto link.

### 4. "'Ready' means 'counted'"

> "Teams is 'Ready' because 'the teams have been counted'? I've done one of these migrations. Counting 31 teams tells you nothing about readiness. This is a checklist with traffic lights."

- Trigger: sample report: "The teams have been counted, there are no guests, and the chat history" (Ready); status.yaml `ready` blocks are `exists` checks plus one or two yes/no answers; "Licences: Ready".
- Fair: yes. The rules are shallow, and "Ready" overstates what two answers establish. Practitioners will pile on with examples (meeting recordings, Planner tabs in teams, shared channels, mail-enabled apps).
- Smallest change: copy in locales and status.yaml. Rename the status from "Ready" to "No blocker found" (DE: "Kein Hindernis festgestellt" collides with existing wording, so pick with care) and reword reasons as "No guests and no chat retention requirement reported", not "counted". Drop "Licences" as an area with a readiness status, since nothing moves.

### 5. "Most of the evidence is a questionnaire the user fills in"

> "The home page talks about finding 'hundreds of business-critical macros'. The macro count in the report is a number the user typed into a YAML file. The tool will never scan files; it says so itself."

- Trigger: site/index.html "hundreds of business-critical macros"; report "Files that may contain macros 271 files Provided"; DECISIONS.md D13 defers file inventory.
- Fair: yes. In the sample, every status-deciding finding outside licences and counts is "Provided". The planned collection (licence and directory counts, usage CSVs) will not change that for macros, Power Platform, telephony, integrations or SSO apps.
- Smallest change: copy. Say it on the home page: "Fazit measures what licences and usage reports show. Everything else is a structured interview, and the report labels it as such." Replace the macro example with one the tool can actually measure (an assigned Teams Phone licence).

### 6. "The invented numbers happen to show exit saves 135,000 euros"

> "Sample report: staying costs 600k, full exit 464k. All inputs 'invented'. So the demo's one memorable number is a made-up saving in the direction the author wants."

- Trigger: sample report "Difference from staying … EUR -135,650.00"; "Hosting per user per month … EUR 8.50".
- Fair: partly. Every amount is labelled invented, but the headline result of the only public report is a fabricated win for leaving. "Productivity loss" is a single number the user types, which the thread will call a spreadsheet with extra steps.
- Smallest change: sample data. Make the town sample come out with exit more expensive or roughly equal over five years (higher migration, training and parallel running), or leave one material input empty so the full-exit total reads "Unknown". That demonstrates the claimed honesty better than any sentence.

### 7. "The privacy promises are true of `echo`"

> "'0 network connections', 'keeps no tokens', 'read-only'. It has no network code, so yes. You are advertising the security properties of software that does not exist yet."

- Trigger: site/index.html stat tile "0 network connections in the current version"; "Fazit never writes to Microsoft 365 and keeps no tokens".
- Fair: yes. The interesting safeguards (host allowlist, endpoint allowlist, tokens in memory) are untested because unbuilt; SECURITY.md says so, the site's "Every safeguard has a test anyone can run" does not.
- Smallest change: copy. Split the block into "True today" (no network code, report loads nothing, no JavaScript in the report, CSP `default-src 'none'`, writes only inside `--out`) and "Design commitments for sign-in, not yet built". Remove the "0 network connections" tile.

### 8. "Lead generation for a consultancy"

> "Pilots page, integrators directory, cal.com booking link, 'founding pilots' with a deadline. The tool is the funnel. DECISIONS.md literally says 'Yes to the services business'."

- Trigger: DECISIONS.md F1 "Yes to the services business."; site/pilots/, site/integrators/ "Public list of firms"; PROJECT.md:73 Prototype Fund deadline 30 November 2026.
- Fair: partly. Selling services around free software is normal; hiding it is what gets punished. The site never says it, the repository does, and the grant deadline eight days after the post makes the timing look instrumental.
- Smallest change: copy plus cut. One plain sentence on the home page: "The tool is free and complete. The maintainer plans to earn from paid assessments." Remove the integrators directory page until one assessment exists (it currently describes an empty list for a feature that is not built).

### 9. "git clone and uv for a council IT officer?"

> "Target user is a municipal IT person on Windows. Install path is 'install Git, install uv, clone, run from source'. Not on PyPI. No binary. No release tag."

- Trigger: README.md:73 "Fazit runs from a clone and is not yet published on PyPI."; no git tags.
- Fair: yes, and cheap to fix. The wheel already builds and is tested offline (tests/test_installed_package.py).
- Smallest change: process. Tag v0.1.0, publish to PyPI, and make the command `uvx fazit demo`. Attach the wheel and its SHA-256 to a GitHub release. The trademark opinion flagged in D27 is the stated blocker; resolve or consciously accept it first.

### 10. "The mappings were skimmed from an architecture page in an afternoon"

> "10 of 19 openDesk rows cite the same architecture overview URL, all 'checked 21 November'. openDesk ships XWiki and CryptPad and neither appears. Who checked this, the model?"

- Trigger: src/fazit/rules/mappings/opendesk.yaml (10 rows cite docs.opendesk.eu/operations/architecture/; no XWiki, CryptPad or Notes); site "checked against project documentation on 21 and 22 November 2026".
- Fair: yes as far as I can tell from the files. SharePoint intranet pages and OneNote have an obvious openDesk counterpart in XWiki and Notes, and Visio in CryptPad's diagram editor; their absence suggests nobody who runs openDesk has read the mapping. I did not verify the openDesk component list against its site today.
- Smallest change: process. Before launch, get one openDesk and one Nextcloud practitioner to review the two YAML files and record their names and date in the file header. Until then say "drafted from public documentation, not yet reviewed by an operator".

### 11. "Nobody can produce a scan.json"

> "'A compatible scan.json' appears six times and there is no schema, no docs, and no tool that emits one. The format is defined by reading model.py."

- Trigger: README.md:7 "a compatible `scan.json`"; docs/ contains only the interview checklist.
- Fair: yes.
- Smallest change: docs. Add `docs/scan-format.md` with the field list and one minimal hand-written example, or stop mentioning the scan path and describe only `demo` plus `inputs.yaml` until `import` exists.

### 12. "The repository is a museum of prompts"

> "HANDOFF.md, AGENTS.md, .claude/, 70 files of .planning with PLAN/SUMMARY/REVIEW per task, and a plan that says the founder wanted the home page 'closer to pandex.io'. The header of HANDOFF.md still calls the tool Befund."

- Trigger: HANDOFF.md:1 "The tool is now called Befund."; .planning/quick/261122-ego-home-page-rework-after-pandex-comparison/PLAN.md; DESIGN.md "apple.com neutrals".
- Fair: partly. Publishing the process is defensible; publishing stale and unflattering parts of it (a named site to imitate, three renames in a day, STATE.md "Total plans completed: 0", roadmap Phase 1 ticked with all seven plans unticked) hands the thread its quotes.
- Smallest change: cut. Keep DECISIONS.md, ROADMAP.md and the review findings; move HANDOFF.md and the per-task PLAN/SUMMARY files out of the default branch or into one `docs/history/` folder; fix the Befund line; rename the pandex directory; trim D24/D25/D27 to one entry.

## 2. Claims that overreach

| Quote | Where | Problem | Replacement |
|---|---|---|---|
| "Know what leaving Microsoft 365 would take" | site hero, title | The tool cannot tell any real organisation anything yet. | "A report format for deciding whether to leave Microsoft 365. Sample data today." |
| "For digital sovereignty in Germany, Austria and Switzerland" | site hero eyebrow | Slogan; reads as grant language. | "For public bodies and integrators in Germany, Austria and Switzerland" |
| "Find the blockers before the project does" | site section title | The tool finds nothing; the user enters the blockers. | "Write the blockers down before the project starts" |
| "Few can say exactly what they depend on." | site/index.html | Unverifiable generalisation. | Cut, or cite the Swiss study's finding directly. |
| "hundreds of business-critical macros" | site/index.html | Fazit does not scan macros and has deferred doing so. | "an assigned Teams Phone licence nobody planned for" |
| "0 network connections in the current version" | site stat tile | True only because there is no collection code. | Remove the tile. |
| "2 languages: German and English" | site stat tile | Filler presented as a metric. | Replace with "52 licence products and 1,343 service plans classified" if that count still holds. |
| "Private by design" | site section title | Marketing phrase; vacuous while nothing is collected. | "What stays on your computer" |
| "Fazit never writes to Microsoft 365 and keeps no tokens" | site tile "Read-only" | Present tense for unbuilt behaviour. | "The planned sign-in will be read-only and keep tokens in memory. Not built yet." |
| "Every safeguard has a test anyone can run." | site tile "Open to inspection" | Contradicted by SECURITY.md: host, endpoint and token safeguards are untested. | "Each safeguard that exists today has a test. Sign-in safeguards will get theirs with the code." |
| "Disconnect from the network and the demo still works." | site/index.html | Proves nothing about a program with no network code. | "The report opens with the network off and loads nothing external." |
| "What Fazit never does … Write to a Microsoft tenant" | site, README.md:79 | "Never" for a two-day-old alpha is a promise, not a property. | Head the list "Commitments" and add "enforced by test once the code exists". |
| "Invent figures" / "Invent results" | README.md:83, site | The demo's prices are labelled "Invented amount". | "Present an invented or missing figure as measured." |
| "Measured" (on simulated sample values) | sample report, home page finding | A chip saying Measured beside a made-up number. | In sample runs render the chip as "Measured (simulated)". |
| "AI-assisted, human-reviewed." | site, README.md:95 | 57k lines in 26 hours; PROJECT.md:71 says the founder cannot audit every line. | "Written with AI tools under one human maintainer, who cannot audit every line." |
| "signs off every change and is responsible for it" | site "Owned by" tile | Sign-off is a git trailer, not review. | "Decides what is built and answers for it." |
| "review the whole codebase independently … including security" | README.md:95, CONTRIBUTING.md | Model output described as an audit. | "Two other models are asked to find faults before a release; their findings are in the repository." |
| "both at maximum effort" | README.md:95 | Vendor setting as quality claim. | Cut. |
| "every change is tested before it is committed" | README.md:95 | Unverifiable; means "the suite ran". | "CI runs the suite on Linux, Windows and macOS." |
| "We work by the No AI Slop manifesto" | site/index.html:405 | Self-certification; invites a slop hunt. | Cut. |
| "checked against project documentation on 21 and 22 November 2026" | site coverage table note | Does not say who checked; 10 rows share one URL. | "Drafted from the linked documentation pages; not yet reviewed by someone who operates these suites." |
| "Fazit runs on Windows, macOS and Linux." | site/start | Supported by CI only; fine, but say so. | "CI runs it on Windows, macOS and Linux." |
| "Fazit will help you find those dependencies before the project starts" | site/index.html | Future promise in the problem statement. | "Local import is planned; today the report shows the format with sample data." |
| "Firms that complete an assessment will be eligible for a free listing." | site/index.html, integrators | A directory for a product that cannot assess. | Cut until import exists. |
| "Fazit is built to be translated" | site, CONTRIBUTING.md | Filler; the guide has six manual steps across code and YAML. | "Adding a language means one locale file and edits in the rule files; see the guide." |
| "A few minutes later the sample report is on your computer" | site "How it works" | The run takes under a second; the minutes are installing Git and uv. | "After installing Git and uv, the demo takes about a second." |
| "Made with [heart] in Germany" | site footer | Stock footer line. | Cut. |
| "It builds reports from bundled samples or a compatible `scan.json`" | README.md:7 | No documented format, no producer. | "It builds reports from two bundled samples. You can change the answers and costs." |

## 3. Remove or cut

- The text-scramble animation on the hero and 13 section headings (site.js `decode`, `data-scramble`). On a site whose pitch is sobriety for public administrations, glyph-scramble headings read as a template effect, and the public plan file says it was ported from another site. Also cut the staggered reveal on tiles.
- The four stat tiles. Three of the four numbers (2, 0, 3) are not achievements.
- The whole "How it is made" block with model names and "Max" badges, and the manifesto line. One disclosure sentence is enough.
- site/integrators/ and the "Public list of firms". An empty directory with listing criteria for a capability that does not exist.
- The pilots deadline ("until 28 February 2027") and "Founding pilots" naming. Scarcity framing for a free offer that cannot start until import ships. Keep a plain "Want to try it on real data when import lands? Email."
- The "Who it is for" cards written in the future tense ("you will be able to"). Three cards that each say "not yet".
- The roadmap timeline's five steps on the home page. Five future phases under a product with two commands makes the ratio of promise to code visible. Link to ROADMAP.md instead.
- The cal.com and LinkedIn icons in the footer. They signal sales; the email address suffices.
- Phases 1.1 to 1.3 from public copy (Copilot area, `fazit verify`, sovereignty criteria links). They are inserted ahead of the one feature the thread will ask for and look like scope creep before the core works.
- HANDOFF.md, the per-task .planning PLAN/SUMMARY files, .claude/CLAUDE.md, and the pandex-named directory, from the default branch (see comment 12).
- DECISIONS.md D24, D25 and D27 as three entries (Fazit, Befund, Fazit in one day), and the "Claude vs Codex analysis" heading. Keep the outcome, drop the theatre.
- "Licences" as a readiness area with a status.
- "Download (HTML, 290 KB)" next to "Open the sample report". Two buttons for one file.
- The home page's present-tense "What Fazit never does" list as a hero-level section; fold it into the security page under "commitments".

## 4. Missing before launch

- A way to use it on your own tenant. Without `import`, there is nothing to try beyond a sample.
- A release: git tag, PyPI package, `uvx fazit demo`, wheel checksum on a GitHub release. Signing can wait; a tag cannot.
- A terminal recording or plain-text transcript of the CLI on the start page. The site shows no CLI output at all.
- A screenshot of the report above the fold that is legible, plus one of the cost table. The hero image links to the report but HN readers decide from the image.
- `docs/scan-format.md` and a note on stability of `schema_version` 1.0.
- A limitations section, in one place, in the README: no collection, no file or macro scan ever planned in v1, status rules are shallow, mappings unreviewed by operators, cost model is user-supplied arithmetic, samples are 85 and 20 people while the target is 200 to 2,000.
- A threat model for the planned sign-in: who registers the Entra app, which delegated scopes, which Graph endpoints are on the allowlist, how the allowlist is enforced, what a malicious `scan.json` or `inputs.yaml` can do to the report (HTML injection through organisation and application names is the obvious question; the tests reject `@` and control characters, say what else).
- Comparison with what exists. PROJECT.md already names Google's migration-planner, Plan EU's macro scan, ShareGate and Microsoft's own inventories; the site and README name none. Add four lines.
- The business model in one sentence on the site.
- Who the maintainer is, in two sentences: background, and whether they have ever run an M365 migration. The thread will ask; if the answer is no, say so and say who reviewed the rules.
- A named domain reviewer for the status rules and mappings.
- A sample where the answer is "do not move yet" with a higher exit cost, since S4 says the report must be useful for "not yet".
- A sample at the size of the stated audience (for example 600 seats).
- The GitHub repository made public with issues enabled, and the "Phase 1 reviews" link checked. I could not confirm either from here.
- A plain statement of what the German text quality rests on (native review or not), since German readers will check.

## 5. Launch timing

Do not post now. The project is 26 hours of commits old, has no release, and cannot assess a real tenant; the thread would be about AI-written vapourware and the model list rather than about leaving Microsoft 365, and a Show HN gets one clean shot. The minimum that changes the conversation is Phase 2: `fazit import` turning real admin-centre CSV exports into a report, proven on at least one real tenant (the maintainer's own or a pilot's, described in aggregate), published as a tagged PyPI release runnable with `uvx`, with the mappings and status rules read by one named person who operates openDesk or Nextcloud, and with the home page cut to what exists. Skip phases 1.1 to 1.3 to get there sooner. If the Prototype Fund deadline of 30 November is driving the date, keep the two apart: the application does not need an HN thread, and a bad thread is a permanent search result under the project's name. If a post before import is unavoidable, post the sample report and the evidence model as a request for critique from people who have done such migrations, title it as a format rather than a tool, and remove everything listed in section 3 first.

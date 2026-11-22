# Launch critique: what both reviewers found

On 2026-11-22, Claude Fable 5.2 and Codex GPT-6.2-Astra each read the site and repository as sceptical Hacker News readers, independently ([brief](BRIEF.md), [Fable](CRITIC-fable.md), [Astra](CRITIC-astra.md)). Both say: do not announce before local import and a release (already the launch gate in phase 2.1). This file sorts their findings by who acts on them. "Both" means both reviewers raised it.

## A. Honest wording and small fixes (site, README, repository)

1. **Present-tense claims about unbuilt code (both).** "Every safeguard has a test", "keeps no tokens", "never writes to Microsoft 365" and "0 network connections" describe sign-in code that does not exist. Split into "true today" and "planned for sign-in".
2. **Review claims (both).** "Signs off every change", "human-reviewed", "every change is tested before it is committed" and "at maximum effort" overstate what happens; PROJECT.md says the maintainer cannot audit every line. Say who directs the work and point to the public review records.
3. **Sample data labelled "Measured" (both).** Simulated figures carry the same label as real ones, and Astra reproduced the README walkthrough putting a real organisation name above the fictional town's measured inventory.
4. **The macro example (both).** "Hundreds of business-critical macros" is a typed-in count; Fazit does not scan files. Use an example the tool can measure.
5. **Start command fails in Windows PowerShell 5.1 (Astra).** `&&` needs PowerShell 7. Show three separate commands.
6. **Pilots and integrators (both).** Say pilots start after import; take the empty integrator directory out of the navigation until a firm is listed.
7. **Business model (both).** One plain sentence: the tool is free and complete; the maintainer plans to earn from assessments and support.
8. **Privacy page (Astra).** "Does not use browser storage" next to cache headers; Bunny settings to be confirmed from the account once it exists.
9. **README is stale (both).** Packaging is now phase 2.1; the rules directory is deferred; "a compatible `scan.json`" has no documented format; "footer" listed as a report feature.
10. **Repository leftovers (Fable).** HANDOFF.md still says "now called Befund"; a plan folder is named after another site; CONTRIBUTING asks human-only patches to credit both models.
11. **Limits and comparison (both).** One page that says what comes from an export, what someone must answer, what stays Unknown, and how Fazit compares with admin-centre exports plus a spreadsheet, Google's Migration Planner and Plan EU's macro scan.

## B. Decisions for the founder

1. **Model roster, "Max" labels and the No AI Slop link (both: cut to one disclosure sentence).**
2. **Heading scramble and staggered reveals (both: cut).**
3. **"Made with ♥ in Germany" (both: cut).**
4. **Hero (both).** "Know what leaving Microsoft 365 would take" promises an assessment the tool cannot run on real data yet; "For digital sovereignty" reads as campaign language. Both suggest naming the audience instead.
5. **Home page repetition (Astra).** Private by design, four safeguard tiles, What Fazit never does and Check it yourself make one argument four times.
6. **Roadmap order (both).** Import before phases 1.1 to 1.3 (Copilot, `fazit verify`, sovereignty criteria), so the core works first.
7. **The word "Ready" (both).** It means "the current checks passed", not "ready to move". Rename or define it next to the legend.

## C. Rules and report (Codex)

1. **Readiness ignores the target (Astra).** All fifteen statuses are the same for openDesk, Nextcloud and the generic profile; the evaluator receives no target.
2. **Shallow rules (both).** Teams is Ready because teams were counted; Licences has a readiness status; only telephony can produce a Blocker.
3. **Contradiction checks miss a simple case (Astra).** 10 devices with 20 of them on Windows passes.
4. **`.xls` is missing from the risky file types (Astra).**
5. **Mappings (both).** The openDesk file has no XWiki, CryptPad or Notes; 10 of 19 rows cite one page; "Not available" should read "Direct transfer undocumented" where only the method is undocumented; SharePoint workflows and VBA need interview fields.
6. **Windows desktop inference (Astra).** Two Windows-only applications turn "desktops needed" into Yes, although they could run on a remote Windows host.
7. **Report lists (Astra).** "Unknowns to resolve first" omits open evidence inside Needs work areas; next steps point to an import that does not exist yet; the stock "how a move proceeds" steps appear even with an open blocker.
8. **The sample's result (both).** The only public report shows leaving saving EUR 135,650 on invented prices. Show the break-even assumption, or leave one material input empty.
9. **Missing pieces.** `docs/scan-format.md`; a sample at the target size (about 600 seats); a short threat model; a CLI transcript on the start page.

## D. Founder actions

- One person who runs openDesk or Nextcloud reviews the mappings and status rules, named with the date in the files.
- One operator in the 200 to 2,000 range runs the import unaided before the launch.

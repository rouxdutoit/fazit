# Apple lens: site and report, section by section

2026-11-22. One question per section: is this the best thing to show here, and what would Apple do? Apple's structure, as `DESIGN.md` adopts it, means one thing to look at first, the conclusion before the evidence, headings that say what the reader gains, and no meta labels.

**Scope.** The website as it stands in the working tree today (`site/index.html`, `start`, `security`, `pilots`, `integrators`, `privacy`, and the German twins), and the report as specified in `.planning/report-redesign/UI-SPEC.md` revision 4. Other sessions are editing the footer and the About page right now, so neither is reviewed here. Nothing in `site/`, the spec or the code was changed.

**Fixed points this review does not reopen:** D1 and D20 (no score, no verdict), founder decision C3 (no part-of-whole picture in the summary), C13 (keep "Blocker" / "Hindernis"), and the `DESIGN.md` rules. Where a change touches one of them, it is marked as a founder decision.

## The short answer

1. **Change the homepage example from Telephony to Mail** (section 1 below). Mail is Needs work, the status of 9 of the 14 assessed areas. Its one card shows all three kinds of evidence, Measured, Provided and Unknown, plus "Evidence still needed" and, once RR-01 lands, a next step. Its target line is good news ("in the suite" on openDesk). Telephony is the one area a current rule can call a Blocker (launch critique C2), so the homepage spends its only example on the rarest outcome, shown without a next step.
2. **Retitle that section by what the reader gains.** "One finding in full" names the exhibit, not the benefit. Recommended: "Evidence and a next step for every area" / "Nachweise und nächster Schritt für jeden Bereich" (*draft*). Drop the rhetorical question in the intro, which `DESIGN.md` forbids.
3. **The homepage must change in step with the redesign.** It describes the old report in four places: the hero screenshot shows the readiness bar and a Ready Licences row, "15 areas" becomes 14 assessed areas once Licences loses its status (C2), the tally lists statuses Ready first, and "What you get" lists the nine old sections, including "Suggested path", which the redesign removes. Ship these with RR-02 to RR-04, not afterwards.
4. **The homepage tells one argument several times and buries the product.** Thirteen sections; the privacy case appears as four tiles, a "never" list and "Check it yourself", and again on the security page (launch critique B5, still open). Apple would show the product early and once, then give the proof. A proposed order is in section 2.
5. **In the report, two changes give the most for little cost.** Merge the count line and the status definitions into one list, so each status, its count and its meaning sit together once. Inside the area groups, make the area name the card's anchor, not the status, because the group heading already states the status. Details in section 4.
6. **One spec copy bug:** the German `readiness.evidence_summary` says "gemessen, angegeben", but the report labels provenance "Erhoben" and "Bereitgestellt" (`src/fazit/locales/de.yaml`, `provenance`). Same thing, same word.

## 1. The homepage example (`site/index.html#example`)

**Job today.** Proves to a sceptical IT lead or integrator that a finding is traceable: status, reason, three evidence rows with source and date, the target's coverage. It also bridges from "Find the blockers before the project does" to the product.

**Why it reads as negative.** The words are not the problem; the context is. The intro opens with a question the card answers "no" to ("Can the town give up Teams Phone?"). The only colour on the page below the hero is the Blocker orange. The card ends on "not in the suite and needs a separate provider", with no next step, so the reader's last impression is a dead end. And the tally underneath ("4 Ready, 9 Needs work, 1 Blocker, 1 Unknown") makes it plain that the page chose the one exception.

**Does it earn its place?** The section does: it is the only place on the homepage where a visitor sees what Fazit actually says. The choice of finding does not.

**What Apple would do.** Show the product doing its everyday job well, with the conclusion first and the benefit in the heading. Apple's feature sections show the typical case at its best, not the edge case. For Fazit, the typical case is Needs work with a gap in the evidence, and its best is that the report says so honestly and says what to do next.

### Candidates

| Finding | Status | What it demonstrates | Weakness |
|---|---|---|---|
| **Mail** (recommended) | Needs work, Evidence incomplete | Measured (91 mailboxes, with reporting period), Provided (other systems send mail), Unknown (shared mailboxes, with reason and fix) in one card; "Evidence still needed"; target line in the suite on openDesk and with limits on Nextcloud; the RR-01 example next step is the Mail one | Busier card: four evidence records in the report; the homepage shows three |
| Directory | Needs work | Two measured counts, complete coverage; a plain `decide` step about guest access, clearly worth doing even if the town stays | No Unknown, so it hides Fazit's most distinctive behaviour |
| Telephony with its next step | Blocker | Strongest story ("a Teams Phone licence no project plan mentions") | Rarest status; the story is already told in the "Find the blockers" section above, so showing it twice spends both moments on the same edge case |
| Power Platform | Needs work | Measured licence plus a provided answer | Relevant only to some readers |

Every organisation has mail, every reader understands it, and the card shows the Unknown honesty that is Fazit's core value. The Telephony hook stays where it already is, in "Find the blockers before the project does", as a sentence.

### The smallest concrete change

Two steps, so the site never shows what the shipped sample does not.

**Now (before RR-01 lands):**

- Heading: "Evidence and a next step for every area" / "Nachweise und nächster Schritt für jeden Bereich" (*draft*). Until the next step ships, use "Every area shows its evidence" / "Jeder Bereich mit seinen Nachweisen" (*draft*), so the heading does not promise what the card lacks. Alternatives if the founder prefers: "See why each area has its status" / "Warum jeder Bereich seinen Status hat"; "Know what to do next in each area" (only once next steps ship; it echoes the h1).
- Intro, replacing the rhetorical question: "Each area shows its status, the evidence behind it and what is still missing. This one is Mail, from the sample report for a fictional town; its measurements are simulated." German, for native review: "Jeder Bereich zeigt seinen Status, die Nachweise dazu und was noch fehlt. Hier der Bereich E-Mail aus dem Beispielbericht einer fiktiven Stadtverwaltung; die Messwerte sind simuliert."
- Card: the Mail card copied from the regenerated demo, not hand-written: area, status (Needs work symbol and word), the "Evidence incomplete" marker, the reason ("Other systems send mail through Microsoft and will need another way to send it."), "Evidence still needed: Shared mailboxes" with its fix, then three evidence rows: Mailboxes 91 (Simulated … reporting period 6 May to 1 November 2026, complete), Other systems send mail through Microsoft Yes (Provided …), Shared mailboxes shown as the Unknown status label, never blank. Target line from `mappings/opendesk.yaml`: on openDesk, mail and calendar are in the suite (Open-Xchange), checked 21 November 2026.
- Tally in the report's display order and wording: "Of 15 areas in the sample: Blocker 1, Needs work 9, Unknown 1, Ready 4", with status symbols, as the report's count line. It becomes "Of 14 areas … Ready 3" in the same commit that regenerates the demo after RR-01's Licences change.
- Link: "Open the readiness section" names a section, not a benefit. Use "See all areas in the sample report" / "Alle Bereiche im Beispielbericht ansehen".

**When RR-01 and RR-02 land:** copy the redesigned card in full, including category ("Mail · Communication") and "Next step" with the RR-01 sentence, drafted in the plan as "The IT team lists every system that sends mail through the organisation's account and plans a new sending route for each." / "Die IT-Abteilung erfasst alle Systeme, die über das Konto der Organisation E-Mails versenden, und plant für jedes einen neuen Versandweg." Swap the heading to the "next step" version. If RR-01 classifies that step as `clarify`, one sentence after the card may say it is among the steps the report lists as worth doing even if the town stays. That is the positive frame the founder wants, and it is true of the report rather than a claim about it.

**Cost.** `site/index.html` and `site/de/index.html`, and `site/check_site.py`: `check_tally` (around line 456) builds the expected tally from the demo report, in `STATUSES` order with the prefix "All {} areas in the sample" / "Alle {} Bereiche im Beispiel", so the new wording and display order need a matching change there. The checker does not assert the Telephony card's text. No locale, rule or report test change. Native German review for the new strings.

### "Blocker" itself

The name stays: the founder confirmed "Blocker" / "Hindernis" on 2026-11-22 (decision 13 in `.planning/research/report-usefulness/SYNTHESIS.md`). The negative feel is answered by framing, and this review's changes all work that way: a benefit-led heading, a typical Needs work card in place of the lone Blocker, the card's next step, the scoped "What blocks this move" in the report, and the "Worth doing even if you stay" group. The homepage problem above is one of context, and the change above fixes it without touching the word.

## 2. Homepage, section by section

A proposed order follows the table. Each row's smallest change can ship on its own.

| Section | Job, for whom | Earns its place? | What Apple would put here | Smallest change |
|---|---|---|---|---|
| **Hero** (eyebrow, h1, sub, two buttons, status line) | Tells an IT lead or integrator in DACH what Fazit does and that it is sample-only today | Yes. The h1 is a benefit statement; the status line keeps it honest (launch critique A1, B4) | The same: name, one-line benefit, one main action | None. "What you rely on, what needs work and what it would cost" is a stacked triad; acceptable because it lists the report's three answers, but watch it |
| **Report preview** (screenshot) | Shows the product | Yes, it is the one thing to look at first | The product's best screen. Today it shows the readiness bar (the part-of-whole picture C3 removed from the summary), Ready listed first, and Licences as a Ready row, which C2 removes | After RR-02 to RR-04, replace the four images with page one of the redesigned report: the count line with definitions, "What blocks this move", "What is still unknown", the three totals. Update `og.png` and the alt text the same way |
| **Figures strip** (15 / 2 / 1 / 3) | Quick facts | Partly. "15 areas" and "3 targets" inform; "2 languages" and "1 file" are details the hero already implies | Apple uses big numbers for benefits a buyer would quote. Two would do | Keep areas and targets; fold languages and offline into one line under the preview. "15 areas" must become 14 assessed areas when Licences loses its status, and 15 again when Copilot ships in 1.1 |
| **Find the blockers before the project does** (`#why`) | Motivation for the decider | Yes. Clear benefit heading; Telephony as the hook belongs here | Same | None. It keeps the Telephony story once the example moves to Mail |
| **What stays on your computer** (`#privacy`) | Reassures the IT lead and the data protection officer | Yes, but it says the same thing four ways: intro, four tiles, a "never" list, "Check it yourself" (launch critique B5) | One statement, three proof points, one link to the full page | Keep intro, the "never" list and "Check it yourself"; drop the four tiles (each repeats a "never" line) or keep the tiles and drop the list. Founder's choice which |
| **One finding in full** (`#example`) | See section 1 | | | Section 1 |
| **What you get** (`#report`) | Tells the reader what the report contains | Yes, but it lists the nine old sections; "What we found" and "Suggested path" disappear in the redesign, and "Report details" is a label | Apple lists what the buyer can do with it, in the product's own order | Rewrite against UI-SPEC §1 order once RR-02 lands: Summary for the council (one printed page), What to do next (worth doing even if you stay; needed for a move), Where each area stands, Costs over five years, What replaces what, What needs a closer look, How the report was made. Heading "What you get" is fine; German "Was der Bericht enthält" is fine |
| **What the targets cover** (`#coverage`) | Integrators comparing openDesk and Nextcloud | It informs, but a 13-row, two-column table is the heaviest block on the page and partly answers a different question (what the suites cover, not what the organisation needs) | Apple moves comparison tables to a "Compare" page and links to it from the homepage | Move the table to its own page or to the integrators page, keep a two-line summary and a link here. The note that mappings are not yet operator-reviewed must travel with the table, and `site/check_site.py` (which checks every coverage cell against the mapping files) must follow it to the new page |
| **Who it is for** (`#audience`) | Self-selection | Weak. The eyebrow already names the audience; two of three tiles are future tense | Apple rarely has a "who it's for" section; the audience shows in the examples | Cut, or fold the IT-lead line ("Run the demo without a Microsoft account …") into "How it works" |
| **How it works** (`#how`) | Gets the reader to the start page | Yes, it is the main action | Three numbered steps or the three commands, then the button | Show the three commands from the start page here, as Apple shows the product in use; keep the link |
| **Reading the findings** (`#claims`) | Explains provenance and the no-verdict rule | Its content matters, but after the Mail card it repeats what the card shows | Put the explanation next to the example it explains | Merge its last paragraph (Fazit cannot establish that an inventory is true) into the example section as a note under the card; drop the rest |
| **Sources** (`#sources`) | Credibility for public-sector readers | Yes, but separated from the table it supports | Footnotes next to the claim | Move with the coverage table |
| **Free and open source** (`#free`) | Licence and business model; links to pilots, integrators, security | Yes for the licence sentence; the three cards repeat the bar's navigation | One statement and one link | Keep the statement and the Pilots card (it is the only call to action for an organisation); drop the other two cards |
| **Project status** (`#status`) | Honest roadmap | Yes. It is the most trust-building section for a sceptical reader | Apple would not show a roadmap; Fazit must, because it ships before import | Keep. "Now" and "Next" carry the weight; collapse "Then", "After that", "Later" into one "Later" row |
| **How it is made** (`#development`) | AI disclosure | Needed somewhere | The About page, which another session is writing and which already has "Wie Fazit entsteht" | Once the About page ships, keep one sentence and a link here, or move it entirely. Do not change it before the About session finishes |

**Proposed order.** Hero; report preview; Find the blockers before the project does; the example (Mail) with the reading note; What you get; What stays on your computer; Project status; How it works (with commands); Free and open source (with Pilots). Coverage and Sources move to their own page. Who it is for and How it is made fold into other sections or the About page. That is nine sections instead of thirteen, and the product appears three times before the privacy case.

## 3. Other site pages

**Get started (`/start/`).** The best page on the site by this lens: the h1 is the action, the three commands come first, then what you need, then what happens. One issue: "Next" is a label, and its three cards repeat the bar. Apple ends a how-to page with the one next thing. Smallest change: retitle "Next" as "See the result without installing" and keep only the sample report card; the other two are in the bar. The "With your own data" section is honest and should stay.

**Security and privacy (`/security/`).** Its job is to let a data protection officer or a sceptical admin verify claims. The h1 is a label, which is acceptable for a reference page, and the intro states the conclusion. "Principles" is a label: Apple would write "What Fazit does and does not do" and lead with the two that hold today (offline report, no network code) before the six that describe planned sign-in. Smallest change: sort the eight tiles into "True today" and "Planned for sign-in" (launch critique A1 in structure, not only in wording), and rename "Principles" to "What is true today and what is planned". "Limits of the evidence" is the most honest section on the site and should stay as it is.

**Pilots (`/pilots/`).** Clear and short; the h1 states the offer, the deadline sits in the intro. "Contact" is a label; Apple would make the last section the action: "Express interest" with the email and what to include. Smallest change: retitle "Contact" to "Express interest" (German "Interesse bekunden", *draft*), matching the button in the intro. "What you receive" should name the redesigned report's page one for the council once it exists, because that is what a public body's approval process wants to see.

**Integrators (`/integrators/`).** The page's main content is a list with no entries. Apple would not publish an empty list. Launch critique A6 took it out of the navigation; the page itself still leads with it in two of three sections. Smallest change: lead with what an integrator can do with the report (the open-points list grouped by evidence, the owner roles, the CSV planned for 1.2), and shrink the list to one sentence with the listing criteria. If the coverage table moves off the homepage, this is a good home for it.

**Privacy (`/privacy/`).** A legal page; the summary list at the top (Cookies: None, and so on) already gives the conclusion first, which is exactly Apple's privacy-page pattern. No change.

**German pages.** Same structure, and the headings read as German rather than translated. Two points: "Ein Befund im Detail" carries the same meta-label problem as the English; and the home page's "Möglicher Ablauf" (the old "Suggested path") disappears with the redesign. The provenance words on the home page ("Bereitgestellt", "erhoben") match the current report and should stay; it is the spec that needs fixing (section 5).

## 4. The report (UI-SPEC revision 4), section by section

The spec already does most of what Apple would: findings first, no verdict, page one for the council, a next step on every card. The points below are refinements.

**Header (§1.1).** Organisation as eyebrow, h1 "What leaving Microsoft 365 would take", one meta row, the sample note. Earns its place; the h1 matches the site. No change.

**Count line and status definitions (§1.2 items 1 and 2).** Job: the conclusion for the council, and a page one that explains its own words. Both earn their place, but together they show each status name twice in a row: once with its count, once with its definition. Apple would show each item once with everything the reader needs. Smallest change: one `dl` of four rows in display order, each row the symbol, status name and count at `--fs-lead`, then the definition at `--fs-footnote` in `--fg-2` on the same row (wrapping under it at 360 px). It keeps "Of {n} areas:" as the introduction, removes one block from page one and makes acceptance criterion 2 (first blocker row visible at 1280 × 800) easier to meet. It is still a count, not a part-of-whole picture, so C3 holds.

**What the target covers (item 3, after RR-07).** Job: says how much of what the organisation uses the target replaces, by name. It earns its place. But placed third, it pushes "What blocks this move" down, and acceptance criterion 2 was written before the scope statement existed. Smallest change: move it after "What is still unknown" and before the cost tiles, which also fits the council's question order (what stops it, what is open, then what a move would take and cost). Re-check criterion 2 when RR-07 lands.

**What blocks this move (item 4).** Conclusion-first heading, scoped to this move (C8). One meta line: "Confirmed blockers: 1 of 1". When nothing is cut off, "{shown} of {total}" is meta that tells the reader nothing. Smallest change: show the line only when total exceeds shown; keep "All blockers" when total is at least one. The zero-blocker sentence with its caveat is right and should stay exactly as specified.

**What is still unknown (item 5).** Good. Placing it before the costs is the honest choice. No change.

**Cost tiles (item 6).** Three totals, Stay first, with origin, then the Stay assumption and the break-even line. These will be the loudest thing on page one; a council reads the money first whatever the layout does. That is acceptable because the tiles say where every figure came from and the unknowns sit above them. One wording point: the Stay tile's main line "Today's yearly costs for five years" repeats the assumption sentence under the tiles almost word for word. Smallest change: keep the main line, and cut the first clause of the note so the note carries only "with no price change" and the break-even lines. Copy change only.

**Decision window (item 7, Phase 1.1).** Good; dates a council can act on. No change.

**What to do next (`path`, §4.1).** This is the positive reframe the founder asked for and it works. One ordering point: group one, "Worth doing even if you stay", opens with the open points (exports and answers still missing), then the clarify and decide steps. A reader who expects things worth doing meets a list of missing evidence first. Apple leads with the benefit. Smallest change: inside group one, list the clarify and decide steps first, then the open points under their own small heading ("Evidence still needed", reusing the card's label), keeping `#not-examined` on that subheading so the summary's link still lands on it. No new hook; the order assertion in the tests needs updating.

**Where each area stands (§2): readiness bar.** It now sits above the filter as the filter's visual (C3). It repeats the counts the status pills already show, and it is still a part-of-whole picture of areas, one screen below page one. Apple's segmented controls carry no extra chart. Founder decision, low priority: drop the bar (cost: `data-segment` hooks and permitted test edit 4, the CSS, the site screenshot) or keep it as decided. This review would drop it, but it is not worth delaying the build for.

**Filters (§2.2).** An Apple segmented control above a list is the right pattern. The search hint is an instruction about the browser; its useful part is the warning. Smallest change: shorten to "Filtered-out areas and, in some browsers, closed sections are not searched." / "Ausgeblendete Bereiche und, je nach Browser, geschlossene Abschnitte werden nicht durchsucht."

**Area cards (§2.3).** The best part of the spec. One structural point: inside a status group, every card repeats the group's status as its anchor at `--fs-headline`, so the Needs work group shows the same large label nine times and the area names, which the reader scans for, are smaller. Apple's grouped lists make the item the title and its state secondary. Smallest change: inside `.areas`, use the compact Ready treatment for all cards: area name as the anchor, status (symbol and word) at `--fs-body` on the line under it. The status stays on every card, so a linked or printed card still states it. This is exception 6 in §6.2 widened from Ready to all cards. The homepage example, shown alone, keeps the status as its anchor.

**Costs (§3).** Good heading, one scale, Unknown never zero, break-even on a named input. No change.

**What replaces what (`moves`).** Benefit-neutral heading, which is right for a reference table. No change.

**What needs a closer look (`attention`).** Fine. No change.

**Recorded inventory (`found`).** A label, not a statement. Smallest change: "What Fazit recorded" / "Was Fazit erfasst hat" (*draft*). Low priority.

**How this report was made (`appendix`).** Good, and "What Fazit does not look at" is exactly the kind of honest limit Apple would state plainly. No change.

**Navigation (§5).** Seven links is two more than Apple's local navs usually hold, but each maps to a section a professional reader jumps to. No change.

## 5. Copy and consistency bugs

1. **German provenance words in the spec.** UI-SPEC §8 `readiness.evidence_summary` German: "{measured} gemessen, {provided} angegeben, {unknown} unbekannt". The report's provenance labels are "Erhoben" and "Bereitgestellt" (`src/fazit/locales/de.yaml`), and the site uses the same. Change the spec string to "{measured} erhoben, {provided} bereitgestellt, {unknown} unbekannt" before RR-01 writes it. `DESIGN.md`: same word for the same thing.
2. **Status order on the site.** The homepage tally, the hero screenshot's legend and its alt text list Ready first; the report's display order is Blocker, Needs work, Unknown, Ready (UI-SPEC §1). Align with the redesign.
3. **Area count.** The tally is checked against the demo report, so it cannot drift. The other mentions are not: "15 areas in every report" in the figures strip and "readiness across 15 areas" on `/pilots/` (both languages) become 14 assessed areas when RR-01 removes Licences' status, and 15 again with Copilot in 1.1. Change them in the commit that regenerates the demo, or add them to the checker.
4. **Rhetorical question.** "Can the town give up Teams Phone?" / "Kann die Stadt auf Teams Phone verzichten?" breaks the `DESIGN.md` copy rule. Fixed by section 1.

## 6. For the founder

Nothing here needs a decision before the build except these two, both optional:

1. **Homepage example.** Approve Mail in place of Telephony, and the heading. Recommended: yes, in two steps as in section 1.
2. **Readiness bar above the filters.** Keep (as C3 decided) or drop. Recommended: drop, when convenient.

Everything else is a copy or order change inside the existing decisions, and can go into the relevant RR plan or a site task once the sessions editing `site/` have finished.

## Not covered

The About page, the footer and the legal notice (being edited by other sessions); the sample report pages under `site/demo/` (they are generated); the README. No real reader was asked; the "one real reader before RR-02" step in the spec remains the better test of page one than any review.

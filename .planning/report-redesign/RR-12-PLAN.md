---
plan: RR-12
title: Home page cut to Apple's landing-page shape
depends_on: ["RR-11"]
autonomous: true
---

# RR-12: the home page gets the gist across; detail moves one click away

Founder decision (2026-11-23): the home page has about 1,160 words in seven sections. A visitor should get the gist from the home page and click through for more. Model: how Apple would build a "Switch from Windows to Mac" page. Each section makes one claim: a short headline, one sentence, one visual that proves it, and a standalone "›" link to the detail. Target: 200 to 250 words in `main` on `site/index.html`, and the same in German on `site/de/index.html`.

## Read first
`AGENTS.md`, `DESIGN.md` (binding), `.planning/report-redesign/RR-08-PLAN.md` and its summary (the current home page), and the RR-09 to RR-11 summaries (the final report components).

## New home page, in order
1. **Hero:** the eyebrow shrinks to Apple length and names no audience, because Fazit serves companies as well as public bodies: EN "Free and open source", DE "Kostenlos und quelloffen". The home page names no single audience anywhere; public bodies stay the focus on the Pilots, Integrators and About pages. Integrators keep their navigation link; the region (Germany, Austria, Switzerland) moves to the closing band's facts line. The closing band then must not repeat "Free and open source"; it starts with "Sample data today; …". Otherwise unchanged: headline, one-line subhead, "Get started" (solid) and "View sample report" (secondary), the status note and the report image. Drop the caption under the image except the two links ("Open the sample report ›", "Download HTML, … KB ›"); the facts line moves to section 7.
2. **"Know what you rely on."** One sentence: Fazit sorts 14 areas into Blocker, Needs work, Unknown and Ready, each from evidence. Visual: the report's status list component, rendered from the demo. Link: "See the sample report ›".
3. **"Every finding shows its evidence."** One sentence: missing evidence stays "Unknown", never a guess. Visual: the Mail card (as today, the report's card component). Link: "See all areas ›" to `/demo/en/#readiness-title`.
4. **"See what it would cost."** One sentence: staying, a partial move and a full move over five years, from the costs you enter. Visual: the report's three cost tiles, rendered from the demo. Link: "How costs are calculated ›" to the report's cost section.
5. **"Nothing leaves your computer."** One sentence. Visual: three icon facts in a row (symbol and a two- or three-word label, one short line under each): *Runs locally*, *Read-only*, *Open source*. Link: "How Fazit handles data ›" to the Security page.
6. **"Try it in three commands."** The command component as today, with no paragraph before it except one short line ("Needs Git and uv."). Link: "Get started ›".
7. **Closing band:** one line, "Free and open source. Sample data today; import of your own exports comes next." with links "Pilot assessments ›" and "About Fazit ›". Then the facts line: "14 areas, three targets, English and German, one file that opens offline."

Section headings sit in the left column as today (the site's `.sec grid`); each section body is one sentence plus its visual and link. No section has a second paragraph.

## Where the removed copy goes (nothing is lost)
- **"Find the blockers before the project does"** (sovereignty context, telephony example, "no overall score, no supplier"): the About page, in "Where it started" or a short new section "What Fazit is for". Keep "It gives no overall score and recommends no supplier." It may also be the closing line of section 2 if it fits in one sentence.
- **"What you get" cards:** removed; the sample report shows the sections. Keep the coverage comparison link: it becomes a link in section 4 or 5's area ("Compare openDesk and Nextcloud ›") if it fits; otherwise in the footer under Project.
- **"What Fazit will never do" list and "Check it yourself":** move to the Security page, at the top, unchanged in substance.
- **"Project status" timeline:** move to a new page `site/roadmap/index.html` and `site/de/roadmap/index.html` ("Roadmap" / "Fahrplan"), same component and copy; add it to the footer's Project column and the sitemap. The translation-guide footnote moves with it.
- **"Free and open source"** essay and "Claude and Codex write the code…": the About page's "Why it is free" / "How it is made" already cover this; merge anything missing there. The founding pilots card moves to the Pilots page if not already there.

## Rules
- DESIGN.md binds: monochrome controls, colour only for status, every button leads with a symbol, standalone links end in a chevron, no forced line breaks, `hyphens: manual`.
- Copy: plain, specific, no marketing adjectives; native, formal German written from the meaning, not translated word by word. Read the area count and the status counts from the demo report as the checker requires.
- Visuals are live HTML components shared with the report, not screenshots, except the hero image.
- `site/check_site.py`: update its home page checks to the new structure, keep its link, count and asset checks, and check the new roadmap pages. Never weaken a safeguard.
- Keep code lean: delete CSS that only the removed sections used.

## Verify
- `uv run pytest -q`, `uv run ruff check .`, `uv run ruff format --check .`, `uv run python site/check_site.py` pass.
- Word count of `main` on both home pages reported in the summary (target 200 to 250).
- Screenshots at 1280 × 800 and 360 × 800, light and dark, EN and DE, into `.shots/report-redesign/rr12/`, full page. No horizontal scroll, no visible scrollbar.

## Summary
Write `.planning/report-redesign/RR-12-SUMMARY.md`: the new structure, the word counts before and after, where each removed piece went, files changed, deviations, and a native-review table of new German strings.

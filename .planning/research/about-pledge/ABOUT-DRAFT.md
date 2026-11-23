# About page: draft copy for approval

Drafted on 2026-11-22. English only. Nothing in `site/` has changed. German follows once the English is approved, and gets a native review before release.

## Decisions so far

- An About page on fazit.dev, linked from the footer only.
- No pledge, no badge, no movement page. People join through the work.
- The No AI Slop manifesto is an internal guideline and stays off the site.
- The post that prompted Fazit is Jordan Krueger, "We don't need more apps. We need better open source." (17 November 2026). Fazit's first commit is dated 21 November 2026.

## What I took from the founder's Medium writing

- One idea per sentence. Short lines. Plain words.
- Says what a thing is not, then what it is ("It does not mean doing nothing. It means…").
- First person, concrete, ends on something that can be done.
- Recurring ideas that fit Fazit: enough already exists; no performing for an audience; what is shared belongs to everyone.

What stays out, because DESIGN.md or the audience rules it out: rhetorical questions, stacked lists for rhythm, swearing, and the political pieces. The page does not link the Medium profile.

## The copy

Structure follows `site/pilots/index.html`: an intro, then sections with a label on the left and the text on the right.

---

**Page title:** About Fazit

### Intro

# Enough open source exists. Fazit helps you reach it.

Fazit is made by Ruan "Roux" du Toit in Feldkirchen, near Munich. I started it in November 2026, four days after reading one blog post.

### Where it started

Jordan Krueger wrote that [we do not need more apps, we need better open source](https://jordankrueger.com/blog/better-open-source-not-more-apps/). Krueger asked people who build with AI to stop adding new things and help the tools others already rely on.

I had spent too long building products because a language model made them easy to build. Nobody needed them. The post said what I already knew.

Fazit is a new tool, so it does not follow that advice to the letter. It replaces nothing. openDesk, Nextcloud and LibreOffice already exist. What was missing was a way for an organisation to see, in its own numbers, what moving to them would take.

### Why it is free

The organisations that most need these numbers are public bodies. The public pays for their software, so the public should be able to read the tool that measures it.

Fazit is free and open source under AGPL-3.0-or-later. All features and rules are in the repository. Anyone may use, change and share it. Anyone who passes on a changed version shares the changes too.

I believe machines should serve all of us. This is my part of that.

### What you can check

Each of these is a statement you can test, not a promise to take on trust.

- **Open.** The whole tool and its rules are public. [Read the licence](https://github.com/rouxdutoit/fazit/blob/main/LICENSE)
- **Local.** Today's version runs on your computer and contains no network code. [How Fazit handles data](/security/)
- **Unknown stays unknown.** A missing figure is shown as missing, with the reason and a next step. [See it in the sample report](/demo/en/)
- **No tracking.** This site sets no cookies and loads nothing from other servers. [Privacy](/privacy/)
- **Not finished.** Today Fazit runs on sample data. Import of real exports and a first release come next. [Project status](/#status)

### How it is made

I design Fazit: what it does, how it is structured and what counts as correct. I answer for what ships.

Claude and Codex write the code. I work with them as I would with a team. We settle the architecture together, they write and test, and before each release other models read the whole codebase cold and look for faults.

I do not write the code and I do not read every line. I check the review findings, which are public. [Read the reviews](https://github.com/rouxdutoit/fazit/tree/main/.planning/phases/01-demo-and-report)

The rules about openDesk and Nextcloud need a person who runs them, not a model. That review is open.

### How it pays its way

Fazit stays free. I plan to earn from assessments and support around it. [Three pilot assessments are free](/pilots/).

### How to help

Fazit's rules say where openDesk and Nextcloud cover a Microsoft 365 function and where they fall short. If you run either, read a mapping and correct what is wrong. [Read the mappings](https://github.com/rouxdutoit/fazit/tree/main/src/fazit/rules/mappings)

When Fazit shows a gap in an open source project, the fix belongs in that project, with the people who maintain it.

To add a language, follow [the translation guide](https://github.com/rouxdutoit/fazit/blob/main/CONTRIBUTING.md#translating-fazit).

---

## Founder's answers, 2026-11-22

- **What the founder checks:** the review findings. The section says only that; "the tests, the report" is removed.
- **"A team I could not afford to hire":** the founder asked for a suggestion. Cut to "as I would with a team". The page already says Fazit is one person's work, and a buyer of assessments could read "could not afford" as a doubt about staying power.
- **"I had spent too long building products… Nobody needed them":** true as worded. Stays.
- **"I", not "we".**
- **"I believe machines should serve all of us. This is my part of that.":** stays. It is the founder's personal stance and is marked as belief.
- **Krueger's post:** linked and credited.

Built on 2026-11-22 as `site/about/index.html` and `site/de/about/index.html` (quick task `261122-abt-about-page`), not committed. Three small wording changes were made while building: the intro is in the first person throughout ("I am Ruan “Roux” du Toit. I make Fazit in Feldkirchen, near Munich."), "That review is open" became "That review has not happened yet", and "Fazit's rules say where…" became "Fazit's mappings record where…".

Added on 2026-11-22 at the founder's request (relayed by the main session): "Where it started" now opens with the consulting origin. The founder's words: "in my consulting work … companies have asked if it's possible to 'go open source'. It's also that along with this post that made me click." The page says only that: companies asked, then the post, and the two together. No client names, no "many", and no claim about what the founder could or could not answer at the time. The built pages in `site/about/` and `site/de/about/` are now the current copy; the text under "The copy" below is the earlier draft.

Still as drafted unless the founder objects: the headline, "Fazit stays free", and "near Munich".

## Lines that needed the founder's eye (history)

1. **"I had spent too long building products because a language model made them easy to build. Nobody needed them."** This paraphrases "I'm tired of wasting my time building products an LLM pushed me into building." Only the founder knows whether it is true as worded.
2. **"I" or "we".** The story is in the first person because the Impressum names one person. The pilots page says "we". If a second person is behind Fazit, the intro names them and the page says "we".
3. **"I believe machines should serve all of us. This is my part of that."** The one sentence of conviction on the page. It is the founder's own, marked as belief. The two critics would likely still cut it.
4. **The headline.** "Enough open source exists. Fazit helps you reach it." Alternatives: "Fazit exists so a move to open source starts with facts." / "One person, one blog post and a tool that replaces nothing."
5. **"Fazit stays free."** True of every released version under AGPL. It reads as a promise about the future too, which the founder must be willing to keep.
6. **"near Munich".** The Impressum gives Feldkirchen. Say so only if the founder wants the region named.
7. **The link to Krueger's blog.** His site carries a "Progressives for AI" newsletter. Linking is honest credit; the founder decides.
8. **"How it is made", second version (2026-11-22).** The founder is a product person who works with frontier models as a team, with the models checking each other and giving cold reads. The section now says that as a way of working, not as a shortfall against Krueger's "checks every line". Two things for the founder to confirm: "I check the result: the tests, the report and the review findings" must describe what actually happens, and "a team I could not afford to hire" is their own phrase and their call to publish.
9. **No job title, third version (2026-11-22).** The founder sees themself as an AI-assisted engineer who does the architecture and not the coding. The section uses neither "engineer" nor "product person" and says what they do instead. A title invites an argument about the title; a description of the work cannot be disputed. In the German page, "Ingenieur" is also a protected professional title under the state engineering laws, so it stays out unless the founder holds the qualifying degree (not legal advice; check before using it).
10. **Model reviews are not presented as human review.** One critic wrote "LLMs reviewing LLMs is not review". The section therefore names what the models do and where a person is still needed (the rules), and claims nothing more.

## If approved, what gets built

- New files: `site/about/index.html` and `site/de/about/index.html`, entries in `PAGE_PAIRS` and `site/sitemap.xml`.
- One footer link, "About" / "Über Fazit", on every page. This touches existing files, so the site coordinator is asked first.
- "What you can check" as a row list with one link each; no new CSS unless the existing classes cannot carry it.
- `uv run python site/check_site.py`, then commit and push.

## Later, not now

- A public list of the gaps Fazit's mappings record in openDesk and Nextcloud, once a named operator has reviewed the mappings.
- Telling Jordan Krueger about Fazit after the first release. His post invites it; the founder sends it.
- Note for any future badge idea: the pilots page already says "We also never ask for a logo, coat of arms, quote or badge on your website."

## Added on 2026-11-23

The founder asked for the main session's two remaining suggestions for "Where it started": "There was no quick, honest way to answer." after the companies' question, and "and it clicked" where the post is introduced ("made me click" is the founder's own phrase). German: "Eine schnelle und ehrliche Antwort darauf gab es nicht." and "und bei mir machte es klick". Changed in `site/about/index.html` and `site/de/about/index.html`, not committed.

The founder also found "I had spent too long building products… Nobody needed them." too harsh ("Makes me sound silly"). Replaced on 2026-11-23, with the founder's choice of wording: "I had built things because a language model made them easy to build, not because anyone had asked for them. The post said what I already knew. This time, companies had asked." German: "Ich hatte Produkte entwickelt, weil ein Sprachmodell es mir leicht machte, nicht weil jemand danach gefragt hatte. Kruegers Beitrag sprach aus, was ich schon wusste. Diesmal hatten Unternehmen gefragt."

The founder then clarified that those projects were personal, not consultancy work ("There I build what solves problems"). The sentence now opens "In my own time, I had built projects…" / "Privat hatte ich Projekte entwickelt…".

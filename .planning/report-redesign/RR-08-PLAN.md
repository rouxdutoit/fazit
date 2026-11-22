---
plan: RR-08
title: The website follows the redesigned report
depends_on: ["RR-01", "RR-06", "RR-07", "RR-02", "RR-03", "RR-04", "RR-05"]
files_modified:
  - site/index.html
  - site/de/index.html
  - site/coverage/index.html
  - site/de/coverage/index.html
  - site/start/index.html
  - site/de/start/index.html
  - site/security/index.html
  - site/de/security/index.html
  - site/pilots/index.html
  - site/de/pilots/index.html
  - site/integrators/index.html
  - site/de/integrators/index.html
  - site/style.css
  - site/check_site.py
  - site/sitemap.xml
  - site/og.png
  - publiccode.yml
autonomous: true
---

# RR-08: The website follows the redesigned report

Plan 8 of 8. Runs after RR-05, when the redesigned report and its sample demos are final. Site only: no change to `src/`, `tests/` or `site/demo/`.

## Why

The home page describes the old report, shows its one Blocker as the only example, and makes one privacy argument four times. The Apple-lens review (`.planning/research/apple-lens/REVIEW.md`, sections 1, 2, 3 and 5) went through every section. On 2026-11-22 the founder decided:

- Mail replaces Telephony as the home page example.
- The home page shrinks from 13 sections to 9, in the order below.
- In the privacy section, the "What Fazit will never do" list stays and the four tiles go.
- The readiness bar is gone from the report (RR-02), so nothing on the site may show it.

## Read first

- `AGENTS.md`, `DESIGN.md` (binding: structure, copy, symbols, buttons, accessibility).
- `.planning/research/apple-lens/REVIEW.md`, all of it.
- `.planning/report-redesign/UI-SPEC.md` §1 (section order and names), §2.3 (cards), §8 (copy).
- The final `site/demo/en/index.html` and `site/demo/de/index.html` (the redesigned sample reports).
- The current `site/index.html`, `site/de/index.html` and `site/check_site.py` (in particular `check_tally`, the coverage checks and `PAGE_PAIRS`).
- The About pages (`site/about/`, `site/de/about/`), so the home page's "How it is made" can point to them.

## Tasks

### Task 1: Home page, new order and content (EN and DE)

New section order, nine sections: hero; report preview; "Find the blockers before the project does"; the example; "What you get"; "What stays on your computer"; "Project status"; "How it works"; "Free and open source".

1. **Hero and preview:** unchanged apart from the alt text, which RR-05 already updated. Under the preview, fold the languages and offline facts into one line in the figure caption.
2. **Figures strip:** two figures, not four. Keep the assessed-area count and the targets. Read the count from the demo report, never as a literal. Delete "2 report languages" and "1 file".
3. **The example** (`#example`), Apple-lens section 1, the "when RR-01 and RR-02 land" step:
   - Heading: "Evidence and a next step for every area" / "Nachweise und nächster Schritt für jeden Bereich".
   - Intro, replacing the rhetorical question: "Each area shows its status, the evidence behind it and what is still missing. This one is Mail, from the sample report for a fictional town; its measurements are simulated." / "Jeder Bereich zeigt seinen Status, die Nachweise dazu und was noch fehlt. Hier der Bereich E-Mail aus dem Beispielbericht einer fiktiven Stadtverwaltung; die Messwerte sind simuliert."
   - The card: the Mail card copied from the regenerated demo, not hand-written. It shows the area with its category, the status as the anchor (shown alone, so the status leads), the reason, the next step, the evidence rows and "Evidence still needed". The site's `.finding` styles render it; add only what the report's card needs and the site lacks.
   - Under the card, merge the last paragraph of today's "Reading the findings" as a note: Fazit cannot establish that a supplied inventory is true. Then the tally in the report's display order and wording (Blocker first), and the link "See all areas in the sample report" / "Alle Bereiche im Beispielbericht ansehen".
4. **"What you get":** rewrite the tiles against UI-SPEC §1, in section order:
   - the summary for the council (one printed page);
   - what to do next (worth doing even if you stay; needed for a move);
   - where each area stands;
   - costs over five years;
   - what replaces what;
   - what needs a closer look;
   - how the report was made.

   Keep one symbol per tile, all or none.
5. **"What stays on your computer":** keep the lead paragraph, the "What Fazit will never do" list and "Check it yourself". Delete the four tiles and any CSS only they used.
6. **"Project status":** keep "Now" and "Next". Fold "Then", "After that" and "Later" into one "Later" step with the same facts.
7. **"How it works":** show the three commands from the start page as a static code block (no copy button), then keep the link to Get started.
8. **"Free and open source":** keep the licence and business-model sentences and the Pilots card. Delete the Integrators and Security cards.
9. **Cut from the home page:**
   - "Who it is for": move the IT-lead line into "How it works" if it still adds something.
   - "Reading the findings": its note now sits under the example.
   - "How it is made": replace with one sentence and a link to the About page, in the free-and-open-source section. Keep the No AI Slop manifesto off the site.
   - "What the targets cover" and "Sources": these move to the new coverage page (Task 2). Leave a two-line summary and a link in "What you get" or under the example, whichever reads better.

### Task 2: A coverage page

Create `site/coverage/index.html` and `site/de/coverage/index.html`, built like `site/pilots/index.html`, with:
- the coverage table;
- its legend and note, including that the mappings are not yet reviewed by someone who runs these suites;
- the sources and target projects from the home page;
- an intro sentence on what the table answers: what the suites cover, not what an organisation needs.

The coverage cells must not use a status symbol; RR-04 already replaced `.cov-full`'s symbol, so keep its choice. Update the following to the new page:
- `PAGE_PAIRS` in `site/check_site.py`;
- `site/sitemap.xml`;
- the coverage-cell checks in `site/check_site.py`.

Link the page from the home page, and from the integrators page (Task 3).

### Task 3: Other pages (Apple-lens section 3)

- **Start:** retitle "Next" as "See the result without installing" / "Das Ergebnis ohne Installation ansehen", and keep only the sample report card.
- **Security:** rename "Principles" to "What is true today and what is planned" / "Was heute gilt und was geplant ist". Sort the tiles into two groups, true today and planned for sign-in, each with a small heading. Keep "Limits of the evidence" as it is.
- **Pilots:** retitle "Contact" to "Express interest" / "Interesse bekunden". In "What you receive", name the report's page one for the council.
- **Integrators:**
  - Lead with what an integrator can do with the report: the open-points list grouped by evidence, the owner roles, and the planned CSV in 1.2.
  - Shrink the list of firms to one sentence with the listing criteria.
  - Link the coverage page.

### Task 4: Checks, consistency and images

- `site/check_site.py`:
  - `check_tally` follows the new tally wording and the report's display order (Blocker, Needs work, Unknown, Ready);
  - the coverage checks follow the table to its new page;
  - keep every other check.
- Area count: wherever the site states the number of assessed areas, it must equal the demo's count. That covers the home figures and `/pilots/` in both languages. Add a check for it if none exists.
- `publiccode.yml`: say the assessed-area count in both descriptions (14 today).
- `site/og.png`: regenerate at 1200 × 630 from the redesigned report's page one, in light mode, in the style of the current image (wordmark and the report excerpt). Keep it under 150 KB.
- Copy rules from DESIGN.md: headings are statements; no rhetorical questions; the same word for the same thing ("Erhoben" and "Bereitgestellt" for provenance, as in the report); British English; German native and formal.

## Verify

- `uv run python site/check_site.py` prints "No errors."
- `uv run pytest -q` still passes (nothing in `src/` or `tests/` changes).
- At 360 px and 1280 px, in light and dark mode, both languages: no horizontal scroll, and the Mail card matches the demo report's Mail card.
- `grep -rn "readiness-bar\|data-segment\|One finding in full\|Ein Befund im Detail\|Kann die Stadt\|Can the town" site --include=*.html | grep -v /demo/` prints nothing.

## Summary to write

`.planning/report-redesign/RR-08-SUMMARY.md` with:
- the new home page outline;
- the files changed;
- every deviation;
- a native-review table of all new German strings.

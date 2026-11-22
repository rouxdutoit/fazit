---
quick_id: 261122-abt-about-page
status: incomplete
date: 2026-11-22
---

# About page

Status is incomplete because the founder reviews the pages before anything is committed.

1. **English page.** `site/about/index.html`, built on the shell of the pilots page with existing classes only: an intro, six label-left sections, and five linked tiles under "What you can check". No new CSS, script or asset.
2. **German page.** `site/de/about/index.html`, written in German, formal, with the founder's story in the first person. Claude drafted it and a second model read it cold as a native editor; its corrections (pronoun collisions with "Sie/Ihre", an unmarked quote, three translated-sounding sentences) are applied. No human native speaker has read it yet. DESIGN.md asks for that before release.
3. **Footer link.** "About" / "Über Fazit" is the first item of the footer's Project list on all sixteen existing pages and on the two new ones. The site's coordinating session agreed to the position first.
4. **Checker and sitemap.** `about` is in `PAGE_PAIRS`; the sitemap has both entries.

## Changes to the approved copy made while building

- The intro is in the first person throughout: "I am Ruan “Roux” du Toit. I make Fazit in Feldkirchen, near Munich."
- "That review is open" became "That review has not happened yet."
- "Fazit's rules say where…" became "Fazit's mappings record where…", and "The rules about openDesk and Nextcloud" became "The mappings to openDesk and Nextcloud".
- "Claude and Codex" is introduced as "The AI tools Claude and Codex", so a reader who does not know the names understands the sentence.
- "How it pays its way" links the founder's consultancy, rouxdutoit.com. The founder gave the address in the main session; the wording is not yet confirmed.

## Open for the founder

- The headlines differ. English: "Enough open source exists. Fazit helps you reach it." German: "Open-Source-Software gibt es genug. Fazit zeigt, was der Umstieg erfordert." (Fazit shows what the move takes). The German claim is the more exact one.
- The home page, README and CONTRIBUTING still describe how Fazit is made in their older words. The coordinating session aligns them once the founder approves this page.

## Verification

- `uv run python site/check_site.py`: 20 pages and 710 references, no errors.
- `uv run ruff check site/check_site.py`, `uv run ruff format --check site/check_site.py`, `uv run pytest -q tests/test_repo_basics.py` (11 passed), `git diff --check`.
- Viewed in the browser: English at desktop width in light mode; German at 375 px in dark mode with no sideways scroll, five tiles and the footer link present. Not compared pixel by pixel across all four width and colour combinations.

## Not done

- Nothing is staged, committed or pushed.
- `.planning/STATE.md` is not updated, because it is shared with other sessions and this task is not yet complete.

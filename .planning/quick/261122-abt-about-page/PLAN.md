---
quick_id: 261122-abt-about-page
status: complete
date: 2026-11-22
---

# Quick task: the About page

Source: the copy and decisions in `.planning/research/about-pledge/ABOUT-DRAFT.md`, approved by the founder on 2026-11-22 with "build, don't push. I want to review."

## Do

1. **English page.** `site/about/index.html`, structured like `site/pilots/index.html`: an intro, then label-left sections. Sections: where it started, why it is free, what you can check, how it is made, how it pays its way, how to help. "What you can check" is five linked tiles without symbols.
2. **German page.** `site/de/about/index.html`, written in German (formal, Sie; the founder's story in the first person), not translated. The founder is at B2 and asked Claude to review it for native quality.
3. **Footer link.** A new first item "About" / "Über Fazit" in the footer's Project list on all sixteen pages. Announced to the site's coordinating session first.
4. **Checker and sitemap.** Add `about` to `PAGE_PAIRS` in `site/check_site.py` and two `url` entries to `site/sitemap.xml`.

## Rules

- `DESIGN.md` is binding. No new CSS; use existing classes.
- No pledge, no badge, no link to the No AI Slop manifesto or to the founder's Medium profile.
- Touch nothing in `site/style.css`, `site/site.js`, `src/` or `site/demo/`.
- Do not stage, commit or push. Other sessions push `main` from this checkout, so a local commit would go out with theirs.

## Done means

- `uv run python site/check_site.py` passes.
- Both pages render at 1280 and 375 px, light and dark, with no sideways scroll.
- `SUMMARY.md` records what was built and what is left for the founder.

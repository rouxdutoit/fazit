# Design review of UI-SPEC.md (Claude Fable 5.2), 2026-11-22

Read-only review against `site/style.css`, `site/index.html`, `site/de/index.html` and the locales.

## Required changes

**One product**
1. §5 bar: use the site structure `header.bar > .bar-in > a.wordmark + nav.bar-links > .bar-links-in`. Phone: list sideways scroll as a forced difference in §6.2 and write its rules (`.bar-in` flex; `.bar-links { min-width: 0; overflow-x: auto }`; links `inline-flex; min-height: var(--hit)`).
2. §6.1 tokens: add aliases `--solid-bg`, `--solid-fg`, `--link-glow`. Name the `a:hover` exception explicitly. Add `h4` to the margin reset.
3. §6.1 spacing: add 20 px as the gutter exception; the unknown cost segment becomes 48 px.
4. §3.2 / §9: delete the old `table:not(.cost-table)` card-stack rules; the 40rem query keeps only `.cost-table`.
5. §1.1 tiles: money in tiles at `--fs-headline` with `white-space: nowrap`; add a seven-digit test.
6. §2.2 card: `p.note-text` instead of bare `<small>`; define `.finding-next` and `.finding-missing`; when the status drops to `--fs-headline`, override `.evidence-value` too; list both in criterion 13.
7. §4: whatever follows `.timeline` gets `margin-top: 64px`.
8. §1.1: wrap each `h3` + `dl.rows` block in `.subsection`; `h3 + .rows { margin-top: 12px }`.
9. §1.1 / §3.1: readiness and cost bars share radius 999 px and a 2 px gap; "no pill shapes" applies to `.prov` only.

**Apple's standard**
10. Cost tile: the difference as the anchor, "less/more than staying" directly under it in `.tile-title` style, totals out of the tile.
11. §3.1: no hatch for parallel running; pattern means only Unknown. Fourth solid tint; `min-width: 2px` for small segments.
12. §2.1: group headings carry the status symbol; drop "Show" from the Ready summary.
13. Header: specify its rules; move the local/offline sentences to run details so the first tiles appear above the fold.

**Copy (old → new)**
14. DE title: "Was ein Ausstieg aus Microsoft 365 erfordert" → "Was ein Umstieg von Microsoft 365 erfordert".
15. Scenarios: Partial exit → Partial move; Full exit → Full move; Teilausstieg → Teilweiser Umstieg; Vollausstieg → Vollständiger Umstieg; Ausstiegsszenarien → Umstiegsszenarien; "exit scenario" → "move scenario". Add to §9's permitted edits.
16. Status sentence: "Of 15 areas: 1 Blocker, 9 Needs work, 1 Unknown, 4 Ready." / "Von 15 Bereichen: 1 Hindernis, 9 Handlungsbedarf, 1 Unbekannt, 4 Bereit."
17. summary.blockers: "What blocks the move" / "Was dem Umstieg entgegensteht".
18. summary.unknown: "What is still unknown" / "Was noch unbekannt ist".
19. readiness.title: "Where each area stands" / "Wo jeder Bereich steht".
20. costs.title: "What staying and moving cost over five years" / "Was Verbleib und Umstieg in fünf Jahren kosten".
21. "{n} areas are Unknown, so a Blocker cannot be ruled out." / "{n} Bereiche sind unbekannt; ein Hindernis lässt sich daher nicht ausschließen."
22. Add the missing keys to §8 in both languages (same as staying, "and {n} more", everything not examined, known so far, evidence incomplete, evidence summary, "{n} inputs are missing", seven nav labels; DE nav: Überblick, Bereiche, Kosten, Ersatz, Prüfbedarf, Nächste Schritte, Anhang).
23. "Partial move · over five years" consistently.

**Coverage symbols**
24. `announced` → cancel (not contrast): announced is not available today.
25. Symbols in `--fg`, cancel in `--fg-2`, never a status colour.
26. German labels as on the site: "In der Suite", "In der Suite mit Einschränkungen", "Open-Source-Lösung der Community". The report shows the label (the site hides it): a deliberate difference; label on line one (600), replacement on line two.

**Phone and print**
27. Phone at 360 px: wrap rule for the cost row heading, block values one per line, legend wrap, `dl.report-meta` wrap, bar rules from item 1.
28. Print: all type tokens in pt (24, 18, 14, 12, 10, 9, 8); `break-inside: avoid` only on the card head; 0.5 pt borders on tiles, rows and notes; links in `--fg`; tiles fixed at two columns; card padding in pt.

## Optional
- Consider the legend at lead size as the count line and dropping the sentence (the counts appear three times).
- Consider the organisation name as h1 and the statement as eyebrow.
- Cap the target line at two sentences, then link to "What replaces what".
- Edge fade as a scroll hint on the phone bar.
- DE attention.title: "Was genauer zu prüfen ist".
- Add a nav link to `found` or state the omission.

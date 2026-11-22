# Design rules

Binding for the website (`site/`) and the report (`src/fazit/templates/report.html.j2`). Build to these rules from the start; reviews confirm them, they should not discover them. Apple's own sites and the Human Interface Guidelines are the reference for structure, hierarchy, spacing and behaviour. Fazit's own identity is its colours in dark mode, its fonts and its wordmark.

When a rule here and a habit disagree, the rule wins. Change a rule only with a decision in `DECISIONS.md`.

## Tokens

- Use the tokens in `site/style.css` `:root`. No colour, font or radius values anywhere else. The report defines the same tokens, and a test keeps both in step.
- **Light mode:** apple.com neutrals (`#ffffff`, `#f5f5f7`, `#1d1d1f`, `#6e6e73`). **Dark mode:** Fazit's green on near-black (`#050906`, `#c4f7d0`). Buttons, links and symbols take the text colour in both modes. The only other colours are the iOS system colours for status.
- The page follows the device's light or dark setting. There is no theme switch.
- **Type:** Figtree for all text, Geist Mono only for code. Seven sizes only: display, title, headline, lead, body, subhead, footnote. Three weights: 400, 600 for labels and buttons, 700 never in body copy.
- **Spacing:** 4, 8, 12, 16, 24, 32, 48, 64, 96 px. The gutter is 20 px (16 px on phones).
- **Line length:** one measure, `--measure` (680 px), for all running text whatever its size; set in rem so small type does not wrap early. Paragraphs wrap with `text-wrap: pretty`, so no paragraph ends on a lone word; headings use `text-wrap: balance`. Never force line breaks with `<br>` or narrow boxes, except in postal addresses.

## Colour

- Colour carries meaning, nothing else. Status colours mean status; everything else, buttons and links included, is monochrome.
- Never colour a heading, a tile or a background to decorate it.
- Status is never colour alone: every status shows its symbol and its word.

## Structure

- **Hierarchy:** the conclusion first, then the evidence. Each screen has one thing to look at first.
- **Sections:** a label on the left, the content on the right; one line between sections, running from the content's left edge to its right edge.
- **Lists of facts are tiles:** a soft fill, no border, the card radius, 24 px padding. Each tile has one anchor (a symbol, a large number or a name), never two, then a short label or main line, then one line of detail. Within a group, either every tile has a symbol or none does.
- **A sequence is a timeline,** not tiles: a rail with one dot per step, filled only for what exists today.
- **No borders on cards.** Lines only separate rows and sections; in icon lists they start at the text.
- **Badges show state.** A card can show a status or incomplete evidence in a non-interactive capsule at the top right. On phones the badges wrap below the name. Use pressable pills for controls such as filters.

## Symbols

- Google Material Symbols, rounded, from `site/icons/` (the report inlines the same paths). Apache-2.0; keep the licence file.
- A symbol sits on the first line of its text, sized in `em`, with wrapped lines aligned after it.
- Never reuse a status symbol (check, warning triangle, stop octagon, question mark) for anything but status.

## Links and buttons

- **Text links:** the text colour; on hover they lighten, and in dark mode they also glow. A link inside running text carries a thin static underline in the secondary text colour and no chevron; a standalone link ends in a chevron, has no underline and sits a step back in dark grey (`--link-quiet`), coming forward to the text colour on hover. Footer and bar links have neither.
- **A card that leads to another page is one link as a whole:** black title, a circled neutral chevron in the corner, and on hover the card grows by about 1.5 % with a deeper shadow.
- **Buttons follow apple.com:** pill shape, regular weight (500 in Figtree), 15 px text with 7 × 15 px padding in content, 12 px with 3 × 10 px in the bar. The primary button lightens on hover and darkens when pressed; the text never changes colour.
- Every button leads with a symbol that says what happens (Material Symbols, in the button's text colour, sized in `em`); a button whose action no symbol can name gets none, and then no button in its group has one.
- One main action per screen. The bar holds the page links and one button. The main action is "Get started" / "Jetzt starten" until the first release, then "Install" / "Installieren".

## Motion

- Motion explains, it does not decorate: cards respond to hover and press, and the menu opens smoothly. Text and content never animate in; a page is readable the moment it loads. The one exception is the brand signature: the wordmark decodes in about half a second, in the bar when a visitor arrives from another site and in the footer as it comes into view.
- Durations of 0.2 to 0.8 s with Apple's ease curves. Nothing loops, nothing blocks reading.
- With reduced motion switched on, nothing moves. Without JavaScript, everything is visible and usable.

## Copy

- Headings are statements a cold reader understands ("Know what leaving Microsoft 365 would take"), not labels ("Overview").
- Short sentences, one idea each, plain words. No marketing filler, no stacked triads for rhythm, no rhetorical questions.
- **English** is British. **German** is native, formal (Sie), and written in German rather than translated; every German string gets a native review before release.
- **The name:** lowercase "fazit" only in the wordmark, the favicon and the command (`fazit demo`). Everywhere else, including buttons and headings, it is "Fazit": a German noun is always capitalised.
- Use the same word for the same thing everywhere: Umstieg, area or Bereich, finding or Befund, and the status names exactly as Ready, Needs work, Blocker, Unknown and Bereit, Handlungsbedarf, Hindernis, Unbekannt.
- Never overclaim: say what exists today, mark what is planned, and never say "completely secure" or "guaranteed".

## Accessibility and weight

- Contrast meets WCAG AA. Every control works by keyboard. Screen readers get plain text for every animated or symbol-only element.
- Every page works at 360 px wide without sideways scrolling.
- **Lean:** no CSS, script, asset or wrapper that nothing uses. Images in WebP, fonts subset to what is used, no third-party requests.
- **The report** loads nothing, runs no script and stays one file; its interactivity is HTML and CSS only.

## Checks

What a machine can check is checked automatically: colours only as tokens, only the two font families, symbols only from the shared set, and the shared palette between site and report. `uv run python site/check_site.py` and the report tests carry these checks; the design checks are added with the report redesign. Everything else in this file is checked by a person and by the release review before each release.

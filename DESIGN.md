# Design rules

Binding for the website (`site/`) and the report (`src/fazit/templates/report.html.j2`). Build to these rules from the start; reviews confirm them, they should not discover them. Apple's own sites and the Human Interface Guidelines are the reference for structure, hierarchy, spacing and behaviour. Fazit's own identity is its colours in dark mode, its fonts and its wordmark.

When a rule here and a habit disagree, the rule wins. Change a rule only with a decision in `DECISIONS.md`.

## Tokens

- Use the tokens in `site/style.css` `:root` for colour, fonts and corner radii. Timeline circles use the radius specified under Structure. The site and report share these tokens, and a test keeps both in step.
- **Light mode:** apple.com neutrals (`#ffffff`, `#f5f5f7`, `#1d1d1f`, `#6e6e73`). **Dark mode:** Fazit's green on near-black (`#050906`, `#c4f7d0`). Buttons, links and symbols take the text colour in both modes. The only other colours are the iOS system colours for status.
- The page follows the device's light or dark setting. There is no theme switch.
- **Type.** Figtree for all text, Geist Mono for code. The seven text sizes are display, title, headline, lead, body, subhead and footnote. Body copy uses weight 400, button labels 500, and headings and semibold labels 600.
- **Spacing:** 4, 8, 12, 16, 24, 32, 48, 64, 96 px. The section and command rules below also use 20, 40 and 56 px. The gutter is 20 px (16 px on phones).
- **Button tokens.** `--btn-height` is 44 px and `--btn-compact-height` is 28 px. `--btn-symbol-gap` is `0.4em` for buttons, filter segments, category options and language links. Status badges use a 4 px gap. The site and report share these tokens.
- **Line length:** one measure, `--measure` (680 px), for all running text whatever its size; set in rem so small type does not wrap early. Paragraphs wrap with `text-wrap: pretty`, so no paragraph ends on a lone word; headings use `text-wrap: balance`. Never force line breaks with `<br>` or narrow boxes, except in postal addresses.

## Colour

- Colour carries meaning, nothing else. Status colours mean status; everything else, buttons and links included, is monochrome.
- Never colour a heading, a tile or a background to decorate it.
- Status is never colour alone. Each status has a symbol and a word. Compact report filters show the symbol and count, with the word in visually hidden text and in the segment's title.
- Status symbols use Apple's system colours at full strength. Status badges mix 12% of the status colour into the surface fill. In dark mode the symbol and label both use the status colour. In light mode the symbol uses the status colour and the label uses the main text colour. The Evidence incomplete badge uses the neutral fill and text.
- With `prefers-contrast: more`, use Apple's increased contrast colours for the current screen theme. Print uses the default light palette.

| Status | Apple colour | Light | Dark | Increased contrast, light | Increased contrast, dark |
| --- | --- | --- | --- | --- | --- |
| Blocker | Orange | `#FF8D28` | `#FF9230` | `#C55300` | `#FFA056` |
| Needs work | Yellow | `#FFCC00` | `#FFD600` | `#A16A00` | `#FEDF43` |
| Ready | Green | `#34C759` | `#30D158` | `#008932` | `#4AD968` |
| Unknown | Gray (`systemGray`) | `#8E8E93` | `#8E8E93` | `#6C6C70` | `#AEAEB2` |

Apple updated these values on 9 June 2025. Accessed on 23 November 2026. [Apple Human Interface Guidelines, Color](https://developer.apple.com/design/human-interface-guidelines/color#System-colors)

WCAG contrast ratios against the badge's actual sRGB tint (`#F5F5F7` surface in light mode, `#111712` in dark). Small labels need at least 4.5:1. The light status colours fall below that threshold on their tints.

| Status | Light status colour | Light label | Increased contrast light status colour | Increased contrast light label | Dark label | Increased contrast dark label |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Blocker | 1.93:1 | 14.09:1 | 3.58:1 | 13.24:1 | 6.72:1 | 7.31:1 |
| Needs work | 1.33:1 | 14.75:1 | 3.64:1 | 13.36:1 | 9.84:1 | 10.34:1 |
| Ready | 1.86:1 | 14.12:1 | 3.57:1 | 13.24:1 | 7.28:1 | 7.87:1 |
| Unknown | 2.68:1 | 13.84:1 | 4.14:1 | 13.33:1 | 4.76:1 | 6.69:1 |

## Vertical rhythm

The website and report share the same gaps for each screen width. Measure from the end of one border box to the start of the next, including the actual separation left by collapsing margins. Use the inline axis for cards that share a row and for links in a row.

| Relation | Token | Below 768 px | 768–1079 px | 1080 px and up |
| --- | --- | ---: | ---: | ---: |
| Page top to first heading | `--rhythm-page-heading` | 64 px | 64 px | 64 px |
| Before and after a section divider, and before the footer | `--rhythm-section-gap` | 40 px | 56 px | 64 px |
| Section heading to its first content | `--rhythm-section-heading` | 16 px | 16 px | 16 px |
| Paragraph to paragraph | `--rhythm-paragraph` | 12 px | 12 px | 12 px |
| Lede to visual | `--rhythm-lede-visual` | 24 px | 24 px | 24 px |
| Visual to standalone link | `--rhythm-visual-link` | 16 px | 16 px | 16 px |
| Text to standalone link | `--rhythm-text-link` | 24 px | 24 px | 24 px |
| Card to card in a group | `--rhythm-card` | 12 px | 12 px | 12 px |
| Group to group | `--rhythm-group` | 32 px | 32 px | 32 px |
| Subsection heading to its content | `--rhythm-subheading` | 12 px | 12 px | 12 px |
| Caption to the element it describes | `--rhythm-caption` | 16 px | 16 px | 16 px |
| Inline gap between standalone links in a row | `--rhythm-inline-links` | 24 px | 24 px | 24 px |
| Command block padding | `--card-padding` | 20 px | 24 px | 24 px |

Page top is the content edge below the bar. An eyebrow uses some of the heading gap and can wrap above the heading. Measure the section gap from the end of the preceding block to the top of the rule, and from the bottom of the rule to the next content. This applies from the hero or page introduction to the first section as well. When the section heading and its first content sit in columns, their top edges align. A disclosure title acts as a subsection heading when expanded.

Visuals include cards, tile groups, lists, tables and command blocks. A lede introduces the next visual. A caption can sit above or below its visual. The home report download is a centred caption. A standalone link can appear alone or in a row. The footer gap ends at the footer's top edge. The report uses compact print spacing so the council summary fits on the first page.

Command lines use a line height of 1.7 with no added gap. Centre the copy button vertically and inset it so the symbol has the same right padding as the text has on the left.

## Structure

- **Hierarchy:** the conclusion first, then the evidence. Each screen has one thing to look at first.
- **Sections:** a label on the left, the content on the right; one line between sections, running from the content's left edge to its right edge.
- **Lists of facts are tiles:** a soft fill, no border, the card radius, 24 px padding. Each tile has one anchor (a symbol, a large number or a name), never two, then a short label or main line, then one line of detail. Within a group, either every tile has a symbol or none does.
- **A sequence is a timeline.** Use 11 × 11 px dots with a 50% radius. The dot and the 1 px rail use the same left edge as their reference, with the rail in the dot's centre column. Each dot centres on its title's cap band. The current step uses a solid dot in the text colour. Future steps use an outlined dot with an opaque fill in the page background colour, so the rail meets each dot at its edge.
- **No borders on cards.** Lines only separate rows and sections; in icon lists they start at the text.
- **Badges show state.** A card can show a status or incomplete evidence in a non-interactive capsule at the top right. On phones the badges wrap below the name. Use pressable pills for controls such as filters.

## Symbols

- Google Material Symbols, rounded, from `site/icons/` (the report inlines the same paths). The website language link uses Material Symbols Outlined (D40). The symbols use the Apache-2.0 licence. Keep the licence file.
- A symbol sits on the first line of its text, sized in `em`, with wrapped lines aligned after it.
- Leading action symbols centre on the cap band. Fazit's chevron uses a two-segment SVG with round caps and joins in the text colour. Its ink is 0.29 em wide and 0.50 em high. A right-facing chevron sits on the baseline up to the x-height, with 0.40 em from the last letter's ink to the chevron's ink. A trailing chevron stays with the last word when a label wraps. Disclosure chevrons sit beside the first line and rotate around the same centre.
- Match the chevron stroke to the Figtree stem. The measured widths are 0.084 em at weight 400, 0.100 em at weight 500 and 0.117 em at weight 600.
- Never reuse a status symbol (check, warning triangle, stop octagon, question mark) for anything but status.

## Links and buttons

- **Text links** use the text colour. On hover they lighten, and in dark mode they also glow. At rest, only links in running text carry a 1 px underline in the secondary text colour. A standalone link uses a trailing chevron and sits a step back in dark grey (`--link-quiet`) until hover, when it takes the text colour.
- **Underline on interaction.** On hover or keyboard focus, a 1 px underline in the link's current colour draws from left to right over 250 ms with `--ease` and retracts when the interaction ends. A gradient's `background-size` transition keeps the layout in place. The line sits over the resting underline in running text. On standalone links and linked card titles, it sits at the same offset and covers only the words. The chevron keeps its gap. The top bar, navigation, phone menu and footer are outside this rule. Reduced motion shows the line immediately. Print uses the resting styles.
- **A card that leads to another page is one link as a whole.** Its title ends with the plain trailing chevron in the title's text colour. The same gap and baseline rules apply as for standalone links. On hover the card grows by about 1.5 % with a deeper shadow.
- **Buttons follow apple.com.** Standard pills are 44 px high with 15 px text and 16 px horizontal padding. The desktop bar pill is 28 px high with 12 px text and 12 px horizontal padding. It has a hit area at least 44 px high. The copy button is 44 px square. The shared symbol and label primitive centres button content. Button labels use weight 500 in Figtree. The primary button lightens on hover and darkens when pressed while its text keeps the same colour.
- **Report status filters** use a single capsule track with a 2 px inset and one row of same-height segments. The selected segment is a capsule. Use the full status labels when they fit the track. When space is tight, share the track width equally and show symbols and counts. Keep the word and count for All / Alle at every width.
- **Browser-managed select text** uses normal line height with room for the full glyphs. Keep the trigger and options on one line.
- **The category pill** fits the selected label. A down chevron follows at `--btn-symbol-gap`, with 16 px padding at both ends. The native picker uses the same trigger geometry.
- Every button leads with a symbol that says what happens (Material Symbols, in the button's text colour, sized in `em`); a button whose action no symbol can name gets none, and then no button in its group has one.
- One main action per screen. The bar holds the page links and one button. The main action is "Get started" / "Jetzt starten" until the first release, then "Install" / "Installieren".

## Motion

- Cards respond to hover and press, and the menu opens smoothly. Body text and content are in place on load. Two exceptions apply to text. On the website, the wordmark decodes in about half a second, in the bar when a visitor arrives from another site and in the footer as it comes into view. Content link underlines draw on hover and keyboard focus.
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

`uv run python site/check_site.py` and the report tests check colour tokens, font families, shared symbols and the status palette. `node site/check_alignment.mjs` checks symbol alignment, chevron ink, button heights, timeline geometry, control wrapping, label clipping and segment heights at 360, 390, 768 and 1280 px. It checks button gaps within 0.5 px and measures the category trigger's gap and equal padding for every selection in both picker modes. Timeline dots are checked at device scales 1, 2 and 3, with 0.1 px allowed for centre and width-to-height differences. Alignment also checks underline behaviour for content and navigation links. `node site/check_spacing.mjs` measures the rhythm on every page at 360, 768 and 1280 px and checks that the section gap matches the home page. Both checks run in Chromium and WebKit and also use a 390 × 844 px iPhone viewport with touch and mobile settings. The release review checks the remaining design rules.

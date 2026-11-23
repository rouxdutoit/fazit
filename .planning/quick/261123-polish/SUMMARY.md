# Badge and spacing polish

Implemented and verified on `polish` at `489a577`, the `origin/main` tip when work began. `origin/main` advanced by two commits during the work. The screen rhythm uses one value per relation at all three widths. Page-top measurements start below the bar. The first heading, stacked section headings and standalone links are measured at their own border boxes. In a two-column section, the heading and content each start 32 px below the divider.

## Rhythm measurements

All values are in CSS pixels. The same checker measured the original `polish` checkout and the updated site. Each run covered 24 pages in light and dark, with 144 initial views, 12 report views with all disclosures expanded and 12 report views with an empty filter result.

| Relation | Token | Before at 360 | Before at 768 | Before at 1280 | After at all widths |
| --- | --- | --- | --- | --- | ---: |
| Page top to first heading | `--rhythm-page-heading` | 32, 48.98, 84.98, 123.42, 135.91 | 48, 48.98, 117.98, 183.70 | 48, 56.98, 117.98, 174.52 | 64 |
| Section divider to section content | `--rhythm-divider` | 23, 31 | 23, 47 | 23, 47 | 32 |
| Section heading to its first content | `--rhythm-section-heading` | 8, 12, 16, 32 | 8, 12, 16, 32 | 8, 12, 16, 48 | 16 |
| Paragraph to paragraph | `--rhythm-paragraph` | 0, 4, 8, 12 | 0, 4, 8, 12 | 0, 4, 8, 12 | 12 |
| Lede to visual | `--rhythm-lede-visual` | 4, 8, 12, 16, 24, 32, 48 | 4, 8, 12, 16, 24, 32, 54.39 | 4, 8, 12, 16, 24, 32, 80 | 24 |
| Visual to standalone link | `--rhythm-visual-link` | 12, 24, 30.09 | 12, 24, 30.09 | 12, 24, 30.09 | 16 |
| Text to standalone link | `--rhythm-text-link` | 4, 12, 24, 30.09 | 4, 12, 24, 30.09 | 4, 12, 24, 30.09 | 24 |
| Card to card in a group | `--rhythm-card` | 12 | 12 | 12 | 12 |
| Group to group | `--rhythm-group` | 0, 12, 16, 24, 32, 64 | 0, 12, 16, 24, 32, 48, 64 | 0, 12, 16, 24, 32, 48, 64 | 32 |
| Subsection heading to its content | `--rhythm-subheading` | 0, 4, 8, 12, 16, 18.97, 24 | 0, 4, 8, 12, 16, 18.97, 24 | 0, 4, 8, 12, 16, 18.97, 24 | 12 |
| Caption to the element it describes | `--rhythm-caption` | 0, 8, 12, 16, 24 | 0, 8, 12, 16, 24 | 0, 8, 12, 16, 24 | 16 |
| Last section to footer | `--rhythm-footer` | 0, 32, 122.44, 134.94 | 0, 32, 182.73 | 0, 32, 173.53 | 48 |
| Inline gap between standalone links in a row | `--rhythm-inline-links` | 24 | 24 | 24 | 24 |

The original had 6,588 gaps outside the specified relation value out of 9,316 measurements. Thirty-three of the 39 relation and width combinations failed. The updated site passed all 9,316 measurements. The home closing line now sits 24 px above its two links in both languages, up from 12 px. The links have 24 px between them when they share a row.

## Website margin and gap changes

| Selectors | Change |
| --- | --- |
| `.hero`, `.hero h1`, `.hero-sub`, `.hero-actions`, `.hero-status`, `.report-preview` | Replaced the hero's responsive top and bottom padding, the heading's 12 px margin, the lede's 16 px margin and the actions and status margins of 24 and 16 px. The heading starts at 64 px, with the eyebrow using part of that space, and the lede starts 16 px below it. The actions and status use 32 px group gaps. The preview has a 24 px gap above it and a 32 px group gap before the following section, replacing its 16 px top margin and responsive bottom margin. |
| `.page-intro`, `.page-intro p`, `.page-intro h1 + p`, `.page-intro .btn`, `.center-page`, `.center-page h1`, `.center-page .btn` | Replaced intro padding, 12 and 16 px paragraph and heading offsets, and 24 px action offsets. The 404 page drops its 64 and 96 px padding, 8 and 16 px heading margins, and flex growth above the footer. Both use 64 px page starts, 16 px heading gaps, 12 px paragraph gaps and 32 px group gaps. |
| `.grid`, `.sec`, `.sec-body > :first-child`, `.subsection`, `.sec-body h3 + p`, consecutive paragraphs | Replaced responsive 32 and 48 px section padding with 32 px before the divider and 32 px after its 1 px rule. Stacked headings use the 16 px token. Removed the first-child margin reset and the separate 32 px subsection, 8 px heading and 12 px paragraph rules in favour of the shared relations. |
| `.command`, `.page-intro .command`, `.sec-body > .command`, `.command-label` | Removed 16/32 px and 32/8 px command margins, the section-end override and the 8 px label bottom margin. The preceding lede uses 24 px, the label uses 16 px and the following note uses 32 px. |
| `.finding`, `.finding-evidence`, `.status-summary`, `.preview-blockers`, `.preview-blockers .finding`, `.preview-blockers .finding > p`, `.preview-blockers > .more` | Replaced the finding's 24 px margin, evidence's 16 px margin, tally's 12 px margin and the preview's 24, 8, 12 and 12 px offsets. Uses 24 px from lede to evidence visual, 32 px from tally to blockers, 12 px from the heading or card header to content and 16 px from the card to its link. |
| `.legend`, `.table-note`, `.note-text`, `.report-preview figcaption`, `.summary-costs`, `.summary-costs .cost-origin`, `.summary-costs .tiles` | Removed the legend's 8 px lower margin, notes' 16 px upper margins, figure caption's 12 px margin, cost group's 24 px margin, cost origin's 8 px lower margin and the tiles' zero-margin override. Captions use 16 px. Notes and the costs group take their adjacent relation. |
| `.tiles`, `.tiles h3`, `.tiles .tile-title`, `#principles .tile-title` | Removed the tiles' 24 px upper margin, heading's 4 px lower margin and Security page's zero upper margin override. Headings use 12 px to their content, and cards use the 12 px shared grid gap. |
| `.timeline`, `.lead + .timeline`, `.timeline-step`, `.timeline-text`, `.timeline + .note-text` | Replaced the list's margin reset and lede's 24 px override with the shared lede gap. Switched 32 px step padding to the group margin. Removed the 4 px text and 64 px trailing note offsets. Step titles are subsection headings with 12 px below them. The rail fades into the 32 px gap before the note. |
| `.section-link`, `.sec-body p:has(> .more)`, `.flow-links`, `.home-closing .sec-body`, `.home-closing .note-text` | Removed the two 24 px link margin rules, the closing band's 12 px grid gap and its note override. Single links use their own boxes. Links after visuals use 16 px, links after text use 24 px, and the closing note starts a 32 px group gap below the links. The row's 24 px inline gap is tokenised. |
| `.legal-intro`, `.legal-layout`, `.has-summary`, `.legal-part + .legal-part`, `.legal-part p`, `.legal-part address`, `main`, `footer` | Replaced legal intro and layout padding, the legal parts' 32 px margin and 8 px content margin. Headings use 16 px to content and groups use 32 px. The shared 48 px footer gap comes from `main`. The site footer takes spare height on short pages. |

## Report margin and gap changes

| Selectors | Change |
| --- | --- |
| `.page-intro`, `.page-intro p`, `.page-intro .eyebrow`, `.page-intro .note`, `.report-meta` | Removed the header's 24 px padding and 32/16 px wide-screen override, paragraph's 12 px margin, eyebrow's zero-margin override, note's 16 px margin and metadata's 12 px margin. The headline starts at 64 px, the metadata follows after 16 px and the sample note starts a new group. |
| `.grid`, `.sec`, `[data-section=summary] .sec`, `h3`, `.sec-body > :first-child`, `.subsection`, `.subsection > :first-child`, consecutive paragraphs | Replaced responsive 32 and 48 px padding and the summary's 24 px override. Every divider is measured from its bottom edge to content at 32 px. The grid uses the 16 px heading token. The old global `h3` margins of 32 and 12 px and per-subsection margins and resets became 32 px group gaps and 12 px subsection and paragraph gaps. |
| `.status-summary`, `.coverage-summary`, `.scope-needed`, `.scope-links`, `.rows`, `h3 + .rows`, `p + .rows`, `h4 + .rows` | Replaced the 12 px summary margins, 12/4 px scope heading and 12 px scope-links bottom margins, `.rows` reset and its 12 px heading and paragraph overrides. A lede to a list uses 24 px, a heading to a list uses 12 px and separate groups use 32 px. |
| `.summary-links`, `.finding-target`, `.finding-target > .more` | Replaced the summary row's 12 px top and 16 px inline gaps. Summary links use 16 px below a visual and 24 px below text, with 24 px inline. Replacement text now has its own box, giving its standalone link 24 px in place of the former 4 px offset. The target paragraph's old 16 px margin became a group gap. |
| `.tiles`, `.summary-costs .tiles`, `.summary-costs .cost-origin`, `.cost-notes`, `.cost-notes p` | Removed the 24 px tile margin, zero summary tile override, 12 px cost-origin lower margin, 12 px cost-notes margin, 8 px gap and paragraph reset. The caption uses 16 px, the cards use 12 px, the notes start after a 32 px group gap and their paragraphs use 12 px. |
| `.table-scroll`, `.workload-evidence .table-scroll`, `caption`, `.table-note`, `.note-text` | Removed 12/24 px table margins and the 24 px evidence-table override. Tables follow a heading, lede or group with the corresponding token. Moved the caption gap out of its 8 px padding into an actual 16 px margin. Replaced note top margins of 16 px with their adjacent paragraph, caption or group relation. |
| `.finding-reason`, `.finding-next`, `.finding-missing`, `.finding .workload-evidence`, `.status-group > h3`, `.status-group + .status-group`, `.filters`, `.filters .note-text`, `.areas-empty` | Replaced 16 px finding margins and the 12 px disclosure margin with a 12 px heading gap and 32 px group gaps. The filter's 32 px lower margin and hint reset became flow rules. The empty message replaces the hidden list and sits one 32 px group gap below the filters. Status-group headings and cards use separate 12 px tokens. The 32 px status group spacing moved from a sibling margin to the areas grid. |
| `.finding ul`, `.rule-details ul`, `.open-details p + p`, `.finding-missing li p + p`, `.mapping-gaps`, `.rule-evidence`, `.cost-inputs`, `.licence-products`, `.run-details`, `.rule-details`, `.mapping-details`, appendix lists | Replaced offsets of 4, 8, 12, 16, 24 and 32 px on lists, disclosures and adjacent paragraphs. A short list inside a finding reason uses a 4 px start gap. Section lists, disclosures and their paragraphs use the shared heading, lede, paragraph or group gap. |
| `.cost-bars .legend`, `.cost-chart-row`, `.cost-chart-heading h3`, `.cost-chart-heading > p`, `.cost-bar`, `.cost-segment.is-unknown`, `.cost-known-blocks`, `.cost-chart-values` | Removed the legend's 24/8 px margins, chart row's 24 px margin, heading and label reset and the 8 px chart offsets. Legend and values use the 16 px caption gap, the bars and unknown marker start 12 px below their header and separate chart rows use 32 px. The unknown marker uses a block-level flex box so its caption starts 16 px below the marker. |
| `main`, `footer`, print `.sec-body > h3:first-child`, `.finding > * + *`, `.cost-chart-row + .cost-chart-row`, `.table-scroll`, `caption`, `.finding-target > .more`, and summary `.cost-notes` | Moved the 32 px footer margin into the shared 48 px screen gap. Print uses an equivalent 24 pt footer margin, zero margin above the first subsection heading, 8 pt margins for finding groups, chart rows and table blocks, and 4 pt gaps for captions and replacement links. The compact summary keeps its 4 pt cost-note offset. |

## Badge contrast

Dark status capsules use Apple’s full-strength status colour for both symbol and label, including the preference for increased contrast. The fill mixes 12% status colour into the surface. In light mode and in print the label takes the main text colour. Evidence incomplete takes the neutral text and fill in each palette.

| Status | Light status colour on its tint | Light label | Increased contrast light label | Dark label | Increased contrast dark label |
| --- | ---: | ---: | ---: | ---: | ---: |
| Blocker | 1.93:1 | 14.09:1 | 13.24:1 | 6.72:1 | 7.31:1 |
| Needs work | 1.33:1 | 14.75:1 | 13.36:1 | 9.84:1 | 10.34:1 |
| Ready | 1.86:1 | 14.12:1 | 13.24:1 | 7.28:1 | 7.87:1 |
| Unknown | 2.68:1 | 13.84:1 | 13.33:1 | 4.76:1 | 6.69:1 |

Chromium verified 640 computed badge styles across the two home pages and demo reports, using the four screen palettes and print. The weakest shipped label is dark Unknown at 4.76:1. The 4.5:1 small-text threshold explains the neutral light labels. [Design rules](../../../DESIGN.md#colour)

## Checks and generated files

- `site/check_spacing.mjs` reads the gap values from `DESIGN.md` and measures the rendered edges. It checks stacked and side-by-side cards, standalone links inside and outside rows, visible table rows beneath captions, and reports with disclosures open or filters that return no matches. Both browser checks share the local server, page discovery and Chromium setup in `site/check_browser.mjs`.
- A temporary copy with a 12 px closing link gap and a 13 px report card gap failed at all three widths. A separate check with bilingual nonprofit and all-Unknown reports added passed 23,856 measurements.
- `tests/test_report.py` checks the themed badge rule, the neutral evidence badge and the 4.5:1 threshold for each status in the four screen palettes. All five badge tests passed from the unpacked source distribution.
- `uv run ruff check .` and `uv run ruff format --check .` pass. `uv run python site/check_site.py` passes for 24 pages and 972 references.
- `uv run pytest -q` passed all 983 tests against the final template.
- `node site/check_alignment.mjs` passed 8,548 measurements across 144 views. The largest offset was 0.30 px, within the 0.75 px limit.
- Both CLI demo commands regenerated the published reports. The matched home download labels now show 428 KB in English and 440 KB in German. Both reports open from disk with networking and JavaScript disabled, and the status and category filters work in Chromium.
- A4 first-page verification passed for the town, nonprofit and all-Unknown reports in English and German, with backgrounds enabled and disabled.

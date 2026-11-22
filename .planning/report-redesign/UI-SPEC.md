# UI-SPEC: Fazit report redesign

Design contract. One design, no options. It touches the report template, the locales, the status rule YAML, `report.py`, and the tests and `site/check_site.py` only where section 9 says so.

## 0. Intent

Today the report is 24,000 px tall at 1280 px and opens with inventory tiles and a licence table; readiness starts three screens down, in a four-column table. The redesign puts the verdict first, turns each area into a card, draws the costs, and makes the report look like the website. Nothing about what is measured, provided or unknown changes.

**If the site has the component, copy its rules from `site/style.css` unchanged.** Invent only what section 6.2 lists.

## 1. Page order and what the reader sees first

`SECTION_ORDER` becomes:

`header, summary, readiness, costs, moves, attention, path, found, appendix, footer`

A cold reader asks three things in order: can we move, what stops us, what does it cost. The first screen answers all three and says what is unknown. Detail follows in the order of those questions; inventory and method come last.

### 1.1 Summary (`data-section="summary"`, new)

1. **Status sentence** (`p.lead`): counts in the fixed order Blocker, Needs work, Unknown, Ready, zero counts included. EN: "1 area is a blocker, 9 need work, 1 is unknown and 4 are ready." It states counts only. No adjective, no score, no percentage.
2. **Readiness bar** and legend: the existing `.readiness-bar` and `.status-legend`, moved here with the same hooks (`data-segment`, `data-count`, `flex-grow`). Segment and legend order change to Blocker, Needs work, Unknown, Ready, so the eye meets the obstacles first. Height 12 px.
3. **Summary tiles** (`ul.tiles.tiles-2`), in this order:
   - **One tile per exit scenario** (Partial exit, Full exit). Label: scenario name and "over five years". Main line (`.figure-num`): the absolute difference from staying. Detail: "less than staying" or "more than staying" or "the same as staying", then the scenario total and the stay total, then the cost origin text (`data-cost-origin`, unchanged strings). If the difference is unknown the main line is the Unknown status label (symbol and word), never a number and never a dash; the detail is "N inputs are missing" with a link to `#costs-missing`.
   - **Latest notice date** and **Next renewal** (Phase 1.1, D-90): two tiles, main line the date, detail "Provided · {source} · {date}". Without the inputs, each tile's main line is "Not provided" and the detail names the two fields to add to `inputs.yaml`. Hooks: `data-decision="notice"` and `data-decision="renewal"`, each with `data-provenance`. Absent until 1.1 ships.
4. **Blockers that matter** (`h3` + `dl.rows`): at most **3** rows. Order: blockers with complete evidence before those with `data-incomplete`, then catalogue order. Each row: `dt` area name linking to `#readiness-{workload}`; `dd` the deciding reason, one sentence. More than 3: a final line "and N more" linking to `#status-blocker`. None: the existing `path.empty.blocker` sentence. If any area is Unknown, a second sentence follows it: "N areas are unknown, so a blocker cannot be ruled out."
5. **What is not known** (`h3` + `dl.rows`): at most **4** rows, in this order: Unknown areas (catalogue order), then areas with incomplete evidence, then one row for missing cost inputs ("N cost inputs missing"). Each `dd` is the fix sentence from `reason.*.fix`. A closing link "Everything not examined" goes to `#not-examined`. This block is never omitted; with nothing unknown it shows `path.empty.unknown`.

Every figure in the summary is printed again, with provenance, further down.

## 2. Areas (`data-section="readiness"`)

One card per area, in `div.areas`, replaces the table. `h2#readiness-title` stays.

### 2.1 Grouping and order

Four groups, each an `h3` with id `status-{status}` and text "{status label} · {count}": Blocker, Needs work, Unknown, Ready. Empty groups are omitted. Inside a group: complete evidence before incomplete, then catalogue order (so "AI assistants (Copilot)" is second among its peers after 1.1).

The Ready group's cards sit inside one `<details class="ready-group">` whose `summary` is the group heading. It is closed on screen and open in print.

### 2.2 Card: the site's finding card

Mirrors `.finding` from `site/style.css` (see `site/index.html`, "One finding in full"). Markup:

```html
<article data-workload="mail" data-status="needs_work" data-incomplete
         class="finding" id="readiness-mail" aria-labelledby="area-mail">
  <h4 class="finding-area" id="area-mail">Mail</h4>
  <p class="finding-status">{{ status_label(row.status) }}</p>
  <small>Evidence incomplete</small>
  <p class="finding-reason">…one sentence…</p>
  <p class="finding-next"><strong>Next step</strong> …one sentence…</p>
  <div class="finding-missing">…Evidence still needed, li[data-missing]…</div>
  <details class="workload-evidence" data-evidence-workload="mail">
    <summary>Evidence · 4 measured, 1 provided, 1 unknown</summary>
    <dl class="evidence">…findings the rule used, [data-evidence]…</dl>
    <table class="coverage">…every finding, tr[data-finding]…</table>
  </details>
  <p class="finding-target">On openDesk: … Checked 21 November 2026.</p>
</article>
```

Attribute order on `article` is fixed as shown; the "Evidence incomplete" line appears only with `data-incomplete`. `status_label` is unchanged.

- **Status is the anchor.** `.finding-status` uses the site rule; the only override is `font-size: var(--fs-headline)` inside `.areas`, because there are sixteen cards and not one.
- **Reason**: exactly as `status_reason` resolves it today, one sentence. Notes from other fired rules follow as a plain list.
- **Next step**: new. Each non-ready rule in the status rule YAML gains `next_step: {en, de}`: one sentence, an action and who typically owns it, no supplier or product named. Areas without a deciding rule use `reason.*.fix`. Ready cards have no next step line.
- **Evidence still needed** stays outside the disclosure: it is the next step for an incomplete card.
- **Evidence disclosure**: closed by default (a test requires no `open`). The summary counts this area's findings by provenance in words. Areas without findings have no disclosure. Inside: first the findings the rule used, as the site's `dl.evidence` (each `div[data-evidence]`: value, label, `.evidence-meta`); then the full finding table from today's "Evidence behind the figures", with `caption[data-sample]` and the sample note row.
- **Target line** (`.finding-target`): one sentence per mapped function for this area, with coverage label and check date. Areas in `mapping.no_function` show `moves.no_function`.

Cards stack in one column at every width.

### 2.3 Measured, provided, unknown: no pills

Provenance is a word in a sentence, set in `.evidence-meta` (footnote size, `--muted`), with the provenance word first at weight 600 in `--text`: "**Measured** · Sample licence inventory · 2 November 2026 · Complete, 3 of 3 scanned". Existing `.prov` and `data-provenance` stay on the same elements. No border, background or capsule anywhere.

An unknown value shows the Unknown status label (help symbol and word) where the figure would be, followed by reason and fix. It is never blank, zero, a dash or styled like a measured value.

`div[data-subsection="not-examined"]` stays at the end of this section with `id="not-examined"`, hooks unchanged.

## 3. Costs as a picture (`data-section="costs"`)

Order inside the section: invented-amounts note (`.note`, when applicable), the chart, the results table, the rounding note, missing inputs (`id="costs-missing"`), then the `Cost inputs` disclosure and its table.

### 3.1 The chart (`.cost-bars`, new)

Three rows: Stay, Partial exit, Full exit. Each row has a heading line (scenario name left; total and difference from staying right), the bar, and a line of exact block values (see the wireframe).

- The bar is `div.cost-bar[aria-hidden="true"]`, a flex row, height 24 px, radius `--radius` (8 px), 2 px gaps in `--bg`. Its width is `calc(var(--share) * 100%)`, with `--share` = scenario total ÷ largest known total, set in an inline `style` (inline custom properties and `flex-grow` only; no `url()`).
- Segments are `span.cost-segment[data-block]` with `flex-grow` = the block's amount. Fills carry no status meaning and use no status colour: running `--text`; direct project `--muted`; productivity loss `color-mix(in srgb, var(--muted) 45%, var(--surface))`; parallel running a 45° `repeating-linear-gradient` of `--text` and `--surface`, 3 px bands. The legend above the chart shows each swatch with its block name.
- **Exact values are text.** The line under each bar lists every block with its amount, in table order. A real zero is listed as "EUR 0.00" and gets no segment. "Not applicable" lines are omitted.
- **Unknown is never zero.** If a block is unknown, the bar ends in `span.cost-segment.is-unknown`: fixed 56 px, transparent, 1 px dashed `--muted` border, help symbol centred. The known blocks are scaled against the largest known sum. The right-hand text reads "Total unknown" and the line below reads "Known so far EUR X · {block} Unknown". No difference is shown. If every block is unknown the row shows only the dashed segment at 56 px.
- With no inputs at all the chart is omitted and `costs.provide_inputs` appears in `.note`.
- A negative amount gets no segment; its value is still listed.

### 3.2 The table

The results table is unchanged in structure and hooks. It takes the site's `.coverage` cell padding and header style. It is always visible; the chart never replaces it. The narrow layout stays.

## 4. Every current section

| Current | Decision | Reason |
|---|---|---|
| Header | Keep, shortened | Title becomes a statement; organisation is the eyebrow; the five meta items become one footnote-size row (`dl.report-meta`, hooks kept). The local and offline sentences stay as `.note-text`; the sample note uses `.note`. |
| What we found: headline tiles | Move to `found`, after `path` | Inventory is context, not the verdict. Rendered as `ul.tiles.tiles-2`; number in `.figure-num`, unit in the label so "91 accounts" cannot break mid-word at 375 px. |
| Licence products | Keep in `found`, inside a closed `<details>` | It is a reference table. Summary: "Licence products found: 3 · Measured". |
| Evidence behind the figures | Merge into the area cards | Evidence belongs beside the status it supports. |
| Five-year cost comparison | Keep; chart added; moves after the areas | The reader needs the obstacles before the price. |
| Readiness by area | Keep; becomes cards; bar moves to the summary | Section 2. |
| What moves where | Keep as the site's `.coverage` table | Columns: Microsoft function; Replacement (a `.cov-cell`: coverage symbol, coverage label, replacement name); Checked on; Area status (status label, linked to the card). The reason column is dropped: it is on the card. |
| Needs attention | Keep | File types as a `.coverage` table; software counts and transfer gaps as `dl.rows`. Hooks unchanged. |
| Suggested path | Keep; becomes the site's `.timeline` | Three steps (blockers, unknowns, ready areas), the first non-empty one `.on`; each lists its areas (path hooks unchanged). The pilot sentences and the four generic steps (`ol.steps`) follow. |
| Appendix | Keep; each part in a closed `<details>` except run details | The parts serve the auditor; run details identify the report. |
| Footer | Keep unchanged | Plain text, no link. |

## 5. Navigation

A sticky top bar that mirrors the site's `.bar`, `.bar-in`, `.wordmark` and `.bar-links`: `nav.bar[aria-label]`, the word "fazit" as plain text on the left (not a link), seven in-page links on the right: Summary, Areas, Costs, Replacements, Closer look, Next steps, Appendix. Links are `href="#…"` only. Below 820 px `.bar-links` becomes `overflow-x: auto; scrollbar-width: none` with 44 px link height; no menu button, no checkbox hack. `html { scroll-padding-block-start: calc(var(--bar-h) + 16px) }`. A skip link (`.skip`) to `#main` is the first element in `body`. The bar is hidden in print.

## 6. Typography, spacing, components

### 6.1 Tokens

- The report's `:root` and dark `@media` block keep their current names and mechanism (the token test parses them). Add the site's names as aliases in a second rule so site CSS pastes in unchanged: `--fg: var(--text); --fg-2: var(--muted); --rule: var(--line); --fill: var(--surface); --link: var(--accent); --link-hover: var(--accent-hover);` plus `--sans`, `--mono`, `--ease`, `--gutter` (20 px; 16 px to 600 px), `--max: 1120px`, `--bar-h: 52px`, `--hit: 44px`, `--radius: 8px`, `--radius-pill: 999px`.
- Type: `--fs-display` h1; `--fs-title` figures and evidence values; `--fs-headline` section labels and card status; `--fs-lead` the status sentence; `--fs-body` text; `--fs-subhead` tables, tile detail, card area name; `--fs-footnote` provenance and meta. Weights 400 and 600 only.
- Spacing: only 4, 8, 12, 16, 24, 32, 48, 64, 96 px and the site's clamps. Print uses pt.

### 6.2 Components

Reused from the site, rules copied unchanged:

| Report use | Site selector |
|---|---|
| Section frame: label left, body right from 880 px, sticky label, hairline rule | `.sec`, `.grid`, `.sec-label`, `.sec-body`, `.sec-intro`, `.subsection` |
| Top bar and skip link | `.bar`, `.bar-in`, `.wordmark`, `.bar-links`, `.skip`, `.sr-only` |
| Summary and inventory tiles | `.tiles`, `.tiles-2`, `.tile-label`, `.tile-title`, `.figure-num` |
| Area card | `.finding`, `.finding-area`, `.finding-status`, `.finding-reason`, `.evidence`, `.evidence-value`, `.evidence-meta`, `.finding-target` |
| Tables | `.coverage`, `.cov-cell`, `.cov`, `.table-note`, and its 600 px stacked layout with `attr(data-label)` |
| Key-value lists | `.rows` |
| Next steps | `.timeline`, `.timeline-step(.on)`, `.timeline-dot`, `.timeline-name`, `.timeline-text`, `.steps` |
| Notes, legend, counts | `.note`, `.note-text`, `.legend`, `.tally` |
| Links, focus ring, code | `a`, `a:hover`, `:focus-visible`, `code` |

One forced difference: the site draws symbols with `mask: url()`, which the report's CSP forbids. The report keeps inline `<svg class="icon">` with the same Material Symbols paths at the site's sizes. Coverage symbols: `in_suite` check-circle; `in_suite_with_limits`, `announced` contrast; `open_source_community`, `open_source_third_party` code; `component_vendor_solution`, `proprietary_third_party`, `not_available` cancel. The coverage label is always visible text beside the symbol.

New, in the same visual language (card radius 14 px, `--fill` surfaces, hairline `--rule`):

| Component | States |
|---|---|
| `.readiness-bar` (existing) | four segments; a zero count has no segment but stays in the legend |
| `.cost-bars`, `.cost-bar`, `.cost-segment` | known; zero (no segment); unknown (`.is-unknown`); no inputs (chart omitted) |
| `details` disclosure | closed, open, `:focus-visible`, print (open). Summary in `--link`, chevron rotates 90° with `--ease` (not under reduced motion), min-height 44 px |
| Card | four statuses, each with or without `data-incomplete`. The surface is identical in all: only symbol colour and words differ. No coloured borders or tints. |

## 7. Print

- Hide `.bar` and the skip link. Light palette only (dark stays `screen`-scoped).
- `details::details-content { content-visibility: visible; display: block; block-size: auto }` for every `details`, including `.ready-group`; chevrons hidden.
- `.grid` becomes one column; `.sec-label` is not sticky; section padding 16pt.
- `break-inside: avoid` on cards, tiles, rows, cost rows, `tr` and timeline steps; `break-after: avoid` on headings and `summary`; `break-before: page` on `costs` and `appendix`.
- `print-color-adjust: exact` so bar fills print; cards gain a 0.5pt `--rule` border in case backgrounds are switched off.
- Body 10pt, h1 24pt, `@page { margin: 15mm }`.

## 8. Copy

Headings are statements. Status names are used exactly and never paraphrased: Ready, Needs work, Blocker, Unknown / Bereit, Handlungsbedarf, Hindernis, Unbekannt.

| Key | English | German |
|---|---|---|
| `header.title` | What leaving Microsoft 365 would take | Was ein Ausstieg aus Microsoft 365 erfordert |
| `summary.title` | Where the organisation stands | Wo die Organisation steht |
| `summary.blockers` | Blockers that matter | Hindernisse, auf die es ankommt |
| `summary.unknown` | What is not known | Was nicht bekannt ist |
| `readiness.title` | What stands in the way, area by area | Was dem Wechsel im Weg steht, Bereich für Bereich |
| `costs.title` | What five years would cost | Was fünf Jahre kosten würden |
| `moves.title` | What replaces what | Was wodurch ersetzt wird |
| `attention.title` | What needs a closer look | Was genauer geprüft werden muss |
| `path.title` | What to do next | Was als Nächstes zu tun ist |
| `found.title` | What the organisation runs today | Was die Organisation heute nutzt |
| `appendix.title` | How this report was made | Wie dieser Bericht entstanden ist |
| `readiness.next_step` | Next step | Nächster Schritt |
| `costs.less_than_staying` | {amount} less than staying | {amount} weniger als beim Verbleib |
| `costs.more_than_staying` | {amount} more than staying | {amount} mehr als beim Verbleib |
| `costs.total_unknown` | Total unknown | Summe unbekannt |

Rules: no "score", "recommended", "best", "safe", "easy". A cost difference is described as less or more, never as a saving. Every new string exists in both locales; every `th`/`td` `data-label` is a locale string. The German strings here and all new German `next_step` sentences need a native-speaker pass before merge. Both languages use the same markup and CSS; no rule may depend on text length.

## 9. What must not change

**Honesty.** No overall score, grade, percentage or supplier recommendation. Unknown is never grouped with, coloured like or counted as Ready. A skipped collector never improves a status. Every figure carries measured, provided or unknown in words. Sample and invented data keep their labels. Status is always symbol plus word.

**Privacy and security.** CSP unchanged. One `<style>`, two embedded fonts, no other `url()`, no script, `img` or form, every `href` starts with `#`, no link in the footer, autoescape on, no person names or email addresses.

**Hooks kept exactly.** Every `data-*` attribute in the current template keeps its name, values, attribute order and host element unless listed below. `data-subsection` keeps the order `not-examined`, `cannot-be-moved`, `run-details`. Also kept: classes `status {status}`, `subtotals`, `totals`; ids `readiness-title`, `readiness-{workload}`, `software-title`; the `:root` and dark token blocks; `a:hover { color: var(--accent-hover); }`; a `(max-width: 40rem)` query; `content: attr(data-label)`; `@page { margin: … }`; the print `::details-content` rule.

**Permitted test and checker edits, and no others:**

1. `SECTION_ORDER` gains `summary` and takes the order in section 1.
2. Readiness rows: `<tr data-workload=… >…</tr>` becomes `<article data-workload=… >…</article>`; regexes change the tag only. `<li data-evidence=…><strong>` becomes `<div data-evidence=…><dt>`. `site/check_site.py` counts `article[id^="readiness-"]` in place of `tr`.
3. Tests that read `data-segment` look in the `summary` section and expect the order Blocker, Needs work, Unknown, Ready.
4. Tests that slice `found` for per-area evidence or the directory note slice `readiness`.
5. Moves rows: assertions on the reason text inside a `data-function` row are removed; status label and link assertions stay.
6. New assertions are added for: summary caps, `next_step` present on every non-ready rule in both languages, unknown cost never rendered as a zero-width or zero-value segment, cost-bar text equals table amounts, navigation links resolve to ids.

## 10. Wireframes

Desktop, 1280 px (content 1120 px; label column 4/12, body 8/12):

```
[fazit            Summary  Areas  Costs  Replacements  Closer look  Next steps  Appendix]  sticky
Stadtverwaltung Musterstadt
What leaving Microsoft 365 would take                                   (h1, display)
Evidence 2 Nov 2026 · Inputs 10 Nov 2026 · openDesk · 0.1.0             (footnote row)
[ The scan measurements in this report are simulated. ]                 (.note)
------------------------------------------------------------------------------------------
Where the          1 area is a blocker, 9 need work, 1 is unknown and 4 are ready.  (lead)
organisation       [##|##################|##|########]   bar: Blocker Needs work Unknown Ready
stands             legend: symbol, word and count for each status
                   +--------------------------+ +--------------------------+
                   | Partial exit, five years | | Full exit, five years    |
                   | EUR 72,200.00            | | EUR 135,650.00           |
                   | less than staying · ...  | | less than staying · ...  |
                   +--------------------------+ +--------------------------+
                   | Latest notice date (1.1) | | Next renewal (1.1)       |
                   Blockers that matter   [ Telephony · reason ]
                   What is not known      [ Power Platform · fix ]  Everything not examined >
------------------------------------------------------------------------------------------
What stands in     Blocker · 1
the way, area      +------------------------------------------------------------+
by area            | Telephony                                                  |
                   | (!) Blocker                                                |
                   | Reason sentence.  Next step: one sentence.                 |
                   | > Evidence · 1 measured, 2 provided  · target line         |
                   +------------------------------------------------------------+
                   Needs work · 9      (cards)
                   Unknown · 1         (card)
                   > Ready · 4  Show   (closed)
                   Not examined        (list)
------------------------------------------------------------------------------------------
What five years    Legend: [#] Running [▒] Direct project [░] Productivity loss [//] Parallel
would cost         Stay                                                   EUR 600,000.00
                   [################################################################]
                   Partial exit              EUR 527,800.00 · EUR 72,200.00 less than staying
                   [#############################################|▒▒▒▒|░|////]
                   Full exit                 (same pattern)
                   (table, always visible)   > Cost inputs
------------------------------------------------------------------------------------------
then: replacements table / closer look / next steps (timeline) /
inventory tiles, > licences / appendix (> parts) / footer
```

Phone, 375 px (one column, 16 px gutter; label above body):

```
[fazit  Summary  Areas  Costs  Repl… →]   scrolls sideways
organisation / h1 (three lines) / meta row / [ sample note ]
Where the organisation stands
status sentence / [#|#########|#|####] / legend (two lines)
[ Partial exit tile ]
[ Full exit tile ]
Blockers that matter [rows] / What is not known [rows]
What stands in the way, area by area
Blocker · 1
[ card: area / status / reason / next step / > Evidence / target ]
What five years would cost
Stay  EUR 600,000.00
[##################]
block values, one per line; then the table
```

## 11. Acceptance criteria

1. One HTML file; the CSP string is byte-identical to today's; no script, `img`, `form` or external reference; every `href` starts with `#`.
2. At 1280 × 800 the first screen shows title, status sentence, readiness bar, legend and the first tile row, in both languages and both samples.
3. The summary shows at most 3 blockers and at most 4 unknown rows, in the stated order; it shows no score, percentage or recommendation.
4. Areas render as `article.finding` in the order Blocker, Needs work, Unknown, Ready; Ready is inside a closed `details`; every non-ready card has a reason and a next step; evidence disclosures are closed by default.
5. Unknown is never shown as Ready, zero, blank or a dash, in cards, tiles or the chart. A report built with a missing cost input shows a dashed unknown segment, "Total unknown", no difference, and `data-amount="unknown"` in the table.
6. Each cost bar's listed amounts equal the table's amounts for the same scenario; with no inputs there is no chart.
7. Every status shows symbol and word; every figure shows measured, provided or unknown as text; no pill shapes exist in the CSS (`.prov` has no border, background or radius).
8. At 360 px there is no horizontal page scroll and no word breaks inside a number or unit; the top bar scrolls sideways; touch targets are at least 44 px.
9. Light and dark both pass the existing contrast test; the report/site token test passes unchanged.
10. Tab reaches the skip link, every nav link and every `summary` in order with a visible focus ring. One `h1`, heading levels never skip, each `article` is labelled by its area name, bars are `aria-hidden` with their values in text.
11. Print to PDF (A4): no top bar, every `details` open, no card, tile or table row split across pages, costs and appendix start on a new page, bar fills visible.
12. German and English reports have identical element structure (same tags, classes and hooks in the same order).
13. Every reused component's rules match `site/style.css` declaration for declaration, apart from the icon technique and the `.finding-status` size. No spacing value lies outside the scale.
14. A side-by-side of the site and the report at 1280 and 375 px, in light and dark, looks like one product: same bar, section frame, tiles, card, table, timeline, type and spacing. Both reviewers sign this off.
15. Existing tests pass, with selectors and section names updated only as section 9 permits; new tests from section 9 item 6 exist; all six "Done means" commands in `AGENTS.md` succeed; both demo reports are regenerated into `site/demo/`.

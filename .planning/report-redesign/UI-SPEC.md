# UI-SPEC: Fazit report redesign

Design contract, revision 3, with both reviews and the filter request applied. One design, no options.

Scope: the report template, both locales, `rules/findings.yaml`, `rules/status.yaml`, `catalogue.py`, `rules.py`, `report.py`, `icons/`, and the tests and `site/check_site.py` only where section 9 permits.

## 0. Intent

Today the report opens with inventory tiles and a licence table; readiness starts three screens down in a four-column table. The redesign puts the verdict first, turns each area into a card the reader can filter, draws the costs, and makes the report look like the website. What is measured, provided or unknown does not change. There is no script of any kind.

**If the site has the component, copy its rules from `site/style.css`.** The only exceptions are listed in 6.2.

## 1. Page order and first screen

`SECTION_ORDER` becomes `header, summary, readiness, costs, moves, attention, path, found, appendix, footer`.

A cold reader asks: can we move, what stops us, what does it cost. The first screen answers the first two; costs and unknowns follow directly.

**Display order of statuses** is Blocker, Needs work, Unknown, Ready. The report sorts its own copy (`report.py`). It never reorders the `STATUSES` tuple, which the rule engine uses for severity.

### 1.1 Header

`<header data-section="header">` with the site's `.page-intro` rules: organisation as `.eyebrow`, `h1`, `dl.report-meta` as one wrapping row at `--fs-footnote` (`display: flex; flex-wrap: wrap; gap: 4px 24px; margin-top: 16px`, hooks kept), the sample note as `.note` (`margin-top: 24px`). The local and offline sentences move to run details.

### 1.2 Summary (`data-section="summary"`, new)

In this order:

1. **Count line.** `.status-legend` at `--fs-lead`, introduced by "Of 15 areas:" in `--fg-2`: symbol, status name, count; zero counts stay. This is the only count line in the summary. No sentence, score or percentage.
2. **Readiness bar**: the existing `.readiness-bar` and hooks, in display order. Height 12 px, gap 2 px, radius 999 px.
3. **What blocks the move** (`div.subsection` > `h3` + `dl.rows`; `h3 + .rows { margin-top: 12px }`). Under the heading: "Confirmed blockers: {shown} of {total}" and a link "All blockers" to `#status-blocker`. At most **3** rows, catalogue order. `dt`: area name linking to its card, plus "Evidence incomplete" when the row is incomplete. `dd`: the deciding rule's reason, unshortened. With no blocker: `path.empty.blocker`, and whenever any area is Unknown or incomplete: "{n} areas are Unknown or have incomplete evidence, so a Blocker cannot be ruled out."
4. **Cost tiles** (`ul.tiles.tiles-2`), one per move scenario:
   - `.tile-label`: "Partial move · five-year difference from staying".
   - Anchor (`.figure-num` at `--fs-headline`, `white-space: nowrap`): the absolute difference, formatted by `Formatter.money` in the input currency.
   - Under it, in `.tile-title` style: "less than staying", "more than staying", "the same as staying" (difference exactly zero), or "differs by less than one cent".
   - Detail `p`: the cost origin (`data-cost-origin`: calculated, or calculated from sample or invented inputs).
   - **Unknown comparison** (either total unknown): the anchor is the Unknown status label, never a number or dash. The detail shows the scenario's own total if it is known ("Total EUR 507,800.00"), then "{n} inputs are missing", where n counts distinct missing input paths across that scenario and Stay, linking to `#costs-missing`.
5. **Decision window** (ships with Phase 1.1, D-90; absent before): two tiles, "Next renewal" and "Latest notice date", each with `data-decision` and `data-provenance`. They reuse Phase 1.1's date calculation, source and `as_of` fallback. An end date without a notice period gives a Provided renewal and an Unknown notice date; each tile names only the input it lacks. The planned `licence-contract` detail stays in `found`.
6. **What is still unknown** (same structure as 3): at most **4** rows. Areas that are Unknown or incomplete, deduplicated, in catalogue order. `dd`: for an Unknown area, the fix for `row.reason_code`; for an incomplete decided area, the fix of its first missing item. Then two links: "Everything not examined" to `#not-examined`, and "{n} inputs are missing" to `#costs-missing` with `costs.missing_fix`. Never omitted; with nothing unknown it shows `path.empty.unknown`.

## 2. Areas (`data-section="readiness"`)

Exactly one card per workload, in `div.areas`, replaces the table. `h2#readiness-title` stays. Order inside: filters, status groups, empty state, not-examined list.

### 2.1 Grouping

Four `div.status-group[data-status-group]` in display order, each with `h3#status-{status}` showing symbol and status name. Empty groups are omitted. **Inside a group, catalogue order**, so Copilot follows Licences wherever both share a group (D-81 as amended, section 9).

Ready cards are **compact**, not hidden: no next step, no missing list, `padding: 16px 24px`, and the status at `--fs-body` on the line under the area name. Nothing is collapsed, so links, search and the keyboard always reach every card.

### 2.2 Filters (no script)

Two groups of real radio inputs read by CSS `:has()`. No `<form>` element (tests forbid it; radios group by `name`).

```html
<div class="filters">
  <fieldset class="segmented" data-filter="status">
    <legend class="sr-only">Show areas by status</legend>
    <label><input type="radio" name="f-status" id="f-status-all" checked>All · 15</label>
    <label><input type="radio" name="f-status" id="f-status-blocker">{{ icon }}Blocker · 1</label>
    …
  </fieldset>
  <fieldset class="segmented" data-filter="category">…f-category-all (checked), f-category-{id}…</fieldset>
  <p class="note-text">…search hint…</p>
</div>
```

- **Status pills**: symbol, exact status name, count; a status with count 0 is `disabled`. **Category pills**: label only, since a count would not follow the status filter.
- **Look**: an Apple segmented control. Track: `display: inline-flex; padding: 2px; gap: 2px; border-radius: var(--radius-pill); background: var(--fill)`. Segment (`label`): `min-height: var(--hit); padding: 0 16px; border-radius: var(--radius-pill); font: 600 var(--fs-subhead)`, colour `--fg-2`. Selected (`label:has(:checked)`): `background: var(--bg); color: var(--fg); box-shadow: 0 1px 3px rgb(0 0 0 / 12%)`. Hover: `--fg`. Disabled: 40% opacity. Focus: `label:has(:focus-visible)` takes the site's focus ring. Background transition 0.2 s `--ease`, none under reduced motion. Below 40rem the track wraps and takes `--radius-card`. `fieldset` has no border, margin or padding; 12 px between tracks and before the hint.
- **Inputs** are hidden with the `.sr-only` rules, never `display: none`: Tab reaches each group, arrow keys move and select, screen readers announce group, option, position and state.
- **Rules**, all inside `@media screen` and `@supports selector(:has(*))`, generated by a Jinja loop over status and category ids (`R` = `[data-section="readiness"]`):
  1. `R:has(#f-status-S:checked) .status-group:not([data-status-group="S"]) { display: none }`
  2. `R:has(#f-category-C:checked) .finding:not([data-category="C"]) { display: none }`
  3. `R:has(#f-category-C:checked) .status-group:not(:has(.finding[data-category="C"])) { display: none }`
  4. `R:has(#f-status-S:checked):has(#f-category-C:checked):not(:has(.finding[data-status="S"][data-category="C"])) .areas-empty { display: block }`
  5. A card that is the `:target` of a link, and its group, always show.
- The filters combine (status AND category). The two "All" options are the default and the reset. Filters hide area cards on screen and nothing else.
- **Empty state**: `p.areas-empty.note`, hidden by default, centred, `--fg-2`, no symbol; text in section 8.
- **Hint**, one line; text in section 8.
- Without `:has()`, `.filters` is hidden (`@supports not selector(:has(*))`) and every card shows. Print ignores the filters and hides the controls.

**Categories** live in the catalogue. `rules/findings.yaml` gains a top-level `categories:` list (`id`, `label: category.{id}`) in the order below, and every `workloads:` entry gains a required `category:`. `catalogue.py` loads both and rejects a missing or unregistered value.

| id | English | German | Areas, in catalogue order |
|---|---|---|---|
| `communication` | Communication | Kommunikation | mail, teams, telephony |
| `files` | Files and documents | Dateien und Dokumente | onedrive, sharepoint, office_files |
| `identity_devices` | Identity and devices | Identität und Geräte | directory, device_management, windows_software, identity_access |
| `automation_ai` | Automation and AI | Automatisierung und KI | copilot (1.1, first), power_platform, small_apps, integrations |
| `security` | Security and compliance | Sicherheit und Compliance | security_compliance |
| `contracts_costs` | Contracts and costs | Verträge und Kosten | licences |

### 2.3 Card: the site's finding card

```html
<article data-workload="mail" data-status="needs_work" data-incomplete
         data-category="communication" class="finding" id="readiness-mail" aria-labelledby="area-mail">
  <h4 class="finding-area" id="area-mail">Mail <span class="finding-category">Communication</span></h4>
  <p class="finding-status">{{ workload_status(row) }}</p>
  <div class="finding-reason">…reason…</div>
  <p class="finding-next"><strong>Next step</strong> …</p>
  <div class="finding-missing">…Evidence still needed, li[data-missing]…</div>
  <details class="workload-evidence" data-evidence-workload="mail">
    <summary>Evidence · 4 measured, 1 provided, 1 unknown</summary>
    <ul class="rule-evidence">…li[data-evidence], markup as today…</ul>
    <table class="coverage">…tr[data-finding], as today…</table>
  </details>
  <p class="finding-target">…</p>
</article>
```

The first three attributes keep this order. `status_label` and `workload_status` are unchanged; the "Evidence incomplete" marker is restyled as `.note-text`.

- **Status is the anchor.** Site rules, with `.finding-status` at `--fs-headline` inside `.areas` (sixteen cards, not one).
- **Category**: `.finding-category`, weight 400, `--fg-2`, after a middle dot.
- **Reason**: exactly what `status_reason` gives today, unshortened. A rule with two sentences keeps both (the Windows-software rule distinguishes the desktop dependency from the Microsoft 365 move). Notes from other fired rules follow as a list.
- **Next step** (`.finding-next`: `max-width: 36em; margin-top: 12px`). `StatusRule` (frozen) gains `next_step`; `rules.py` accepts and requires it in both languages for every problem rule, and `status.yaml` supplies it for all 31. Each is one sentence: an action and who typically owns it, no supplier or product. The card shows the deciding rule's action. For an Unknown area the reason is the label of `row.reason_code` and the next step is its fix, rendered separately. Ready cards have none.
- **Evidence still needed** (`.finding-missing`: `margin-top: 16px; font-size: var(--fs-subhead)`) lists every gap and stays outside the disclosure.
- **Evidence disclosure**: rendered, closed, whenever the area has catalogue observations (`groups`) or rule evidence (`row.evidence`, which includes derived licence signals). The summary counts each observation once across both lists, by provenance. Inside: the rule evidence first (`ul.rule-evidence`, laid out with the site's `.evidence` grid values: three columns from 640 px, gaps 24 and 32 px), then the full finding table, both through today's `evidence_pair` macro, so precedence, competing observations, conflicts, source, date, period, coverage, "at least" and "in the items checked" wording, `caption[data-sample]` and the sample note are preserved.
- **Target line** (`.finding-target`): at most two mapped functions with coverage label and check date, then a link "All replacements" to `#moves-title`. `mapping.no_function` areas show `moves.no_function`.

### 2.4 Measured, provided, unknown

Provenance is a word in a sentence in `.evidence-meta`, the provenance word first at weight 600 in `--fg`: "**Measured** · Sample licence inventory · 2 November 2026 · Complete, 3 of 3 scanned". `.prov` and `data-provenance` stay where they are; `.prov` has no border, background or radius. Only provenance is barred from pill shapes.

An unknown value shows the Unknown status label where the figure would be, with reason and fix. Never blank, zero, a dash or styled as measured.

`div[data-subsection="not-examined"]` stays at the end of this section with `id="not-examined"`. It is the full index: Unknown areas, every `row.missing` gap (new hook `data-unexamined-gap`), unknown findings and skipped collectors.

## 3. Costs (`data-section="costs"`)

Order: the chart, the results table, the rounding note, missing inputs (`id="costs-missing"`, with `costs.missing_fix`), the `Cost inputs` disclosure. Both tables keep their `caption[data-invented-amounts]`.

### 3.1 The chart (`.cost-bars`, new)

Three rows: Stay, Partial move, Full move. Each has a heading line (scenario left; total, difference and cost origin right), the bar, and the block values in text.

- **One scale.** `--share` = the row's sum of known blocks ÷ the largest such sum across the three rows, set in an inline `style` with `flex-grow` (numbers only). A zero denominator draws no fill.
- The bar is `div.cost-bar[aria-hidden="true"]`: flex, 24 px high, radius 999 px, gap 2 px. Its filled part is `calc(var(--share) * (100% - 56px))` wide, so the unknown marker sits outside the scale.
- Segments are `span.cost-segment[data-chart-block]` (not `data-block`: a test counts those) with `flex-grow` = the block amount and `min-width: 2px`. Four solid tints, no status colour, no pattern: running `--fg`; direct project `--fg-2`; productivity loss `color-mix(in srgb, var(--fg-2) 55%, var(--bg))`; parallel running `color-mix(in srgb, var(--fg-2) 25%, var(--bg))`. A wrapping `.legend` names each swatch.
- **Exact values are text**: every block with its amount, in table order. An explicit zero reads "EUR 0.00" and has no segment. "Not applicable" lines are omitted.
- **Unknown is never zero; pattern means only Unknown.** A row with any unknown block ends in `span.cost-segment.is-unknown`: 48 px, transparent, 1 px dashed `--fg-2`, help symbol. The heading reads "Total unknown"; the values line reads "Total of known blocks EUR X", then names every unknown block as Unknown. No difference is shown. With every block unknown, the row shows the marker and Unknown alone.
- The chart is omitted when the cost inputs are absent or entirely null; `costs.provide_inputs` appears in `.note`.

### 3.2 The table

The results table keeps its structure, hooks and plain-text cells, and is always visible, with the site's `.coverage` padding and header style. The old `table:not(.cost-table)` card-stack rules are deleted; other tables use the site's `.coverage` stacked layout. In the `(max-width: 40rem)` query each `.cost-table` row stacks: heading, then one line per scenario with `content: attr(data-label)` left and the amount right, so long German amounts never clip.

## 4. Every current section

| Current | Decision | Reason |
|---|---|---|
| Header | Keep, shortened | 1.1. |
| Headline tiles | Move to `found`, after `path` | Inventory is context. `ul.tiles.tiles-2`; today's `value_text` output (with its "at least" wording) in `.figure-num`; no nav link. |
| Licence products | Keep in `found`, in a closed `<details>` | Reference. Summary from `product_count` with its provenance, including Unknown for an empty partial inventory. |
| Evidence behind the figures | Merge into the area cards | Evidence belongs beside its status. |
| Cost comparison | Keep; chart added; after the areas | Obstacles before price. |
| Readiness | Keep; cards, filters; bar moves to the summary | Section 2. |
| What moves where | Keep as the site's `.coverage` table | Columns: Microsoft function; Replacement (`.cov-cell`: symbol, coverage label at 600, replacement on line two); Checked on (no-project-check wording kept); Area status (`workload_status` with its incomplete marker, linked to the card with `aria-label` "{area}: {status}" and an underline). No-function lines kept. |
| Needs attention | Keep | File types as `.coverage`; software counts as `dl.rows`; transfer gaps stay `ul.mapping-gaps > li[data-gap]`, styled as rows. |
| Suggested path | Keep; the site's `.timeline` | Steps: blockers, unknowns, ready areas (path hooks unchanged). `.on` marks the first non-empty of blockers and unknowns; the Ready step is `.on` only when no area is Blocker, Unknown or Needs work. What follows `.timeline` gets `margin-top: 64px`: pilot sentences, then `ol.steps`. |
| Appendix | Keep; parts in closed `<details>` except run details | Run details stay open and carry the local and offline sentences. |
| Footer | Unchanged | |

Each `<section data-section="…">` tag stays literal, with no added class or id; the site's frame is an inner `div.sec.grid`. Links target heading ids.

## 5. Navigation

`div.bar > .bar-in > a.wordmark[href="#main"] + nav.bar-links[aria-label] > .bar-links-in`, sticky, seven links: Summary, Areas, Costs, Replacements, Closer look, Next steps, Appendix. `main` has `id="main"`; `.skip` is first in `body`; `html { scroll-padding-block-start: calc(var(--bar-h) + 16px) }`. Hidden in print.

## 6. Tokens and components

### 6.1 Tokens

- The report's `:root` and dark `@media` block keep their names and mechanism (a test parses them). A second rule adds the site's names so site CSS pastes in: `--fg`, `--fg-2`, `--rule`, `--fill`, `--link`, `--link-hover` as aliases; `--solid-bg`, `--solid-fg`, `--link-glow` with the site's values per palette; `--sans`, `--mono`, `--ease`, `--gutter`, `--max: 1120px`, `--bar-h: 52px`, `--hit: 44px`, `--radius: 8px`, `--radius-pill: 999px`.
- Margin reset: `h1, h2, h3, h4, p { margin: 0 }`.
- Type: `--fs-display` h1; `--fs-title` inventory figures; `--fs-headline` section labels, card status, money in tiles; `--fs-lead` count line; `--fs-subhead` tables, tile detail, filters; `--fs-footnote` provenance and meta. Weights 400 and 600.
- Spacing: 4, 8, 12, 16, 24, 32, 48, 64, 96 px and the site's clamps; exceptions are the 20 px gutter and the 2 px bar and track gaps.

### 6.2 Components

Reused from the site:

| Report use | Site selector |
|---|---|
| Section frame, label left from 880 px | `.sec`, `.grid`, `.sec-label`, `.sec-body`, `.sec-intro`, `.subsection` |
| Header | `.page-intro`, `.eyebrow` |
| Bar, skip link | `.bar`, `.bar-in`, `.wordmark`, `.bar-links`, `.bar-links-in`, `.skip`, `.sr-only` |
| Tiles | `.tiles`, `.tiles-2`, `.tile-label`, `.tile-title`, `.figure-num` |
| Area card | `.finding`, `.finding-area`, `.finding-status`, `.finding-reason`, `.evidence-meta`, `.finding-target` |
| Tables | `.coverage`, `.cov-cell`, `.cov`, `.table-note`, its 600 px stacked layout |
| Lists | `.rows`, `.steps`, `.timeline` and its parts |
| Notes, legend | `.note`, `.note-text`, `.legend` |
| Links, focus ring, code | `a`, `:focus-visible`, `code` |

Exceptions to copying, and no others:

1. **Resources.** The two embedded font data URLs are the only `url()`. Site font paths, icon masks and rules that depend on the site's script (menu, reveal, copy) are not copied.
2. **Symbols** are inline `<svg class="icon"><path>` at the site's sizes, never `use`. `contrast`, `code` and `cancel` are packaged in `icons/` and registered in `report.py`.
3. **Bar.** `div.bar`, not `header.bar` (tests split on the report's one `header`). Below 820 px there is no menu: `.bar-in { display: flex }`; `.bar-links { min-width: 0; overflow-x: auto; scrollbar-width: none; padding: 4px; mask-image: linear-gradient(to left, transparent, #000 32px) }` so the row visibly continues and focus rings are not clipped; links `inline-flex`, `min-height: var(--hit)`.
4. **Hover** stays `a:hover { color: var(--accent-hover); }` (a test matches the text).
5. **Coverage label is visible**, because a printed report has no legend nearby.
6. **Cards** in `.areas`: status size, compact Ready cards, and evidence kept as today's list markup in place of the site's `dl.evidence` (2.1, 2.3).

Coverage symbols are drawn in `--fg`, cancel in `--fg-2`, never a status colour: `in_suite` check-circle; `in_suite_with_limits` contrast; `open_source_community`, `open_source_third_party` code; `announced`, `component_vendor_solution`, `proprietary_third_party`, `not_available` cancel.

New, in the same visual language:

| Component | States |
|---|---|
| `.cost-bars`, `.cost-bar`, `.cost-segment` | known; zero; unknown (`.is-unknown`); all unknown; chart omitted |
| `.filters`, `.segmented` | segment: default, hover, selected, focus-visible, disabled; track: inline, wrapped; hidden (print, no `:has()`) |
| `details` | closed, open, focus-visible, print. Summary in `--link`, chevron rotates 90° with `--ease` (not under reduced motion), min-height 44 px |
| Card | four statuses, with or without `data-incomplete`; compact (Ready); filtered out; link target. Same surface in all: only symbol colour and words differ, no coloured borders or tints |

## 7. Phone and print

**Phone (360 px).** One column, 16 px gutter. Meta row, legends and filter tracks wrap; cost heading wraps, block values one per line, cost table rows stack (3.2). No horizontal page scroll.

**Print.**

- Hide `.bar`, `.skip`, `.filters`, `.areas-empty`. Filter rules are screen-only. Light palette.
- Every `details` open: `details::details-content { content-visibility: visible; display: block; block-size: auto }`; chevrons hidden.
- Type in pt: display 24, title 18, headline 14, lead 12, body 10, subhead 9, footnote 8. Card padding 12pt, section padding 16pt. One column; tiles two columns.
- Breaks: the card head (area, status, reason, next step) stays together; evidence may break between rows; `thead { display: table-header-group }`; `.table-scroll { overflow: visible }`. `break-inside: avoid` on tiles, rows, cost rows and `tr`. `break-before: page` on `costs` and `appendix`.
- `print-color-adjust: exact`; 0.5pt `--rule` borders on cards, tiles, rows, notes and bar segments, so everything stays legible with backgrounds off; links in `--fg`. `@page { margin: 15mm }`.

## 8. Copy

Status names are used exactly and capitalised: Ready, Needs work, Blocker, Unknown / Bereit, Handlungsbedarf, Hindernis, Unbekannt. German is formal and administrative. The word is "move" / "Umstieg".

| Key | English | German |
|---|---|---|
| `header.title` | What leaving Microsoft 365 would take | Was ein Umstieg von Microsoft 365 erfordert |
| `summary.title` | Where the organisation stands | Wo die Organisation steht |
| `summary.of_areas` | Of {n} areas: | Von {n} Bereichen: |
| `summary.blockers` | What blocks the move | Was dem Umstieg entgegensteht |
| `summary.confirmed` | Confirmed blockers: {shown} of {total} | Bestätigte Hindernisse: {shown} von {total} |
| `summary.all_blockers` | All blockers | Alle Hindernisse |
| `summary.caveat` | {n} areas are Unknown or have incomplete evidence, so a Blocker cannot be ruled out. | {n} Bereiche sind unbekannt oder unvollständig belegt; ein Hindernis lässt sich daher nicht ausschließen. |
| `summary.unknown` | What is still unknown | Was noch unbekannt ist |
| `summary.not_examined` | Everything not examined | Alles, was nicht geprüft wurde |
| `readiness.title` | Where each area stands | Wo jeder Bereich steht |
| `readiness.next_step` | Next step | Nächster Schritt |
| `readiness.evidence_summary` | Evidence · {measured} measured, {provided} provided, {unknown} unknown | Nachweise · {measured} gemessen, {provided} angegeben, {unknown} unbekannt |
| `readiness.all_replacements` | All replacements | Alle Ersatzlösungen |
| `filter.status_legend` | Show areas by status | Bereiche nach Status anzeigen |
| `filter.category_legend` | Show areas by category | Bereiche nach Kategorie anzeigen |
| `filter.all` / `all_categories` | All / All categories | Alle / Alle Kategorien |
| `filter.empty` | No area matches this selection. Choose "All" to see every area. | Kein Bereich entspricht dieser Auswahl. Wählen Sie „Alle“, um alle Bereiche anzuzeigen. |
| `filter.search_hint` | Ctrl+F or Cmd+F searches the report. Filtered-out areas and, in some browsers, closed sections are not searched. | Mit Strg+F oder Cmd+F durchsuchen Sie den Bericht. Ausgeblendete Bereiche und, je nach Browser, geschlossene Abschnitte werden nicht durchsucht. |
| `costs.title` | What staying and moving cost over five years | Was Verbleib und Umstieg in fünf Jahren kosten |
| `costs.partial_exit` / `full_exit` | Partial move / Full move | Teilweiser Umstieg / Vollständiger Umstieg |
| `costs.difference_label` | {scenario} · five-year difference from staying | {scenario} · Differenz zum Verbleib über fünf Jahre |
| `costs.less` / `more` / `same` | less than staying / more than staying / the same as staying | weniger als beim Verbleib / mehr als beim Verbleib / gleich viel wie beim Verbleib |
| `costs.sub_cent` | differs by less than one cent | weicht um weniger als einen Cent ab |
| `costs.total_unknown` | Total unknown | Summe unbekannt |
| `costs.known_blocks` | Total of known blocks {amount} | Summe der bekannten Blöcke: {amount} |
| `costs.inputs_missing` | {n} inputs are missing | {n} Angaben fehlen |
| `costs.missing_fix` | Enter the missing amounts in the inputs file and build the report again. | Tragen Sie die fehlenden Beträge in die Eingabedatei ein und erstellen Sie den Bericht erneut. |
| `moves.title` | What replaces what | Was wodurch ersetzt wird |
| `attention.title` | What needs a closer look | Was genauer zu prüfen ist |
| `path.title` | What to do next | Was als Nächstes zu tun ist |
| `found.title` | Recorded inventory | Erfasster Bestand |
| `appendix.title` | How this report was made | Wie dieser Bericht entstanden ist |
| `nav.*` | Summary, Areas, Costs, Replacements, Closer look, Next steps, Appendix | Überblick, Bereiche, Kosten, Ersatz, Prüfbedarf, Nächste Schritte, Anhang |
| `mapping_coverage.*` (German only) | unchanged | In der Suite; In der Suite mit Einschränkungen; Open-Source-Lösung der Community |

Locale keys keep their names; only values change. In the cost formulas "exit scenario" becomes "move scenario" and "Ausstiegsszenarien" becomes "Umstiegsszenarien". A cost difference is less or more, never a saving; no "score", "recommended", "best", "safe" or "easy". Every string exists in both locales; every `data-label` is a locale string. The 31 German `next_step` sentences need a native-speaker pass before merge.

## 9. What must not change

**Honesty.** No overall score, grade, percentage or supplier recommendation. Unknown is never grouped with, coloured like or counted as Ready. A skipped collector never improves a status. Every figure carries measured, provided or unknown in words; sample and invented data keep their labels; status is always symbol plus word. Filters only hide cards on screen: they change no count, status, summary or printed page. Rule evaluation, `STATUSES` and the cost model are untouched; `rules.py` changes only to load `next_step`.

**Privacy and security.** CSP unchanged. One `<style>`, two embedded fonts, no other `url()`, no `script`, `img`, `form`, SVG `use` or event-handler attribute, every `href` starts with `#`, no link in the footer, autoescape on, no person names or email addresses. Nothing is submitted or stored.

**Hooks kept exactly.** Every `data-*` attribute in the current template keeps its name, values, attribute order and host element unless listed below. `data-block` appears exactly four times in `costs`. Also kept: classes `status {status}`, `subtotals`, `totals`; ids `readiness-title`, `readiness-{workload}`, `software-title`; the token blocks; and the CSS the style test matches (a `(max-width: 40rem)` query, `content: attr(data-label)`, `@page { margin: … }`, `break-inside: avoid`, `print-color-adjust: exact`, the print `::details-content` rule).

**Decisions to record when this is built.** In `DECISIONS.md`: the departure from D-19, D-26 and D-64 (ten sections, cards in place of the table, new order). In `01.1-CONTEXT.md`, the **D-81 amendment**: area cards are grouped by status; inside a group they keep catalogue order, so Copilot follows Licences wherever both share a group; in the category filter Copilot is first under Automation and AI; the report sorts a display copy and never reorders `STATUSES`.

**Permitted test and checker edits, and no others:**

1. `SECTION_ORDER` and the CLI test's hardcoded nine sections take the ten in section 1. When Phase 1.1 ships, the `data-subsection` order assertion gains `licence-contract`.
2. Readiness rows: `<tr data-workload=…>…</tr>` becomes `<article data-workload=…>…</article>`; regexes change the tag only. `site/check_site.py` counts `article[id^="readiness-"]`.
3. CLI and simulation tests that assert catalogue order of readiness rows assert instead: group order, catalogue order inside each group, exactly one card per workload.
4. `data-segment` is read from `summary`, in display order.
5. The directory-note test slices `readiness` in place of `found`.
6. Conflict assertions are scoped to one evidence record, because a card shows an observation in two lists.
7. The headline `.figure` selector becomes `.figure-num`; the qualified-zero wording assertions stay.
8. Header assertions on the local and offline sentences look in run details.
9. Expectations that contain old scenario, coverage or title wording follow the locale.
10. Rule and catalogue fixtures gain `next_step` and `category`.
11. New tests: summary caps and deduplication; zero-blocker caveat; unknown comparison with a known total (the 507,800 case); one chart scale, unknown marker outside it, no chart for null inputs; chart text equals table amounts; a seven-digit amount on one line in a tile; `next_step` in both languages on all problem rules; every workload has a registered category and a matching `data-category`; two radio groups, one checked each, zero-count statuses disabled; filter rules inside `@media screen`; nav links resolve; no `script`, `form`, `use` or `on*`.

## 10. Wireframes

Desktop, 1280 px (content 1120 px; label 4/12, body 8/12):

```
[fazit            Summary  Areas  Costs  Replacements  Closer look  Next steps  Appendix]
Stadtverwaltung Musterstadt
What leaving Microsoft 365 would take
meta row                                                       [ sample note ]
-----------------------------------------------------------------------------------------
Where the         Of 15 areas:  (!) Blocker 1   /!\ Needs work 9   (?) Unknown 1   (v) Ready 4
organisation      [##|##################|##|########]
stands            What blocks the move      Confirmed blockers: 1 of 1 · All blockers
                  [ Telephony · reason ]
                  [ Partial move · five-year difference ] [ Full move · …              ]
                  [ EUR 72,200.00  less than staying    ] [ EUR 135,650.00  less than… ]
                  [ Next renewal (1.1) ]                  [ Latest notice date (1.1)   ]
                  What is still unknown
                  [ Security and compliance · fix ]   Everything not examined · inputs missing
-----------------------------------------------------------------------------------------
Where each        ( All · 15 | Blocker · 1 | Needs work · 9 | Unknown · 1 | Ready · 4 )
area stands       ( All categories | Communication | Files and documents | … )
                  search hint
                  (!) Blocker
                  [ Telephony · Communication / (!) Blocker / reason / next step ]
                  [ > Evidence · 1 measured, 2 provided / target line           ]
                  /!\ Needs work (9 cards)   (?) Unknown (1)   (v) Ready (4 compact)
                  [ empty state ]   Not examined (full index)
-----------------------------------------------------------------------------------------
What staying      legend
and moving cost   Partial move   EUR 527,800.00 · EUR 72,200.00 less than staying · origin
over five years   (#############################################|222|3|44)
                  block values in text      table      > Cost inputs
-----------------------------------------------------------------------------------------
replacements / closer look / next steps / recorded inventory / appendix / footer
```

Phone, 375 px: bar scrolls sideways with an edge fade; h1 on three lines; legend on two lines; blockers; tiles one per row; filter pills wrap; cards full width; cost heading stacked, block values one per line; cost table rows stacked.

## 11. Acceptance criteria

1. One HTML file; the CSP is byte-identical to today's; no `script`, `img`, `form`, SVG `use`, event-handler attribute or external reference; every `href` starts with `#`. The report works identically with scripting disabled.
2. At 1280 × 800 the first screen shows the title, the count line, the readiness bar and the first blocker row (or the zero-blocker sentence with its caveat), in both languages and both samples.
3. Counts appear once in the summary. At most 3 blockers, labelled "{shown} of {total}", and at most 4 deduplicated unknown rows. No score, percentage or recommendation.
4. Default view: one `article.finding` per workload, grouped Blocker, Needs work, Unknown, Ready, catalogue order inside each group; every non-ready card has a reason and a next step; every card shows its category; evidence disclosures start closed. `STATUSES` is unchanged.
5. A status filter shows only that group; a category filter shows only that category's cards and drops groups left empty; both combine; the two "All" options restore the default.
6. A combination with no match shows the empty state and no group heading; a status with count 0 is disabled.
7. Keyboard only: Tab reaches each filter group once; arrow keys move and select; the focus ring is visible; no trap. A screen reader announces group name, option, position, state and, for statuses, the count.
8. Filters change nothing outside the area cards; a link to a filtered-out card reveals it; without `:has()` the controls are absent and every card shows.
9. Print and PDF render the same with any filter active as with none.
10. Unknown is never shown as Ready, zero, blank or a dash. With Stay unknown and a move total known, the tile shows Unknown, the known total and the missing-input count. A row with an unknown block shows the dashed marker outside the scale, "Total unknown", every unknown block named, and no difference. No other segment has a pattern.
11. All three bars share one scale; listed amounts equal the table's; origins appear beside tile and chart values; null inputs give no chart.
12. Every status shows symbol and word; every figure shows measured, provided or unknown as text; `.prov` has no border, background or radius; coverage symbols use no status colour.
13. At 360 px: no horizontal page scroll; no break inside a number or unit; a seven-digit amount on one line in its tile; long German cost cells unclipped; the bar scrolls with visible continuation and unclipped focus; filter tracks wrap; targets at least 44 px.
14. Light and dark: the contrast and token tests pass; chart outlines, the unknown marker and the skip link's focus are visible in both.
15. One `h1`; levels never skip; each `article` is labelled by its area; repeated status links have area-specific names; bars are `aria-hidden` with values in text; Tab reaches the skip link, nav links and every `summary`.
16. Print (A4), checked on a real PDF: its text contains evidence from Ready cards, the licence table and every appendix part; no bar or filters; card heads unsplit; table headers repeat; costs and appendix start new pages; amounts and borders legible with backgrounds on and off.
17. Both languages have identical element structure; wording matches section 8.
18. Reused components match `site/style.css` declaration for declaration, apart from the six exceptions in 6.2; no spacing value outside the scale and its exceptions.
19. A side-by-side of site and report at 1280 and 375 px, light and dark, looks like one product; both reviewers sign this off.
20. Changing an area's `category` in the catalogue changes its card and filter result with no template edit.
21. Existing tests pass with edits only as section 9 permits; the new tests exist; all six "Done means" commands in `AGENTS.md` succeed; both demo reports are regenerated; the decisions in section 9 are recorded.

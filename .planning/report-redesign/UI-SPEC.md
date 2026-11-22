# UI-SPEC: Fazit report redesign

Design contract, revision 4, with both reviews, the filter request, the launch critique decisions and the usefulness review applied. One design, no options.

**Revision 4.1** (2026-11-22) adds the Apple-lens review (`.planning/research/apple-lens/REVIEW.md`, section 4 and copy bugs): one status list with counts and definitions; scope statement after the open questions; the blocker count line only when rows are cut off; the area name as every card's anchor; next steps before open points in "Worth doing even if you stay"; shorter search hint and Stay note; German provenance words.

**Revision 4** (2026-11-22) applies the founder's decisions on the usefulness review (`.planning/research/report-usefulness/SYNTHESIS.md`, sections A and C): findings, not a verdict; page one written for the council, on screen and in print; no readiness bar in the summary; three cost totals with the Stay assumption and a break-even line; one open-points list straight after the summary, split into what is worth doing even if the organisation stays and what only a move needs; scoped blocker wording; a coverage symbol that no status uses; a scope statement once RR-06 and RR-07 have landed. It also takes in the launch-critique changes already in RR-01: Licences has no status, card or category, and the area count comes from the catalogue. German copy marked *draft* needs the native review before merge.

Scope: the report template, both locales, `rules/findings.yaml`, `rules/status.yaml`, `catalogue.py`, the rule loaders, `report.py`, `icons/`, `site/icons/circle.svg`, and the tests and `site/check_site.py` only where section 9 permits.

## 0. Intent

Today the report opens with inventory tiles and a licence table; readiness starts three screens down in a four-column table. The redesign puts the findings first, turns each area into a card the reader can filter, draws the costs, and makes the report look like the website. There is no verdict, score or recommendation (D1, D20): the report says what a move would take, what stops it, what is still open and what it costs.

**Two readers, one document.** Page one (header and summary) is written for the council or committee, which usually receives the report printed with a Beschlussvorlage; it has the same content on screen and on paper. Everything after page one is the working file of the IT lead and the integrator. Specialists (finance, procurement, data protection, staff representation) get facts from the same findings, never their own narrative and never legal judgements. What is measured, provided or unknown does not change. There is no script of any kind.

**If the site has the component, copy its rules from `site/style.css`.** The only exceptions are listed in 6.2.

## 1. Page order and first screen

`SECTION_ORDER` becomes `header, summary, path, readiness, costs, moves, attention, found, appendix, footer`.

A cold reader asks: what would a move take, what stops it, what is still open, what does it cost. Page one answers all four in that order, with facts and open questions only. It never proposes what the council should decide.

**Display order of statuses** is Blocker, Needs work, Unknown, Ready. The report sorts its own copy (`report.py`). It never reorders the `STATUSES` tuple, which the rule engine uses for severity.

### 1.1 Header

`<header data-section="header">` with the site's `.page-intro` rules: organisation as `.eyebrow`, `h1`, `dl.report-meta` as one wrapping row at `--fs-footnote` (`display: flex; flex-wrap: wrap; gap: 4px 24px; margin-top: 16px`, hooks kept), the sample note as `.note` (`margin-top: 24px`). The local and offline sentences move to run details.

### 1.2 Summary (`data-section="summary"`, new)

The summary is page one's body. In this order:

1. **Statuses: count and meaning in one list** (`dl.status-summary`), introduced by "Of {n} areas:" in `--fg-2`, where n is the number of assessed areas in the catalogue (never a literal; 14 before Phase 1.1). Four rows in display order, zero counts kept. Each row: `dt` with symbol, status name and count at `--fs-lead`; `dd` with the definition from section 8 at `--fs-footnote` in `--fg-2`, on the same row from 640 px and wrapping under it below. Each status appears once, with its count and its meaning, so a printed page one explains its own words (launch critique B7). This is the only count in the summary. No sentence, score, percentage, bar, pie or other part-of-whole picture: a share of areas reads as "how ready are we".
2. **What blocks this move** (`div.subsection` > `h3` + `dl.rows`; `h3 + .rows { margin-top: 12px }`). Under the heading, only when the cap cuts rows off (total greater than shown): "Confirmed blockers: {shown} of {total}". Only when total is at least 1: a link "All blockers" to `#status-blocker`. At most **3** rows, catalogue order. `dt`: area name linking to its card, plus "Evidence incomplete" when the row is incomplete. `dd`: the deciding rule's reason, unshortened. With no blocker: `path.empty.blocker`, and whenever any area is Unknown or incomplete: "{n} areas are Unknown or have incomplete evidence, so a Blocker cannot be ruled out."
3. **What is still unknown** (same structure as 2): at most **4** rows. Areas that are Unknown or incomplete, deduplicated, in catalogue order. `dd`: for an Unknown area, the fix for `row.reason_code`; for an incomplete decided area, the fix of its first missing item. Then two links: "All open points" to `#not-examined`, and "{n} inputs are missing" to `#costs-missing` with `costs.missing_fix`. Never omitted; with nothing unknown it shows `path.empty.unknown`. It comes before the costs because an unknown changes how far the totals can be trusted.
4. **What the target covers** (ships with RR-07, after RR-06 removes the desktop inference; absent before, and absent for a profile without dated project sources, such as `generic`). `div.subsection` > `h3` "What {profile} covers". One line: "Of the {n} functions Fazit checks for {profile}:" then each coverage label present in the profile's mapping with its count, as text in `--fg` (the profile's own categories, never merged into three). Then `dl.rows` "Outside {profile} and needed here": each function whose transfer gap has the organisation's need Yes, linking to its gap; then "{n} more are outside {profile} and still Unknown here." Counts and names only: never a fraction, percentage or bar. The counts equal the replacements table. While the profile's mapping has no operator review date, the statement ends with the same unreviewed-mapping sentence the replacements section shows. It sits after the open questions and before the costs, matching the council's order: what stops it, what is open, what a move would take, what it costs.
5. **Cost tiles** (`ul.tiles.tiles-3`), one per scenario in the order Stay, Partial move, Full move:
   - `.tile-label`: "{scenario} · five-year total".
   - Anchor (`.figure-num` at `--fs-headline`, `white-space: nowrap`): the scenario total, formatted by `Formatter.money` in the input currency and **rounded to whole currency units**; the table keeps cents.
   - Main line (`.tile-title` style): for Stay, "Today's yearly costs for five years"; for a move, the absolute difference, also whole units, with "less than staying", "more than staying", "the same as staying" (difference exactly zero) or "differs by less than one cent".
   - Detail `p`: the cost origin (`data-cost-origin`: calculated, or calculated from sample or invented inputs). With invented prices the detail says so in words, not only in a caption.
   - **Unknown total**: the anchor is the Unknown status label, never a number or dash; the main line shows "Total of known blocks {amount}" when any block is known; the detail reads "{n} inputs are missing", counting distinct missing input paths of that scenario, linking to `#costs-missing`. **Unknown comparison** (a move total known, Stay unknown): the move tile shows its total and the main line reads "Comparison unknown" with the missing-input count.
   - Under the tiles, `p.note-text`: `costs.stay_assumption`, then one break-even line per move scenario whose comparison is known (section 3.3).
6. **Decision window** (ships with Phase 1.1, D-90; absent before): two tiles, "Next renewal" and "Latest notice date", each with `data-decision` and `data-provenance`. They reuse Phase 1.1's date calculation, source and `as_of` fallback. An end date without a notice period gives a Provided renewal and an Unknown notice date; each tile names only the input it lacks. The planned `licence-contract` detail stays in `found`.

**Page one.** Header and summary fill the first A4 page in both languages for both samples and for a report with every area Unknown; the next section starts a new page (section 7). Page one carries the organisation, evidence and answer dates, the sample or invented-price note, the definitions, blockers or the zero-blocker sentence, the open questions and the three totals with their origin. It never carries a proposed resolution.

## 2. Areas (`data-section="readiness"`)

Exactly one card per assessed workload, in `div.areas`, replaces the table. Licences has no status, card or category (launch critique C2); its evidence stays in `found`. `h2#readiness-title` stays. Order inside: the readiness bar, filters, status groups, empty state.

**No readiness bar.** Founder's decision on 2026-11-22, after the Apple-lens review: the segmented bar is removed from the report entirely, from the summary and from above the filters. A coloured bar reads as a score or progress; the status filter's counts carry the distribution.

### 2.1 Grouping

Four `div.status-group[data-status-group]` in display order, each with `h3#status-{status}` showing symbol and status name. Empty groups are omitted. **Inside a group, catalogue order.** Licences has no card, so Copilot is the first card of whichever group it is in (D-81 as amended, section 9).

Every card in `.areas` takes the area name as its anchor and the status (symbol and word) at `--fs-body` on the line under it, because the group heading already states the status. Ready cards are also **compact**, not hidden: no next step, no missing list, `padding: 16px 24px`. Nothing is collapsed, so links, search and the keyboard always reach every card.

### 2.2 Filters (no script)

Two groups of real radio inputs read by CSS `:has()`. No `<form>` element (tests forbid it; radios group by `name`).

```html
<div class="filters">
  <fieldset class="segmented" data-filter="status">
    <legend class="sr-only">Show areas by status</legend>
    <label><input type="radio" name="f-status" id="f-status-all" checked>All · {n}</label>
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

There is no `contracts_costs` category: Licences is not assessed (C2). The catalogue refuses a category on an unassessed area.

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

- **The area name is the anchor** inside `.areas` (`.finding-area` at `--fs-headline`); `.finding-status` at `--fs-body` under it, so the Needs work group does not repeat one large label nine times. A card shown alone, such as the site's example, keeps the site rule with the status as anchor. The status stays on every card, so a linked or printed card still states it.
- **Category**: `.finding-category`, weight 400, `--fg-2`, after a middle dot.
- **Reason**: exactly what `status_reason` gives today, unshortened. A rule with two sentences keeps both (the Windows-software rule distinguishes the desktop dependency from the Microsoft 365 move). A reason of a Needs work rule never says the area "blocks" anything; only a Blocker rule may (RR-06 rewords the Windows-software rule). Notes from other fired rules follow as a list.
- **Next step** (`.finding-next`: `max-width: 36em; margin-top: 12px`). `StatusRule` (frozen) gains `next_step`; `rules.py` accepts and requires it in both languages for every problem rule, and `status.yaml` supplies it for all 31. Each is one sentence: an action and who typically owns it, as a role from RR-01's fixed set, no supplier or product. Each also carries `kind`: `clarify` (find out, count, review), `decide` (the organisation must choose) or `replace` (work that only makes sense for a move), set per sentence from the action it names, not per rule type, and reviewed with the sentences. `rules.py` requires `kind` beside `next_step`. The card shows the deciding rule's action. For an Unknown area the reason is the label of `row.reason_code` and the next step is its fix, rendered separately. Ready cards have none.
- **Evidence still needed** (`.finding-missing`: `margin-top: 16px; font-size: var(--fs-subhead)`) lists every gap and stays outside the disclosure.
- **Evidence disclosure**: rendered, closed, whenever the area has catalogue observations (`groups`) or rule evidence (`row.evidence`, which includes derived licence signals). The summary counts each observation once across both lists, by provenance. Inside: the rule evidence first (`ul.rule-evidence`, laid out with the site's `.evidence` grid values: three columns from 640 px, gaps 24 and 32 px), then the full finding table, both through today's `evidence_pair` macro, so precedence, competing observations, conflicts, source, date, period, coverage, "at least" and "in the items checked" wording, `caption[data-sample]` and the sample note are preserved.
- **Target line** (`.finding-target`): at most two mapped functions with coverage label and check date, then a link "All replacements" to `#moves-title`. A function with a transfer gap the organisation needs (need Yes) comes first, so the two-function cap never hides it (Teams: chat history is the third mapping); then catalogue order. `mapping.no_function` areas show `moves.no_function`.

### 2.4 Measured, provided, unknown

Provenance is a word in a sentence in `.evidence-meta`, the provenance word first at weight 600 in `--fg`: "**Measured** · Sample licence inventory · 2 November 2026 · Complete, 3 of 3 scanned". `.prov` and `data-provenance` stay where they are; `.prov` has no border, background or radius. Only provenance is barred from pill shapes.

An unknown value shows the Unknown status label where the figure would be, with reason and fix. Never blank, zero, a dash or styled as measured.

The not-examined index moves to `path` as the open-points list (section 4.1), keeping `div[data-subsection="not-examined"]` and `id="not-examined"`.

## 3. Costs (`data-section="costs"`)

Order: the chart, the Stay assumption and break-even lines (3.3), the results table, the rounding note, `costs.vat_note`, missing inputs (`id="costs-missing"`, with `costs.missing_fix`), the `Cost inputs` disclosure. Both tables keep their `caption[data-invented-amounts]`.

The section prints as a unit, because finance detaches it: its intro line names the organisation, the evidence and answer dates and the price origin, and `costs.profile_note` says the costs come from the inputs file and are the same for every target profile. Productivity loss is labelled as an internal estimate, not a payment.

### 3.1 The chart (`.cost-bars`, new)

Three rows: Stay, Partial move, Full move. Each has a heading line (scenario left; total, difference and cost origin right), the bar, and the block values in text.

- **One scale, known totals only.** `--share` = the row's total ÷ the largest known total across the three rows, set in an inline `style` with `flex-grow` (numbers only). A zero denominator draws no fill. A row whose total is unknown draws no bar at all, so no reader compares a partial bar with a whole one.
- The bar is `div.cost-bar[aria-hidden="true"]`: flex, 24 px high, radius 999 px, gap 2 px. Its filled part is `calc(var(--share) * (100% - 56px))` wide, so the unknown marker sits outside the scale.
- Segments are `span.cost-segment[data-chart-block]` (not `data-block`: a test counts those) with `flex-grow` = the block amount and `min-width: 2px`. Four solid tints, no status colour, no pattern: running `--fg`; direct project `--fg-2`; productivity loss `color-mix(in srgb, var(--fg-2) 55%, var(--bg))`; parallel running `color-mix(in srgb, var(--fg-2) 25%, var(--bg))`. A wrapping `.legend` names each swatch.
- **Exact values are text**: every block with its amount, in table order. An explicit zero reads "EUR 0.00" and has no segment. "Not applicable" lines are omitted.
- **Unknown is never zero; pattern means only Unknown.** A row with any unknown block shows only `span.cost-segment.is-unknown` in place of the bar: 48 px, transparent, 1 px dashed `--fg-2`, help symbol. The heading reads "Total unknown"; the values line reads "Total of known blocks EUR X", then names every unknown block as Unknown. No difference is shown. With every block unknown, the row shows the marker and Unknown alone.
- The chart is omitted when the cost inputs are absent or entirely null; `costs.provide_inputs` appears in `.note`.

### 3.3 Stay assumption and break-even

- `costs.stay_assumption` states that staying assumes no price change; the Stay tile's main line already says it is today's yearly costs for five years. It appears under the summary tiles and under the chart.
- **Break-even**, one line per move scenario whose comparison is known: the yearly target operations cost (`operations_per_year` of that scenario in `inputs.yaml`) at which the scenario's five-year total equals staying, all other inputs fixed, with the entered value beside it. The varied input is always this one and the sentence names it. Computed from the existing cost model, never added to it; exact Decimal, displayed in whole currency units. If even zero operations would leave the move dearer, `costs.break_even_none`. Absent when the operations input is unknown. Town example: full move breaks even at EUR 39,130 a year, entered EUR 12,000.

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
| Readiness | Keep; cards, filters; bar stays here as the filter's visual | Section 2. |
| What moves where | Keep as the site's `.coverage` table | Columns: Microsoft function; Replacement (`.cov-cell`: symbol, coverage label at 600, replacement on line two); Checked on (no-project-check wording kept); Area status (`workload_status` with its incomplete marker, linked to the card with `aria-label` "{area}: {status}" and an underline). No-function lines kept. |
| Needs attention | Keep | File types as `.coverage`; software counts as `dl.rows`; transfer gaps stay `ul.mapping-gaps > li[data-gap]`, styled as rows. |
| Suggested path | Rewrite as "What to do next", directly after the summary | Section 4.1. The status timeline, the pilot sentences and the stock `ol.steps` are removed: evidence states are not project stages, and the stock steps appeared even with an open blocker (C7). |
| Appendix | Keep; parts in closed `<details>` except run details | Run details stay open and carry the local and offline sentences. A short open part, "What Fazit does not look at", lists file contents, mail, data about individual people, departments and the target system's settings. |
| Footer | Unchanged | |

Each `<section data-section="…">` tag stays literal, with no added class or id; the site's frame is an inner `div.sec.grid`. Links target heading ids.

### 4.1 What to do next (`data-section="path"`)

The IT lead's and the integrator's working list, built only from findings. Two groups, each an `h3` with `dl.rows`:

1. **Worth doing even if you stay** (`path.even_if_staying`). First the next steps of kind `clarify` and `decide` from Blocker and Needs work areas (`dd[data-step-kind]`), in display order, each linked to its card. Then, under the subheading "Evidence still needed" (`readiness.missing`, the card's own label), the open points (`div[data-subsection="not-examined"]` with `id="not-examined"` on that subheading, so the summary's link lands on it): every Unknown area, every `row.missing` gap including gaps inside decided areas (`data-unexamined-gap`), unknown findings and skipped collectors, **grouped by the evidence requested**, so one missing export or answer is one row (`dt[data-open-point]`). Each row: what is open; the affected areas as links to their cards; the owner role; what closes it, as the `inputs.yaml` key in `code` or, where this version has no manual route, the fix that says the figure stays Unknown (C7).
2. **Needed for a move** (`path.for_move`): next steps of kind `replace`, in display order, each linked to its card.

With nothing open and no step, `path.empty.unknown` and `path.empty.blocker` as today. No timeline, no pilot sentences, no stock steps, no proposed decision.

## 5. Navigation

`div.bar > .bar-in > a.wordmark[href="#main"] + nav.bar-links[aria-label] > .bar-links-in`, sticky, seven links in section order: Summary, Next steps, Areas, Costs, Replacements, Closer look, Appendix. `main` has `id="main"`; `.skip` is first in `body`; `html { scroll-padding-block-start: calc(var(--bar-h) + 16px) }`. Hidden in print.

## 6. Tokens and components

### 6.1 Tokens

- The report's `:root` and dark `@media` block keep their names and mechanism (a test parses them). A second rule adds the site's names so site CSS pastes in: `--fg`, `--fg-2`, `--rule`, `--fill`, `--link`, `--link-hover` as aliases; `--solid-bg`, `--solid-fg`, `--link-glow` with the site's values per palette; `--sans`, `--mono`, `--ease`, `--gutter`, `--max: 1120px`, `--bar-h: 52px`, `--hit: 44px`, `--radius: 8px`, `--radius-pill: 999px`.
- Margin reset: `h1, h2, h3, h4, p { margin: 0 }`.
- Type: `--fs-display` h1; `--fs-title` inventory figures; `--fs-headline` section labels, card area names, money in tiles; `--fs-lead` status list counts; `--fs-subhead` tables, tile detail, filters; `--fs-footnote` provenance and meta. Weights 400 and 600.
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
2. **Symbols** are inline `<svg class="icon"><path>` at the site's sizes, never `use`. `circle`, `contrast`, `code` and `cancel` are packaged in `icons/` and registered in `report.py`.
3. **Bar.** `div.bar`, not `header.bar` (tests split on the report's one `header`). Below 820 px there is no menu: `.bar-in { display: flex }`; `.bar-links { min-width: 0; overflow-x: auto; scrollbar-width: none; padding: 4px; mask-image: linear-gradient(to left, transparent, #000 32px) }` so the row visibly continues and focus rings are not clipped; links `inline-flex`, `min-height: var(--hit)`.
4. **Hover** stays `a:hover { color: var(--accent-hover); }` (a test matches the text).
5. **Coverage label is visible**, because a printed report has no legend nearby.
6. **Cards** in `.areas`: area name as anchor and status at body size on every card, compact Ready cards, and evidence kept as today's list markup in place of the site's `dl.evidence` (2.1, 2.3).

Coverage symbols are drawn in `--fg`, cancel in `--fg-2`, never a status colour, and never a status symbol (`DESIGN.md`, "Symbols"): `in_suite` circle (Material Symbols Rounded, filled, added to `site/icons/` and `icons/` with the existing licence), so a full circle and the half-filled contrast read as a pair; `in_suite_with_limits` contrast; `open_source_community`, `open_source_third_party` code; `announced`, `component_vendor_solution`, `proprietary_third_party`, `not_available` cancel.

New, in the same visual language:

| Component | States |
|---|---|
| `.cost-bars`, `.cost-bar`, `.cost-segment` | known; zero; total unknown (marker only, no bar); all unknown; chart omitted |
| `dl.status-summary` | four rows, display order, count and definition per row; definition wrapped below 640 px; print |
| `.filters`, `.segmented` | segment: default, hover, selected, focus-visible, disabled; track: inline, wrapped; hidden (print, no `:has()`) |
| `details` | closed, open, focus-visible, print. Summary in `--link`, chevron rotates 90° with `--ease` (not under reduced motion), min-height 44 px |
| Card | four statuses, with or without `data-incomplete`; compact (Ready); filtered out; link target. Same surface in all: only symbol colour and words differ, no coloured borders or tints |

## 7. Phone and print

**Phone (360 px).** One column, 16 px gutter. The status list and blockers come before any secondary figure. Meta row, legends and filter tracks wrap; cost heading wraps, block values one per line, cost table rows stack (3.2). No horizontal page scroll.

**Print.**

- Hide `.bar`, `.skip`, `.filters`, `.areas-empty`. Filter rules are screen-only. Light palette.
- Every `details` open: `details::details-content { content-visibility: visible; display: block; block-size: auto }`; chevrons hidden.
- Type in pt: display 24, title 18, headline 14, lead 12, body 10, subhead 9, footnote 8. Card padding 12pt, section padding 16pt. One column; tiles two columns.
- Breaks: the card head (area, status, reason, next step) stays together; evidence may break between rows; `thead { display: table-header-group }`; `.table-scroll { overflow: visible }`. `break-inside: avoid` on tiles, rows, cost rows and `tr`. `break-before: page` on `path`, `costs` and `appendix`, so header and summary are page one.
- `print-color-adjust: exact`; 0.5pt `--rule` borders on cards, tiles, rows, notes and bar segments, so everything stays legible with backgrounds off; links in `--fg`. `@page { margin: 15mm }`.

## 8. Copy

Status names are used exactly and capitalised: Ready, Needs work, Blocker, Unknown / Bereit, Handlungsbedarf, Hindernis, Unbekannt. German is formal and administrative. The word is "move" / "Umstieg".

| Key | English | German |
|---|---|---|
| `header.title` | What leaving Microsoft 365 would take | Was ein Umstieg von Microsoft 365 erfordert |
| `summary.title` | Where the organisation stands | Wo die Organisation steht |
| `summary.of_areas` | Of {n} areas: | Von {n} Bereichen: |
| `summary.blockers` | What blocks this move | Was diesem Umstieg entgegensteht |
| `summary.confirmed` | Confirmed blockers: {shown} of {total} | Bestätigte Hindernisse: {shown} von {total} |
| `summary.all_blockers` | All blockers | Alle Hindernisse |
| `summary.caveat` | {n} areas are Unknown or have incomplete evidence, so a Blocker cannot be ruled out. | {n} Bereiche sind unbekannt oder unvollständig belegt; ein Hindernis lässt sich daher nicht ausschließen. |
| `summary.unknown` | What is still unknown | Was noch unbekannt ist |
| `summary.not_examined` | All open points | Alle offenen Punkte (*draft*) |
| `summary.define.blocker` | A confirmed obstacle that must be resolved before this move. | Ein bestätigtes Problem, das vor diesem Umstieg gelöst sein muss. (*draft*) |
| `summary.define.needs_work` | The checks found work to do before a move. | Die Prüfungen haben Aufgaben ergeben, die vor einem Umstieg zu erledigen sind. (*draft*) |
| `summary.define.unknown` | Evidence is missing, so this version cannot assess the area. | Es fehlen Nachweise, daher kann diese Version den Bereich nicht bewerten. (*draft*) |
| `summary.define.ready` | RR-01's `summary.ready_definition`, without the status name if the row's `dt` already gives it | as RR-01 |
| `summary.scope_title` | What {profile} covers | Was {profile} abdeckt (*draft*) |
| `summary.scope_of` | Of the {n} functions Fazit checks for {profile}: | Von den {n} Funktionen, die Fazit für {profile} prüft: (*draft*) |
| `summary.scope_needed` | Outside {profile} and needed here | Nicht in {profile} enthalten und hier benötigt (*draft*) |
| `summary.scope_unknown` | {n} more are outside {profile} and still Unknown here. | Weitere {n} sind nicht in {profile} enthalten; ob sie hier benötigt werden, ist unbekannt. (*draft*) |
| `readiness.title` | Where each area stands | Wo jeder Bereich steht |
| `readiness.next_step` | Next step | Nächster Schritt |
| `readiness.evidence_summary` | Evidence · {measured} measured, {provided} provided, {unknown} unknown | Nachweise · {measured} erhoben, {provided} bereitgestellt, {unknown} unbekannt (the report's provenance words) |
| `readiness.all_replacements` | All replacements | Alle Ersatzlösungen |
| `filter.status_legend` | Show areas by status | Bereiche nach Status anzeigen |
| `filter.category_legend` | Show areas by category | Bereiche nach Kategorie anzeigen |
| `filter.all` / `all_categories` | All / All categories | Alle / Alle Kategorien |
| `filter.empty` | No area matches this selection. Choose "All" to see every area. | Kein Bereich entspricht dieser Auswahl. Wählen Sie „Alle“, um alle Bereiche anzuzeigen. |
| `filter.search_hint` | Filtered-out areas and, in some browsers, closed sections are not searched. | Ausgeblendete Bereiche und, je nach Browser, geschlossene Abschnitte werden nicht durchsucht. |
| `costs.title` | What staying and moving cost over five years | Was Verbleib und Umstieg in fünf Jahren kosten |
| `costs.partial_exit` / `full_exit` | Partial move / Full move | Teilweiser Umstieg / Vollständiger Umstieg |
| `costs.total_label` | {scenario} · five-year total | {scenario} · Summe über fünf Jahre (*draft*) |
| `costs.stay_basis` | Today's yearly costs for five years | Heutige Jahreskosten über fünf Jahre (*draft*) |
| `costs.comparison_unknown` | Comparison unknown | Vergleich unbekannt (*draft*) |
| `costs.stay_assumption` | Staying assumes no price change. | Für den Verbleib ist keine Preisänderung angenommen. (*draft*) |
| `costs.break_even` | {scenario} costs the same as staying if target operations cost {amount} a year (entered: {entered}). | {scenario} kostet gleich viel wie der Verbleib, wenn der Betrieb des Zielsystems {amount} pro Jahr kostet (angegeben: {entered}). (*draft*) |
| `costs.break_even_none` | {scenario} costs more than staying even with no operations cost. | {scenario} kostet auch ohne Betriebskosten mehr als der Verbleib. (*draft*) |
| `costs.vat_note` | Amounts are as entered. The inputs file does not say whether they include VAT. | Beträge wie angegeben. Die Eingabedatei gibt nicht an, ob sie Umsatzsteuer enthalten. (*draft*) |
| `costs.profile_note` | The costs come from the inputs file and are the same for every target profile. | Die Kosten stammen aus der Eingabedatei und sind für jedes Zielprofil gleich. (*draft*) |
| productivity-loss labels | Lost working time (internal estimate, not a payment) | Verlorene Arbeitszeit (interne Schätzung, keine Zahlung) (*draft*) |
| `costs.less` / `more` / `same` | less than staying / more than staying / the same as staying | weniger als beim Verbleib / mehr als beim Verbleib / gleich viel wie beim Verbleib |
| `costs.sub_cent` | differs by less than one cent | weicht um weniger als einen Cent ab |
| `costs.total_unknown` | Total unknown | Summe unbekannt |
| `costs.known_blocks` | Total of known blocks {amount} | Summe der bekannten Blöcke: {amount} |
| `costs.inputs_missing` | {n} inputs are missing | {n} Angaben fehlen |
| `costs.missing_fix` | Enter the missing amounts in the inputs file and build the report again. | Tragen Sie die fehlenden Beträge in die Eingabedatei ein und erstellen Sie den Bericht erneut. |
| `moves.title` | What replaces what | Was wodurch ersetzt wird |
| `attention.title` | What needs a closer look | Was genauer zu prüfen ist |
| `path.title` | What to do next | Was als Nächstes zu tun ist |
| `path.even_if_staying` | Worth doing even if you stay | Sinnvoll, auch wenn Sie bleiben (*draft*) |
| `path.for_move` | Needed for a move | Für einen Umstieg nötig (*draft*) |
| `appendix.not_looked` | What Fazit does not look at | Was Fazit nicht betrachtet (*draft*) |
| `appendix.not_looked_text` | File contents, mail, data about individual people, departments, and the settings of the target system. | Dateiinhalte, E-Mails, Daten zu einzelnen Personen, Abteilungen und die Einstellungen des Zielsystems. (*draft*) |
| `found.title` | What Fazit recorded | Was Fazit erfasst hat (*draft*) |
| `appendix.title` | How this report was made | Wie dieser Bericht entstanden ist |
| `nav.*` | Summary, Next steps, Areas, Costs, Replacements, Closer look, Appendix | Überblick, Nächste Schritte, Bereiche, Kosten, Ersatz, Prüfbedarf, Anhang |
| `mapping_coverage.*` (German only) | unchanged | In der Suite; In der Suite mit Einschränkungen; Open-Source-Lösung der Community |

Locale keys keep their names; only values change. In the cost formulas "exit scenario" becomes "move scenario" and "Ausstiegsszenarien" becomes "Umstiegsszenarien". A cost difference is less or more, never a saving; no "score", "verdict", "recommended", "recommendation", "best", "safe" or "easy" (German: no "Urteil", "Empfehlung", "empfohlen"). The report gives no effort estimate in days or money; it shows the counts that drive effort. Every string exists in both locales; every `data-label` is a locale string. The German `next_step` sentences and every value marked *draft* need a native-speaker pass before merge. Legal procedures are named, never cited by paragraph, unless a qualified person has checked the reference.

## 9. What must not change

**Honesty.** No overall score, grade, percentage, verdict, proposed resolution or supplier recommendation. No part-of-whole picture of area statuses on page one. The scope statement is counts with names, never a fraction or bar. Unknown is never grouped with, coloured like or counted as Ready. A skipped collector never improves a status. Every figure carries measured, provided or unknown in words; sample and invented data keep their labels; status is always symbol plus word. Filters only hide cards on screen: they change no count, status, summary or printed page. `STATUSES` and the cost model are untouched; break-even is computed from the cost model, not added to it. Rule evaluation changes only through RR-06 and RR-07 (launch critique); the rule loaders change to load `next_step` with `kind` and the `assessed` flag.

**Privacy and security.** CSP unchanged. One `<style>`, two embedded fonts, no other `url()`, no `script`, `img`, `form`, SVG `use` or event-handler attribute, every `href` starts with `#`, no link in the footer, autoescape on, no person names or email addresses. Nothing is submitted or stored.

**Hooks kept exactly.** Every `data-*` attribute in the current template keeps its name, values, attribute order and host element unless listed below. `data-block` appears exactly four times in `costs`. Also kept: classes `status {status}`, `subtotals`, `totals`; ids `readiness-title`, `readiness-{workload}`, `software-title`; the token blocks; and the CSS the style test matches (a `(max-width: 40rem)` query, `content: attr(data-label)`, `@page { margin: … }`, `break-inside: avoid`, `print-color-adjust: exact`, the print `::details-content` rule).

**Decisions to record when this is built.** In `DECISIONS.md`: the departure from D-19, D-26 and D-64 (ten sections, cards in place of the table, new order); Licences without a status, amending D21 and RULE-02; page one for the council, which pulls OUTP-03's one-page summary into the redesign. In `01.1-CONTEXT.md`, the **D-81 amendment**: area cards are grouped by status; inside a group they keep catalogue order; Licences has no card, so Copilot is the first card of whichever group it is in; in the category filter Copilot is first under Automation and AI; the report sorts a display copy and never reorders `STATUSES`.

**Permitted test and checker edits, and no others:**

1. `SECTION_ORDER` and the CLI test's hardcoded nine sections take the ten in section 1, with `path` third. When Phase 1.1 ships, the `data-subsection` order assertion gains `licence-contract`.
2. Readiness rows: `<tr data-workload=…>…</tr>` becomes `<article data-workload=…>…</article>`; regexes change the tag only. `site/check_site.py` counts `article[id^="readiness-"]`.
3. CLI and simulation tests that assert catalogue order of readiness rows assert instead: group order, catalogue order inside each group, exactly one card per workload.
4. The `data-segment` assertion is replaced by counting cards per status in `readiness`, in display order (the bar is removed).
5. The directory-note test slices `readiness` in place of `found`.
6. Conflict assertions are scoped to one evidence record, because a card shows an observation in two lists.
7. The headline `.figure` selector becomes `.figure-num`; the qualified-zero wording assertions stay.
8. Header assertions on the local and offline sentences look in run details.
9. Expectations that contain old scenario, coverage or title wording follow the locale.
10. Rule and catalogue fixtures gain `next_step`, `kind` and `category`; Licences assertions follow C2.
12. `ul[data-path-status]` lists and the stock-step assertions are replaced by `dt[data-open-point]` and `dd[data-step-kind]`; the `not-examined` hooks keep their names in `path`.
11. New tests: summary caps and deduplication; zero-blocker caveat; unknown comparison with a known total (the 507,800 case); one chart scale, unknown marker outside it, no chart for null inputs; chart text equals table amounts; no bar on a row with an unknown total; break-even on the town (EUR 39,130 operations for the full move) and its absent and none cases; three tiles with whole units; a seven-digit amount on one line in a tile; every next step has a `kind`; no Needs work reason contains "block" or "Hindernis"; open points grouped by the evidence requested; `next_step` in both languages on all problem rules; every workload has a registered category and a matching `data-category`; two radio groups, one checked each, zero-count statuses disabled; filter rules inside `@media screen`; nav links resolve; no `script`, `form`, `use` or `on*`.

## 10. Wireframes

Desktop, 1280 px (content 1120 px; label 4/12, body 8/12). Town sample, openDesk; the scope statement appears after RR-07:

```
[fazit            Summary  Next steps  Areas  Costs  Replacements  Closer look  Appendix]
Stadtverwaltung Musterstadt
What leaving Microsoft 365 would take
meta row (dates, profile)                                      [ sample note ]
-----------------------------------------------------------------------------------------
Where the         Of 14 areas:
organisation      (!) Blocker 1       A confirmed obstacle that must be resolved before this move.
stands            /!\ Needs work 9    The checks found work to do before a move.
                  (?) Unknown 1       Evidence is missing, so this version cannot assess the area.
                  (v) Ready 3         The current checks found no blocker and no missing evidence.
                  What blocks this move                                        All blockers
                  [ Telephony · reason ]
                  What is still unknown
                  [ Security and compliance · fix ]   [ Mail · shared mailboxes · fix ]
                  All open points · {n} inputs are missing
                  ( What openDesk covers: after RR-07 )
                  [ Stay · five-year total ] [ Partial move · …       ] [ Full move · …       ]
                  [ EUR 600,000            ] [ EUR 527,800            ] [ EUR 464,350         ]
                  [ today's yearly costs   ] [ EUR 72,200 less than … ] [ EUR 135,650 less …  ]
                  Staying assumes no price change.
                  Full move costs the same as staying if target operations cost EUR 39,130 a year (entered: EUR 12,000).
                  [ Next renewal (1.1) ]                  [ Latest notice date (1.1)   ]
=================================== page break in print ==================================
What to do        Worth doing even if you stay
next              [ clarify / decide steps ] …   Evidence still needed: [ open point · areas · role · inputs key ] …
                  Needed for a move
                  [ replace steps ] …
-----------------------------------------------------------------------------------------
Where each        [##|##################|##|######]   (the filter's visual)
area stands       ( All · 14 | Blocker · 1 | Needs work · 9 | Unknown · 1 | Ready · 3 )
                  ( All categories | Communication | Files and documents | … )
                  search hint
                  (!) Blocker
                  [ Telephony · Communication / (!) Blocker / reason / next step ]
                  [ > Evidence · 1 measured, 2 provided / target line           ]
                  /!\ Needs work (9 cards)   (?) Unknown (1)   (v) Ready (3 compact)
                  [ empty state ]
-----------------------------------------------------------------------------------------
What staying      intro line (organisation, dates, price origin, same for every profile)
and moving cost   Partial move   EUR 527,800.00 · EUR 72,200.00 less than staying · origin
over five years   (#############################################|222|3|44)
                  Stay assumption and break-even      table      VAT note      > Cost inputs
-----------------------------------------------------------------------------------------
replacements / closer look / recorded inventory / appendix (with "What Fazit does not look at") / footer
```

The unfavourable case gets the same attention. Non-profit sample: no blocker, so "What blocks this move" shows the zero-blocker sentence and its caveat; the full move's productivity-loss input is missing, so its tile shows Unknown, the known blocks and "1 input is missing", there is no break-even line for it, and its chart row shows the Unknown marker without a bar. A report with every area Unknown shows the status list, the caveat, four unknown rows with "All open points", and three Unknown tiles. Each of the three must fit page one.

Phone, 375 px: bar scrolls sideways with an edge fade; h1 on three lines; legend on two lines; blockers; tiles one per row; filter pills wrap; cards full width; cost heading stacked, block values one per line; cost table rows stacked.

## 11. Acceptance criteria

1. One HTML file; the CSP is byte-identical to today's; no `script`, `img`, `form`, SVG `use`, event-handler attribute or external reference; every `href` starts with `#`. The report works identically with scripting disabled.
2. At 1280 × 800 the first screen shows the title, the status list (counts with definitions) and the first blocker row (or the zero-blocker sentence with its caveat), in both languages and both samples. The summary contains no readiness bar or other part-of-whole picture.
3. Counts appear once in the summary, in the status list with the definitions; "Of {n} areas" takes n from the catalogue. At most 3 blockers, "{shown} of {total}" only when rows are cut off, "All blockers" only when total is at least 1, and at most 4 deduplicated unknown rows, placed before the cost tiles. No score, percentage, verdict, proposed resolution or recommendation.
4. Default view: one `article.finding` per workload, grouped Blocker, Needs work, Unknown, Ready, catalogue order inside each group; every non-ready card has a reason and a next step; every card shows its category; evidence disclosures start closed. `STATUSES` is unchanged.
5. A status filter shows only that group; a category filter shows only that category's cards and drops groups left empty; both combine; the two "All" options restore the default.
6. A combination with no match shows the empty state and no group heading; a status with count 0 is disabled.
7. Keyboard only: Tab reaches each filter group once; arrow keys move and select; the focus ring is visible; no trap. A screen reader announces group name, option, position, state and, for statuses, the count.
8. Filters change nothing outside the area cards; a link to a filtered-out card reveals it; without `:has()` the controls are absent and every card shows.
9. Print and PDF render the same with any filter active as with none.
10. Unknown is never shown as Ready, zero, blank or a dash. Three tiles show the five-year totals in whole currency units with their origin; a move tile's main line gives the difference. With Stay unknown and a move total known, the Stay tile shows Unknown and the move tile shows its total with "Comparison unknown" and the missing-input count. A row with an unknown block shows the dashed marker and no bar, "Total unknown", every unknown block named, and no difference. No other segment has a pattern.
11. All drawn bars share one scale built from known totals; listed amounts equal the table's; origins appear beside tile and chart values; null inputs give no chart. The Stay assumption appears under the tiles and the chart; the break-even line names the operations input, shows the entered value, and equals the cost model's result (town full move: EUR 39,130).
12. Every status shows symbol and word; every figure shows measured, provided or unknown as text; `.prov` has no border, background or radius; coverage symbols use no status colour and no status symbol (`in_suite` is `circle`).
13. At 360 px: no horizontal page scroll; no break inside a number or unit; a seven-digit amount on one line in its tile; long German cost cells unclipped; the bar scrolls with visible continuation and unclipped focus; filter tracks wrap; targets at least 44 px.
14. Light and dark: the contrast and token tests pass; chart outlines, the unknown marker and the skip link's focus are visible in both.
15. One `h1`; levels never skip; each `article` is labelled by its area; repeated status links have area-specific names; bars are `aria-hidden` with values in text; Tab reaches the skip link, nav links and every `summary`.
16. Print (A4), checked on a real PDF in both languages: header and summary are page one and fit it for the town, the non-profit sample and an all-Unknown report; page one carries organisation, dates, sample note, definitions, blockers or the zero-blocker sentence, open questions and the three totals or Unknown; its text contains evidence from Ready cards, the licence table and every appendix part; no bar or filters; card heads unsplit; table headers repeat; `path`, costs and appendix start new pages; amounts and borders legible with backgrounds on and off.
17. Both languages have identical element structure; wording matches section 8.
18. Reused components match `site/style.css` declaration for declaration, apart from the six exceptions in 6.2; no spacing value outside the scale and its exceptions.
19. A side-by-side of site and report at 1280 and 375 px, light and dark, looks like one product; both reviewers sign this off.
20. Changing an area's `category` in the catalogue changes its card and filter result with no template edit.
22. "What to do next" follows the summary: every open point, including gaps inside decided areas, appears once, grouped by the evidence requested, with its areas, owner role and the key or fix that closes it; the "Worth doing even if you stay" group holds `clarify` or `decide` steps first, then the open points under "Evidence still needed"; no status timeline, pilot sentence or stock step remains.
23. A card's target line shows a needed transfer gap before the two-function cap.
24. With RR-07: the scope statement's counts equal the replacements table, keep the profile's own coverage labels, name every needed function outside the profile, and are absent for a profile without dated sources.
21. Existing tests pass with edits only as section 9 permits; the new tests exist; all six "Done means" commands in `AGENTS.md` succeed; both demo reports are regenerated; the decisions in section 9 are recorded.

**Before RR-02 (founder action, not a build criterion):** give page one, unexplained, to one council clerk or Kämmerer and ask what it supports and what is still open; record the answer beside this spec.

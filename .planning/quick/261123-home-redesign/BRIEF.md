# Brief: ship the redesigned home page

You are working in `/home/roux/Documents/open`. Read `AGENTS.md` and `DESIGN.md` first; both are binding except where this brief changes a rule, and every rule change below must be recorded (see "Decisions"). Do not commit, push or deploy. The maintainer's coordinator reviews, commits and publishes.

## Goal

Replace the English home page (`site/index.html`) and the German home page (`site/de/index.html`) with the approved redesign, and make the small site-wide changes listed below. The approved English reference is `.planning/quick/261123-home-redesign/reference-home-en.html`. It loads the live `site/style.css` and adds a page-level `<style>` block. Port it properly: move its rules into `site/style.css` as named, token-based components scoped to the home page, remove the inline `<style>`, and keep everything lean (no dead rules, no duplicated declarations, no `!important` unless a live rule truly forces it; prefer fixing specificity). The reference also carries the copy before the final polish; use the copy in this brief, not the reference's.

Keep the existing `<head>` of both live home pages (metadata, JSON-LD, hreflang, preload, script and stylesheet links, with the cache-busting version bumped). Keep the live header, phone menu, footer and skip link markup.

## Page structure (both languages)

1. **Hero** (centred): eyebrow, `h1`, subline, two buttons, status line.
2. **Hero report window**: the existing `report-card` with the Linux window bar (minimise, maximise, close controls, file name), 62.5 rem wide at most. Inside:
   - eyebrow line with the sample organisation and target profile;
   - `preview-title` heading and `sec-intro`;
   - four status tiles in one row (two by two below 760 px). Each tile: the plain status label (status symbol and word, the report's status-summary style, no badge), then the count at the shared value size with a small grey unit ("area"/"areas"), then a one-line caption. All rows the same height (`grid-auto-rows: 1fr`).
   - a row of two cards (stacked below 760 px): the blocker card (label row with "What blocks this move" at left and the Blocker badge at top right, then "Telephony" at value size, then a caption) and the cost card (label row, figure at value size, caption).
   - One treatment for every card here: label row (fixed height so rows align whether or not a badge is present), value 2.25 rem weight 600, caption at subhead size in the secondary colour. Values and captions must line up across each row (measure it).
3. **Five sections** ("beats"). Each is a two-column grid at 880 px and up: copy column and a panel column, split 5 : 7 (panel on the right for beats 1, 3, 5; on the left for beats 2 and 4). Copy column: `h2` at the title size, lede in the secondary colour, then one standalone link (beat 5 also has the note line before the link). Below 880 px the beat is one column, copy first.
   - **Panel**: neutral fill, 32 px radius, width `min(100%, 48vw, 34rem)` centred in its column (full width below 880 px), padding `clamp(20px, 2.6vw, 32px)`, height fits its content (no fixed aspect ratio). Cards on the panel use the page background, no border or outline ring, and a soft drop shadow (`0 16px 32px -16px rgb(0 0 0 / 16%)`). Cards fill the panel width up to 30 rem.
   - Beat 1: the Telephony finding card (badge top right, wrapping below the name on phones as the live component already does). No category line.
   - Beat 2: the Mail finding card with its two badges and the two evidence rows. No category line.
   - Beat 3: "Calculated from sample inputs" note, then three stacked cost tiles, each: label, figure, caption. Equal heights.
   - Beat 4: the three privacy tiles from the live component, in a row of three with the symbol above the title (symbol, title, detail; equal heights; titles on one line). When the panel's inner width is below 26 rem, they stack as short rows with the symbol inline (use a container query on the panel).
   - Beat 5: the command card: the panel holds one card containing the command label (led by the terminal symbol, inside the card) and the command lines with the copy button. No inner box.
4. **Closing section** (centred): heading at display size and the two buttons. No other text.

## Spacing ("breathing room")

- Hero status line to the report window: `clamp(48px, 7vw, 72px)`.
- Report window to the first beat, and beat to beat: `clamp(120px, 14vw, 200px)`.
- Last beat to the closing section: `clamp(136px, 16vw, 216px)`; closing section to the footer: `clamp(96px, 12vw, 136px)`.
- Express these as named tokens in `:root` and add them to the vertical-rhythm table in `DESIGN.md`.

## Site-wide changes

1. **Gutter**: `--gutter: clamp(16px, 5.5vw, 64px)`, keeping 16 px at 600 px and below.
2. **Standalone links** (`.more`) everywhere: text colour at rest (not `--link-quiet`), body size, weight 500, `letter-spacing: -0.01em`, chevron stem matched to weight 500 (`--chevron-stem: 0.100`). Hover and underline behaviour unchanged.
3. **Text buttons have no leading symbols** on every page (bar CTA, hero and closing buttons, any others). The icon-only copy button keeps its symbol.
4. **Security page safeguards list**: row padding 16 px top and bottom (one-line rows become 44 px).

## Copy

British English and native formal German (Sie). Use exactly this copy. German strings marked (existing) are already live and reviewed; keep them byte for byte.

| Place | English | German |
| --- | --- | --- |
| Eyebrow | Free and open source | Kostenlos und quelloffen (existing) |
| h1 | Know what leaving Microsoft 365 would take | Was beim Umstieg von Microsoft 365 nötig ist (existing) |
| Subline | See what your organisation relies on, what blocks a move to open source and what it would cost. One report, written on your computer. | Worauf Ihre Organisation angewiesen ist, was einem Umstieg auf Open Source entgegensteht und was er kosten würde. Ein Bericht, der auf Ihrem Rechner entsteht. |
| Buttons | Get started · View sample report | Jetzt starten · Beispielbericht ansehen (existing) |
| Status line | Today with sample data. Import of your own Microsoft 365 exports comes next. | Derzeit mit Beispieldaten. Als Nächstes kommt der Import Ihrer eigenen Microsoft-365-Exporte. (existing) |
| Window eyebrow | Stadtverwaltung Musterstadt · Target openDesk | Stadtverwaltung Musterstadt · Zielprofil openDesk |
| Window heading, intro | Where the organisation stands · Of 14 areas: | Wo die Organisation steht · Von 14 Bereichen: (existing) |
| Blocker tile | Blocker · 1 area · A confirmed obstacle to resolve first. | Hindernis · 1 Bereich · Ein bestätigtes Hindernis, das zuerst auszuräumen ist. |
| Needs work tile | Needs work · 9 areas · Work to do before a move. | Handlungsbedarf · 9 Bereiche · Vor einem Umstieg ist etwas zu erledigen. |
| Unknown tile | Unknown · 1 area · Evidence is missing. | Unbekannt · 1 Bereich · Es fehlen Nachweise. |
| Ready tile | Ready · 3 areas · No blocker, no missing evidence. | Bereit · 3 Bereiche · Kein Hindernis, keine fehlenden Nachweise. |
| Blocker card | What blocks this move · Telephony · Microsoft telephony with no confirmed replacement. | Was diesem Umstieg entgegensteht · Telefonie · Telefonie über Microsoft ohne bestätigte Alternative. |
| Cost card | Full move, five years · EUR 464,350 · EUR 135,650 less than staying, from sample inputs. | Vollständiger Umstieg, fünf Jahre · 464.350 EUR · 135.650 EUR weniger als beim Verbleib, aus Beispielangaben. |
| Beat 1 | The blocker comes first · Anything that stops the move sits at the top, with its reason in one sentence. · All blockers | Hindernisse stehen an erster Stelle · Was den Umstieg verhindert, steht oben, mit der Begründung in einem Satz. · Alle Hindernisse (existing) |
| Beat 1 card | Telephony · Blocker · The organisation uses Microsoft telephony and has confirmed that it has no replacement. | Telefonie · Hindernis · Die Organisation nutzt Telefonie über Microsoft und hat bestätigt, dass keine Alternative verfügbar ist. (existing) |
| Beat 2 | Every finding shows its evidence · When evidence is missing, the report says Unknown. A gap never counts as Ready. · See all areas | Jeder Befund führt die Nachweise auf (existing) · Fehlen Nachweise, steht im Bericht „Unbekannt“. Eine Lücke gilt nie als „Bereit“. · Alle Bereiche ansehen (existing) |
| Beat 2 card | as live: Mail, badges, Mailboxes 91 Measured (simulated), Shared mailboxes Unknown | as live (existing) |
| Beat 3 | See what it would cost · Compare five years of staying with a partial or full move, using your own figures. · How costs are calculated | Was der Umstieg kosten würde (existing) · Vergleichen Sie fünf Jahre Verbleib mit einem teilweisen oder vollständigen Umstieg, auf Basis Ihrer eigenen Zahlen. · So werden die Kosten berechnet (existing) |
| Beat 3 tiles | Stay · EUR 600,000 · Today’s yearly costs for five years. Partial move · EUR 527,800 · EUR 72,200 less than staying. Full move · EUR 464,350 · EUR 135,650 less than staying. | Labels and figures as live (existing). Captions: take the German wording for these three lines verbatim from `site/demo/de/index.html` (cost summary), so the home page matches the report. |
| Beat 4 | Nothing leaves your computer · After setup, the demo runs offline and makes no network requests. Fazit never changes your Microsoft 365 tenant. · How Fazit handles data | Prüfdaten bleiben auf Ihrem Rechner (existing) · Nach der Einrichtung läuft die Demo offline und greift nicht auf das Netzwerk zu. Fazit ändert nichts an Ihrem Microsoft-365-Mandanten. · So verarbeitet Fazit Ihre Daten (existing) |
| Beat 4 tiles | as live | as live (existing) |
| Beat 5 | Try it in three commands · See the sample report on your own computer. · Needs Git and uv. What you need · Get started | Drei Befehle genügen (existing) · So sehen Sie den Beispielbericht auf Ihrem eigenen Rechner. · Sie brauchen Git und uv. Was Sie brauchen (existing) · Jetzt starten (existing) |
| Beat 5 card | Run in a terminal + the live commands | Im Terminal ausführen (existing) + the live German commands (with `--lang de`) |
| Closing | Start with the sample report + the two buttons | Beginnen Sie mit dem Beispielbericht + the two buttons |

Units: English "area"/"areas", German "Bereich"/"Bereiche". Use typographic quotes and apostrophes. Use `&nbsp;` in "Microsoft&nbsp;365" where the live pages do.

## Decisions and design rules

Add one dated entry to `DECISIONS.md` (next free number after D48, newest first, same style as D44 to D48) covering: the home page's beat layout and panels replacing the label-left sections with rules on the home page only (other pages keep their structure); the hero report window and the card treatment; panels sized to content; the wider responsive gutter; standalone links in the text colour at weight 500; text buttons without leading symbols; the looser safeguards list; and the home spacing tokens. The founder approved all of these on 23 November 2026. Update `DESIGN.md` in place so its rules match (Tokens: gutter; Vertical rhythm: new home tokens; Structure: home beats, panels, card treatment; Links and buttons: standalone link style and button symbols; Checks if they change). Keep DESIGN.md's voice: short, binding statements.

## Checks (all must pass; extend them where the redesign changes what they measure)

- `uv run python site/check_site.py`
- `node site/check_alignment.mjs`
- `node site/check_spacing.mjs` — the spacing check currently compares every website page with the home page's opening and section gaps. Update it so the home page is measured against its new tokens and the other pages keep their existing comparison. Do not loosen tolerances.
- `node tests/browser/check-scrollbars.mjs`
- `uv run python site/generate_llms.py` to rebuild `site/llms-full.txt`.

Both Chromium and WebKit are expected. On this machine headless Chromium has been crashing under memory pressure from other sessions' leftover browsers; if Chromium crashes, rerun that check with `PLAYWRIGHT_ENGINE=webkit`, then retry Chromium once, and report exactly which engine passed what. Never report a check as passed that did not run.

Also verify, and report the numbers: no horizontal scrolling at 360, 390, 768, 960, 1130 and 1280 px; equal card heights in each row; values and captions aligned across the hero rows; privacy titles on one line where the row layout applies; light and dark mode; `prefers-contrast: more`; keyboard focus order; both languages.

## Report

Write `.planning/quick/261123-home-redesign/SUMMARY.md` in the style of `.planning/quick/261123-breathing/SUMMARY.md`: what changed, the decision reference, the verification results with numbers, and before and after screenshots at 1280 px and 390 px in English and German saved under `.shots/home-redesign/` (git-ignored). List every file you changed.

# RR-08 part 1 (home and site pages; Mail card and og.png follow after RR-05)

## Home outline

1. Hero
2. Report preview, with a caption for the offline English and German HTML and a strip showing 14 assessed areas and three target profiles
3. Find the blockers before the project does
4. Evidence and a next step for every area, with the Mail example, the evidence limit, the sample tally and a link to all assessed areas
5. What you get, with seven tiles in report order and a short link to the coverage comparison
6. How it works, with the three commands from the start page and a link to Get started
7. What stays on your computer, with the five safeguards and the offline verification instructions
8. Project status, with Now, Next and Later
9. Free and open source, with the licence and business model, the link to how Fazit is made, and the Pilots card

The Mail card retains the status, category, reason, next step, four rule-evidence rows, five table rows, missing-evidence note and target line from the matching checked-in demo. The tally follows the demo’s display order and shows the symbol, label and count for each status.

## Files

| Files | Changes |
| --- | --- |
| `site/index.html`, `site/de/index.html` | Reordered the sections, copied in Mail, moved the coverage table and sources, reduced the figures and timelines, rewrote the report tiles, and replaced the audience, claims and development sections with the relevant copy in the new outline. |
| `site/coverage/index.html`, `site/de/coverage/index.html` | Added the paired comparison pages with the existing table, legend, mapping review note, sources and target projects. Added a localised introduction that explains what the table answers. |
| `site/start/index.html`, `site/de/start/index.html` | Renamed the last section and retained the sample report card. Its detail identifies the fictional town and simulated measurements. |
| `site/security/index.html`, `site/de/security/index.html` | Put each principle in a current or planned group. Kept the offline verification and evidence limits. |
| `site/pilots/index.html`, `site/de/pilots/index.html` | Named the council summary on the first printed page, marked the assessed-area count for checking and aligned the contact heading with the action. |
| `site/integrators/index.html`, `site/de/integrators/index.html` | Led with planning the next steps from the findings, named the redesigned grouping and role information and the planned phase 1.2 CSV, linked the comparison, and reduced the directory to its entry criteria. |
| `site/style.css` | Grouped the Mail, command block, coverage and security additions under RR-08 comments. Removed rules for the old evidence grid, the old status shape, unused tile icons and the four-figure and three-tile layouts. Retained the shared embedded-symbol mechanism. |
| `site/check_site.py` | Registered the coverage routes, moved coverage validation there and checked the new tally and stated area counts. |
| `site/sitemap.xml` | Added the two coverage URLs and reciprocal language alternates. |
| `publiccode.yml` | Set the assessed-area count in both descriptions from the demos. |
| `.planning/report-redesign/RR-08-SUMMARY.md` | Recorded the scope, decisions, checks and German copy for review. |

## Deviations and implementation choices

- This part uses the RR-03 demos present at `fca1649`. Each home page has the requested provenance comment immediately before Mail. The copy differs from the report markup only in indentation, the heading level (`h3` under the home section) and the replacements link, which opens that section in the matching demo. The disclosure starts closed, as in the demo. The refresh from the final reports and the new `og.png` follow RR-05.
- The current branch predates RR-04’s coverage symbol. A scoped CSS circle gives full coverage the intended neutral mark in the comparison and its legend. Once RR-04’s shared Material circle lands, the temporary `#coverage .cov-full::before` rule can be removed. The coverage cells, legend and notes moved verbatim.
- The report screenshots and their alternative text are reserved for RR-05. The old readiness bar remains visible in those preview images, and the existing download-size labels predate the current demo files. The website markup check excludes demo files and passes.
- The current-versus-planned distinction determines the security groups. Five principles apply today and three describe live collection. The planned offline import is named in the introduction. The two allowed hosts and the browser sign-in details sit with the planned group. The evidence limits are identical to the original.
- The council copy describes the summary prepared for the first printed page. The A4 fit is part of the report work. The integrator page attributes the grouped open-points list and its owner roles to the redesign in progress, since the current demo still has the earlier list.
- The optional IT-lead sentence was omitted. The commands section already explains that the demo needs no Microsoft account, and Now still covers supplying answers and costs. The preview caption carries the current report languages, with the roadmap retaining the note on French and Italian. Later uses one timeline marker with three short paragraphs.
- The German pilot button and deadline sentence use the same verb as the new heading, “bekunden”. The directory criteria are one sentence, and the instruction to keep client data with the client remains a separate paragraph.
- The assessed-area figures are static text taken from the demo cards, with `data-assessed-areas` marking the visible counts on both home and pilot pages for the checker. RR-08 was executed in the working tree with the plan’s commit and phase bookkeeping omitted for this handoff.

## Test and check changes

| Existing check or addition | Change |
| --- | --- |
| `PAGE_PAIRS` | Added `/coverage/` and `/de/coverage/` to the existing language-pair checks. |
| `check_pages` coverage dispatch | Runs `check_coverage` on the comparison pages. The mapping, badge, replacement text and duplicate-cell assertions are the original ones. |
| `check_tally` | Matches “Of … areas in the sample” / “Von … Bereichen im Beispiel” and checks label before count in Blocker, Needs work, Unknown, Ready order. The total and each count still come from the demo cards. |
| New `check_area_counts`, called from `check_pages` | Requires one marked count on each home and pilot page and checks it against its language’s demo. |
| `tests/` and the other site checks | All original tests and all safeguard, privacy, offline, button-icon, embedded-symbol, asset and link checks apply. |

## Verification

| Check | Result |
| --- | --- |
| `uv run python site/check_site.py` | Checked 22 pages and 815 references. No errors. |
| `uv run pytest -q` | 928 passed. |
| `uv run ruff check .` and `uv run ruff format --check .` | Passed. Ruff confirmed formatting for 167 files. |
| `uv run fazit demo --lang de` and `uv run fazit demo --lang en` | Both succeeded with temporary output directories. The generated HTML matched the site copies byte for byte. |
| Browser layout | Visually checked the home, coverage, start, security, pilots and integrators pages in Chromium at 360 and 1280 px in light and dark mode, in English and German. All 48 views fit the viewport without horizontal scroll. The Mail disclosure and its table also fit when opened by keyboard. Local fonts and the expected screenshot variants loaded. |
| Phone menu and navigation | The small start button and its icon are visible in the open phone menu in both languages and schemes. The bar and footer wordmarks decoded in both languages. The links from home to coverage and between the coverage languages resolved in Chromium. |
| Offline demos | Both checked-in demos opened as local files with the browser offline and JavaScript disabled at both widths and in both schemes. Each loaded its embedded font and requested no external resource. |
| Source comparison | Confirmed the nine sections, the two figures, the three roadmap steps, the three commands from Start, the exact source of both Mail cards, and the moved coverage copy. The hero, preview image markup, existing footers, navigation and safeguards match the baseline. No retired markup or headings from the plan’s grep check appeared outside the demos. |
| Checker regressions | Temporary copies with wrong home and pilot counts in both languages, a wrong status tally and a stale coverage cell were rejected. |

## Native German review

The table covers new and revised German copy. The shared navigation and footer on the coverage pages, and the relocated coverage cells, legend, note and sources, use the existing copy. The Mail text below is included for review as it appears on the home page.

| Location | German |
| --- | --- |
| Home, preview caption | Beispielbericht für eine fiktive Stadtverwaltung. Eine HTML-Datei auf Deutsch oder Englisch, offline lesbar. |
| Home, areas figure | 14 bewertete Bereiche, darunter E-Mail und Telefonie |
| Home, example title | Nachweise und nächster Schritt für jeden Bereich |
| Home, example intro | Für jeden Bereich nennt der Bericht den Status, die Nachweise und die noch offenen Angaben. Das Beispiel zeigt den Bereich E-Mail im Bericht für eine fiktive Stadtverwaltung. Die Messwerte sind simuliert. |
| Home, evidence limit | Fazit prüft den Aufbau der Eingaben und ausgewählte Zusammenhänge zwischen Zahlen. Ob die Angaben zum Bestand stimmen, kann Fazit nicht feststellen. Die Aussagekraft des Berichts hängt von den Personen und Programmen ab, die die Nachweise geliefert haben. |
| Home, tally | Von 14 Bereichen im Beispiel: Hindernis 1, Handlungsbedarf 9, Unbekannt 1, Bereit 3. |
| Home, link to areas | Alle Bereiche im Beispielbericht ansehen |
| Home, council tile title | Übersicht für den Gemeinderat |
| Home, council tile detail | Eine Zusammenfassung für die erste Druckseite mit bestätigten Hindernissen, offenen Fragen und den Gesamtkosten über fünf Jahre. |
| Home, next-steps tile title | Was als Nächstes zu tun ist |
| Home, next-steps tile detail | Aufgaben, die auch beim Verbleib sinnvoll sind, und Arbeiten, die ein Umstieg erfordert. |
| Home, areas tile title | Wo jeder Bereich steht |
| Home, areas tile detail | Die Begründung und die Nachweise zeigen, wie der Status zustande kommt. |
| Home, costs tile title | Kosten über fünf Jahre |
| Home, costs tile detail | Der Vergleich stellt die Kosten für Verbleib, teilweisen und vollständigen Umstieg anhand Ihrer Angaben gegenüber. |
| Home, replacements tile title | Was wodurch ersetzt wird |
| Home, replacements tile detail | Mögliche Ersatzlösungen und dokumentierte Lücken für das gewählte Zielprofil. |
| Home, closer-look tile title | Was genauer zu prüfen ist |
| Home, closer-look tile detail | Dateitypen mit Prüfbedarf, reine Windows-Anwendungen und Funktionen, für die eine gesonderte Lösung nötig sein kann. |
| Home, report methods tile title | Wie dieser Bericht entstanden ist |
| Home, report methods tile detail | Erhebungsmethoden, Prüfregeln, Kostenberechnung und Angaben zum Programmlauf. |
| Home, coverage summary | Die Tabelle vergleicht die dokumentierten Funktionen von openDesk und Nextcloud. Der Bericht zeigt, welche Funktionen Ihre Organisation benötigt. |
| Home, coverage link | openDesk und Nextcloud vergleichen |
| Home, how it works | Installieren Sie Git und uv. Führen Sie anschließend diese Befehle aus. Beim ersten Lauf lädt uv die benötigten Pakete. Danach läuft das Beispiel ohne Netzwerkverbindung und ohne Microsoft-Konto. |
| Home, later packaging plans | Geplant sind die Installation mit einem Befehl und ein signiertes Windows-Programm, das ohne Python läuft. Zu jeder Version gehören Prüfsummen und eine Liste der enthaltenen Komponenten. |
| Home, later report plans | Der Bericht soll Microsoft 365 Copilot und Copilot Studio als eigenen Bereich abdecken und die Frist für die Entscheidung über die Lizenzverlängerung nennen. Vorgesehen sind außerdem ein CSV-Export für Projektpläne, eine Prüfung auf nachträgliche Änderungen am Bericht und Verweise auf die Souveränitätskriterien des ZenDiS, des Bundeszentrums hinter openDesk. |
| Home, language plans | Französisch und Italienisch sind mit dem Schweizer Pilotprojekt geplant. Die Übersetzungsanleitung zeigt, wie eine Sprache hinzukommt. |
| Home, development note | Claude und Codex schreiben den Code unter Leitung des Projektverantwortlichen. |
| Home, development link | Wie Fazit entsteht |
| Coverage, heading | Was openDesk und Nextcloud abdecken |
| Coverage, title and social title | Was openDesk und Nextcloud abdecken · Fazit |
| Coverage, page and social description | Der Vergleich zeigt, welche Funktionen openDesk und Nextcloud laut Projektdokumentation je Bereich abdecken. |
| Coverage, introduction | Die Tabelle zeigt, welche Funktionen von Microsoft 365 die beiden Suiten abdecken. Welche Funktionen Ihre Organisation benötigt, ergibt sich aus der Bestandsaufnahme. |
| Coverage, comparison heading | Funktionsumfang nach Bereich vergleichen |
| Start, last heading | Das Ergebnis ohne Installation ansehen |
| Start, sample card detail | Der Bericht zeigt die Ergebnisse für eine fiktive Stadtverwaltung mit simulierten Messwerten. |
| Security, planned import | Beim geplanten Import sollen Nutzungsberichte ohne Netzwerkverbindung eingelesen werden. |
| Security, principles heading | Was heute gilt und was geplant ist |
| Security, current heading | Gilt heute |
| Security, current local processing | Die Prüfdaten bleiben auf Ihrem Rechner, wenn Erhebungsdatei, Eingabedatei und das Verzeichnis für `--out` auf einem lokalen Datenträger liegen. Über eine Netzwerkfreigabe werden diese Dateien übertragen. |
| Security, current one command | Nach der Einrichtung erstellt ein Befehl den Bericht aus den Beispieldaten mit eigenen Antworten und Kosten. Die Messwerte in den Beispielen sind simuliert. |
| Security, sign-in heading | Für die Anmeldung geplant |
| Security, two hosts | Für die Anmeldung soll Fazit nur `login.microsoftonline.com` und `graph.microsoft.com` kontaktieren. Telemetrie, Nutzungsanalysen, Update-Abfragen und CDN-Zugriffe sind ausgeschlossen. |
| Security, planned sign-in | Für die Anmeldung ist der Browser mit PKCE vorgesehen, ersatzweise ein Gerätecode. |
| Pilots, deadline | Sie können Ihr Interesse bis zum 28. Februar 2027 bekunden. Die Frist endet früher, wenn alle Plätze vergeben sind. |
| Pilots, action and contact heading | Interesse bekunden |
| Pilots, council summary and areas | Wir unterstützen Sie dabei, Fazit auf einem Rechner Ihrer Organisation auszuführen. Der HTML-Bericht bleibt bei Ihnen. Er beginnt mit einer Zusammenfassung für den Gemeinderat, die für die erste Druckseite vorgesehen ist. Der Bericht bewertet 14 Bereiche und zeigt Abhängigkeiten, mögliche Open-Source-Alternativen und einen Kostenvergleich über fünf Jahre auf Grundlage Ihrer Angaben. |
| Integrators, page and social description | Planen Sie mit dem Fazit-Bericht die nächsten Schritte für Ihre Kunden und vergleichen Sie, welche Funktionen openDesk und Nextcloud abdecken. |
| Integrators, heading | Mit den Befunden die nächsten Schritte planen |
| Integrators, introduction | Nutzen Sie die Befunde, um fehlende Exporte und Antworten mit Ihren Kunden zu klären. Für den überarbeiteten Bericht ist eine Liste vorgesehen, die offene Punkte nach dem benötigten Nachweis bündelt und die zuständige Rolle nennt. So genügt eine Anfrage, auch wenn mehrere Bereiche betroffen sind. |
| Integrators, CSV | Für Phase 1.2 ist ein CSV-Export für die Projektplanung vorgesehen. |
| Integrators, coverage link | Funktionsumfang von openDesk und Nextcloud vergleichen |
| Integrators, directory heading | Wie Unternehmen in das Verzeichnis aufgenommen werden |
| Integrators, directory criteria | Nach den ersten Bestandsaufnahmen können Sie einen kostenlosen Eintrag im alphabetischen Verzeichnis beantragen, wenn Sie Fazit mindestens einmal mit realen Daten eingesetzt haben und den Namen und die öffentliche Website Ihres Unternehmens sowie Ihre Zustimmung an hello@rouxdutoit.com senden. |
| `publiccode.yml`, assessed areas | Der offline lesbare HTML-Bericht bewertet 14 Bereiche, nennt die Nachweise und vergleicht die Kosten über fünf Jahre. |

### German Mail card from the current demo

| Element | German |
| --- | --- |
| Area and category | E-Mail · Kommunikation |
| Status | Handlungsbedarf |
| Incomplete marker | Datengrundlage unvollständig |
| Reason | Andere Systeme versenden E-Mails über Microsoft und benötigen dafür künftig einen anderen Versandweg. |
| Next-step label | Nächster Schritt |
| Next step | Die IT-Abteilung plant für die betroffenen Systeme einen neuen Versandweg für E-Mails. |
| Missing-evidence heading | Noch benötigte Angaben |
| Shared mailboxes | Freigegebene Postfächer |
| Missing source | Export der Exchange-Empfänger |
| Missing reason and next step | Aus der Postfachnutzung allein geht die Zahl der freigegebenen Postfächer nicht hervor. Lassen Sie die Zahl gesondert von der für E-Mail zuständigen Stelle ermitteln. Im Bericht bleibt sie unbekannt. |
| Disclosure | Nachweise · 4 erhoben, 1 bereitgestellt, 1 unbekannt |
| Mailboxes label and value | Postfächer · 91 Postfächer |
| Mailbox usage provenance | Erhoben (simuliert) · Postfachnutzung aus Beispieldaten · 2. November 2026 · 6. Mai bis 1. Nov. 2026 · Vollständig |
| Unknown shared mailbox count | Unbekannt |
| Other sending systems | E-Mail-Versand anderer Systeme über Microsoft |
| Positive value | Ja |
| Provided provenance | Bereitgestellt · Beispielangabe · 10. November 2026 |
| Assigned licence | Im Produkt enthaltene, zugewiesene Lizenz für E-Mail |
| Licence provenance | Erhoben (simuliert) · Lizenzbestand aus Beispieldaten · 2. November 2026 · Vollständig, 3 von 3 geprüft, 0 fehlgeschlagen |
| Evidence caption | Die Messwerte der Erhebung sind simuliert. |
| Evidence column labels | Merkmal · Wert |
| Collection methods | Erhebungsverfahren · Bericht zur Postfachnutzung |
| Collection methods | Erhebungsverfahren · Export der Exchange-Empfänger |
| Storage label and value | Speicherbedarf der Postfächer · 312,4 GB |
| Items label and value | Elemente in den Postfächern · 504.210 Elemente |
| Target coverage and date | Open-Xchange (OX App Suite) · In der Suite · 22. November 2026 |
| Replacements link | Alle Ersatzlösungen |

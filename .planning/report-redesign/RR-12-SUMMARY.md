# RR-12 summary

The English and German homepages now give an overview in seven sections.

| Section | What it shows |
| --- | --- |
| Hero | The free and open source eyebrow, the existing introduction and actions, and the report preview with links to open and download it. |
| Dependencies | The four status labels, symbols and counts from the sample report, followed by a link to the report. |
| Evidence | The sample report’s Mail card header and badges, a simulated mailbox count and an unknown shared mailbox count. The link opens all areas in the report. |
| Costs | The sample report’s three five-year totals with their calculation origin. The link opens the calculation details. |
| Local processing | Three icon tiles for local operation, read-only access and open source. The link opens Security. |
| Three commands | The Git and uv prerequisite, the copyable demo commands shared with Start, and a link to the setup guide. |
| Closing band | The current sample and planned import, links to Pilots and About, and the facts line including Germany, Austria and Switzerland. |

## Word count

Chromium counted the rendered text in `main`, with the old Mail evidence disclosure expanded so its copy is included. The count includes link labels, figures and commands. Spaces separate words and punctuation-only tokens are excluded.

| Homepage | Before | After |
| --- | ---: | ---: |
| English | 1,134 | 245 |
| German | 1,150 | 235 |

## Where the detail went

| Previous home content | Destination |
| --- | --- |
| Sovereignty, data protection and cost context, the Teams Phone example, and the statement on overall scores and suppliers | Added to “Where it started” on About. |
| Seven cards describing the report and the coverage comparison | The sample report shows the seven topics in context. The comparison is linked from Project in the site footer. |
| Full Mail example and its evidence limit | The Areas link opens the full report cards. Security’s “Limits of the evidence” explicitly carries the note about the accuracy of a supplied inventory. |
| “What Fazit will never do” and the offline instructions | The five safeguards open the content sections on Security, immediately followed by the existing step-by-step offline check. The local storage condition appears on both Home and Security. |
| Project status and the translation guide | Moved to Roadmap / Fahrplan. Links from Pilots and Integrators open the next step. The About status card and both Project footers link to the roadmap. |
| Licence, business model, development disclosure and founding pilots | About already carries the licence and public rules under “Why it is free”, the development disclosure under “How it is made” and the service model under “How it pays its way”. Pilots already carries the three free assessments, the countries and the import prerequisite. |

## Files

| Files | Change |
| --- | --- |
| `site/index.html`, `site/de/index.html` | Seven-section homepages with live report excerpts and localised detail links. |
| `site/{about,security,pilots,integrators}/index.html` and their `site/de/` counterparts | Relocated the About and Security copy, and redirected the existing project status links. |
| `site/roadmap/index.html`, `site/de/roadmap/index.html`, `site/sitemap.xml` | Bilingual roadmap pages, the timeline and translation guide, and sitemap entries with reciprocal language alternates. |
| `site/{start,coverage,impressum,privacy}/index.html`, their `site/de/` counterparts and both `404.html` pages | Added the roadmap and comparison links to the Project footer, as on the other site pages. |
| `site/style.css` | Added the compact preview styles and removed the full home Mail disclosure, inline tally and retired tile icon styles. The roadmap reuses the timeline styles. |
| `site/check_site.py` | Adapted the home checks and registered the roadmap pages. |
| `.shots/report-redesign/rr12/`, `.planning/report-redesign/RR-12-SUMMARY.md` | Eight full-page PNGs and this summary. |

## Implementation choices

- The homepage uses compact versions of the report components to fit the word target. The status list shows names and counts. The Mail card shows two evidence rows. The cost tiles show totals and their calculation origin. The linked report carries the status definitions, full Mail card, and cost comparisons and assumptions.
- The plan’s hero instruction puts “Free and open source” in the eyebrow. The closing line begins with the sample-data status and the planned import.
- The existing home status fragment leads to the closing band. The roadmap has a direct fragment for the planned import.

## Check changes

| Check | Change |
| --- | --- |
| `check_tally` | Replaced the inline tally assertion with a check of the four status rows. Localised labels, symbols, display order and counts agree with the matching demo. |
| `check_area_counts` | Checks both homepage mentions and the pilot page mention against the corresponding demo’s assessed areas. |
| Home structure and cost previews | Checks the seven sections in order, their detail destinations, the three scenario totals and the matching calculation origin. |
| `PAGE_PAIRS` and roadmap | Includes both pages in the normal structure, metadata, asset, link and sitemap checks. Checks the three timeline steps, the first step’s active state and the translation-guide link. |

The existing tests ran as written. The link, asset, coverage, command, security header and fresh-demo checks all passed.

## Verification

| Check | Result |
| --- | --- |
| `uv run pytest -q` | 959 passed. |
| `uv run ruff check .` | Passed. |
| `uv run ruff format --check .` | Passed. |
| `uv run python site/check_site.py` | Passed. Checked 24 pages and 953 references. |
| `uv run fazit demo --lang de` and `uv run fazit demo --lang en` | Passed using temporary output directories. Both HTML files matched the published demos byte for byte. |
| Chromium | Captured [eight full-page screenshots](../../.shots/report-redesign/rr12/) at 1280 × 800 and 360 × 800 in light and dark, in both languages. Checked status and cost data, Mail evidence, keyboard copying, the download and report links, and the roadmap language switch. |
| Scrollbars and offline reports | The browser scrollbar check passed for all 24 site pages and both offline reports at 360, 768 and 1280 px in both schemes. The demos loaded embedded fonts with the browser offline and scripting disabled. |
| Checker regression | Temporary mutations were rejected for incorrect area and status counts, totals, cost provenance, a report section destination, the roadmap active state and the translation-guide link. |

## German copy for native review

The timeline and translation note retain their wording from Home. The status, Mail and cost labels and provenance come from the German demo.

| Location | German |
| --- | --- |
| Home eyebrow | Kostenlos und quelloffen |
| Dependencies heading | Worauf Ihre Organisation angewiesen ist |
| Dependencies sentence | Im Beispielbericht bewertet Fazit 14 Bereiche anhand der vorliegenden Nachweise. |
| Dependencies link | Beispielbericht ansehen |
| Evidence heading | Jeder Befund führt die Nachweise auf |
| Evidence sentence | Fehlende Angaben kennzeichnet der Bericht als „Unbekannt“. |
| Evidence link | Alle Bereiche ansehen |
| Costs heading | Was der Umstieg kosten würde |
| Costs sentence | Aus Ihren Angaben berechnet Fazit die Kosten für fünf Jahre bei Verbleib, teilweisem und vollständigem Umstieg. |
| Costs link | So werden die Kosten berechnet |
| Local processing heading | Prüfdaten bleiben auf Ihrem Rechner |
| Local processing sentence | Speichern Sie Prüfdaten lokal in einem Ordner ohne Synchronisierung. |
| Local operation tile | Läuft lokal. Die Demo läuft offline. |
| Read-only tile | Nur Lesezugriff. Mit Freigabeliste. |
| Open source tile | Quelloffen. Prüfregeln sind einsehbar. |
| Security link | So verarbeitet Fazit Ihre Daten |
| Commands heading and prerequisite | Drei Befehle genügen. Sie brauchen Git und uv. |
| Closing band | Derzeit arbeitet Fazit mit Beispieldaten. Der Import eigener Exporte folgt. |
| Closing links | Pilotprüfungen / Über Fazit |
| Closing facts | 14 Bereiche, drei Zielprofile, Deutsch und Englisch, eine offline lesbare HTML-Datei · Deutschland, Österreich und die Schweiz |
| About, reasons for a move and telephony example | Öffentliche Stellen und Unternehmen erwägen einen Umstieg von Microsoft 365, etwa aus Gründen der digitalen Souveränität, des Datenschutzes oder der Kosten. Vor der Entscheidung müssen sie wissen, welche Funktionen sie benötigen. Eine zugewiesene Lizenz für Teams Phone kann zum Beispiel auf eine Abhängigkeit hinweisen, die im Umstiegsplan noch fehlt. |
| About, evidence and scope | Fazit führt die Nachweise zu jedem Befund auf und kennzeichnet fehlende Angaben als „Unbekannt“. Fazit vergibt keine Gesamtnote und empfiehlt keinen Anbieter. |
| Security, read allowlist | In einen Microsoft-365-Mandanten schreiben oder Endpunkte außerhalb der Freigabeliste für Lesezugriffe aufrufen. |
| Security, local data and future sign-in | Prüfdaten von Ihrem Rechner übertragen. Für die geplante Anmeldung sind nur die Microsoft-Anmeldung und Microsoft Graph vorgesehen. |
| Security, what can be stored | Anmeldetokens, erhobene Personennamen oder E-Mail-Adressen auf einem Datenträger speichern. Im Bericht können der von Ihnen angegebene Organisationsname und die Namen reiner Windows-Anwendungen stehen. |
| Security, report resources | Externe Ressourcen in den Bericht nachladen. |
| Security, missing figures and skipped checks | Eine fehlende Zahl als erhoben ausgeben oder einen Bereich wegen einer ausgelassenen Prüfung besser einstufen. |
| Security, accuracy of the inventory | Ob die Angaben zum Bestand stimmen, kann Fazit nicht feststellen. Auch erfundene Angaben, die zueinander passen, können zu einem Bericht führen. Die Aussagekraft hängt von den Personen und Programmen ab, die die Nachweise erstellt haben. |
| Roadmap title and footer link | Fahrplan |
| Roadmap metadata description | Der Fahrplan zeigt, was Fazit heute leistet und welche Funktionen als Nächstes geplant sind. |
| Comparison footer link | openDesk und Nextcloud vergleichen |

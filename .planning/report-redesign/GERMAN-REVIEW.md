# German review of the redesign (coordinator, 2026-11-22)

A native-level review of the new and changed German strings in `src/fazit/locales/de.yaml`, `src/fazit/rules/` and the rebuilt German site pages. Apply each change exactly as given, unless the string has changed since: then apply the same intent. Keep the matching English unchanged unless noted. Every change must keep the same placeholders.

## Wrong terms (must fix)
1. **"Dienstpläne" is wrong for Microsoft's service plans.** In German it means duty rosters. Microsoft's German term is **"Servicepläne"**. Replace it everywhere in `de.yaml`, `src/fazit/rules/` and the German site pages, for example: "Lassen Sie durch die Lizenzverwaltung prüfen, welche Servicepläne zum Produkt gehören."
2. **"Grundcode" means nothing.** The English is "reason code". Use **"Begründungscode"**: "Prüfen Sie die Version des Erhebungsprogramms und den Begründungscode in der Erhebungsdatei."
3. **"Sperren für Rechtsverfahren"** (legal hold): write **"Aufbewahrung für Rechtsverfahren (Legal Hold)"**. The sentence becomes: "Organisationsweite Aufbewahrung und die Aufbewahrung für Rechtsverfahren (Legal Hold) sind dort nicht beschrieben."
4. **"Übersicht für den Gemeinderat"** (home page, "What you get") is too narrow: the report also goes to Kreistage, city councils and boards. Write **"Übersicht für das Entscheidungsgremium"**. The English "Summary for the council" stays.

## Grammar and clarity
5. **`summary.caveat`:** areas are not unknown; their status is. Write: "Bei {n} Bereichen ist der Status unbekannt oder die Nachweise sind unvollständig; ein Hindernis lässt sich daher nicht ausschließen." (It now matches `caveat_one`.)
6. **`summary.define.blocker`:** "Ein bestätigtes Hindernis, das vor diesem Umstieg ausgeräumt sein muss."
7. **`summary.define.unknown`:** "Es fehlen Nachweise, daher kann diese Version von Fazit den Bereich nicht bewerten."
8. **`summary.define.ready`:** "Die aktuellen Prüfungen haben weder ein Hindernis noch fehlende Nachweise ergeben."
9. **`summary.scope_needed`:** "Nicht in {profile} enthalten, aber in dieser Organisation benötigt"
10. **`summary.scope_unknown`:** "Weitere {n} sind nicht in {profile} enthalten; ob diese Organisation sie benötigt, ist unbekannt."
11. **`costs.stay_basis`:** "Die heutigen Jahreskosten für fünf Jahre"
12. **`costs.stay_assumption`:** "Beim Verbleib wird keine Preisänderung angenommen."
13. **`costs.break_even`:** "{scenario} kostet so viel wie der Verbleib, wenn der Betrieb des Zielsystems {amount} pro Jahr kostet (eingetragen: {entered})."
14. **`costs.vat_note`:** "Alle Beträge wie eingetragen. Die Eingabedatei gibt nicht an, ob sie Umsatzsteuer enthalten."
15. **`costs.known_blocks`:** "Summe der bekannten Posten: {amount}". ("Blöcke" is jargon; check that the English counterpart reads naturally too.)
16. **`readiness.title`:** "Wo die einzelnen Bereiche stehen"
17. **`path.even_if_staying`:** "Sinnvoll, auch wenn Sie bei Microsoft 365 bleiben"
18. **`appendix.not_looked_text`:** "Dateiinhalte, E-Mails, Daten zu einzelnen Personen, Auswertungen nach Abteilungen und die Einstellungen des Zielsystems." Adjust the English to match ("analysis by department") if it says "departments".
19. **`nav.replacements`:** "Ersatzlösungen" (instead of "Ersatz"). Check that the phone navigation still fits at 360 px.

## Consistency checks to run
- The German home page's section heading for areas must use the same wording as `readiness.title` after change 16.
- The status names stay exactly Bereit, Handlungsbedarf, Hindernis, Unbekannt.
- "Umstieg" is used throughout. Neither "Ausstieg" nor "Wechsel" may appear in new strings; search both and report any hit.

## Applied

1. Done. Used Serviceplan and Servicepläne for Microsoft licensing.
2. Done. Used Begründungscode in the scan file guidance.
3. Adapted. Used Aufbewahrung für Rechtsverfahren (Legal Hold) in the openDesk and Nextcloud notes. The Nextcloud note calls for a separate assessment.
4. Adapted. Used Übersicht für das Entscheidungsgremium in the home page tile and on the pilot page.
5. Done. Clarified the status and evidence in `summary.caveat`.
6. Done. Updated the definition of Hindernis.
7. Done. Updated the definition of Unbekannt.
8. Done. Updated the definition of Bereit.
9. Done. Clarified which functions the organisation needs in `summary.scope_needed`.
10. Done. Clarified which needs remain unknown in `summary.scope_unknown`.
11. Done. Updated the five-year basis for staying.
12. Done. Updated the price assumption for staying.
13. Done. Updated the break-even sentence with all three placeholders.
14. Done. Updated the VAT note to refer to the entered amounts.
15. Done. Used Posten in German and “Total for known cost categories” in English.
16. Done. Matched `readiness.title` to the home page's areas tile.
17. Done. Named Microsoft 365 in the heading for steps worth taking even if you stay.
18. Done. Used Auswertungen nach Abteilungen and “analysis by department”.
19. Done. Used Ersatzlösungen in the report navigation. The link fits and reaches its section at 360 px in both colour schemes.

Verified the four status names and all placeholders. The search found zero `Ausstieg` matches. Four instances of `Wechsel` in the rules and one on the coverage page now use `Umstieg`. The only remaining match is in the Swiss study's PDF filename in its link URL.

Regenerated both offline demos and the four German RR-05 previews. Checked the first printed page for both samples and the all-Unknown report in both languages, with and without backgrounds.

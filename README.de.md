# Fazit

[English](https://github.com/rouxdutoit/fazit/blob/main/README.md)

Fazit ist ein freies Open-Source-Werkzeug für die Kommandozeile, mit dem Sie einen Umstieg von Microsoft 365 auf eine Lösung wie openDesk oder Nextcloud prüfen können. Fazit erstellt den HTML-Bericht lokal auf Deutsch oder Englisch. Die Datei lässt sich ohne Netzwerkverbindung öffnen.

Fazit steht am Anfang der Entwicklung (Alpha). Es erstellt Berichte aus mitgelieferten Beispielen oder einer kompatiblen `scan.json` mit Ihren Antworten und Kosten aus `inputs.yaml`. Messwerte stammen derzeit aus den Beispielen.

## Ausprobieren

Installieren Sie `uv` und klonen Sie dieses Repository. Führen Sie den Befehl im Verzeichnis des Klons aus.

```sh
uv run fazit demo
```

Beim ersten Aufruf lädt `uv` die benötigten Python-Pakete aus dem Internet. Trennen Sie anschließend die Netzwerkverbindung und führen Sie denselben Befehl erneut aus. So können Sie prüfen, ob die Berichtserstellung ohne Netzwerk funktioniert. Für die Demo benötigen Sie kein Microsoft-Konto.

Ohne weitere Angaben erhalten Sie einen englischen Bericht für eine fiktive Stadtverwaltung mit dem Zielprofil openDesk. Mit den folgenden Befehlen können Sie die deutsche Fassung, das Beispiel einer gemeinnützigen Organisation oder das Zielprofil Nextcloud ausprobieren.

```sh
uv run fazit demo --lang de --out ./report/de
uv run fazit demo --sample nonprofit --out ./report/nonprofit
uv run fazit demo --profile nextcloud --out ./report/nextcloud
```

Die Demo schreibt `report-<YYYY-MM-DD>-<lang>.html`, `scan-<YYYY-MM-DD>-<lang>.json` und `inputs-<YYYY-MM-DD>-<lang>.yaml` standardmäßig nach `./report`. Mit `--out` wählen Sie ein anderes Verzeichnis. Das Datum stammt aus der Bestandsaufnahme. Bei einem erneuten Lauf werden gleichnamige Dateien ersetzt. In der letzten Ausgabezeile steht der Pfad zum HTML-Bericht. Liegt der Bericht im aktuellen Verzeichnis oder darunter, gibt Fazit den relativen Pfad aus. Andernfalls verwendet Fazit die Verzeichnisangabe aus `--out`.

Unter Unix legt Fazit die Ausgabedateien mit der Berechtigung `0600` an. Damit kann nur der Dateieigentümer die Dateien lesen und ändern. Sie enthalten Angaben zur IT der Organisation.

## Bericht neu erstellen

Mit den Dateien aus dem ersten Demo-Lauf können Sie den Bericht auf Deutsch neu erstellen.

```sh
uv run fazit report ./report/scan-2026-11-02-en.json --inputs ./report/inputs-2026-11-02-en.yaml --lang de --out ./report/rebuilt
```

Kopieren Sie die Vorlage, wenn Sie eigene Antworten und Kosten eintragen möchten. Lassen Sie Felder leer, zu denen noch keine Angaben vorliegen. [Interviewleitfaden](https://github.com/rouxdutoit/fazit/blob/main/docs/interview-checklist.de.md)

```sh
cp inputs.example.yaml inputs.yaml
```

Erstellen Sie den Bericht mit derselben Bestandsaufnahme und Ihren Angaben neu.

```sh
uv run fazit report ./report/scan-2026-11-02-en.json --inputs inputs.yaml --lang de --out ./report/with-answers
```

Mit `--lang de` oder `--lang en` wählen Sie die Sprache. Das Zielprofil wählen Sie mit `--profile opendesk`, `--profile nextcloud` oder `--profile generic`. Bei `report` haben diese Optionen Vorrang vor den Einstellungen in der Eingabedatei.

Fazit prüft die Dateien auf Widersprüche und nennt zu jeder Zahl die Quelle. Eine erfundene, in sich stimmige Bestandsaufnahme kann trotzdem zu einem Bericht führen. Wie verlässlich ein Bericht ist, hängt deshalb vom Werkzeug und von der Person ab, die die Bestandsaufnahme erstellt haben.

## Inhalt des Berichts

1. Kopf mit Datum, Herkunft der Daten und Angaben zur Berichtserstellung.
2. Ergebnisse der Bestandsaufnahme.
3. Kostenvergleich über fünf Jahre für Verbleib, teilweisen und vollständigen Wechsel.
4. Bereitschaft nach Bereich, einschließlich der Punkte, die noch nicht untersucht wurden.
5. Funktionen im gewählten Zielsystem.
6. Prüfbedarf, einschließlich der Funktionen, deren direkte Übernahme in das Zielprofil nicht belegt ist.
7. Möglicher Ablauf mit Hindernissen, offenen Fragen und Bereichen für einen Pilotbetrieb.
8. Anhang mit Datenquellen, Regeln, Zuordnungen und Angaben zum Lauf.
9. Fußzeile mit dem Projektnamen.

Der Bericht bewertet fünfzehn Bereiche. Die vier Bewertungen lauten „Bereit“, „Handlungsbedarf“, „Hindernis“ und „Unbekannt“. Zu jeder Bewertung nennt der Bericht die Begründung und die Datengrundlage. An den Zahlen erkennen Sie, ob sie gemessen wurden, aus Ihren Angaben stammen oder unbekannt sind. Bei fehlenden Informationen erfahren Sie, was fehlt und wie Sie es klären können. Der Bericht enthält weder eine Gesamtnote noch eine Entscheidungsempfehlung.

Der Browser kann den lokalen Dateipfad in die Kopf- und Fußzeilen des Ausdrucks übernehmen. Deaktivieren Sie in den Druckeinstellungen **Kopf- und Fußzeilen**, bevor Sie eine PDF-Datei zum Weitergeben speichern. Prüfen Sie in der Vorschau, ob der Pfad angezeigt wird.

## Stand des Projekts

Sie können Fazit aus dem Klon starten. Eine Veröffentlichung auf PyPI steht noch aus. Der Import und die direkte Erhebung sind noch nicht verfügbar.

Als Nächstes sind die Prüfung von KI-Assistenten und Fristen für die Lizenzverlängerung (1.1), der CSV-Export für die Projektplanung und eine Prüfung auf nachträgliche Berichtsänderungen (1.2) sowie Verweise auf Souveränitätskriterien (1.3) geplant. In Phase 2 soll der lokale Import von Exporten aus dem Microsoft-365-Admin-Center folgen. Für Phase 3 sind `doctor`, die Anmeldung im Browser und die Erhebung von Lizenz- und Verzeichnisdaten vorgesehen. In Phase 4 folgen zweisprachige Anleitungen, Installationspakete und eine signierte Windows-Version. [Projektfahrplan (Englisch)](https://github.com/rouxdutoit/fazit/blob/main/.planning/ROADMAP.md)

## Grenzen von Fazit

- Fazit nimmt keine Änderungen an einem Microsoft-Mandanten vor. Für den späteren Zugriff sind nur ausdrücklich freigegebene Leseaufrufe zulässig.
- Nur die Microsoft-Anmeldung und Microsoft Graph dürfen kontaktiert werden. Die aktuelle Version stellt keine Netzwerkverbindung her.
- Fazit speichert standardmäßig keine Zugriffstoken, erfassten Personennamen oder E-Mail-Adressen auf dem Datenträger. Erfasste Daten enthalten keinen Freitext. Der einzige Freitext aus den Eingabedaten im Bericht sind der Name der Organisation und die Namen reiner Windows-Anwendungen, die Sie in `inputs.yaml` eintragen.
- Der Bericht lädt keine externen Inhalte.
- Fazit erfindet keine Zahlen. Eine ausgefallene Datenerhebung verbessert keine Bewertung.

Die Prüfdaten bleiben nur dann auf Ihrem Rechner, wenn die Erhebungsdatei, die Eingabedatei und das Verzeichnis für `--out` auf lokalen Datenträgern liegen, da eine Netzwerkfreigabe die Dateien über das Netzwerk überträgt.

[Sicherheit und Meldung von Schwachstellen](https://github.com/rouxdutoit/fazit/blob/main/SECURITY.md)

## Regeln anpassen

Bereiche, Bewertungsregeln, Lizenzdienste, zu prüfende Dateitypen und Zuordnungen für die Zielprofile stehen als YAML-Dateien in `src/fazit/rules/`. Ändern Sie die Dateien im Klon und führen Sie denselben Befehl erneut aus. Eine Option für ein eigenes Regelverzeichnis ist für die erste Veröffentlichung vorgesehen.

## Wie Fazit entsteht

Fazit entsteht KI-gestützt und wird von Menschen geprüft. Ein Mensch leitet die Arbeit und verantwortet das Ergebnis. Claude Opus 5.5 und Codex GPT-6.2-Sol schreiben den Code, beide mit maximalem Aufwand, und jede Änderung wird getestet, bevor sie übernommen wird. Vor jeder Veröffentlichung prüfen Claude Fable 5.2 und Codex GPT-6.2-Astra, ebenfalls mit maximalem Aufwand, den gesamten Code zunächst unabhängig voneinander und dann gegenseitig, einschließlich der Sicherheit. Ihre Prüfberichte sind öffentlich. [Prüfberichte zu Phase 1 (Englisch)](https://github.com/rouxdutoit/fazit/tree/main/.planning/phases/01-demo-and-report)

## Lizenz

AGPL-3.0-or-later. [Lizenz](https://github.com/rouxdutoit/fazit/blob/main/LICENSE), [Mitwirken](https://github.com/rouxdutoit/fazit/blob/main/CONTRIBUTING.md), [Entscheidungen](https://github.com/rouxdutoit/fazit/blob/main/DECISIONS.md)

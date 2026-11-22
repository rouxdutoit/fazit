# Checkliste für das Erhebungsgespräch

Kopieren Sie vor dem Gespräch `inputs.example.yaml` nach `inputs.yaml` und leiten Sie die passenden Fragen an die jeweils zuständige Stelle weiter.
Halten Sie im Gespräch das Datum der Auskünfte fest und lassen Sie offene Felder leer, damit der Bericht die fehlenden Angaben und den nächsten Schritt nennen kann.
Erstellen Sie den Bericht mit `fazit report SCAN_JSON --inputs inputs.yaml`.

## Organisation und Grundeinstellungen

- Welcher Name der Organisation soll nach Auskunft der Projektleitung im Bericht stehen (`organisation_name`)?
- Welches Währungskürzel aus drei Buchstaben verwendet die Finanzstelle für den Vergleich (`currency`)?
- Benötigt die Projektleitung den Bericht auf Deutsch (`de`) oder auf Englisch (`en`) (`language`)?
- Welches Zielprofil hat die IT-Leitung ausgewählt (`opendesk`, `nextcloud` oder `generic`) (`target_profile`)?
- An welchem Tag wurden die Auskünfte erteilt (`as_of`)?

## Heutige Kosten für Microsoft und die übrige IT

Erfassen Sie beide Jahresbeträge unter `current_costs` und setzen Sie jeden Betrag in Anführungszeichen, auch eine bestätigte Null (`"0"`).

- Welche Ausgaben für Microsoft-Lizenzen verbucht die Finanzstelle pro Jahr (`current_costs.microsoft_licences_per_year`)?
- Wie hoch sind laut Finanzstelle die jährlichen Ausgaben für die übrige IT, die in allen drei Szenarien weiterlaufen (`current_costs.other_it_per_year`)?

## Teilweiser Wechsel

Erfassen Sie beide Szenarien unter `target_costs` und verwenden Sie für den teilweisen Wechsel `target_costs.partial_exit`.

- Wie viele Personen würden nach dem Plan der IT-Leitung beim teilweisen Wechsel auf der neuen Plattform arbeiten (`target_costs.partial_exit.users`)?
- Welche jährlichen Ausgaben setzt die Finanzstelle für die Microsoft-Lizenzen an, die nach dem Parallelbetrieb weiter benötigt werden (`target_costs.partial_exit.retained_microsoft_licences_per_year`)?
- Welche Hostingkosten pro Person und Monat hat der Anbieter der Finanzstelle genannt (`target_costs.partial_exit.hosting_per_user_per_month`)?
- Mit welchen jährlichen Personal- oder Dienstleistungskosten rechnet die IT-Leitung für den Betrieb der neuen Plattform (`target_costs.partial_exit.operations_per_year`)?
- Welche weiteren laufenden Kosten fallen nach Auskunft der Finanzstelle beim teilweisen Wechsel pro Jahr an (`target_costs.partial_exit.other_recurring_per_year`)?
- Welche einmaligen Kosten sieht die IT-Leitung für die Durchführung der teilweisen Umstellung vor (`target_costs.partial_exit.one_time_migration`)?
- Welchen Betrag hat die IT-Leitung für die Anpassung von Anwendungen beim teilweisen Wechsel angesetzt (`target_costs.partial_exit.application_adaptation`)?
- Welche Ausgaben für externe Beratung plant die Finanzstelle für den teilweisen Wechsel ein (`target_costs.partial_exit.external_advice`)?
- Wie viele Schulungstage je Person halten die Fachbereiche für erforderlich (`target_costs.partial_exit.training_days_per_person`)?
- Welchen Betrag setzt die Finanzstelle je Person und Schulungstag an (`target_costs.partial_exit.training_day_rate`)?
- Wie viele Beschäftigte werden nach Einschätzung der Fachbereiche an der Schulung teilnehmen (`target_costs.partial_exit.training_staff`)?
- Welchen Gesamtbetrag veranschlagen Finanzstelle und Fachbereiche für den vorübergehenden Arbeitszeitverlust bei der teilweisen Umstellung (`target_costs.partial_exit.productivity_loss`)?
- Wie viele Monate muss die Finanzstelle voraussichtlich beide Systeme bezahlen (`target_costs.partial_exit.parallel_running_months`)?

## Vollständiger Wechsel

Verwenden Sie für den vollständigen Wechsel `target_costs.full_exit`.

- Wie viele Personen würden nach dem Plan der IT-Leitung beim vollständigen Wechsel auf der neuen Plattform arbeiten (`target_costs.full_exit.users`)?
- Welche jährlichen Ausgaben setzt die Finanzstelle für etwaige Microsoft-Lizenzen nach dem Parallelbetrieb an (`target_costs.full_exit.retained_microsoft_licences_per_year`)?
- Welche Hostingkosten pro Person und Monat hat der Anbieter der Finanzstelle genannt (`target_costs.full_exit.hosting_per_user_per_month`)?
- Mit welchen jährlichen Personal- oder Dienstleistungskosten rechnet die IT-Leitung für den Betrieb der neuen Plattform (`target_costs.full_exit.operations_per_year`)?
- Welche weiteren laufenden Kosten fallen nach Auskunft der Finanzstelle beim vollständigen Wechsel pro Jahr an (`target_costs.full_exit.other_recurring_per_year`)?
- Welche einmaligen Kosten sieht die IT-Leitung für die Durchführung der vollständigen Umstellung vor (`target_costs.full_exit.one_time_migration`)?
- Welchen Betrag hat die IT-Leitung für die Anpassung von Anwendungen beim vollständigen Wechsel angesetzt (`target_costs.full_exit.application_adaptation`)?
- Welche Ausgaben für externe Beratung plant die Finanzstelle für den vollständigen Wechsel ein (`target_costs.full_exit.external_advice`)?
- Wie viele Schulungstage je Person halten die Fachbereiche für erforderlich (`target_costs.full_exit.training_days_per_person`)?
- Welchen Betrag setzt die Finanzstelle je Person und Schulungstag an (`target_costs.full_exit.training_day_rate`)?
- Wie viele Beschäftigte werden nach Einschätzung der Fachbereiche an der Schulung teilnehmen (`target_costs.full_exit.training_staff`)?
- Welchen Gesamtbetrag veranschlagen Finanzstelle und Fachbereiche für den vorübergehenden Arbeitszeitverlust bei der vollständigen Umstellung (`target_costs.full_exit.productivity_loss`)?
- Wie viele Monate muss die Finanzstelle voraussichtlich beide Systeme bezahlen (`target_costs.full_exit.parallel_running_months`)?

## Anwendungen, die nur unter Windows laufen

Ersetzen Sie `null` durch einen Eintrag je Anwendung oder tragen Sie `[]` ein, wenn die IT-Leitung bestätigt, dass es keine solchen Anwendungen gibt.

- Welche Anwendungen können ausschließlich unter Windows betrieben werden (`windows_only_software`)?
- Unter welchem Namen führt die IT-Stelle die Anwendung (`windows_only_software.name`)?
- Wie viele Personen nutzen die Anwendung nach Auskunft der Fachbereiche (`windows_only_software.users`)?
- Bietet der Softwareanbieter eine Webversion an (`windows_only_software.vendor_has_web_version`)?

## Fragen zu den einzelnen Arbeitsbereichen

Erfassen Sie die Anzahlen unter `provided_counts` und verwenden Sie unter `confirmations` die Werte `true` oder `false`.

### Lizenzen

- Hat die Vergabestelle die Vertragsbedingungen der Microsoft-Lizenzen geprüft (`licences.contract_terms_known`)?

### Verzeichnisdienst

- Hat die IT-Stelle die aktuelle Kontenliste geprüft (`directory.account_list_reviewed`)?

### E-Mail

- Versenden weitere Systeme, etwa Scanner oder Fachanwendungen, E-Mails über Microsoft (`mail.other_systems_send_mail`)?

### OneDrive

- Gibt Ihre Organisation Dateien aus OneDrive für Personen außerhalb der Organisation frei (`onedrive.external_sharing_in_use`)?

### SharePoint

- Setzt Ihre Organisation individuell angepasste SharePoint-Lösungen ein (`sharepoint.custom_solutions_in_use`)?

### Teams

- Muss der Chatverlauf aus Teams nach Auskunft der Fachbereiche oder der Schriftgutverwaltung erhalten bleiben (`teams.chat_history_must_be_kept`)?

### Office-Dateien

- Wie viele Dateien hat die IT-Stelle mit Endungen erfasst, die Makros zulassen (`.xlsm`, `.xltm`, `.xlam`, `.xlsb`, `.docm`, `.dotm`, `.pptm`, `.potm`, `.ppam`, `.ppsm`, `.sldm`) (`office_files.kind.macro`)?
- Wie viele Access-Datenbankdateien für Daten, Formulare oder Abfragen hat die IT-Stelle erfasst (`.accdb`, `.mdb`) (`office_files.kind.access`)?
- Wie viele Publisher-Dateien zur Seitengestaltung hat die IT-Stelle erfasst (`.pub`) (`office_files.kind.publisher`)?
- Wie viele Visio-Zeichnungsdateien für Diagramme hat die IT-Stelle erfasst (`.vsdx`) (`office_files.kind.visio`)?
- Wie viele OneNote-Dateien für Notizen hat die IT-Stelle erfasst (`.one`) (`office_files.kind.onenote`)?

### Geräteverwaltung

- Wie viele Geräte umfasst der von der IT-Stelle erfasste Bestand (`device_management.device_count`)?
- Wie viele dieser Geräte laufen nach Auskunft der IT-Stelle unter Windows (`device_management.windows_device_count`)?
- Verwaltet Ihre Organisation Geräte über Microsoft (`device_management.in_use`)?
- Benötigen Sie Windows-Arbeitsplätze für Anwendungen, Geräte oder Peripherie (`device_management.windows_desktops_required`)?

### Power Platform

- Nutzt Ihre Organisation Dienste der Power Platform wie Power Apps, Power Automate oder Power BI (`power_platform.in_use`)?

### Telefonie

- Läuft die Telefonie Ihrer Organisation ganz oder teilweise über Microsoft (`telephony.in_use`)?
- Steht für die eingesetzte Microsoft-Telefonie eine Alternative zur Verfügung (`telephony.replacement_available`)?

### Identitäten und Zugriff

- Wie viele Anwendungen nutzen laut IT-Stelle die zentrale Anmeldung über Microsoft (`identity_access.sso_application_count`)?
- Setzt Ihre Organisation den bedingten Zugriff von Microsoft ein (`identity_access.conditional_access_in_use`)?

### Sicherheit und Regelkonformität

- Sind nach Auskunft der Informationssicherheit oder der Schriftgutverwaltung Schutz- oder Aufbewahrungsfunktionen von Microsoft im Einsatz (`security_compliance.protection_or_retention_in_use`)?

### Kleinere Microsoft-Anwendungen

- Nutzen die Fachbereiche kleinere Microsoft-Anwendungen wie Forms, Planner oder Bookings (`small_apps.in_use`)?

### Anwendungsanbindungen

- Wie viele Fachanwendungen sind laut IT-Stelle an Microsoft 365 angebunden (`integrations.application_count`)?

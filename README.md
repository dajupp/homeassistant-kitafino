# Kitafino für Home Assistant

Die Custom Integration erstellt Bestellstatus- und Datumssensoren für Montag bis Freitag, einen Sensor für den heutigen Bestellstatus sowie einen Diagnose-Zeitstempel der letzten erfolgreichen Abfrage. Die Wochentage sind mit `01` bis `05` chronologisch benannt. Die Daten werden alle 30 Minuten aktualisiert.

## Installation über HACS

1. Öffne in Home Assistant **HACS** und wähle im Menü oben rechts **Benutzerdefinierte Repositories**.
2. Füge `https://github.com/dajupp/homeassistant-kitafino` hinzu und wähle als Kategorie **Integration**.
3. Suche in HACS nach **Kitafino** und installiere die Integration.
4. Starte Home Assistant neu und füge Kitafino unter **Einstellungen > Geräte & Dienste** hinzu. Beim Einrichten gibst du Benutzername und Passwort ein.

## Manuelle Installation

1. Kopiere `custom_components/kitafino` in den `custom_components`-Ordner deiner Home-Assistant-Konfiguration.
2. Starte Home Assistant neu.
3. Füge unter **Einstellungen > Geräte & Dienste** die Integration **Kitafino** hinzu und gib beim Einrichten Benutzername und Passwort ein.

Die Integration prüft die Anmeldung vor dem Speichern. Home Assistant legt die Zugangsdaten im Config Entry ab und lädt sie nach Neustarts wieder. Das Passwortfeld ist im Einrichtungsdialog maskiert. Home Assistant verschlüsselt Config-Entry-Daten standardmäßig nicht; schütze daher den Zugriff auf den Konfigurationsordner und dessen Backups. Zugangsdaten werden von der Integration nicht in Logs geschrieben.
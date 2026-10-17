# Kitafino für Home Assistant

Die Custom Integration erstellt Bestellstatus- und Datumssensoren für Montag bis Freitag, einen Sensor für den heutigen Bestellstatus sowie einen Diagnose-Zeitstempel der letzten erfolgreichen Abfrage. Die Wochentage sind mit `01` bis `05` chronologisch benannt. Standardmäßig werden die Daten alle 60 Minuten aktualisiert; das Intervall ist in den Integrationsoptionen zwischen 5 und 1440 Minuten einstellbar.

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

## Abrufintervall ändern

Öffne **Einstellungen > Geräte & Dienste > Kitafino > Optionen konfigurieren**. Dort kannst du das Intervall in Minuten zwischen 5 und 1440 einstellen. Nach dem Speichern wird die Integration automatisch mit dem neuen Intervall neu geladen.

## Zugangsdaten ändern

Öffne **Einstellungen > Geräte & Dienste > Kitafino**, wähle das Menü des Eintrags und dann **Neu konfigurieren**. Der Benutzername ist vorausgefüllt. Gib das neue Passwort ein; nach erfolgreicher Anmeldung wird derselbe Eintrag aktualisiert und die Integration neu geladen. Die vorhandenen Sensoren bleiben dabei erhalten.
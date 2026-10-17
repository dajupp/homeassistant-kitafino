# Kitafino für Home Assistant

Die Custom Integration erstellt fünf Binary-Sensoren, einen für jeden Wochentag von Montag bis Freitag. Ein Sensor ist eingeschaltet, wenn in der zugehörigen `order_table` der Marker `bestellt_check success icon_check` vorhanden ist. Die Daten werden alle 30 Minuten aktualisiert.

## Installation über HACS

1. Öffne in Home Assistant **HACS** und wähle im Menü oben rechts **Benutzerdefinierte Repositories**.
2. Füge `https://github.com/dajupp/homeassistant-kitafino` hinzu und wähle als Kategorie **Integration**.
3. Suche in HACS nach **Kitafino** und installiere die Integration.
4. Lege die `.env` separat in den Home-Assistant-Konfigurationsordner neben `configuration.yaml`. HACS überträgt diese Datei nicht.
5. Starte Home Assistant neu und füge Kitafino unter **Einstellungen > Geräte & Dienste** hinzu.

## Manuelle Installation

1. Kopiere `custom_components/kitafino` in den `custom_components`-Ordner deiner Home-Assistant-Konfiguration.
2. Lege die vorhandene `.env` in den Home-Assistant-Konfigurationsordner, also neben `configuration.yaml`. Sie muss die Schlüssel `username` und `password` enthalten.
3. Starte Home Assistant neu.
4. Füge unter **Einstellungen > Geräte & Dienste** die Integration **Kitafino** hinzu.

Die Integration prüft die Anmeldung beim Hinzufügen. Zugangsdaten werden weder in Logs geschrieben noch in der Integration angezeigt. Die `.env` sollte nicht in ein Versionskontrollsystem eingecheckt werden.
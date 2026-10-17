# Kitafino für Home Assistant

Die Custom Integration erstellt fünf Binary-Sensoren, einen für jeden Wochentag von Montag bis Freitag. Ein Sensor ist eingeschaltet, wenn in der zugehörigen `order_table` der Marker `bestellt_check success icon_check` vorhanden ist. Die Daten werden alle 30 Minuten aktualisiert.

## Installation

1. Kopiere `custom_components/kitafino` in den `custom_components`-Ordner deiner Home-Assistant-Konfiguration.
2. Lege die vorhandene `.env` in den Home-Assistant-Konfigurationsordner, also neben `configuration.yaml`. Sie muss die Schlüssel `username` und `password` enthalten.
3. Starte Home Assistant neu.
4. Füge unter **Einstellungen > Geräte & Dienste** die Integration **Kitafino** hinzu.

Die Integration prüft die Anmeldung beim Hinzufügen. Zugangsdaten werden weder in Logs geschrieben noch in der Integration angezeigt. Die `.env` sollte nicht in ein Versionskontrollsystem eingecheckt werden.
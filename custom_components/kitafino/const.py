from datetime import timedelta

DOMAIN = "kitafino"
PLATFORMS = ["binary_sensor", "sensor"]
SCAN_INTERVAL = timedelta(minutes=30)
LOGIN_URL = "https://auth.kitafino.de/sys_k2/index.php?action=login"
WEEKDAYS = (
    ("monday", "Montag"),
    ("tuesday", "Dienstag"),
    ("wednesday", "Mittwoch"),
    ("thursday", "Donnerstag"),
    ("friday", "Freitag"),
)
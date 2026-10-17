DOMAIN = "kitafino"
PLATFORMS = ["binary_sensor", "sensor"]
CONF_SCAN_INTERVAL = "scan_interval"
DEFAULT_SCAN_INTERVAL = 60
MIN_SCAN_INTERVAL = 5
MAX_SCAN_INTERVAL = 1440
LOGIN_URL = "https://auth.kitafino.de/sys_k2/index.php?action=login"
WEEKDAYS = (
    ("monday", "Montag"),
    ("tuesday", "Dienstag"),
    ("wednesday", "Mittwoch"),
    ("thursday", "Donnerstag"),
    ("friday", "Freitag"),
)
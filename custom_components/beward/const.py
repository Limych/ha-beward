"""Constants for Beward integration."""

# Base component constants
DOMAIN = "beward"
DATA_BEWARD = DOMAIN
VERSION = "0.0.1"
REQUIRED_FILES = [
    ".translations/en.json",
    "binary_sensor.py",
    "const.py",
    "config_flow.py",
    "manifest.json",
    "sensor.py",
]
ISSUE_URL = "https://github.com/Limych/ha-beward/issues"
ATTRIBUTION = "Data provided by Beward device."

# Configuration
CONF_EVENTS = 'events'
#
DEFAULT_ARGUMENTS = '-pred 1'

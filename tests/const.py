"""Constants for tests."""
from homeassistant.const import (
    CONF_BINARY_SENSORS,
    CONF_HOST,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_SENSORS,
    CONF_USERNAME,
)

from custom_components.beward import CONF_CAMERAS

MOCK_HOST = "192.168.0.2"
MOCK_PORT = 81
MOCK_USERNAME = "test_username"
MOCK_PASSWORD = "test_password"

# Mock config data to be used across multiple tests
MOCK_CONFIG = {
    CONF_HOST: MOCK_HOST,
    CONF_PORT: MOCK_PORT,
    CONF_USERNAME: MOCK_USERNAME,
    CONF_PASSWORD: MOCK_PASSWORD,
}
MOCK_OPTIONS = {
    CONF_CAMERAS: ["live", "last_motion"],
    CONF_BINARY_SENSORS: [],
    CONF_SENSORS: ["last_motion"],
}

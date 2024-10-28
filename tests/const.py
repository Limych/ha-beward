"""Constants for tests."""

from typing import Final

from homeassistant.const import (
    CONF_BINARY_SENSORS,
    CONF_HOST,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_SENSORS,
    CONF_USERNAME,
)

from custom_components.beward import CONF_CAMERAS

MOCK_HOST: Final = "192.168.0.2"
MOCK_PORT: Final = 81
MOCK_USERNAME: Final = "test_username"
MOCK_PASSWORD: Final = "test_password"

# Mock config data to be used across multiple tests
MOCK_CONFIG: Final = {
    CONF_HOST: MOCK_HOST,
    CONF_PORT: MOCK_PORT,
    CONF_USERNAME: MOCK_USERNAME,
    CONF_PASSWORD: MOCK_PASSWORD,
}
MOCK_OPTIONS: Final = {
    CONF_CAMERAS: ["live", "last_motion"],
    CONF_BINARY_SENSORS: [],
    CONF_SENSORS: ["last_motion"],
}
MOCK_YAML_CONFIG = MOCK_CONFIG.copy()
MOCK_YAML_CONFIG.update(MOCK_OPTIONS)

MOCK_DEVICE_ID: Final = "test_device_37354"
MOCK_DEVICE_NAME: Final = "Test Device 37354"

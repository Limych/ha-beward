"""
Component to integrate with Beward devices.

For more details about this component, please refer to
https://github.com/Limych/ha-beward
"""
import logging
import os
from datetime import timedelta

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME, CONF_HOST, \
    CONF_DEVICES
from homeassistant.util import slugify
from integrationhelper.const import CC_STARTUP_VERSION

from .const import CONF_BINARY_SENSOR, CONF_ENABLED, CONF_NAME, CONF_SENSOR, \
    DEFAULT_NAME, DOMAIN_DATA, DOMAIN, ISSUE_URL, PLATFORMS, \
    REQUIRED_FILES, VERSION, CONF_EVENTS

MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=30)

_LOGGER = logging.getLogger(__name__)

NOTIFICATION_ID = 'beward_notification'
NOTIFICATION_TITLE = 'Beward Setup'

DEVICE_SCHEMA = vol.Schema({
    vol.Required(CONF_HOST): cv.string,
    vol.Required(CONF_USERNAME): cv.string,
    vol.Required(CONF_PASSWORD): cv.string,
    vol.Optional(CONF_EVENTS, default=[]): vol.All(
        cv.ensure_list, [cv.string]),
    vol.Optional(CONF_NAME): cv.string,
})

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_DEVICES): vol.All(cv.ensure_list, [DEVICE_SCHEMA])
    }),
}, extra=vol.ALLOW_EXTRA)


def setup(hass, config):
    """Set up the Beward component."""

    # Print startup message
    _LOGGER.info(
        CC_STARTUP_VERSION.format(name=DOMAIN, version=VERSION,
                                  issue_link=ISSUE_URL)
    )

    # Check that all required files are present
    file_check = await check_files(hass)
    if not file_check:
        return False

    from beward import Beward

    devices = []

    for index, device_config in enumerate(config[DOMAIN][CONF_DEVICES]):
        device_ip = device_config.get(CONF_HOST)
        username = device_config.get(CONF_USERNAME)
        password = device_config.get(CONF_PASSWORD)
        events = device_config.get(CONF_EVENTS)

        device = Beward.factory(device_ip, username, password)

        if device is None:
            _LOGGER.error("Authorization rejected by Beward device for %s@%s",
                          username, device_ip)
            return False
        if not device.ready():
            _LOGGER.error("Could not connect to Beward device as %s@%s",
                          username, device_ip)
            return False

        name = (device_config.get(CONF_NAME)
                or 'Beward %s' % device.system_info.get('DeviceID',
                                                        '#%d' % (index + 1)))

        beward = ConfiguredBeward(device, name, events)
        devices.append(beward)
        _LOGGER.info('Connected to Beward device "%s" as %s@%s',
                     beward.name, username, device_ip)

        # Subscribe to doorbell or motion events
        if events:
            try:
                beward.register_events(hass)
            except HTTPError:
                hass.components.persistent_notification.create(
                    'Beward device configuration failed. Please verify that '
                    'API Operator permission is enabled for the device '
                    'user. A restart will be required once permissions have '
                    'been verified.',
                    title='Beward device Configuration Failure',
                    notification_id='beward_schedule_error')

                return False

    hass.data[DOMAIN] = devices

    return True


async def check_files(hass):
    """Return bool that indicates if all files are present."""

    # Verify that the user downloaded all required files.
    base = f"{hass.config.path()}/custom_components/{DOMAIN}/"
    missing = []
    for file in REQUIRED_FILES:
        fullpath = "{}{}".format(base, file)
        if not os.path.exists(fullpath):
            missing.append(file)

    if missing:
        _LOGGER.critical("The following files are missing: %s", str(missing))
        return False

    return True


class ConfiguredBeward:
    """Attach additional information to pass along with configured device."""

    def __init__(self, device, name, events):
        """Initialize configured device."""

        self._name = name
        self._device = device
        self._events = events

    @property
    def name(self):
        """Get custom device name."""
        return self._name

    @property
    def device(self):
        """Get the configured device."""
        return self._device

    @property
    def slug(self):
        """Get device slug."""
        return slugify(self._name)

    def register_events(self, hass):
        """Register events on device."""

        # Get the URL of this server
        hass_url = hass.config.api.base_url

        # Override url if another is specified in the configuration
        if self.custom_url is not None:
            hass_url = self.custom_url

        for event in self._events:
            event = self._get_event_name(event)

            self._register_event(hass_url, event)

            _LOGGER.info('Successfully registered URL for %s on %s',
                         event, self.name)

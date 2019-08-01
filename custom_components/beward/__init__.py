"""
Component to integrate with Beward security devices.

For more details about this component, please refer to
https://github.com/Limych/ha-beward
"""

import logging
import os
from datetime import datetime

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME, CONF_HOST, \
    CONF_DEVICES, CONF_NAME
from homeassistant.helpers.storage import STORAGE_DIR
from homeassistant.util import slugify

from beward import BewardGeneric
from beward.const import ALARM_MOTION, ALARM_SENSOR

_LOGGER = logging.getLogger(__name__)

# Base component constants
DOMAIN = "beward"
VERSION = "0.2.2"
REQUIRED_FILES = [
    ".translations/en.json",
    "binary_sensor.py",
    "camera.py",
    "config_flow.py",
    "manifest.json",
    "sensor.py",
]
ISSUE_URL = "https://github.com/Limych/ha-beward/issues"
ATTRIBUTION = "Data provided by Beward device."

DATA_BEWARD = DOMAIN
STORAGE_KEY = DOMAIN

CONF_EVENTS = 'events'
CONF_STREAM = 'stream'
CONF_FFMPEG_ARGUMENTS = 'ffmpeg_arguments'

EVENT_MOTION = 'motion'
EVENT_DING = 'ding'

ALARMS_TO_EVENTS = {
    ALARM_MOTION: EVENT_MOTION,
    ALARM_SENSOR: EVENT_DING,
}

ATTR_DEVICE_ID = 'device_id'

CAT_DOORBELL = 'doorbell'
CAT_CAMERA = 'camera'

DEVICE_SCHEMA = vol.Schema({
    vol.Required(CONF_HOST): cv.string,
    vol.Required(CONF_USERNAME): cv.string,
    vol.Required(CONF_PASSWORD): cv.string,
    vol.Optional(CONF_NAME): cv.string,
    vol.Optional(CONF_STREAM, default=0): int,
})

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_DEVICES): vol.All(cv.ensure_list, [DEVICE_SCHEMA])
    }),
}, extra=vol.ALLOW_EXTRA)


def setup(hass, config):
    """Set up the Beward component."""
    # Print startup message
    _LOGGER.debug('Version %s', VERSION)
    _LOGGER.info('If you have any issues with this you need to open an issue '
                 'here: %s' % ISSUE_URL)

    # Check that all required files are present
    file_check = _check_files(hass)
    if not file_check:
        return False

    from beward import Beward

    devices = []

    for index, device_config in enumerate(config[DOMAIN][CONF_DEVICES]):
        device_ip = device_config.get(CONF_HOST)
        username = device_config.get(CONF_USERNAME)
        password = device_config.get(CONF_PASSWORD)
        stream = device_config.get(CONF_STREAM)

        beward = Beward.factory(device_ip, username, password, stream=stream)

        if beward is None or not beward.ready:
            if beward is None:
                err_msg = "Authorization rejected by Beward device" + \
                          " for %s@%s" % username, device_ip
            else:
                err_msg = "Could not connect to Beward device" + \
                          " as %s@%s" % username, device_ip

            _LOGGER.error(err_msg)
            hass.components.persistent_notification.create(
                'Error: {}<br />'
                'You will need to restart Home Assistant after fixing.'
                ''.format(err_msg),
                title='Beward device Configuration Failure',
                notification_id='beward_connection_error')
            return False

        controller = BewardController(
            hass, beward,
            device_config.get(CONF_NAME)
            or 'Beward %s' % beward.system_info.get('DeviceID',
                                                    '#%d' % (index + 1)))

        devices.append(controller)
        _LOGGER.info('Connected to Beward device "%s" as %s@%s',
                     controller.name, username, device_ip)

    hass.data[DATA_BEWARD] = devices

    return True


def _check_files(hass):
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


def hasmethod(o, name: str) -> bool:
    """Return whether the object has a callable method with the given name."""
    return hasattr(o, name) and callable(getattr(o, name))


class BewardController:
    """Beward device controller."""

    def __init__(self, hass, device: BewardGeneric, name: str):
        """Initialize configured device."""
        self.hass = hass
        self._device = device
        self._name = name

        self.event_timestamp = {}
        self.event_state = {}
        self.sensors = []

    @property
    def unique_id(self):
        """Return a device unique ID."""
        return self._device.system_info.get('DeviceID', self._device.host)

    @property
    def name(self):
        """Get custom device name."""
        return self._name

    @property
    def device(self):
        """Get the configured device."""
        return self._device

    def history_image_path(self, event: str):
        """Return the path to saved image."""
        file_name = '.'.join((STORAGE_KEY, slugify(self.name), event, 'jpg'))
        return self.hass.config.path(STORAGE_DIR, file_name)

    def set_event_state(self, timestamp: datetime, event: str, state: bool):
        self.event_timestamp[event] = timestamp
        self.event_state[event] = state

        for sensor in self.sensors:
            if hasattr(sensor, 'update'):
                sensor.update()

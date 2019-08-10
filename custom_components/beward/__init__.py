"""
Component to integrate with Beward security devices.

For more details about this component, please refer to
https://github.com/Limych/ha-beward
"""

import logging
import os
import tempfile
from datetime import datetime

import homeassistant.helpers.config_validation as cv
import homeassistant.util.dt as dt_util
import voluptuous as vol
from homeassistant.components.binary_sensor import DOMAIN as BINARY_SENSOR
from homeassistant.components.camera import DOMAIN as CAMERA
from homeassistant.components.sensor import DOMAIN as SENSOR
from homeassistant.components.ffmpeg.camera import DEFAULT_ARGUMENTS
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME, CONF_HOST, \
    CONF_NAME, CONF_PORT, CONF_BINARY_SENSORS, CONF_SENSORS
from homeassistant.exceptions import PlatformNotReady
from homeassistant.helpers import discovery
from homeassistant.helpers.dispatcher import dispatcher_send
from homeassistant.helpers.storage import STORAGE_DIR
from homeassistant.util import slugify

import beward
from beward.const import ALARM_MOTION, ALARM_SENSOR
from .helpers import service_signal
from .binary_sensor import BINARY_SENSORS
from .camera import CAMERAS
from .const import CONF_STREAM, DOMAIN, VERSION, ISSUE_URL, DATA_BEWARD, \
    REQUIRED_FILES, ALARMS_TO_EVENTS, UPDATE_BEWARD, CONF_RTSP_PORT, \
    CONF_CAMERAS, CONF_FFMPEG_ARGUMENTS
from .sensor import SENSORS

_LOGGER = logging.getLogger(__name__)

DEVICE_SCHEMA = vol.Schema({
    vol.Required(CONF_HOST): cv.string,
    vol.Required(CONF_USERNAME): cv.string,
    vol.Required(CONF_PASSWORD): cv.string,
    vol.Optional(CONF_NAME): cv.string,
    vol.Optional(CONF_PORT, default=80): int,
    vol.Optional(CONF_RTSP_PORT): int,
    vol.Optional(CONF_STREAM, default=0): int,
    vol.Optional(CONF_FFMPEG_ARGUMENTS, default=DEFAULT_ARGUMENTS): cv.string,
    vol.Optional(CONF_CAMERAS, default=list(CAMERAS)):
        vol.All(cv.ensure_list, [vol.In(CAMERAS)]),
    vol.Optional(CONF_BINARY_SENSORS):
        vol.All(cv.ensure_list, [vol.In(BINARY_SENSORS)]),
    vol.Optional(CONF_SENSORS):
        vol.All(cv.ensure_list, [vol.In(SENSORS)]),
})

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.All(cv.ensure_list, [DEVICE_SCHEMA])
}, extra=vol.ALLOW_EXTRA)


def setup(hass, config):
    """Set up the Beward component."""
    # Print startup message
    _LOGGER.debug('Version %s', VERSION)
    _LOGGER.info('If you have any issues with this you need to open an issue '
                 'here: %s', ISSUE_URL)

    # Check that all required files are present
    # if not _check_files(hass):
    #     return False

    hass.data.setdefault(DATA_BEWARD, {})

    for index, device_config in enumerate(config[DOMAIN]):
        device_ip = device_config.get(CONF_HOST)
        name = device_config.get(CONF_NAME)
        username = device_config.get(CONF_USERNAME)
        password = device_config.get(CONF_PASSWORD)
        port = device_config.get(CONF_PORT)
        rtsp_port = device_config.get(CONF_RTSP_PORT)
        stream = device_config.get(CONF_STREAM)
        ffmpeg_arguments = config.get(CONF_FFMPEG_ARGUMENTS)
        cameras = device_config.get(CONF_CAMERAS)
        binary_sensors = device_config.get(CONF_BINARY_SENSORS)
        sensors = device_config.get(CONF_SENSORS)

        device = beward.Beward.factory(
            device_ip, username, password, port=port, rtsp_port=rtsp_port,
            stream=stream)

        if device is None or not device.available:
            if device is None:
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
            raise PlatformNotReady

        if name is None:
            name = 'Beward %s' % device.system_info.get('DeviceID',
                                                        '#%d' % (index + 1))
        if name in list(hass.data[DATA_BEWARD]):
            _LOGGER.error('Duplicate name! '
                          'Beward device "%s" is already exists.', name)
            continue

        controller = BewardController(hass, device, name)
        hass.data[DATA_BEWARD][name] = controller
        _LOGGER.info('Connected to Beward device "%s" as %s@%s',
                     controller.name, username, device_ip)

        if cameras:
            discovery.load_platform(hass, CAMERA, DOMAIN, {
                CONF_NAME: name,
                CONF_CAMERAS: cameras,
                CONF_FFMPEG_ARGUMENTS: ffmpeg_arguments,
            }, config)

        if binary_sensors:
            discovery.load_platform(hass, BINARY_SENSOR, DOMAIN, {
                CONF_NAME: name,
                CONF_BINARY_SENSORS: binary_sensors,
            }, config)

        if sensors:
            discovery.load_platform(hass, SENSOR, DOMAIN, {
                CONF_NAME: name,
                CONF_SENSORS: sensors,
            }, config)

    if not hass.data[DATA_BEWARD]:
        return False

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


class BewardController:
    """Beward device controller."""

    def __init__(self, hass, device: beward.BewardGeneric, name: str):
        """Initialize configured device."""
        self.hass = hass
        self._device = device
        self._name = name

        self._available = True
        self.event_timestamp = {}
        self.event_state = {}

        # Register callback to handle device alarms.
        self._device.add_alarms_handler(self._alarms_handler)
        self._device.listen_alarms(alarms=(ALARM_MOTION, ALARM_SENSOR))

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

    @property
    def available(self) -> bool:
        """Return True if device is available."""
        available = self._device.available
        if self._available != available:
            self._available = available
            _LOGGER.warning('Device "%s" is %s', self._name,
                            'reconnected' if available else 'unavailable')
        return self._available

    def history_image_path(self, event: str):
        """Return the path to saved image."""
        file_name = slugify('%s last %s' % (self.name, event)) + '.jpg'
        return self.hass.config.path(STORAGE_DIR, DOMAIN, file_name)

    def set_event_state(self, timestamp: datetime, event: str, state: bool):
        """Call Beward to refresh information."""
        _LOGGER.debug("Updating Beward component")
        if state:
            self.event_timestamp[event] = timestamp
        self.event_state[event] = state

    def _cache_image(self, event: str, image):
        """Save image for event to cache."""
        image_path = self.history_image_path(event)
        tmp_filename = ""
        image_dir = os.path.split(image_path)[0]
        _LOGGER.debug('Save camera photo to %s' % image_path)
        if not os.path.exists(image_dir):
            os.makedirs(image_dir, mode=0o755)
        try:
            # Modern versions of Python tempfile create
            # this file with mode 0o600
            with tempfile.NamedTemporaryFile(
                    mode="wb", dir=image_dir, delete=False) as fdesc:
                fdesc.write(image)
                tmp_filename = fdesc.name
            os.chmod(tmp_filename, 0o644)
            os.replace(tmp_filename, image_path)
        except OSError as error:
            _LOGGER.exception('Saving image file failed: %s', image_path)
            raise error
        finally:
            if os.path.exists(tmp_filename):
                try:
                    os.remove(tmp_filename)
                except OSError as err:
                    # If we are cleaning up then something else
                    # went wrong, so we should suppress likely
                    # follow-on errors in the cleanup
                    _LOGGER.error(
                        "Image replacement cleanup failed: %s", err)

    def _alarms_handler(self, device, timestamp: datetime, alarm: str,
                        state: bool):
        """Handle device's alarm events."""
        timestamp = dt_util.as_local(dt_util.as_utc(timestamp))
        _LOGGER.debug('Handle alarm "%s". State %s at %s' % (
            alarm, state, timestamp.isoformat()))
        if alarm in (ALARM_MOTION, ALARM_SENSOR) and device == self._device:
            event = ALARMS_TO_EVENTS[alarm]
            self.event_timestamp[event] = timestamp
            self.event_state[event] = state
            if state and isinstance(self._device, beward.BewardCamera):
                self._cache_image(event, self._device.live_image)

            dispatcher_send(
                self.hass, service_signal(UPDATE_BEWARD, self.unique_id))

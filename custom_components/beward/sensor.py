"""Sensor platform for Beward devices."""

import logging
from os import path

import homeassistant.helpers.config_validation as cv
import homeassistant.util.dt as dt_util
import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import CONF_MONITORED_CONDITIONS, ATTR_ATTRIBUTION, \
    DEVICE_CLASS_TIMESTAMP
from homeassistant.helpers.entity import Entity

from beward import BewardCamera, BewardDoorbell
from custom_components.beward import BewardController
from . import CAT_DOORBELL, CAT_CAMERA, DATA_BEWARD, ATTRIBUTION, \
    ATTR_DEVICE_ID, EVENT_MOTION, EVENT_DING

_LOGGER = logging.getLogger(__name__)

# Sensor types: Name, category, class, units, icon
SENSOR_TYPES = {
    'last_activity': [
        'Last Activity', [CAT_DOORBELL, CAT_CAMERA], DEVICE_CLASS_TIMESTAMP,
        None, 'history'],
    'last_motion': [
        'Last Motion', [CAT_DOORBELL, CAT_CAMERA], DEVICE_CLASS_TIMESTAMP,
        None, 'history'],
    'last_ding': [
        'Last Ding', [CAT_DOORBELL], DEVICE_CLASS_TIMESTAMP, None, 'history'],
}

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_MONITORED_CONDITIONS, default=list(SENSOR_TYPES)):
        vol.All(cv.ensure_list, [vol.In(SENSOR_TYPES)]),
})


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up a sensor for a Beward device."""
    sensors = []
    for controller in hass.data[DATA_BEWARD]:  # type: BewardController
        category = None
        if isinstance(controller.device, BewardCamera):
            category = CAT_CAMERA
        if isinstance(controller.device, BewardDoorbell):
            category = CAT_DOORBELL

        for sensor_type in list(SENSOR_TYPES):
            if category in SENSOR_TYPES.get(sensor_type)[1]:
                sensors.append(BewardSensor(hass, controller, sensor_type))

    add_entities(sensors, True)


class BewardSensor(Entity):
    """A sensor implementation for Beward device."""

    def __init__(self, hass, controller: BewardController, sensor_type: str):
        """Initialize a sensor for Beward device."""
        super().__init__()

        self._sensor_type = sensor_type
        self._controller = controller
        self._name = "{0} {1}".format(
            self._controller.name, SENSOR_TYPES.get(self._sensor_type)[0])
        self._device_class = SENSOR_TYPES.get(self._sensor_type)[2]
        self._units = SENSOR_TYPES.get(self._sensor_type)[3]
        self._icon = 'mdi:{}'.format(SENSOR_TYPES.get(self._sensor_type)[4])
        self._state = None
        self._unique_id = '{}-{}'.format(self._controller.unique_id,
                                         self._sensor_type)

        self._controller.sensors.append(self)

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self._unique_id

    @property
    def device_class(self):
        """Return the class of the sensor."""
        return self._device_class

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        attrs = {
            ATTR_ATTRIBUTION: ATTRIBUTION,
            ATTR_DEVICE_ID: self._controller.unique_id,
        }
        return attrs

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return self._icon

    @property
    def unit_of_measurement(self):
        """Return the units of measurement."""
        return self._units

    @property
    def should_poll(self):
        """Return the polling state."""
        return False

    def _get_file_mtime(self, event):
        image_path = self._controller.history_image_path(event)
        try:
            return dt_util.utc_from_timestamp(path.getmtime(image_path))
        except OSError:
            pass
        return None

    def _get_event_timestamp(self, event):
        event_ts = self._controller.event_timestamp.get(
            event, self._get_file_mtime(event))
        return event_ts

    def update(self):
        """Get the latest data and updates the state."""
        _LOGGER.debug("Updating data for %s sensor", self._name)

        event_ts = None
        if self._sensor_type == 'last_motion':
            event_ts = self._get_event_timestamp(EVENT_MOTION)

        elif self._sensor_type == 'last_ding':
            event_ts = self._get_event_timestamp(EVENT_DING)

        elif self._sensor_type == 'last_activity':
            event_ts = self._get_event_timestamp(EVENT_MOTION)
            ding_ts = self._get_event_timestamp(EVENT_DING)
            if ding_ts is not None and ding_ts > event_ts:
                event_ts = ding_ts

        self._state = dt_util.as_local(event_ts.replace(
            microsecond=0)).isoformat() if event_ts else None

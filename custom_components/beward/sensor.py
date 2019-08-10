"""Sensor platform for Beward devices."""

import logging
from os import path

import homeassistant.util.dt as dt_util
from homeassistant.components.amcrest import service_signal
from homeassistant.const import ATTR_ATTRIBUTION, \
    DEVICE_CLASS_TIMESTAMP, CONF_NAME
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import Entity

import beward
from .const import CAT_DOORBELL, CAT_CAMERA, DATA_BEWARD, ATTRIBUTION, \
    ATTR_DEVICE_ID, EVENT_MOTION, EVENT_DING, UPDATE_BEWARD

_LOGGER = logging.getLogger(__name__)

# Sensor types: Name, category, class, units, icon
SENSORS = {
    'last_activity': [
        'Last Activity', [CAT_DOORBELL, CAT_CAMERA], DEVICE_CLASS_TIMESTAMP,
        None, 'history'],
    'last_motion': [
        'Last Motion', [CAT_DOORBELL, CAT_CAMERA], DEVICE_CLASS_TIMESTAMP,
        None, 'history'],
    'last_ding': [
        'Last Ding', [CAT_DOORBELL], DEVICE_CLASS_TIMESTAMP, None, 'history'],
}


async def async_setup_platform(hass, config, async_add_entities,
                               discovery_info=None):
    """Set up a binary sensors for a Beward device."""
    if discovery_info is None:
        return

    name = discovery_info[CONF_NAME]
    controller = hass.data[DATA_BEWARD][name]
    category = None
    if isinstance(controller.device, beward.BewardCamera):
        category = CAT_CAMERA
    if isinstance(controller.device, beward.BewardDoorbell):
        category = CAT_DOORBELL

    sensors = []
    for sensor_type in list(SENSORS):
        if category in SENSORS.get(sensor_type)[1]:
            sensors.append(
                BewardSensor(hass, controller, sensor_type))

    async_add_entities(sensors, True)


class BewardSensor(Entity):
    """A sensor implementation for Beward device."""

    def __init__(self, hass, controller, sensor_type: str):
        """Initialize a sensor for Beward device."""
        super().__init__()

        self._unsub_dispatcher = None
        self._sensor_type = sensor_type
        self._controller = controller
        self._name = "{0} {1}".format(
            self._controller.name, SENSORS.get(self._sensor_type)[0])
        self._device_class = SENSORS.get(self._sensor_type)[2]
        self._units = SENSORS.get(self._sensor_type)[3]
        self._icon = 'mdi:{}'.format(SENSORS.get(self._sensor_type)[4])
        self._state = None
        self._unique_id = '{}-{}'.format(self._controller.unique_id,
                                         self._sensor_type)

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._controller.available

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

        state = dt_util.as_local(event_ts.replace(
            microsecond=0)).isoformat() if event_ts else None
        if self._state != state:
            self._state = state
            _LOGGER.debug('%s sensor state changed to "%s"', self._name,
                          self._state)

    async def async_on_demand_update(self):
        """Call update method."""
        self.async_schedule_update_ha_state(True)

    async def async_added_to_hass(self):
        """Register callbacks."""
        self._unsub_dispatcher = async_dispatcher_connect(
            self.hass,
            service_signal(UPDATE_BEWARD, self._controller.unique_id),
            self.async_on_demand_update)

    async def async_will_remove_from_hass(self):
        """Disconnect from update signal."""
        self._unsub_dispatcher()

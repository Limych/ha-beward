"""Binary sensor platform for Beward devices."""

import logging
from datetime import timedelta

from homeassistant.components.binary_sensor import BinarySensorDevice, \
    DEVICE_CLASS_MOTION, DEVICE_CLASS_CONNECTIVITY
from homeassistant.const import ATTR_ATTRIBUTION, CONF_NAME, \
    CONF_BINARY_SENSORS
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect

import beward
from .const import BINARY_SENSOR_SCAN_INTERVAL_SECS, EVENT_DING, \
    EVENT_MOTION, EVENT_ONLINE, CAT_DOORBELL, CAT_CAMERA, DATA_BEWARD, \
    ATTRIBUTION, ATTR_DEVICE_ID
from .helpers import service_signal

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=BINARY_SENSOR_SCAN_INTERVAL_SECS)

# Sensor types: Name, category, class
BINARY_SENSORS = {
    EVENT_DING: (
        'Ding', [CAT_DOORBELL], None),
    EVENT_MOTION: (
        'Motion', [CAT_DOORBELL, CAT_CAMERA], DEVICE_CLASS_MOTION),
    EVENT_ONLINE: (
        'Online', [CAT_DOORBELL, CAT_CAMERA], DEVICE_CLASS_CONNECTIVITY),
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
    for sensor_type in discovery_info[CONF_BINARY_SENSORS]:
        if category in BINARY_SENSORS.get(sensor_type)[1]:
            sensors.append(
                BewardBinarySensor(hass, controller, sensor_type))

    async_add_entities(sensors, True)


class BewardBinarySensor(BinarySensorDevice):
    """A binary sensor implementation for Beward device."""

    def __init__(self, hass, controller, sensor_type: str):
        """Initialize a sensor for Beward device."""
        super().__init__()

        self._unsub_dispatcher = None
        self._sensor_type = sensor_type
        self._controller = controller
        self._name = "{0} {1}".format(
            self._controller.name, BINARY_SENSORS.get(self._sensor_type)[0])
        self._device_class = BINARY_SENSORS.get(self._sensor_type)[2]
        self._state = None
        self._unique_id = '{}-{}'.format(self._controller.unique_id,
                                         self._sensor_type)

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def should_poll(self):
        """Return True if entity has to be polled for state."""
        return self._sensor_type == EVENT_ONLINE

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._sensor_type == EVENT_ONLINE or self._controller.available

    @property
    def is_on(self):
        """Return True if the binary sensor is on."""
        return self._state

    @property
    def device_class(self):
        """Return the class of the binary sensor."""
        return self._device_class

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self._unique_id

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        attrs = {
            ATTR_ATTRIBUTION: ATTRIBUTION,
            ATTR_DEVICE_ID: self._controller.unique_id,
        }
        return attrs

    async def async_update(self):
        """Get the latest data and updates the state."""
        self._update_callback(update_ha_state=False)

    @callback
    def _update_callback(self, update_ha_state=True):
        """Get the latest data and updates the state."""
        state = self._controller.available \
            if self._sensor_type == EVENT_ONLINE \
            else self._controller.event_state.get(self._sensor_type, False)
        if self._state != state:
            self._state = state
            _LOGGER.debug('%s binary sensor state changed to "%s"', self._name,
                          self._state)
            if update_ha_state:
                self.async_schedule_update_ha_state()

    async def async_added_to_hass(self):
        """Register callbacks."""
        self._unsub_dispatcher = async_dispatcher_connect(
            self.hass, service_signal('update', self._controller.unique_id),
            self._update_callback)

    async def async_will_remove_from_hass(self):
        """Disconnect from update signal."""
        self._unsub_dispatcher()

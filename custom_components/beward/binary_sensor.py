"""Binary sensor platform for Beward devices."""
import logging

from homeassistant.components.binary_sensor import BinarySensorDevice, \
    DEVICE_CLASS_OCCUPANCY, DEVICE_CLASS_MOTION
from homeassistant.const import ATTR_ATTRIBUTION

from beward import BewardCamera, BewardDoorbell
from custom_components.beward import BewardController
from . import ATTRIBUTION, DATA_BEWARD, ATTR_DEVICE_ID, EVENT_MOTION, \
    EVENT_DING, CAT_DOORBELL, CAT_CAMERA

_LOGGER = logging.getLogger(__name__)

# Sensor types: Name, category, class
SENSOR_TYPES = {
    EVENT_DING: [
        'Ding', [CAT_DOORBELL], DEVICE_CLASS_OCCUPANCY],
    EVENT_MOTION: [
        'Motion', [CAT_DOORBELL, CAT_CAMERA], DEVICE_CLASS_MOTION],
}


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
                sensors.append(
                    BewardBinarySensor(hass, controller, sensor_type))

    add_entities(sensors, True)


class BewardBinarySensor(BinarySensorDevice):
    """A binary sensor implementation for Beward device."""

    def __init__(self, hass, controller: BewardController, sensor_type: str):
        """Initialize a sensor for Beward device."""
        super().__init__()

        self._sensor_type = sensor_type
        self._controller = controller
        self._name = "{0} {1}".format(
            self._controller.name, SENSOR_TYPES.get(self._sensor_type)[0])
        self._device_class = SENSOR_TYPES.get(self._sensor_type)[2]
        self._state = None
        self._unique_id = '{}-{}'.format(self._controller.unique_id,
                                         self._sensor_type)

        self._controller.sensors.append(self)

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

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
    def should_poll(self):
        """Return the polling state."""
        return False

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        attrs = {
            ATTR_ATTRIBUTION: ATTRIBUTION,
            ATTR_DEVICE_ID: self._controller.unique_id,
        }
        return attrs

    def update(self):
        """Get the latest data and updates the state."""
        _LOGGER.debug("Updating data for %s binary sensor", self._name)
        self._state = self._controller.event_state.get(
            self._sensor_type, False)

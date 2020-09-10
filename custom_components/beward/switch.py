"""Sitch platform for Beward devices."""

#  Copyright (c) 2019, Andrey "Limych" Khrolenok <andrey@khrolenok.ru>
#  Creative Commons BY-NC-SA 4.0 International Public License
#  (see LICENSE.md or https://creativecommons.org/licenses/by-nc-sa/4.0/)

import logging

from homeassistant.components.switch import SwitchDevice
from homeassistant.const import ATTR_ATTRIBUTION, CONF_NAME, CONF_SWITCHES

from .const import ATTRIBUTION, ATTR_DEVICE_ID, DOMAIN, OUTPUT1, OUTPUT2, OUTPUT3

_LOGGER = logging.getLogger(__name__)

# Switch types: Name
SWITCHES = {
    OUTPUT1: ["Output 1"],
    OUTPUT2: ["Output 2"],
    OUTPUT3: ["Output 3"],
}


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up a switches for a Beward device."""
    if discovery_info is None:
        return

    name = discovery_info[CONF_NAME]
    device = hass.data[DOMAIN][name]

    switches = []
    for switch_id in discovery_info[CONF_SWITCHES]:
        switches.append(BewardSwitch(device, switch_id))

    async_add_entities(switches, True)


class BewardSwitch(SwitchDevice):
    """A switch implementation for Beward device."""

    def __init__(self, device, switch_id: str):
        """Initialize a sensor for Beward device."""
        super().__init__()

        self._device = device
        self._switch_id = switch_id
        self._name = "{} {}".format(self._device.name, SWITCHES[switch_id][0])
        self._unique_id = f"{self._device.unique_id}-{switch_id}"
        self._state = None

    @property
    def name(self):
        """Return the name of the switch."""
        return self._name

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._device.available

    @property
    def is_on(self):
        """Return True if switch is on."""
        return getattr(self._device, self._switch_id)

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self._unique_id

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        attrs = {
            ATTR_ATTRIBUTION: ATTRIBUTION,
            ATTR_DEVICE_ID: self._device.unique_id,
        }
        return attrs

    def turn_on(self, **kwargs):
        """Turn on the switch."""
        setattr(self._device, self._switch_id, True)

    def turn_off(self, **kwargs):
        """Turn on the switch."""
        setattr(self._device, self._switch_id, False)

"""
Integration of the JQ-300/200/100 indoor air quality meter.

For more details about this component, please refer to
https://github.com/Limych/ha-beward
"""
#  Copyright (c) 2019-2021, Andrey "Limych" Khrolenok <andrey@khrolenok.ru>
#  Creative Commons BY-NC-SA 4.0 International Public License
#  (see LICENSE.md or https://creativecommons.org/licenses/by-nc-sa/4.0/)

import logging
from abc import ABC
from typing import Any, Dict, Optional

from homeassistant.const import EVENT_HOMEASSISTANT_START
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import Entity

from . import BewardController

_LOGGER = logging.getLogger(__name__)


class BewardEntity(Entity, ABC):
    """Beward entity."""

    def __init__(self, controller: BewardController):
        """Initialize a Beward entity."""
        super().__init__()

        self.hass = controller.hass
        self._controller = controller

        self._unique_id = None
        self._name = None
        self._icon = None
        self._device_class = None
        self._state = None
        self._unsub_dispatcher = None

    @property
    def unique_id(self) -> Optional[str]:
        """Return a unique ID of the entity."""
        return self._unique_id

    @property
    def name(self) -> Optional[str]:
        """Return the name of the entity."""
        return self._name

    @property
    def icon(self) -> Optional[str]:
        """Icon to use in the frontend, if any."""
        return self._icon

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._controller.available

    @property
    def should_poll(self) -> bool:
        """Return the polling state."""
        return False

    @property
    def device_class(self) -> Optional[str]:
        """Return the class of the binary sensor."""
        return self._device_class

    @property
    def device_info(self):
        """Return the device info."""
        return self._controller.device_info

    @property
    def device_state_attributes(self) -> Optional[Dict[str, Any]]:
        """Return the state attributes."""
        return self._controller.device_state_attributes

    @callback
    def _update_callback(self, update_ha_state=True) -> None:
        """Get the latest data and updates the state if necessary."""
        pass  # pylint: disable=unnecessary-pass

    async def async_added_to_hass(self) -> None:
        """Register callbacks."""

        # pylint: disable=unused-argument
        @callback
        def sensor_startup(event):
            """Update sensor state on startup."""
            self._unsub_dispatcher = async_dispatcher_connect(
                self.hass,
                self._controller.service_signal("update"),
                self._update_callback,
            )

        self.hass.bus.async_listen_once(EVENT_HOMEASSISTANT_START, sensor_startup)

    async def async_will_remove_from_hass(self) -> None:
        """Disconnect from update signal."""
        if self._unsub_dispatcher is not None:
            self._unsub_dispatcher()

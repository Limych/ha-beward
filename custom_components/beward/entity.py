"""
Integration of the JQ-300/200/100 indoor air quality meter.

For more details about this component, please refer to
https://github.com/Limych/ha-beward
"""

#  Copyright (c) 2019-2024, Andrey "Limych" Khrolenok <andrey@khrolenok.ru>
#  Creative Commons BY-NC-SA 4.0 International Public License
#  (see LICENSE.md or https://creativecommons.org/licenses/by-nc-sa/4.0/)
from __future__ import annotations

import logging
from abc import ABC
from typing import TYPE_CHECKING, Any, Final

if TYPE_CHECKING:
    from collections.abc import Mapping

    from homeassistant.helpers.device_registry import DeviceInfo

    from . import BewardController

from homeassistant.const import EVENT_HOMEASSISTANT_START
from homeassistant.core import Event, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import Entity

_LOGGER: Final = logging.getLogger(__name__)


class BewardEntity(Entity, ABC):
    """Beward entity."""

    def __init__(self, controller: BewardController) -> None:
        """Initialize a Beward entity."""
        super().__init__()

        self.hass = controller.hass
        self._controller = controller

        self._state = None
        self._unsub_dispatcher = None

        self._attr_should_poll = False

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._controller.available

    @property
    def device_info(self) -> DeviceInfo | None:
        """Return the device info."""
        return self._controller.device_info

    @property
    def extra_state_attributes(self) -> Mapping[str, Any] | None:
        """Return entity specific state attributes."""
        return self._controller.extra_state_attributes

    @callback
    def _update_callback(self, update_ha_state: bool = True) -> None:  # noqa: FBT001, FBT002
        """Get the latest data and updates the state if necessary."""
        # pylint: disable=unnecessary-pass

    async def async_added_to_hass(self) -> None:
        """Register callbacks."""

        @callback
        def sensor_startup(event: Event) -> None:  # noqa: ARG001
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

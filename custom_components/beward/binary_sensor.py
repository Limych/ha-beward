"""Binary sensor platform for Beward devices."""

#  Copyright (c) 2019-2024, Andrey "Limych" Khrolenok <andrey@khrolenok.ru>
#  Creative Commons BY-NC-SA 4.0 International Public License
#  (see LICENSE.md or https://creativecommons.org/licenses/by-nc-sa/4.0/)
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from homeassistant.helpers.entity_platform import AddEntitiesCallback
    from homeassistant.helpers.typing import ConfigType

    from . import BewardController

import beward
from homeassistant.components.binary_sensor import ENTITY_ID_FORMAT, BinarySensorEntity
from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry
from homeassistant.const import CONF_BINARY_SENSORS
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import Entity, generate_entity_id

from .const import (
    BINARY_SENSORS,
    CAT_CAMERA,
    CAT_DOORBELL,
    DOMAIN,
    DOMAIN_YAML,
    BewardDeviceEvent,
)
from .entity import BewardEntity

_LOGGER: Final = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> bool:
    """Set up a binary sensors for a Beward device."""
    entities = []

    if entry.source == SOURCE_IMPORT:
        config = hass.data[DOMAIN_YAML]
        for index, device_config in enumerate(config):
            controller = hass.data[DOMAIN][entry.entry_id][index]  # type: BewardController
            entities.extend(_setup_entities(controller, device_config))

    else:
        config = entry.data.copy()
        config.update(entry.options)
        controller = hass.data[DOMAIN][entry.entry_id][0]  # type: BewardController
        entities.extend(_setup_entities(controller, config))

    if entities:
        async_add_entities(entities, update_before_add=True)
    return True


def _setup_entities(controller: BewardController, config: ConfigType) -> list[Entity]:
    """Set up entities for device."""
    category = None
    if isinstance(controller.device, beward.BewardDoorbell):
        category = CAT_DOORBELL
    elif isinstance(controller.device, beward.BewardCamera):
        category = CAT_CAMERA

    return [
        BewardBinarySensor(controller, x)
        for x in config.get(CONF_BINARY_SENSORS, [])
        if category in BINARY_SENSORS[x][1]
    ]


class BewardBinarySensor(BewardEntity, BinarySensorEntity):
    """A binary sensor implementation for Beward device."""

    def __init__(self, controller: BewardController, sensor_type: str) -> None:
        """Initialize a sensor for Beward device."""
        super().__init__(controller)

        self._sensor_type = sensor_type

        self._attr_unique_id = f"{self._controller.unique_id}-{sensor_type}"
        self._attr_name = f"{self._controller.name} {BINARY_SENSORS[sensor_type][0]}"
        self._attr_device_class = BINARY_SENSORS[sensor_type][2]

        self.entity_id = generate_entity_id(
            ENTITY_ID_FORMAT, self._attr_name, hass=self.hass
        )

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return (
            self._sensor_type == BewardDeviceEvent.ONLINE or self._controller.available
        )

    async def async_update(self) -> None:
        """Get the latest data and updates the state."""
        self._update_callback(update_ha_state=False)

    @callback
    def _update_callback(self, update_ha_state: bool = True) -> None:  # noqa: FBT001, FBT002
        """Get the latest data and updates the state if necessary."""
        state = (
            self._controller.available
            if self._sensor_type == BewardDeviceEvent.ONLINE
            else self._controller.event_state.get(self._sensor_type, False)
        )
        if self._attr_is_on != state:
            self._attr_is_on = state
            _LOGGER.debug(
                '%s binary sensor state changed to "%s"',
                self._attr_name,
                self._attr_is_on,
            )
            if update_ha_state:
                self.async_schedule_update_ha_state()

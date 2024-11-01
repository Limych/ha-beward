"""Sensor platform for Beward devices."""

#  Copyright (c) 2019-2024, Andrey "Limych" Khrolenok <andrey@khrolenok.ru>
#  Creative Commons BY-NC-SA 4.0 International Public License
#  (see LICENSE.md or https://creativecommons.org/licenses/by-nc-sa/4.0/)
from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from datetime import datetime

    from homeassistant.helpers.entity_platform import AddEntitiesCallback
    from homeassistant.helpers.typing import ConfigType

    from . import BewardController

import beward
import homeassistant.util.dt as dt_util
from homeassistant.components.sensor import ENTITY_ID_FORMAT, SensorEntity
from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry
from homeassistant.const import CONF_SENSORS
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import Entity, generate_entity_id

from .const import (
    CAT_CAMERA,
    CAT_DOORBELL,
    DOMAIN,
    DOMAIN_YAML,
    ICON_SENSOR,
    SENSOR_LAST_ACTIVITY,
    SENSOR_LAST_DING,
    SENSOR_LAST_MOTION,
    SENSORS,
    BewardDeviceEvent,
)
from .entity import BewardEntity

_LOGGER: Final = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> bool:
    """Set up sensors for a Beward device."""
    entities = []

    if entry.source == SOURCE_IMPORT:
        config = hass.data[DOMAIN_YAML]
        for index, device_config in enumerate(config):
            controller: BewardController = hass.data[DOMAIN][entry.entry_id][index]
            entities.extend(_setup_entities(controller, device_config))

    else:
        config = entry.data.copy()
        config.update(entry.options)
        _LOGGER.debug(hass.data[DOMAIN])
        controller: BewardController = hass.data[DOMAIN][entry.entry_id][0]
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
        BewardSensor(controller, x)
        for x in config.get(CONF_SENSORS, [])
        if category in SENSORS[x][1]
    ]


class BewardSensor(BewardEntity, SensorEntity):
    """A sensor implementation for Beward device."""

    _attr_icon: str = ICON_SENSOR

    def __init__(self, controller: BewardController, sensor_type: str) -> None:
        """Initialize a sensor for Beward device."""
        super().__init__(controller)

        self._sensor_type = sensor_type

        self._attr_unique_id = f"{self._controller.unique_id}-{sensor_type}"
        self._attr_name = f"{self._controller.name} {SENSORS[sensor_type][0]}"
        self._attr_device_class = SENSORS[sensor_type][2]

        self.entity_id = generate_entity_id(
            ENTITY_ID_FORMAT, self._attr_name, hass=self.hass
        )

    def _get_file_mtime(self, event: str) -> datetime | None:
        """Return modification time of file or None."""
        image_path = self._controller.history_image_path(event)
        try:
            return dt_util.utc_from_timestamp(Path(image_path).stat().st_mtime)
        except OSError:
            return None

    def _get_event_timestamp(self, event: str) -> datetime | None:
        """Return event's last timestamp or None."""
        return self._controller.event_timestamp.get(event) or self._get_file_mtime(
            event
        )

    @callback
    def _update_callback(self, update_ha_state: bool = True) -> None:  # noqa: FBT001, FBT002
        """Get the latest data and updates the state."""
        event_ts = None
        if self._sensor_type == SENSOR_LAST_MOTION:
            event_ts = self._get_event_timestamp(BewardDeviceEvent.MOTION)

        elif self._sensor_type == SENSOR_LAST_DING:
            event_ts = self._get_event_timestamp(BewardDeviceEvent.DING)

        elif self._sensor_type == SENSOR_LAST_ACTIVITY:
            event_ts = self._get_event_timestamp(BewardDeviceEvent.MOTION)
            ding_ts = self._get_event_timestamp(BewardDeviceEvent.DING)
            if ding_ts is not None and event_ts is not None and ding_ts > event_ts:
                event_ts = ding_ts

        state = dt_util.as_local(event_ts.replace(microsecond=0)) if event_ts else None
        if self._attr_native_value != state:
            self._attr_native_value = state
            _LOGGER.debug(
                '%s sensor state changed to "%s"',
                self._attr_name,
                self._attr_native_value,
            )

            if update_ha_state:
                self.async_schedule_update_ha_state()

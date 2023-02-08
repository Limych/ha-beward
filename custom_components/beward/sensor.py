"""Sensor platform for Beward devices."""
#  Copyright (c) 2019-2022, Andrey "Limych" Khrolenok <andrey@khrolenok.ru>
#  Creative Commons BY-NC-SA 4.0 International Public License
#  (see LICENSE.md or https://creativecommons.org/licenses/by-nc-sa/4.0/)
from __future__ import annotations

from datetime import datetime
import logging
from os import path
from typing import Final, Optional

import beward

from homeassistant.components.sensor import ENTITY_ID_FORMAT, SensorEntity
from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry
from homeassistant.const import CONF_SENSORS
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import generate_entity_id
from homeassistant.helpers.typing import ConfigType
import homeassistant.util.dt as dt_util

from . import BewardController
from .const import (
    CAT_CAMERA,
    CAT_DOORBELL,
    DOMAIN,
    DOMAIN_YAML,
    EVENT_DING,
    EVENT_MOTION,
    ICON_SENSOR,
    SENSOR_LAST_ACTIVITY,
    SENSOR_LAST_DING,
    SENSOR_LAST_MOTION,
    SENSORS,
)
from .entity import BewardEntity

_LOGGER: Final = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
) -> bool:
    """Set up sensors for a Beward device."""
    entities = []

    if entry.source == SOURCE_IMPORT:
        config = hass.data[DOMAIN_YAML]
        for index, device_config in enumerate(config):
            controller = hass.data[DOMAIN][entry.entry_id][
                index
            ]  # type: BewardController
            entities.extend(_setup_entities(controller, device_config))

    else:
        config = entry.data.copy()
        config.update(entry.options)
        _LOGGER.debug(hass.data[DOMAIN])
        controller = hass.data[DOMAIN][entry.entry_id][0]  # type: BewardController
        entities.extend(_setup_entities(controller, config))

    if entities:
        async_add_entities(entities, True)
    return True


def _setup_entities(controller: BewardController, config: ConfigType) -> list:
    """Set up entities for device."""
    category = None
    if isinstance(controller.device, beward.BewardDoorbell):
        category = CAT_DOORBELL
    elif isinstance(controller.device, beward.BewardCamera):
        category = CAT_CAMERA

    entities = []
    for sensor_type in config.get(CONF_SENSORS, []):
        if category in SENSORS[sensor_type][1]:
            entities.append(BewardSensor(controller, sensor_type))

    return entities


class BewardSensor(BewardEntity, SensorEntity):
    """A sensor implementation for Beward device."""

    def __init__(self, controller: BewardController, sensor_type: str):
        """Initialize a sensor for Beward device."""
        super().__init__(controller)

        self._sensor_type = sensor_type

        self._attr_unique_id = f"{self._controller.unique_id}-{sensor_type}"
        self._attr_name = f"{self._controller.name} {SENSORS[sensor_type][0]}"
        self._attr_icon = ICON_SENSOR
        self._attr_device_class = SENSORS[sensor_type][2]

        self.entity_id = generate_entity_id(
            ENTITY_ID_FORMAT, self._attr_name, hass=self.hass
        )

    def _get_file_mtime(self, event) -> Optional[datetime]:
        """Return modification time of file or None."""
        image_path = self._controller.history_image_path(event)
        try:
            return dt_util.utc_from_timestamp(path.getmtime(image_path))
        except OSError:
            return None

    def _get_event_timestamp(self, event) -> Optional[datetime]:
        """Return event's last timestamp or None."""
        return self._controller.event_timestamp.get(event) or self._get_file_mtime(
            event
        )

    @callback
    def _update_callback(self, update_ha_state=True) -> None:
        """Get the latest data and updates the state."""
        event_ts = None
        if self._sensor_type == SENSOR_LAST_MOTION:
            event_ts = self._get_event_timestamp(EVENT_MOTION)

        elif self._sensor_type == SENSOR_LAST_DING:
            event_ts = self._get_event_timestamp(EVENT_DING)

        elif self._sensor_type == SENSOR_LAST_ACTIVITY:
            event_ts = self._get_event_timestamp(EVENT_MOTION)
            ding_ts = self._get_event_timestamp(EVENT_DING)
            if ding_ts is not None and event_ts is not None and ding_ts > event_ts:
                event_ts = ding_ts

        state = (
            dt_util.as_local(event_ts.replace(microsecond=0)).isoformat()
            if event_ts
            else None
        )
        if self._attr_native_value != state:
            self._attr_native_value = state
            _LOGGER.debug(
                '%s sensor state changed to "%s"',
                self._attr_name,
                self._attr_native_value,
            )

            if update_ha_state:
                self.async_schedule_update_ha_state()

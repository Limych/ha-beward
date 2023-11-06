"""Component to integrate with Beward security devices.

For more details about this component, please refer to
https://github.com/Limych/ha-beward
"""
#  Copyright (c) 2019-2022, Andrey "Limych" Khrolenok <andrey@khrolenok.ru>
#  Creative Commons BY-NC-SA 4.0 International Public License
#  (see LICENSE.md or https://creativecommons.org/licenses/by-nc-sa/4.0/)
from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
import logging
import os
import tempfile
from time import sleep
from typing import Any, Dict, Final, Optional

import beward
import voluptuous as vol

from homeassistant.components.ffmpeg.camera import DEFAULT_ARGUMENTS
from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry
from homeassistant.const import (
    ATTR_ATTRIBUTION,
    CONF_BINARY_SENSORS,
    CONF_HOST,
    CONF_NAME,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_SENSORS,
    CONF_USERNAME,
)
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.dispatcher import dispatcher_send
from homeassistant.helpers.storage import STORAGE_DIR
from homeassistant.helpers.typing import ConfigType
from homeassistant.util import slugify
import homeassistant.util.dt as dt_util

from .const import (
    ALARMS_TO_EVENTS,
    ATTRIBUTION,
    BINARY_SENSORS,
    CAMERAS,
    CONF_CAMERAS,
    CONF_FFMPEG_ARGUMENTS,
    CONF_RTSP_PORT,
    CONF_STREAM,
    DEFAULT_PORT,
    DEFAULT_STREAM,
    DOMAIN,
    DOMAIN_YAML,
    PLATFORMS,
    SENSORS,
    STARTUP_MESSAGE,
    SUPPORT_LIB_URL,
    UNDO_UPDATE_LISTENER,
    BewardDeviceEvent,
)

_LOGGER: Final = logging.getLogger(__name__)

DEVICE_SCHEMA: Final = vol.Schema(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_USERNAME): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
        vol.Optional(CONF_NAME): cv.string,
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
        vol.Optional(CONF_RTSP_PORT): int,
        vol.Optional(CONF_STREAM, default=DEFAULT_STREAM): int,
        vol.Optional(CONF_FFMPEG_ARGUMENTS, default=DEFAULT_ARGUMENTS): cv.string,
        vol.Optional(CONF_CAMERAS, default=list(CAMERAS)): vol.All(
            cv.ensure_list, [vol.In(CAMERAS)]
        ),
        vol.Optional(CONF_BINARY_SENSORS): vol.All(
            cv.ensure_list, [vol.In(BINARY_SENSORS)]
        ),
        vol.Optional(CONF_SENSORS): vol.All(cv.ensure_list, [vol.In(SENSORS)]),
    }
)

CONFIG_SCHEMA: Final = vol.Schema(
    {DOMAIN: vol.All(cv.ensure_list, [DEVICE_SCHEMA])}, extra=vol.ALLOW_EXTRA
)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up this integration using YAML."""
    # Print startup message
    if DOMAIN not in hass.data:
        _LOGGER.info(STARTUP_MESSAGE)
        hass.data[DOMAIN] = {}

    if DOMAIN not in config:
        return True

    if DOMAIN not in hass.config.media_dirs:
        hass.config.media_dirs[DOMAIN] = hass.config.path(STORAGE_DIR, DOMAIN)

    hass.data[DOMAIN_YAML] = config[DOMAIN]
    hass.async_create_task(
        hass.config_entries.flow.async_init(
            DOMAIN, context={"source": SOURCE_IMPORT}, data={}
        )
    )

    return True


async def async_update_listener(hass: HomeAssistant, config_entry: ConfigEntry):
    """Handle options update."""
    await hass.config_entries.async_reload(config_entry.entry_id)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up this integration using UI."""
    hass.data[DOMAIN][entry.entry_id] = {}

    # Add update listener for config entry changes (options)
    undo_listener = entry.add_update_listener(async_update_listener)
    hass.data[DOMAIN][entry.entry_id][UNDO_UPDATE_LISTENER] = undo_listener

    if entry.source == SOURCE_IMPORT:
        config = hass.data[DOMAIN_YAML]

        for index, device_config in enumerate(config):
            hass.data[DOMAIN][entry.entry_id][index] = await _async_setup_device(
                hass, entry, device_config, index=index
            )

    else:
        config = entry.data.copy()
        config.update(entry.options)

        hass.data[DOMAIN][entry.entry_id][0] = await _async_setup_device(
            hass, entry, config
        )

    # Load platforms
    for platform in PLATFORMS:
        hass.async_add_job(
            hass.config_entries.async_forward_entry_setup(entry, platform)
        )

    return len(hass.data[DOMAIN]) > 0


async def _async_setup_device(
    hass: HomeAssistant, entry: ConfigEntry, device_config: ConfigType, index: int = 0
):
    """Set up one device."""
    device_ip = device_config.get(CONF_HOST)
    name = device_config.get(CONF_NAME)
    username = device_config.get(CONF_USERNAME)
    unique_id = entry.entry_id + "_" + str(index + 1)

    _LOGGER.debug("Connecting to device %s", device_ip)

    try:

        def get_device():
            return beward.Beward.factory(
                device_ip,
                username,
                device_config.get(CONF_PASSWORD),
                port=device_config.get(CONF_PORT, DEFAULT_PORT),
                rtsp_port=device_config.get(CONF_RTSP_PORT),
                stream=device_config.get(CONF_STREAM, DEFAULT_STREAM),
            )

        device = await hass.async_add_executor_job(get_device)
    except ValueError as exc:
        _LOGGER.error(exc)
        if exc == 'Unknown device "None"':
            msg = (
                "Device recognition error.<br />"
                "Please try restarting Home Assistant&nbsp;— it usually helps."
            )
        else:
            msg = (
                f"Error: {exc}<br />"
                f'Please <a href="{SUPPORT_LIB_URL}" target="_blank">contact the developers '
                "of the Beward library</a> to solve this problem."
            )
        hass.components.persistent_notification.create(
            msg,
            title="Beward device Initialization Failure",
            notification_id="beward_connection_error",
        )
        raise ConfigEntryNotReady from exc

    if device is None or not await hass.async_add_executor_job(
        lambda: device.available
    ):
        if device is None:
            err_msg = (
                f"Authorization rejected by Beward device for {username}@{device_ip}"
            )
        else:
            err_msg = f"Could not connect to Beward device as {username}@{device_ip}"
        _LOGGER.error(err_msg)
        raise ConfigEntryNotReady

    sys_info = await hass.async_add_executor_job(lambda: device.system_info)
    device_id = sys_info.get("DeviceID", device.host)

    if name is None:
        name = f"Beward {sys_info.get('DeviceID', unique_id)}"

    controller = BewardController(hass, device_id, device, name)
    _LOGGER.info(
        'Connected to Beward device "%s" as %s@%s',
        controller.name,
        username,
        device_ip,
    )

    return controller


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        cfg = hass.data[DOMAIN][entry.entry_id]  # type: dict
        cfg[UNDO_UPDATE_LISTENER]()
        del cfg[UNDO_UPDATE_LISTENER]

        for device in cfg.values():  # type: BewardController
            del device

        del hass.data[DOMAIN][entry.entry_id]

    return unloaded


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)


class BewardController:
    """Beward device controller."""

    def __init__(
        self,
        hass: HomeAssistant,
        unique_id: Optional[str],
        device: beward.BewardGeneric,
        name: str,
    ):
        """Initialize configured device."""
        self.hass = hass
        self.name = name
        self._device = device
        self._unique_id = unique_id

        self._available = True
        self.event_timestamp: Dict[str, datetime] = {}
        self.event_state: Dict[str, bool] = {}

        # Register callback to handle device alarms.
        self._device.add_alarms_handler(self._alarms_handler)
        self._device.listen_alarms(alarms=ALARMS_TO_EVENTS.keys())

    def __del__(self):
        """Destructor."""
        # Remove device alarms handler.
        self._device.remove_alarms_handler(self._alarms_handler)
        sleep(0.1)

    def service_signal(self, service):
        """Encode service and identifier into signal."""
        signal = f"{DOMAIN}_{service}_{slugify(self.unique_id)}"
        return signal

    @property
    def unique_id(self):
        """Return a device unique ID."""
        return self._unique_id

    @property
    def device(self):
        """Get the configured device."""
        return self._device

    @property
    def available(self) -> bool:
        """Return True if device is available."""
        return self._available

    @property
    def device_info(self):
        """Return the device info."""
        return {
            "identifiers": {(DOMAIN, self.unique_id)},
            "name": self.name,
            "manufacturer": "Beward",
            "model": self.device.system_info.get("DeviceModel"),
        }

    @property
    def extra_state_attributes(self) -> Optional[Mapping[str, Any]]:
        """Return entity specific state attributes."""
        return {
            ATTR_ATTRIBUTION: ATTRIBUTION,
        }

    def history_image_path(self, event: str):
        """Return the path to saved image."""
        file_name = slugify(f"{self.name} last {event}") + ".jpg"
        return self.hass.config.path(
            self.hass.config.media_dirs.get(
                DOMAIN, self.hass.config.path(STORAGE_DIR, DOMAIN)
            ),
            file_name,
        )

    def set_event_state(self, timestamp: datetime, event: str, state: bool):
        """Call Beward to refresh information."""
        _LOGGER.debug("Updating Beward component")
        if state:
            self.event_timestamp[event] = timestamp
        self.event_state[event] = state

    def _cache_image(self, event: str, image):
        """Save image for event to cache."""
        image_path = self.history_image_path(event)
        tmp_filename = ""
        image_dir = os.path.split(image_path)[0]

        _LOGGER.debug("Save camera photo to %s", image_path)

        if not os.path.exists(image_dir):
            os.makedirs(image_dir, mode=0o755)

        try:
            # Modern versions of Python tempfile create
            # this file with mode 0o600
            with tempfile.NamedTemporaryFile(
                mode="wb", dir=image_dir, delete=False
            ) as fdesc:
                fdesc.write(image)
                tmp_filename = fdesc.name

            os.chmod(tmp_filename, 0o644)
            os.replace(tmp_filename, image_path)

        except OSError as error:
            _LOGGER.exception("Saving image file failed: %s", image_path)
            raise error

        finally:
            if os.path.exists(tmp_filename):
                try:
                    os.remove(tmp_filename)

                except OSError as err:
                    # If we are cleaning up then something else
                    # went wrong, so we should suppress likely
                    # follow-on errors in the cleanup
                    _LOGGER.error("Image replacement cleanup failed: %s", err)

    def _alarms_handler(self, device, timestamp: datetime, alarm: str, state: bool):
        """Handle device's alarm events."""
        timestamp = dt_util.as_local(dt_util.as_utc(timestamp))

        _LOGGER.debug(
            'Handle alarm "%s". State %s at %s', alarm, state, timestamp.isoformat()
        )

        if alarm in ALARMS_TO_EVENTS and device == self._device:
            event = ALARMS_TO_EVENTS[alarm]

            if event == BewardDeviceEvent.ONLINE:
                if self._available != state:
                    _LOGGER.warning(
                        'Device "%s" is %s',
                        self.name,
                        "reconnected" if state else "unavailable",
                    )

                self._available = state

            else:
                self.event_state[event] = state
                if state:
                    self.event_timestamp[event] = timestamp
                    if isinstance(self._device, beward.BewardCamera):
                        self._cache_image(event, self._device.live_image)

            dispatcher_send(self.hass, self.service_signal("update"))

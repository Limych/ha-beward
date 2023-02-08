"""Adds config flow for Beward."""
#  Copyright (c) 2019-2022, Andrey "Limych" Khrolenok <andrey@khrolenok.ru>
#  Creative Commons BY-NC-SA 4.0 International Public License
#  (see LICENSE.md or https://creativecommons.org/licenses/by-nc-sa/4.0/)
from __future__ import annotations

from typing import Final, Optional

import beward
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import (
    CONF_BINARY_SENSORS,
    CONF_HOST,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_SENSORS,
    CONF_USERNAME,
)
from homeassistant.core import callback
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.typing import ConfigType

from .const import (  # pylint: disable=unused-import
    BINARY_SENSORS,
    CAMERAS,
    CONF_CAMERAS,
    DEFAULT_PORT,
    DOMAIN,
    SENSORS,
)


class BewardFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Beward."""

    VERSION: Final = 1
    CONNECTION_CLASS: Final = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_import(self, platform_config: ConfigType):
        """Import a config entry.

        Special type of import, we're not actually going to store any data.
        Instead, we're going to rely on the values that are in config file.
        """
        if self._async_current_entries():
            return self.async_abort(reason="no_mixed_config")

        return self.async_create_entry(title="configuration.yaml", data=platform_config)

    async def async_step_user(self, user_input: Optional[ConfigType] = None):
        """Handle a flow initialized by the user."""
        errors = {}

        for entry in self._async_current_entries():
            if entry.source == config_entries.SOURCE_IMPORT:
                return self.async_abort(reason="no_mixed_config")

        if user_input is not None:
            valid = await self._test_credentials(user_input)
            if valid:
                await self.async_set_unique_id(user_input[CONF_HOST])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=user_input[CONF_HOST], data=user_input
                )

            errors["base"] = "auth"

        return await self._show_config_form(user_input, errors)

    async def _show_config_form(
        self, cfg: ConfigType, errors
    ):  # pylint: disable=unused-argument
        """Show the configuration form to edit location data."""
        if cfg is None:
            cfg = {}
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST, default=cfg.get(CONF_HOST)): cv.string,
                    vol.Optional(
                        CONF_PORT, default=cfg.get(CONF_PORT, DEFAULT_PORT)
                    ): int,
                    vol.Required(
                        CONF_USERNAME, default=cfg.get(CONF_USERNAME)
                    ): cv.string,
                    vol.Required(
                        CONF_PASSWORD, default=cfg.get(CONF_PASSWORD)
                    ): cv.string,
                }
            ),
            errors=errors,
        )

    async def _test_credentials(self, config: ConfigType):
        """Return true if credentials is valid."""
        try:

            def test_device():
                device = beward.Beward.factory(
                    config[CONF_HOST],
                    config[CONF_USERNAME],
                    config[CONF_PASSWORD],
                    port=config.get(CONF_PORT, DEFAULT_PORT),
                )
                return device.available

            return await self.hass.async_add_executor_job(test_device)
        except Exception:  # pylint: disable=broad-except
            pass
        return False

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get component options flow."""
        return BewardOptionsFlowHandler(config_entry)


class BewardOptionsFlowHandler(config_entries.OptionsFlow):
    """Beward config flow options handler."""

    def __init__(self, config_entry):
        """Initialize Beward options flow."""
        self.config_entry = config_entry
        self.options = dict(config_entry.options)

    async def async_step_init(self, user_input=None):  # pylint: disable=unused-argument
        """Manage the options."""
        if self.config_entry.source == config_entries.SOURCE_IMPORT:
            return self.async_abort(reason="no_options_available")

        return await self.async_step_user()

    async def async_step_user(self, user_input: Optional[ConfigType] = None):
        """Handle a flow initialized by the user."""
        if user_input is not None:
            self.options.update(user_input)
            return self.async_create_entry(
                title=self.config_entry.data.get(CONF_HOST), data=self.options
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_CAMERAS,
                        default=self.options.get(CONF_CAMERAS, list(CAMERAS)),
                    ): cv.multi_select(CAMERAS),
                    vol.Optional(
                        CONF_BINARY_SENSORS,
                        default=self.options.get(CONF_BINARY_SENSORS, []),
                    ): cv.multi_select(BINARY_SENSORS),
                    vol.Optional(
                        CONF_SENSORS, default=self.options.get(CONF_SENSORS, [])
                    ): cv.multi_select(SENSORS),
                }
            ),
        )

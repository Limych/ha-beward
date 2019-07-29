"""
Component to integrate with Beward devices.

For more details about this component, please refer to
https://github.com/Limych/ha-beward
"""

import logging
import os

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME, CONF_HOST, \
    CONF_DEVICES, CONF_NAME
from integrationhelper.const import CC_STARTUP_VERSION

from .const import DOMAIN, DATA_BEWARD, REQUIRED_FILES, VERSION, CONF_EVENTS, \
    ISSUE_URL

_LOGGER = logging.getLogger(__name__)

DEVICE_SCHEMA = vol.Schema({
    vol.Required(CONF_HOST): cv.string,
    vol.Required(CONF_USERNAME): cv.string,
    vol.Required(CONF_PASSWORD): cv.string,
    # vol.Optional(CONF_EVENTS, default=[]): vol.All(
    #     cv.ensure_list, [cv.string]),
    vol.Optional(CONF_NAME): cv.string,
})

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_DEVICES): vol.All(cv.ensure_list, [DEVICE_SCHEMA])
    }),
}, extra=vol.ALLOW_EXTRA)


def setup(hass, config):
    """Set up the Beward component."""

    # Print startup message
    _LOGGER.info(
        CC_STARTUP_VERSION.format(name=DOMAIN, version=VERSION,
                                  issue_link=ISSUE_URL)
    )

    # Check that all required files are present
    file_check = check_files(hass)
    if not file_check:
        return False

    from beward import Beward

    devices = []

    for index, device_config in enumerate(config[DOMAIN][CONF_DEVICES]):
        device_ip = device_config.get(CONF_HOST)
        username = device_config.get(CONF_USERNAME)
        password = device_config.get(CONF_PASSWORD)
        # events = device_config.get(CONF_EVENTS)

        beward = Beward.factory(device_ip, username, password)

        if beward is None or not beward.ready:
            if beward is None:
                err_msg = "Authorization rejected by Beward device" + \
                          " for %s@%s" % username, device_ip
            else:
                err_msg = "Could not connect to Beward device" + \
                          " as %s@%s" % username, device_ip

            _LOGGER.error(err_msg)
            hass.components.persistent_notification.create(
                'Error: {}<br />'
                'You will need to restart Home Assistant after fixing.'
                ''.format(err_msg),
                title='Beward device Configuration Failure',
                notification_id='beward_connection_error')
            return False

        beward.name = (device_config.get(CONF_NAME)
                       or 'Beward %s' % beward.system_info
                       .get('DeviceID', '#%d' % (index + 1)))

        devices.append(beward)
        _LOGGER.info('Connected to Beward device "%s" as %s@%s',
                     beward.name, username, device_ip)

    hass.data[DOMAIN] = devices

    return True


async def check_files(hass):
    """Return bool that indicates if all files are present."""

    # Verify that the user downloaded all required files.
    base = f"{hass.config.path()}/custom_components/{DOMAIN}/"
    missing = []
    for file in REQUIRED_FILES:
        fullpath = "{}{}".format(base, file)
        if not os.path.exists(fullpath):
            missing.append(file)

    if missing:
        _LOGGER.critical("The following files are missing: %s", str(missing))
        return False

    return True

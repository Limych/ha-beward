"""Constants for Beward component."""
#  Copyright (c) 2019-2023, Andrey "Limych" Khrolenok <andrey@khrolenok.ru>
#  Creative Commons BY-NC-SA 4.0 International Public License
#  (see LICENSE.md or https://creativecommons.org/licenses/by-nc-sa/4.0/)
from __future__ import annotations

from enum import StrEnum
from typing import Dict, Final

from beward.const import ALARM_MOTION, ALARM_ONLINE, ALARM_SENSOR

from homeassistant.components.binary_sensor import (
    DOMAIN as BINARY_SENSOR,
    BinarySensorDeviceClass,
)
from homeassistant.components.camera import DOMAIN as CAMERA
from homeassistant.components.sensor import DOMAIN as SENSOR, SensorDeviceClass

# Base component constants
NAME: Final = "Beward Integration"
DOMAIN: Final = "beward"
VERSION: Final = "1.1.28-alpha"
ATTRIBUTION: Final = "Data provided by Beward device."
ISSUE_URL: Final = "https://github.com/Limych/ha-beward/issues"
SUPPORT_LIB_URL: Final = "https://github.com/Limych/py-beward/issues/new/choose"
DOMAIN_YAML: Final = f"{DOMAIN}_yaml"

STARTUP_MESSAGE: Final = f"""
-------------------------------------------------------------------
{NAME}
Version: {VERSION}
This is a custom integration!
If you have ANY issues with this you need to open an issue here:
{ISSUE_URL}
-------------------------------------------------------------------
"""

# Icons
ICON_SENSOR: Final = "mdi:history"

# Platforms
PLATFORMS: Final = [CAMERA, BINARY_SENSOR, SENSOR]

# Configuration and options
CONF_EVENTS: Final = "events"
CONF_RTSP_PORT: Final = "rtsp_port"
CONF_STREAM: Final = "stream"
CONF_FFMPEG_ARGUMENTS: Final = "ffmpeg_arguments"
CONF_CAMERAS: Final = "cameras"

UNDO_UPDATE_LISTENER: Final = "undo_update_listener"

# Defaults
DEFAULT_PORT: Final = 80
DEFAULT_STREAM: Final = 0


# Events
class BewardDeviceEvent(StrEnum):
    """Events class for Beward devices."""

    # Device is online
    ONLINE = "online"

    # Motion detected
    MOTION = "motion"

    # Ding button pressed
    DING = "ding"


# EVENT_* below are DEPRECATED
# use the BewardDeviceEvent enum instead.
EVENT_ONLINE: Final = BewardDeviceEvent.ONLINE
EVENT_MOTION: Final = BewardDeviceEvent.MOTION
EVENT_DING: Final = BewardDeviceEvent.DING

ALARMS_TO_EVENTS: Final = {
    ALARM_ONLINE: BewardDeviceEvent.ONLINE,
    ALARM_MOTION: BewardDeviceEvent.MOTION,
    ALARM_SENSOR: BewardDeviceEvent.DING,
}

CAT_DOORBELL: Final = "doorbell"
CAT_CAMERA: Final = "camera"

CAMERA_LIVE: Final = "live"
CAMERA_LAST_MOTION: Final = "last_motion"
CAMERA_LAST_DING: Final = "last_ding"

CAMERA_NAME_LIVE: Final = "{} Live"
CAMERA_NAME_LAST_MOTION: Final = "{} Last Motion"
CAMERA_NAME_LAST_DING: Final = "{} Last Ding"

SENSOR_LAST_ACTIVITY: Final = "last_activity"
SENSOR_LAST_MOTION: Final = "last_motion"
SENSOR_LAST_DING: Final = "last_ding"

# Camera types are defined like: name template, device class, device event
CAMERAS: Final[Dict[str, list]] = {
    CAMERA_LIVE: [CAMERA_NAME_LIVE, [CAT_DOORBELL, CAT_CAMERA], None],
    CAMERA_LAST_MOTION: [
        CAMERA_NAME_LAST_MOTION,
        [CAT_DOORBELL, CAT_CAMERA],
        BewardDeviceEvent.MOTION,
    ],
    CAMERA_LAST_DING: [CAMERA_NAME_LAST_DING, [CAT_DOORBELL], BewardDeviceEvent.DING],
}

# Sensor types: name, category, class
BINARY_SENSORS: Final[Dict[str, list]] = {
    BewardDeviceEvent.DING: ["Ding", [CAT_DOORBELL], None],
    BewardDeviceEvent.MOTION: [
        "Motion",
        [CAT_DOORBELL, CAT_CAMERA],
        BinarySensorDeviceClass.MOTION,
    ],
    BewardDeviceEvent.ONLINE: [
        "Online",
        [CAT_DOORBELL, CAT_CAMERA],
        BinarySensorDeviceClass.CONNECTIVITY,
    ],
}

# Sensor types: name, category, class, icon
SENSORS: Final = {
    SENSOR_LAST_ACTIVITY: [
        "Last Activity",
        [CAT_DOORBELL, CAT_CAMERA],
        SensorDeviceClass.TIMESTAMP,
    ],
    SENSOR_LAST_MOTION: [
        "Last Motion",
        [CAT_DOORBELL, CAT_CAMERA],
        SensorDeviceClass.TIMESTAMP,
    ],
    SENSOR_LAST_DING: ["Last Ding", [CAT_DOORBELL], SensorDeviceClass.TIMESTAMP],
}

"""Constants for Beward component."""
#  Copyright (c) 2019-2021, Andrey "Limych" Khrolenok <andrey@khrolenok.ru>
#  Creative Commons BY-NC-SA 4.0 International Public License
#  (see LICENSE.md or https://creativecommons.org/licenses/by-nc-sa/4.0/)

from typing import Dict

from beward.const import ALARM_MOTION, ALARM_ONLINE, ALARM_SENSOR
from homeassistant.components.binary_sensor import (
    DEVICE_CLASS_CONNECTIVITY,
    DEVICE_CLASS_MOTION,
)
from homeassistant.components.binary_sensor import DOMAIN as BINARY_SENSOR
from homeassistant.components.camera import DOMAIN as CAMERA
from homeassistant.components.sensor import DOMAIN as SENSOR
from homeassistant.const import DEVICE_CLASS_TIMESTAMP

# Base component constants
NAME = "Beward Integration"
DOMAIN = "beward"
VERSION = "1.1.18.dev0"
ATTRIBUTION = "Data provided by Beward device."
ISSUE_URL = "https://github.com/Limych/ha-beward/issues"
SUPPORT_LIB_URL = "https://github.com/Limych/py-beward/issues/new/choose"
DOMAIN_YAML = f"{DOMAIN}_yaml"

STARTUP_MESSAGE = f"""
-------------------------------------------------------------------
{NAME}
Version: {VERSION}
This is a custom integration!
If you have ANY issues with this you need to open an issue here:
{ISSUE_URL}
-------------------------------------------------------------------
"""

# Icons
ICON_SENSOR = "mdi:history"

# Platforms
PLATFORMS = [CAMERA, BINARY_SENSOR, SENSOR]

# Configuration and options
CONF_EVENTS = "events"
CONF_RTSP_PORT = "rtsp_port"
CONF_STREAM = "stream"
CONF_FFMPEG_ARGUMENTS = "ffmpeg_arguments"
CONF_CAMERAS = "cameras"

UNDO_UPDATE_LISTENER = "undo_update_listener"

# Defaults
DEFAULT_PORT = 80
DEFAULT_STREAM = 0

# Events
EVENT_ONLINE = "online"
EVENT_MOTION = "motion"
EVENT_DING = "ding"
#
ALARMS_TO_EVENTS = {
    ALARM_ONLINE: EVENT_ONLINE,
    ALARM_MOTION: EVENT_MOTION,
    ALARM_SENSOR: EVENT_DING,
}

# Attributes
ATTR_DEVICE_ID = "device_id"


CAT_DOORBELL = "doorbell"
CAT_CAMERA = "camera"

CAMERA_LIVE = "live"
CAMERA_LAST_MOTION = "last_motion"
CAMERA_LAST_DING = "last_ding"

CAMERA_NAME_LIVE = "{} Live"
CAMERA_NAME_LAST_MOTION = "{} Last Motion"
CAMERA_NAME_LAST_DING = "{} Last Ding"

SENSOR_LAST_ACTIVITY = "last_activity"
SENSOR_LAST_MOTION = "last_motion"
SENSOR_LAST_DING = "last_ding"

# Camera types are defined like: name template, device class, device event
CAMERAS: Dict[str, list] = {
    CAMERA_LIVE: [CAMERA_NAME_LIVE, [CAT_DOORBELL, CAT_CAMERA], None],
    CAMERA_LAST_MOTION: [
        CAMERA_NAME_LAST_MOTION,
        [CAT_DOORBELL, CAT_CAMERA],
        EVENT_MOTION,
    ],
    CAMERA_LAST_DING: [CAMERA_NAME_LAST_DING, [CAT_DOORBELL], EVENT_DING],
}

# Sensor types: name, category, class
BINARY_SENSORS: Dict[str, list] = {
    EVENT_DING: ["Ding", [CAT_DOORBELL], None],
    EVENT_MOTION: ["Motion", [CAT_DOORBELL, CAT_CAMERA], DEVICE_CLASS_MOTION],
    EVENT_ONLINE: ["Online", [CAT_DOORBELL, CAT_CAMERA], DEVICE_CLASS_CONNECTIVITY],
}

# Sensor types: name, category, class, icon
SENSORS = {
    SENSOR_LAST_ACTIVITY: [
        "Last Activity",
        [CAT_DOORBELL, CAT_CAMERA],
        DEVICE_CLASS_TIMESTAMP,
    ],
    SENSOR_LAST_MOTION: [
        "Last Motion",
        [CAT_DOORBELL, CAT_CAMERA],
        DEVICE_CLASS_TIMESTAMP,
    ],
    SENSOR_LAST_DING: ["Last Ding", [CAT_DOORBELL], DEVICE_CLASS_TIMESTAMP],
}

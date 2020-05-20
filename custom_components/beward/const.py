"""Constants for Beward component."""
from datetime import timedelta

from beward.const import ALARM_MOTION, ALARM_SENSOR

# Base component constants
DOMAIN = "beward"
VERSION = "1.1.4"
ISSUE_URL = "https://github.com/Limych/ha-beward/issues"
ATTRIBUTION = "Data provided by Beward device."

SUPPORT_LIB_URL = "https://github.com/Limych/py-beward/issues/new/choose"

CONF_EVENTS = "events"
CONF_RTSP_PORT = "rtsp_port"
CONF_STREAM = "stream"
CONF_FFMPEG_ARGUMENTS = "ffmpeg_arguments"
CONF_CAMERAS = "cameras"

EVENT_ONLINE = "online"
EVENT_MOTION = "motion"
EVENT_DING = "ding"

ALARMS_TO_EVENTS = {
    ALARM_MOTION: EVENT_MOTION,
    ALARM_SENSOR: EVENT_DING,
}

ATTR_DEVICE_ID = "device_id"

CAT_DOORBELL = "doorbell"
CAT_CAMERA = "camera"

DEVICE_CHECK_INTERVAL = timedelta(seconds=15)

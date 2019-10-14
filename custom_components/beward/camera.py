"""
Support for viewing the camera feed from a Beward devices.

For more details about this component, please refer to
https://github.com/Limych/ha-beward
"""

import asyncio
import datetime
import logging
from asyncio import run_coroutine_threadsafe

import aiohttp
import async_timeout
from homeassistant.components.camera import Camera, SUPPORT_STREAM
from homeassistant.components.ffmpeg import DATA_FFMPEG
from homeassistant.components.local_file.camera import LocalFile
from homeassistant.const import CONF_NAME
from homeassistant.helpers.aiohttp_client import async_get_clientsession, \
    async_aiohttp_proxy_stream

import beward
from .const import CONF_FFMPEG_ARGUMENTS, EVENT_MOTION, EVENT_DING, \
    CAT_DOORBELL, CAT_CAMERA, CONF_CAMERAS, DATA_BEWARD

_LOGGER = logging.getLogger(__name__)

_UPDATE_INTERVAL_LIVE = datetime.timedelta(seconds=1)
_SESSION_TIMEOUT = 10  # seconds

CAMERA_LIVE = 'live'
CAMERA_LAST_MOTION = 'last_motion'
CAMERA_LAST_DING = 'last_ding'

CAMERA_NAME_LIVE = "{} Live"
CAMERA_NAME_LAST_MOTION = "{} Last Motion"
CAMERA_NAME_LAST_DING = "{} Last Ding"

# Camera types are defined like: name template, device class, device event
CAMERAS = {
    CAMERA_LIVE: (
        CAMERA_NAME_LIVE, [CAT_DOORBELL, CAT_CAMERA], None),
    CAMERA_LAST_MOTION: (
        CAMERA_NAME_LAST_MOTION, [CAT_DOORBELL, CAT_CAMERA], EVENT_MOTION),
    CAMERA_LAST_DING: (
        CAMERA_NAME_LAST_DING, [CAT_DOORBELL], EVENT_DING),
}


async def async_setup_platform(hass, config, async_add_entities,
                               discovery_info=None):
    """Set up a cameras for a Beward device."""
    if discovery_info is None:
        return

    name = discovery_info[CONF_NAME]
    controller = hass.data[DATA_BEWARD][name]
    category = None
    if isinstance(controller.device, beward.BewardCamera):
        category = CAT_CAMERA
    if isinstance(controller.device, beward.BewardDoorbell):
        category = CAT_DOORBELL

    cameras = []
    for camera_type in discovery_info[CONF_CAMERAS]:
        if category in CAMERAS.get(camera_type)[1]:
            if camera_type == CAMERA_LIVE:
                cameras.append(BewardCamera(controller, config))
            else:
                cameras.append(LocalFile(
                    CAMERAS.get(camera_type)[0].format(name),
                    controller.history_image_path(
                        CAMERAS.get(camera_type)[2])))

    async_add_entities(cameras, True)


class BewardCamera(Camera):
    """The camera on a Beward device."""

    def __init__(self, controller, config):
        """Initialize the camera on a Beward device."""
        super().__init__()
        self.hass = controller.hass
        self._unsub_dispatcher = None
        self._controller = controller
        self._name = CAMERA_NAME_LIVE.format(controller.name)
        self._url = controller.device.live_image_url
        self._stream_url = controller.device.rtsp_live_video_url
        self._last_image = None
        self._interval = _UPDATE_INTERVAL_LIVE
        self._last_update = datetime.datetime.min

        self._ffmpeg_input = "-rtsp_transport tcp -i " + self._stream_url
        self._ffmpeg_arguments = config.get(CONF_FFMPEG_ARGUMENTS)

    async def stream_source(self):
        """Return the stream source."""
        return self._stream_url

    @property
    def supported_features(self):
        """Return supported features."""
        if self._stream_url:
            return SUPPORT_STREAM
        return 0

    @property
    def name(self):
        """Get the name of the camera."""
        return self._name

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._controller.available

    def camera_image(self):
        """Return camera image."""
        return run_coroutine_threadsafe(
            self.async_camera_image(), self.hass.loop).result()

    async def async_camera_image(self):
        """Pull a still image from the camera."""
        now = datetime.datetime.now()

        if self._last_image and now - self._last_update < self._interval:
            return self._last_image

        try:
            websession = async_get_clientsession(self.hass)
            with async_timeout.timeout(_SESSION_TIMEOUT):
                response = await websession.get(self._url)

            self._last_image = await response.read()
            self._last_update = now
            return self._last_image
        except asyncio.TimeoutError:
            _LOGGER.error("Camera image timed out")
            return self._last_image
        except aiohttp.ClientError as error:
            _LOGGER.error("Error getting camera image: %s", error)
            return self._last_image

    async def handle_async_mjpeg_stream(self, request):
        """Generate an HTTP MJPEG stream from the camera."""
        if not self._stream_url:
            return None

        from haffmpeg.camera import CameraMjpeg

        ffmpeg_manager = self.hass.data[DATA_FFMPEG]
        stream = CameraMjpeg(ffmpeg_manager.binary, loop=self.hass.loop)
        await stream.open_camera(
            self._ffmpeg_input, extra_cmd=self._ffmpeg_arguments)

        try:
            stream_reader = await stream.get_reader()
            return await async_aiohttp_proxy_stream(
                self.hass, request, stream_reader,
                ffmpeg_manager.ffmpeg_stream_content_type)
        finally:
            await stream.close()

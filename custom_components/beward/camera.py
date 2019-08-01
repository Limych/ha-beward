"""
Support for viewing the camera feed from a Beward devices.

For more details about this component, please refer to
https://github.com/Limych/ha-beward
"""
import asyncio
import datetime
import logging

import aiohttp
import async_timeout
import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.camera import Camera, SUPPORT_STREAM, \
    PLATFORM_SCHEMA
from homeassistant.components.ffmpeg import DATA_FFMPEG
from homeassistant.components.ffmpeg.camera import DEFAULT_ARGUMENTS
from homeassistant.components.local_file.camera import LocalFile
from homeassistant.helpers.aiohttp_client import async_get_clientsession, \
    async_aiohttp_proxy_stream
from homeassistant.util.async_ import run_coroutine_threadsafe

from . import BewardController, DATA_BEWARD, EVENT_MOTION, EVENT_DING, \
    CONF_FFMPEG_ARGUMENTS

_LOGGER = logging.getLogger(__name__)

_NAME_LIVE = "{} Live"
_NAME_LAST_MOTION = "{} Last Motion"
_NAME_LAST_VISITOR = "{} Last Ding"
_INTERVAL_LIVE = datetime.timedelta(seconds=1)
_TIMEOUT = 10  # seconds

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_FFMPEG_ARGUMENTS, default=DEFAULT_ARGUMENTS): cv.string,
})


async def async_setup_platform(hass, config, async_add_entities,
                               discovery_info=None):
    """Set up the Beward camera platform."""
    for device in hass.data[DATA_BEWARD]:  # type: BewardController
        async_add_entities([
            BewardCamera(device, config),
            LocalFile(
                _NAME_LAST_MOTION.format(device.name),
                device.history_image_path(EVENT_MOTION)),
            LocalFile(
                _NAME_LAST_VISITOR.format(device.name),
                device.history_image_path(EVENT_DING)),
        ])


class BewardCamera(Camera):
    """The camera on a Beward device."""

    def __init__(self, controller: BewardController, config):
        """Initialize the camera on a Beward device."""
        super().__init__()
        self.hass = controller.hass
        self._controller = controller
        self._name = _NAME_LIVE.format(controller.name)
        self._url = controller.device.live_image_url
        self._stream_url = controller.device.rtsp_live_video_url
        self._last_image = None
        self._interval = _INTERVAL_LIVE
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
            with async_timeout.timeout(_TIMEOUT):
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

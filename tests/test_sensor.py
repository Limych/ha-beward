# pylint: disable=protected-access,redefined-outer-name
"""Test beward sensors."""
#  Copyright (c) 2019-2023, Andrey "Limych" Khrolenok <andrey@khrolenok.ru>
#  Creative Commons BY-NC-SA 4.0 International Public License
#  (see LICENSE.md or https://creativecommons.org/licenses/by-nc-sa/4.0/)
from __future__ import annotations

from unittest.mock import Mock, patch

from beward import BewardDoorbell
import pytest

from custom_components.beward import BewardController
from custom_components.beward.const import (
    ICON_SENSOR,
    SENSOR_LAST_ACTIVITY,
    SENSOR_LAST_DING,
    SENSOR_LAST_MOTION,
)
from custom_components.beward.sensor import BewardSensor
from homeassistant.const import DEVICE_CLASS_TIMESTAMP
from homeassistant.core import HomeAssistant
import homeassistant.util.dt as dt_util

from .const import MOCK_DEVICE_ID, MOCK_DEVICE_NAME


@pytest.fixture
def controller(hass: HomeAssistant):
    """Generate test controller."""
    device = Mock(BewardDoorbell)
    return BewardController(hass, MOCK_DEVICE_ID, device, MOCK_DEVICE_NAME)


async def test_last_activity_sensor(hass: HomeAssistant, controller: BewardController):
    """Test last activity sensor."""
    mock_ts = dt_util.utcnow()
    mock_ts_local = mock_ts.replace(microsecond=0)

    sensor = BewardSensor(controller, SENSOR_LAST_ACTIVITY)

    assert sensor
    assert sensor.unique_id == f"{MOCK_DEVICE_ID}-{SENSOR_LAST_ACTIVITY}"
    assert sensor.name == f"{MOCK_DEVICE_NAME} Last Activity"
    assert sensor.icon == ICON_SENSOR
    assert sensor.device_class == DEVICE_CLASS_TIMESTAMP
    assert sensor.entity_id == f"sensor.{MOCK_DEVICE_ID}_{SENSOR_LAST_ACTIVITY}"
    assert sensor.state is None

    with patch.object(sensor, "_get_event_timestamp", return_value=mock_ts):
        sensor._update_callback(True)
        assert sensor.state == mock_ts_local.isoformat()


async def test_last_motion_sensor(hass: HomeAssistant, controller: BewardController):
    """Test last motion sensor."""
    mock_ts = dt_util.utcnow()
    mock_ts_local = mock_ts.replace(microsecond=0)

    sensor = BewardSensor(controller, SENSOR_LAST_MOTION)

    assert sensor
    assert sensor.unique_id == f"{MOCK_DEVICE_ID}-{SENSOR_LAST_MOTION}"
    assert sensor.name == f"{MOCK_DEVICE_NAME} Last Motion"
    assert sensor.icon == ICON_SENSOR
    assert sensor.device_class == DEVICE_CLASS_TIMESTAMP
    assert sensor.entity_id == f"sensor.{MOCK_DEVICE_ID}_{SENSOR_LAST_MOTION}"
    assert sensor.state is None

    with patch.object(sensor, "_get_event_timestamp", return_value=mock_ts):
        sensor._update_callback(True)
        assert sensor.state == mock_ts_local.isoformat()


async def test_last_ding_sensor(hass: HomeAssistant, controller: BewardController):
    """Test last ding sensor."""
    mock_ts = dt_util.utcnow()
    mock_ts_local = mock_ts.replace(microsecond=0)

    sensor = BewardSensor(controller, SENSOR_LAST_DING)

    assert sensor
    assert sensor.unique_id == f"{MOCK_DEVICE_ID}-{SENSOR_LAST_DING}"
    assert sensor.name == f"{MOCK_DEVICE_NAME} Last Ding"
    assert sensor.icon == ICON_SENSOR
    assert sensor.device_class == DEVICE_CLASS_TIMESTAMP
    assert sensor.entity_id == f"sensor.{MOCK_DEVICE_ID}_{SENSOR_LAST_DING}"
    assert sensor.state is None

    with patch.object(sensor, "_get_event_timestamp", return_value=mock_ts):
        sensor._update_callback(True)
        assert sensor.state == mock_ts_local.isoformat()

# pylint: disable=protected-access,redefined-outer-name
"""Test beward setup process."""

from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import STORAGE_DIR
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    assert_setup_component,
)

from custom_components.beward import (
    BewardController,
)
from custom_components.beward.const import DOMAIN, UNDO_UPDATE_LISTENER

from .const import MOCK_CONFIG, MOCK_YAML_CONFIG


async def test_async_setup(hass: HomeAssistant):
    """Test a successful setup component."""
    assert DOMAIN not in hass.config.media_dirs

    with assert_setup_component(1, DOMAIN):
        await async_setup_component(hass, DOMAIN, {DOMAIN: MOCK_YAML_CONFIG})
        await hass.async_block_till_done()

        assert DOMAIN in hass.config.media_dirs
        assert hass.config.media_dirs[DOMAIN] == hass.config.path(STORAGE_DIR, DOMAIN)

    await hass.async_start()
    await hass.async_block_till_done()


async def test_async_setup_2(hass: HomeAssistant):
    """Test a successful setup component."""
    test_path = "/test_path"

    assert DOMAIN not in hass.config.media_dirs

    hass.config.media_dirs[DOMAIN] = test_path

    with assert_setup_component(1, DOMAIN):
        await async_setup_component(hass, DOMAIN, {DOMAIN: MOCK_YAML_CONFIG})
        await hass.async_block_till_done()

        assert DOMAIN in hass.config.media_dirs
        assert hass.config.media_dirs[DOMAIN] == test_path

    await hass.async_start()
    await hass.async_block_till_done()


# We can pass fixtures as defined in conftest.py to tell pytest to use the fixture
# for a given test. We can also leverage fixtures and mocks that are available in
# Home Assistant using the pytest_homeassistant_custom_component plugin.
# Assertions allow you to verify that the return value of whatever is on the left
# side of the assertion matches with the right side.
async def test_setup_unload_and_reload_entry(hass: HomeAssistant, bypass_get_data):
    """Test entry setup and unload."""
    hass.data.setdefault(DOMAIN, {})

    # Create a mock entry so we don't have to go through config flow
    config_entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG, entry_id="test")
    config_entry.add_to_hass(hass)

    # Set up the entry and assert that the values set during setup are where we expect
    # them to be. Because we have patched the beward.Beward.factory call, no code from
    # beward library actually runs.
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    #
    assert config_entry.state is ConfigEntryState.LOADED
    assert DOMAIN in hass.data
    assert config_entry.entry_id in hass.data[DOMAIN]
    #
    cfg = hass.data[DOMAIN][config_entry.entry_id]
    assert UNDO_UPDATE_LISTENER in cfg
    assert callable(cfg[UNDO_UPDATE_LISTENER])
    assert 0 in cfg
    assert isinstance(cfg[0], BewardController)

    # Reload the entry and assert that the data from above is still there
    await hass.config_entries.async_reload(config_entry.entry_id)
    await hass.async_block_till_done()
    #
    assert DOMAIN in hass.data
    assert config_entry.entry_id in hass.data[DOMAIN]
    #
    cfg = hass.data[DOMAIN][config_entry.entry_id]
    assert 0 in cfg
    assert isinstance(cfg[0], BewardController)

    # Unload the entry and verify that the data has been removed
    await hass.config_entries.async_unload(config_entry.entry_id)
    await hass.async_block_till_done()
    #
    assert config_entry.entry_id not in hass.data[DOMAIN]


# ruff: noqa: ERA001
# async def test_setup_entry_exception(hass: HomeAssistant, error_on_get_data):
#     """Test ConfigEntryNotReady when API raises an exception during entry setup."""
#     config_entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG, entry_id="test")
#
#     # In this case we are testing the condition where async_setup_entry raises
#     # ConfigEntryNotReady using the `error_on_get_data` fixture which simulates
#     # an error.
#     with pytest.raises(ConfigEntryNotReady):
#         assert await async_setup_entry(hass, config_entry)

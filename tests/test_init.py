"""Tests for the We-Wash integration."""
from unittest.mock import patch
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.wewash.const import DOMAIN

async def test_setup_unload_config_entry(hass: HomeAssistant) -> None:
    """Test setting up and unloading the config entry."""
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        data={"username": "test@example.com", "password": "test123"},
    )

    # Mock the API responses
    with patch(
        "custom_components.wewash.coordinator.WeWashDataUpdateCoordinator._authenticate"
    ), patch(
        "custom_components.wewash.coordinator.WeWashDataUpdateCoordinator._async_update_data",
        return_value={
            "user": {
                "credits": {"amount": 10.0, "currency": "EUR"},
            },
            "laundry_rooms": {
                "selectedLaundryRooms": [{
                    "id": "test_room",
                    "name": "Test Room",
                    "serviceAvailability": {
                        "availableWashers": 2,
                        "availableDryers": 1,
                    }
                }]
            },
            "reservations": {
                "items": []
            }
        }
    ):
        config_entry.add_to_hass(hass)
        assert await hass.config_entries.async_setup(config_entry.entry_id)
        await hass.async_block_till_done()

        # Verify that the integration was set up correctly
        assert DOMAIN in hass.data
        assert config_entry.entry_id in hass.data[DOMAIN]

        # Test unloading the config entry
        assert await hass.config_entries.async_unload(config_entry.entry_id)
        await hass.async_block_till_done()

        # Verify that the integration was unloaded correctly
        assert config_entry.entry_id not in hass.data[DOMAIN]

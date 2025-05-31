"""Tests for the WeWash binary sensors."""
import pytest
from unittest.mock import patch, MagicMock

from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from custom_components.wewash.binary_sensor import async_setup_entry
from custom_components.wewash.const import DOMAIN


async def test_binary_sensor_setup_no_entities(hass, mock_config_entry, mock_coordinator):
    """Test binary sensor setup creates no entities as per entities.md."""
    # Store the coordinator in hass data
    hass.data[DOMAIN] = {mock_config_entry.entry_id: mock_coordinator}
    
    # Mock the async_add_entities function
    async_add_entities = MagicMock(spec=AddEntitiesCallback)
    
    # Call setup entry
    await async_setup_entry(hass, mock_config_entry, async_add_entities)
    
    # Verify no entities were added (as per entities.md specification)
    assert async_add_entities.call_count == 1
    
    # Get the list of added entities
    entities = async_add_entities.call_args[0][0]
    
    # Check that no entities were created
    assert len(entities) == 0

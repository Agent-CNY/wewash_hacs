"""Tests for the WeWash integration setup."""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry, ConfigEntriesFlowManager
from homeassistant.const import Platform

from custom_components.wewash import (
    async_setup,
    async_setup_entry,
    async_unload_entry,
    PLATFORMS
)
from custom_components.wewash.const import DOMAIN
from custom_components.wewash.coordinator import WeWashDataUpdateCoordinator

# Fixtures and test data are imported from conftest.py automatically


async def test_setup(hass):
    """Test the setup function."""
    # Call setup
    result = await async_setup(hass, {})
    
    # Verify it initializes the domain data structure
    assert DOMAIN in hass.data
    assert result is True


async def test_setup_entry(hass, mock_config_entry):
    """Test setting up an entry."""
    # Initialize domain data
    hass.data[DOMAIN] = {}
    
    # Mock the coordinator and config entry setup with AsyncMock
    with patch(
        "custom_components.wewash.coordinator.WeWashDataUpdateCoordinator.async_config_entry_first_refresh",
        new_callable=AsyncMock
    ), patch.object(
        hass.config_entries, 
        "async_forward_entry_setups",
        new_callable=AsyncMock,
        return_value=None
    ) as mock_forward:
        
        # Test the setup
        result = await async_setup_entry(hass, mock_config_entry)
        
        # Verify results
        assert result is True
        assert mock_config_entry.entry_id in hass.data[DOMAIN]
        assert isinstance(hass.data[DOMAIN][mock_config_entry.entry_id], WeWashDataUpdateCoordinator)
        
        # Check that platforms were set up
        mock_forward.assert_called_once_with(mock_config_entry, PLATFORMS)


async def test_unload_entry(hass, mock_config_entry):
    """Test unloading an entry."""
    # Setup mock coordinator
    coordinator = MagicMock()
    hass.data[DOMAIN] = {mock_config_entry.entry_id: coordinator}
    
    # Mock the unload platforms function with AsyncMock
    with patch.object(
        hass.config_entries,
        "async_unload_platforms",
        new_callable=AsyncMock,
        return_value=True
    ) as mock_unload:
        
        # Test the unload
        result = await async_unload_entry(hass, mock_config_entry)
        
        # Verify results
        assert result is True
        assert mock_config_entry.entry_id not in hass.data[DOMAIN]
        
        # Check that platforms were unloaded
        mock_unload.assert_called_once_with(mock_config_entry, PLATFORMS)

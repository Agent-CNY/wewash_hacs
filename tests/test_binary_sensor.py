"""Tests for the WeWash binary sensors."""
import pytest
from unittest.mock import patch, MagicMock

from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from custom_components.wewash.binary_sensor import (
    async_setup_entry,
    WeWashBinarySensor
)
from custom_components.wewash.const import DOMAIN

# Fixtures and test data are imported from conftest.py automatically
from conftest import (
    RESERVATIONS_RESPONSE, LAUNDRY_ROOMS_RESPONSE
)


async def test_binary_sensor_setup(hass, mock_config_entry, mock_coordinator):
    """Test binary sensor setup."""
    # Store the coordinator in hass data
    hass.data[DOMAIN] = {mock_config_entry.entry_id: mock_coordinator}
    
    # Mock the async_add_entities function
    async_add_entities = MagicMock(spec=AddEntitiesCallback)
    
    # Call setup entry
    await async_setup_entry(hass, mock_config_entry, async_add_entities)
    
    # Verify entities were added
    assert async_add_entities.call_count == 1
    
    # Get the list of added entities
    entities = async_add_entities.call_args[0][0]
    
    # Check that we have the right number of entities
    # We expect binary sensors for reservations with status ACTIVE
    # From the test data, we have 2 reservations, but only 1 is ACTIVE
    assert len(entities) >= 1


async def test_reservation_binary_sensor(hass, mock_coordinator):
    """Test the reservation binary sensor."""
    from custom_components.wewash.binary_sensor import WeWashBinarySensorEntityDescription
    
    # Get the active reservation from test data
    reservations = RESERVATIONS_RESPONSE["items"]
    active_reservation = next((r for r in reservations if r["status"] == "ACTIVE"), None)
    assert active_reservation is not None
    
    # Create a description for the test
    def is_reservation_ready(data, reservation_id):
        for reservation in data["reservations"]["items"]:
            if str(reservation["reservationId"]) == reservation_id:
                return reservation["status"] == "READY"
        return False
    
    description = WeWashBinarySensorEntityDescription(
        key="reservation_ready",
        name="Test Reservation Ready",
        is_on_fn=is_reservation_ready,
    )
    
    # Create the binary sensor  
    sensor = WeWashBinarySensor(
        mock_coordinator, 
        description, 
        str(active_reservation['reservationId'])
    )
    
    # Test basic properties
    assert "Test Reservation Ready" in sensor.name
    assert sensor.unique_id.endswith(f"_{active_reservation['reservationId']}")
    
    # Test the is_on property - it should be False since status is "ACTIVE" not "READY"
    assert sensor.is_on is False


async def test_reservation_binary_sensor_off(hass, mock_coordinator):
    """Test the reservation binary sensor in the OFF state."""
    from custom_components.wewash.binary_sensor import WeWashBinarySensorEntityDescription
    
    # Get the timed out reservation from test data
    reservations = RESERVATIONS_RESPONSE["items"]
    timed_out_reservation = next((r for r in reservations if r["status"] == "RESERVATION_TIMED_OUT"), None)
    assert timed_out_reservation is not None
    
    def is_reservation_ready(data, reservation_id):
        for reservation in data["reservations"]["items"]:
            if str(reservation["reservationId"]) == reservation_id:
                return reservation["status"] == "READY"
        return False
    
    description = WeWashBinarySensorEntityDescription(
        key="reservation_ready",
        name="Test Reservation Ready",
        is_on_fn=is_reservation_ready,
    )
    
    # Create the binary sensor
    sensor = WeWashBinarySensor(
        mock_coordinator, 
        description,
        str(timed_out_reservation['reservationId'])
    )
    
    # Test that the sensor is off (RESERVATION_TIMED_OUT != "READY")
    assert sensor.is_on is False

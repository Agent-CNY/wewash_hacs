"""Tests for the WeWash sensors."""
import pytest
from unittest.mock import patch, MagicMock

from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.sensor import SensorDeviceClass

from custom_components.wewash.sensor import (
    async_setup_entry,
    WeWashSensor,
    WeWashLaundryRoomSensor,
    WeWashMachineSensor,
    WeWashInvoiceSensor
)
from custom_components.wewash.const import DOMAIN, ICON_BALANCE

# Fixtures and test data are imported from conftest.py automatically
from conftest import (
    USER_DATA_RESPONSE, LAUNDRY_ROOMS_RESPONSE, UPCOMING_INVOICES_RESPONSE
)


async def test_sensor_setup(hass, mock_config_entry, mock_coordinator):
    """Test sensor setup."""
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
    
    # Check that we have the expected entities based on the real data structure
    # Expected entities:
    # 1. Balance sensor
    # 2. Invoice sensor (comprehensive)
    # 3. Washing cycles sensor  
    # 4. Drying cycles sensor
    # 5. Days until invoice sensor
    # 6. Laundry room overview sensor
    # 7. Machine sensors for WASHING_MACHINE W1 and DRYER T1
    # 8. Available washers for room lGG6MaVX
    # 9. Available dryers for room lGG6MaVX  
    # 10-11. Washing/drying cost sensors for room lGG6MaVX
    # 12-14. Legacy reservation sensors (status, machine, timeout)
    # 15. Legacy upcoming invoice amount sensor
    # 16-19. Reservation-specific sensors for each reservation (2 reservations × 2 sensors each)
    
    # Expect at least 15+ entities based on the test data
    assert len(entities) >= 15


async def test_user_sensor(hass, mock_coordinator):
    """Test the user sensor."""
    from custom_components.wewash.sensor import WeWashSensorEntityDescription
    
    # Create a balance sensor like the actual implementation
    def get_balance(data: dict, _=None) -> float:
        """Get user balance."""
        return data["user"]["credits"]["amount"]
    
    sensor = WeWashSensor(
        mock_coordinator,
        WeWashSensorEntityDescription(
            key="balance",
            name="Balance",
            native_unit_of_measurement="EUR",
            device_class=SensorDeviceClass.MONETARY,
            icon=ICON_BALANCE,
            value_fn=get_balance,
        ),
    )
      # Test basic properties
    assert "Balance" in sensor.name
    assert sensor.unique_id.endswith("_balance")
    assert sensor.native_value == 0.00  # From test data
    assert sensor.native_unit_of_measurement == "EUR"


async def test_laundry_room_sensor(hass, mock_coordinator):
    """Test the laundry room sensor."""
    from custom_components.wewash.sensor import WeWashSensorEntityDescription
    
    sensor = WeWashLaundryRoomSensor(
        mock_coordinator,
        WeWashSensorEntityDescription(
            key="laundry_room",
            name="Laundry Room",
            icon="mdi:washing-machine",
        ),
    )
    
    # Test basic properties  
    assert "Laundry Room" in sensor.name
    assert sensor.unique_id.endswith("_laundry_room")
    assert "washer(s)" in sensor.native_value
    assert "dryer(s)" in sensor.native_value
    
    # Check attributes
    attributes = sensor.extra_state_attributes
    assert attributes["name"] == "Waschraum"
    assert attributes["address"] == "Mühlbergstrasse 18"
    assert attributes["washing_cost"] == 1.50
    assert attributes["drying_cost"] == 1.50
    assert attributes["available_washers"] == 1
    assert attributes["available_dryers"] == 0


async def test_machine_sensors(hass, mock_coordinator):
    """Test machine sensors (washer and dryer)."""
    from custom_components.wewash.sensor import WeWashSensorEntityDescription
    
    # Create washing machine sensor  
    washer_sensor = WeWashMachineSensor(
        mock_coordinator,
        WeWashSensorEntityDescription(
            key="washing_machine_w1",
            name="Washing Machine W1",
            icon="mdi:washing-machine",
        ),
        None,  # no laundry room id
        "WASHING_MACHINE",
        "W1",
    )
    
    # Create dryer sensor
    dryer_sensor = WeWashMachineSensor(
        mock_coordinator,
        WeWashSensorEntityDescription(
            key="dryer_t1",
            name="Dryer T1", 
            icon="mdi:tumble-dryer",
        ),
        None,  # no laundry room id
        "DRYER",
        "T1",    )
      # Test washer - should show timed out status based on test data
    assert "Washing Machine" in washer_sensor.name
    assert washer_sensor.unique_id.endswith("_WASHING_MACHINE_W1")
    # The washer should show "Reservation Expired" since status is RESERVATION_TIMED_OUT
    assert "Reservation Expired" in washer_sensor.native_value
    
    # Test washer attributes
    washer_attrs = washer_sensor.extra_state_attributes
    assert washer_attrs["price"] == 1.50
    assert washer_attrs["currency"] == "EUR"
    assert washer_attrs["raw_status"] == "RESERVATION_TIMED_OUT"
    assert washer_attrs["reservation_id"] == 20158191
    assert washer_attrs["laundry_room"] == "Waschraum"
      # Test dryer - should show active status based on test data
    assert "Dryer" in dryer_sensor.name
    assert dryer_sensor.unique_id.endswith("_DRYER_T1")
    # The dryer should show "Running" since status is ACTIVE
    assert "Running" in dryer_sensor.native_value
    
    # Test dryer attributes  
    dryer_attrs = dryer_sensor.extra_state_attributes
    assert dryer_attrs["price"] == 1.50
    assert dryer_attrs["currency"] == "EUR"
    assert dryer_attrs["raw_status"] == "ACTIVE"
    assert dryer_attrs["reservation_id"] == 20157655
    assert dryer_attrs["laundry_room"] == "Waschraum"


async def test_invoice_sensor(hass, mock_coordinator):
    """Test the invoice sensor."""
    from custom_components.wewash.sensor import WeWashSensorEntityDescription
    
    sensor = WeWashInvoiceSensor(
        mock_coordinator,
        WeWashSensorEntityDescription(
            key="upcoming_invoice",
            name="Upcoming Invoice",
            native_unit_of_measurement="EUR",
            device_class=SensorDeviceClass.MONETARY,
            icon="mdi:invoice",
        ),
    )
    
    # Test basic properties
    assert "Upcoming Invoice" in sensor.name
    assert sensor.unique_id.endswith("_upcoming_invoice")
    assert sensor.native_value == 10.5  # From UPCOMING_INVOICES_RESPONSE
    assert sensor.native_unit_of_measurement == "EUR"
    
    # Check attributes
    attributes = sensor.extra_state_attributes
    assert attributes["currency"] == "EUR"
    assert attributes["washing_cycles"] == 4
    assert attributes["drying_cycles"] == 3
    assert attributes["payment_threshold"] == 20.0
    assert attributes["item_count"] == 3
    assert "latest_item" in attributes
    assert attributes["latest_item"]["type"] == "WASHING_MACHINE"
    assert attributes["latest_item"]["shortName"] == "W1"
    assert attributes["latest_item"]["amount"] == 1.50

"""Tests for the NextInvoiceSensor."""
import pytest
from unittest.mock import patch, MagicMock
import time
from datetime import datetime, timedelta

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from custom_components.wewash.sensor import (
    WeWashNextInvoiceSensor,
    format_timestamp
)
from custom_components.wewash.coordinator import WeWashDataUpdateCoordinator

@pytest.fixture
def mock_invoice_data():
    """Create mock invoice data for testing."""
    # Current time plus 5 days for the due date
    current_time = int(time.time() * 1000)
    due_date = current_time + (5 * 24 * 60 * 60 * 1000)  # 5 days in milliseconds
    
    return {
        "reservations": [
            {
                "invoiceItemId": 12207486,
                "timestamp": current_time - (3 * 24 * 60 * 60 * 1000),  # 3 days ago
                "amount": 1.50,
                "shortName": "W1",
                "type": "WASHING_MACHINE",
                "invoiceItemStatus": "NEW"
            },
            {
                "invoiceItemId": 12208363,
                "timestamp": current_time - (2 * 24 * 60 * 60 * 1000),  # 2 days ago
                "amount": 1.50,
                "shortName": "T1",
                "type": "DRYER",
                "invoiceItemStatus": "NEW"
            },
            {
                "invoiceItemId": 12309512,
                "timestamp": current_time - (24 * 60 * 60 * 1000),  # 1 day ago
                "amount": 1.50,
                "shortName": "W1",
                "type": "WASHING_MACHINE",
                "invoiceItemStatus": "NEW"
            },
            {
                "invoiceItemId": 12312111,
                "timestamp": current_time - (12 * 60 * 60 * 1000),  # 12 hours ago
                "amount": 1.50,
                "shortName": "T1",
                "type": "DRYER",
                "invoiceItemStatus": "NEW"
            },
            {
                "invoiceItemId": 12397281,
                "timestamp": current_time - (6 * 60 * 60 * 1000),  # 6 hours ago
                "amount": 1.50,
                "shortName": "W1",
                "type": "WASHING_MACHINE",
                "invoiceItemStatus": "NEW"
            },
            {
                "invoiceItemId": 12398931,
                "timestamp": current_time - (2 * 60 * 60 * 1000),  # 2 hours ago
                "amount": 1.50,
                "shortName": "T1",
                "type": "DRYER",
                "invoiceItemStatus": "NEW"
            },
            {
                "invoiceItemId": 12452034,
                "timestamp": current_time - (1 * 60 * 60 * 1000),  # 1 hour ago
                "amount": 1.50,
                "shortName": "W1",
                "type": "WASHING_MACHINE",
                "invoiceItemStatus": "NEW"
            }
        ],
        "amount": 10.5,
        "currency": "EUR",
        "cumulativeInvoicingDate": due_date,
        "washingCycles": 4,
        "dryingCycles": 3,
        "selectedPaymentMethodThreshold": 20.0000
    }

@pytest.fixture
def mock_coordinator(hass, mock_config_entry, mock_invoice_data):
    """Create a mock coordinator with invoice data."""
    coordinator = MagicMock(spec=WeWashDataUpdateCoordinator)
    coordinator.data = {"invoices": mock_invoice_data}
    coordinator.entry = mock_config_entry
    return coordinator

def test_invoice_sensor_native_value(mock_coordinator):
    """Test that the invoice sensor returns the correct total amount."""
    sensor = WeWashNextInvoiceSensor(mock_coordinator)
    
    # Check that the native value is the amount from the invoice data
    assert sensor.native_value == 10.5

def test_invoice_sensor_attributes(mock_coordinator):
    """Test all attributes of the invoice sensor."""
    sensor = WeWashNextInvoiceSensor(mock_coordinator)
    attributes = sensor.extra_state_attributes
      # Payment information
    assert attributes["currency"] == "EUR"
    assert attributes["payment_threshold"] == 20.0
      # Usage statistics
    assert attributes["usage_washing_cycles"] == 4
    assert attributes["usage_drying_cycles"] == 3
    
    # Due date information
    assert "due_date" in attributes
    assert "payment_status" in attributes
    # The exact number might vary slightly depending on time calculation
    assert 4 <= attributes["due_in_days"] <= 5  # Should be approximately 5 days

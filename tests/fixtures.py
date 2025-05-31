"""Fixtures for WeWash tests."""
import pytest
from unittest.mock import patch, MagicMock
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from custom_components.wewash.const import DOMAIN
from custom_components.wewash.coordinator import WeWashDataUpdateCoordinator

# Sample test data
AUTH_RESPONSE = {
    "accessToken": "test_access_token",
    "refreshToken": "test_refresh_token"
}

USER_DATA_RESPONSE = {
    "firstName": "Test",
    "lastName": "User",
    "emailAddress": "test@example.com",
    "balance": {
        "amount": 25.75,
        "currency": "EUR"
    }
}

LAUNDRY_ROOMS_RESPONSE = [
    {
        "id": "room123",
        "name": "Laundry Room 1",
        "devices": [
            {
                "id": "device1",
                "type": "WASHER",
                "name": "Washing Machine 1",
                "status": "AVAILABLE",
                "price": {
                    "amount": 2.5,
                    "currency": "EUR"
                }
            },
            {
                "id": "device2",
                "type": "DRYER",
                "name": "Dryer 1",
                "status": "AVAILABLE",
                "price": {
                    "amount": 1.5,
                    "currency": "EUR"
                }
            }
        ]
    }
]

RESERVATIONS_RESPONSE = [
    {
        "id": "res123",
        "status": "ACTIVE",
        "deviceId": "device1",
        "remainingTime": 1800,
        "startedAt": "2025-05-31T12:00:00.000Z"
    }
]

UPCOMING_INVOICES_RESPONSE = {
    "reservations": [
        {
            "invoiceItemId": 12207486,
            "timestamp": 1746771311308,
            "amount": 1.50,
            "shortName": "W1",
            "type": "WASHING_MACHINE",
            "invoiceItemStatus": "NEW"
        },
        {
            "invoiceItemId": 12208363,
            "timestamp": 1746776029556,
            "amount": 1.50,
            "shortName": "T1",
            "type": "DRYER",
            "invoiceItemStatus": "NEW"
        },
        {
            "invoiceItemId": 12309512,
            "timestamp": 1747569873941,
            "amount": 1.50,
            "shortName": "W1",
            "type": "WASHING_MACHINE",
            "invoiceItemStatus": "NEW"
        }
    ],
    "amount": 10.5,
    "currency": "EUR",
    "cumulativeInvoicingDate": 1748736000000,
    "washingCycles": 4,
    "dryingCycles": 3,
    "selectedPaymentMethodThreshold": 20.0000
}

@pytest.fixture
def mock_config_entry():
    """Create a mock config entry."""
    return ConfigEntry(
        domain=DOMAIN,
        data={
            CONF_USERNAME: "test@example.com",
            CONF_PASSWORD: "password123"
        },
        title="test@example.com",
        version=1,
        entry_id="testentry",
        source="user",
        options={},
        minor_version=1,
    )


@pytest.fixture
async def mock_coordinator(hass, mock_config_entry):
    """Create a mock coordinator with mocked data."""
    coordinator = WeWashDataUpdateCoordinator(hass, mock_config_entry)
    coordinator.access_token = "test_access_token"
    coordinator.refresh_token = "test_refresh_token"
    
    # Mock the data
    coordinator.data = {
        "user": USER_DATA_RESPONSE,
        "laundry_rooms": LAUNDRY_ROOMS_RESPONSE,
        "reservations": RESERVATIONS_RESPONSE,
        "upcoming_invoices": UPCOMING_INVOICES_RESPONSE
    }
    
    return coordinator


@pytest.fixture
def mock_auth_response():
    """Mock authentication response."""
    with patch("aiohttp.ClientSession.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = MagicMock(return_value=AUTH_RESPONSE)
        mock_post.return_value.__aenter__.return_value = mock_response
        yield mock_post


@pytest.fixture
def mock_wewash_responses():
    """Mock all WeWash API responses."""
    with patch("aiohttp.ClientSession.get") as mock_get:
        # Configure the mock to return different responses based on URL
        async def side_effect_function(*args, **kwargs):
            mock_response = MagicMock()
            mock_response.status = 200
            url = args[0]
            
            if "users/me" in url and "laundry-rooms" not in url and "reservations" not in url and "upcoming-invoices" not in url:
                mock_response.json = MagicMock(return_value=USER_DATA_RESPONSE)
            elif "laundry-rooms" in url:
                mock_response.json = MagicMock(return_value=LAUNDRY_ROOMS_RESPONSE)
            elif "reservations" in url:
                mock_response.json = MagicMock(return_value=RESERVATIONS_RESPONSE)
            elif "upcoming-invoices" in url:
                mock_response.json = MagicMock(return_value=UPCOMING_INVOICES_RESPONSE)
            
            return mock_response
            
        mock_get.side_effect = side_effect_function
        return mock_get

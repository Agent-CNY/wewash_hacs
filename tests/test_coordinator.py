"""Tests for the WeWash coordinator."""
import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
import aiohttp

from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.wewash.coordinator import WeWashDataUpdateCoordinator
from custom_components.wewash.const import (
    USER_URL, LAUNDRY_ROOMS_URL, RESERVATIONS_URL, UPCOMING_INVOICES_URL,
    AUTH_URL, AUTH_REFRESH_URL
)

# Fixtures and test data are imported from conftest.py automatically
from conftest import (
    USER_DATA_RESPONSE, LAUNDRY_ROOMS_RESPONSE, RESERVATIONS_RESPONSE, UPCOMING_INVOICES_RESPONSE
)


async def test_coordinator_authentication(hass, mock_config_entry, mock_auth_response):
    """Test that the coordinator can authenticate."""
    coordinator = WeWashDataUpdateCoordinator(hass, mock_config_entry)
    
    # Test authentication
    await coordinator._authenticate()
    
    # Verify auth request was made correctly
    mock_auth_response.assert_called_once()
    args, kwargs = mock_auth_response.call_args
    assert kwargs["json"]["username"] == "test@example.com"
    assert kwargs["json"]["password"] == "password123"
    
    # Verify tokens were saved
    assert coordinator.access_token == "test_access_token"
    assert coordinator.refresh_token == "test_refresh_token"


async def test_coordinator_data_update(hass, mock_config_entry, mock_auth_response, mock_wewash_responses):
    """Test that the coordinator can update data from all endpoints."""
    coordinator = WeWashDataUpdateCoordinator(hass, mock_config_entry)
    coordinator.access_token = "test_access_token"  # Set token to skip auth
    
    # Update data
    data = await coordinator._async_update_data()
    
    # Debug: print what we actually got
    print(f"DEBUG: data keys: {data.keys()}")
    if "user" in data:
        print(f"DEBUG: user data keys: {data['user'].keys()}")
        print(f"DEBUG: user data: {data['user']}")
    
    # Verify data structure
    assert "user" in data
    assert "laundry_rooms" in data
    assert "reservations" in data
    assert "invoices" in data
    
    # Check user data structure
    user_data = data["user"]
    assert "email" in user_data  # Check if email exists first
    assert user_data["email"] == "philipp.cserny@gmail.com"
    assert user_data["firstName"] == "Philipp"
    assert user_data["lastName"] == "Cserny"
    assert user_data["credits"]["amount"] == 0.00
    assert user_data["credits"]["currency"] == "EUR"
    assert user_data["selectedLocationId"] == "lGG6MaVX"
    
    # Check laundry rooms data structure
    laundry_rooms = data["laundry_rooms"]
    assert "selectedLaundryRooms" in laundry_rooms
    assert "suggestedLaundryRooms" in laundry_rooms
    assert len(laundry_rooms["selectedLaundryRooms"]) == 1
    
    room = laundry_rooms["selectedLaundryRooms"][0]
    assert room["id"] == "lGG6MaVX"
    assert room["name"] == "Waschraum"
    assert room["washingCost"]["costOnActive"] == 1.50
    assert room["dryingCost"]["costOnActive"] == 1.50
    assert room["serviceAvailability"]["availableWashers"] == 1
    assert room["serviceAvailability"]["availableDryers"] == 0
    
    # Check reservations data structure
    reservations = data["reservations"]
    assert "items" in reservations
    assert "slots" in reservations
    assert "timestamp" in reservations
    assert len(reservations["items"]) == 2
    
    # Check individual reservation data
    active_reservation = next((r for r in reservations["items"] if r["status"] == "ACTIVE"), None)
    assert active_reservation is not None
    assert active_reservation["applianceType"] == "DRYER"
    assert active_reservation["applianceShortName"] == "T1"
    assert active_reservation["price"] == 1.50
    assert active_reservation["currency"] == "EUR"
    assert active_reservation["laundryRoom"]["id"] == "lGG6MaVX"
    
    timed_out_reservation = next((r for r in reservations["items"] if r["status"] == "RESERVATION_TIMED_OUT"), None)
    assert timed_out_reservation is not None
    assert timed_out_reservation["applianceType"] == "WASHING_MACHINE"
    assert timed_out_reservation["applianceShortName"] == "W1"
    
    # Check upcoming invoices data structure
    invoices = data["invoices"]
    assert "reservations" in invoices
    assert "amount" in invoices
    assert "currency" in invoices
    assert "washingCycles" in invoices
    assert "dryingCycles" in invoices
    assert len(invoices["reservations"]) == 3
    assert invoices["amount"] == 10.5
    assert invoices["currency"] == "EUR"
    assert invoices["washingCycles"] == 4
    assert invoices["dryingCycles"] == 3
    
    # Check individual invoice items
    invoice_item = invoices["reservations"][0]
    assert "invoiceItemId" in invoice_item
    assert "timestamp" in invoice_item
    assert "amount" in invoice_item
    assert "shortName" in invoice_item
    assert "type" in invoice_item
    assert "invoiceItemStatus" in invoice_item


async def test_coordinator_authentication_failure(hass, mock_config_entry):
    """Test authentication failure handling."""
    coordinator = WeWashDataUpdateCoordinator(hass, mock_config_entry)
    
    with patch("aiohttp.ClientSession.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status = 401  # Unauthorized
        mock_post.return_value.__aenter__.return_value = mock_response
        
        with pytest.raises(ConfigEntryAuthFailed):
            await coordinator._authenticate()


async def test_coordinator_connection_error(hass, mock_config_entry):
    """Test connection error handling."""
    coordinator = WeWashDataUpdateCoordinator(hass, mock_config_entry)
    coordinator.access_token = "test_access_token"  # Set token to skip auth
    
    with patch("aiohttp.ClientSession.get", side_effect=aiohttp.ClientError):
        with pytest.raises(UpdateFailed):
            await coordinator._async_update_data()


async def test_coordinator_token_refresh(hass, mock_config_entry):
    """Test that the coordinator can refresh tokens."""
    coordinator = WeWashDataUpdateCoordinator(hass, mock_config_entry)
    coordinator.refresh_token = "existing_refresh_token"
    
    with patch("aiohttp.ClientSession.get") as mock_get:
        # Mock successful refresh
        mock_response = MagicMock()
        mock_response.status = 200
        mock_cookies = MagicMock()
        mock_cookies.get.side_effect = lambda key: {
            "ww_access": "new_access_token",
            "ww_refresh": "new_refresh_token"
        }.get(key)
        mock_response.cookies = mock_cookies
        mock_get.return_value.__aenter__.return_value = mock_response
        
        # Test token refresh
        await coordinator._authenticate()
        
        # Verify refresh request was made
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert args[0] == AUTH_REFRESH_URL
        assert "ww_refresh=existing_refresh_token" in kwargs["headers"]["cookie"]
        
        # Verify new tokens were saved
        assert coordinator.access_token == "new_access_token"
        assert coordinator.refresh_token == "new_refresh_token"


async def test_coordinator_token_refresh_failure_fallback(hass, mock_config_entry):
    """Test that the coordinator falls back to full auth when refresh fails."""
    coordinator = WeWashDataUpdateCoordinator(hass, mock_config_entry)
    coordinator.refresh_token = "expired_refresh_token"
    
    with patch("aiohttp.ClientSession.get") as mock_get, \
         patch("aiohttp.ClientSession.post") as mock_post:
        
        # Mock failed refresh
        mock_get_response = MagicMock()
        mock_get_response.status = 401  # Unauthorized
        mock_get.return_value.__aenter__.return_value = mock_get_response
        
        # Mock successful full auth
        mock_post_response = MagicMock()
        mock_post_response.status = 200
        mock_cookies = MagicMock()
        mock_cookies.get.side_effect = lambda key: {
            "ww_access": "full_auth_access_token",
            "ww_refresh": "full_auth_refresh_token"
        }.get(key)
        mock_post_response.cookies = mock_cookies
        mock_post.return_value.__aenter__.return_value = mock_post_response
        
        # Test authentication
        await coordinator._authenticate()
        
        # Verify both refresh and full auth were attempted
        mock_get.assert_called_once()
        mock_post.assert_called_once()
        
        # Verify full auth request was made correctly
        args, kwargs = mock_post.call_args
        assert args[0] == AUTH_URL
        assert kwargs["json"]["username"] == "test@example.com"
        assert kwargs["json"]["password"] == "password123"
        
        # Verify tokens from full auth were saved
        assert coordinator.access_token == "full_auth_access_token"
        assert coordinator.refresh_token == "full_auth_refresh_token"


async def test_coordinator_handles_401_during_data_fetch(hass, mock_config_entry):
    """Test that the coordinator re-authenticates when receiving 401 during data fetch."""
    coordinator = WeWashDataUpdateCoordinator(hass, mock_config_entry)
    coordinator.access_token = "expired_access_token"

    with patch("aiohttp.ClientSession.get") as mock_get, \
         patch("aiohttp.ClientSession.post") as mock_post:

        call_count = 0
        def get_side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            mock_response = AsyncMock()
            
            if call_count == 1:
                # First call returns 401 (expired token)
                mock_response.status = 401
            else:
                # Second call returns 200 with data
                mock_response.status = 200
                url = args[0]
                if "users/me" in url and "laundry-rooms" not in url and "reservations" not in url and "upcoming-invoices" not in url:
                    mock_response.json.return_value = USER_DATA_RESPONSE
                elif "laundry-rooms" in url:
                    mock_response.json.return_value = LAUNDRY_ROOMS_RESPONSE
                elif "reservations" in url:
                    mock_response.json.return_value = RESERVATIONS_RESPONSE
                elif "upcoming-invoices" in url:
                    mock_response.json.return_value = UPCOMING_INVOICES_RESPONSE
            
            # Create proper async context manager
            context_manager = AsyncMock()
            context_manager.__aenter__.return_value = mock_response
            context_manager.__aexit__.return_value = None
            return context_manager

        mock_get.side_effect = get_side_effect
        
        # Mock re-authentication
        mock_post_response = MagicMock()
        mock_post_response.status = 200
        mock_cookies = MagicMock()
        mock_cookies.get.side_effect = lambda key: {
            "ww_access": "new_access_token",
            "ww_refresh": "new_refresh_token"
        }.get(key)
        mock_post_response.cookies = mock_cookies
        mock_post.return_value.__aenter__.return_value = mock_post_response
        
        # Test data update
        data = await coordinator._async_update_data()
        
        # Verify re-authentication occurred
        mock_post.assert_called_once()
        
        # Verify data was fetched successfully after re-auth
        assert "user" in data
        assert "laundry_rooms" in data
        assert "reservations" in data
        assert "invoices" in data


async def test_coordinator_error_handling_network_timeout(hass, mock_config_entry):
    """Test coordinator handling of network timeouts."""
    coordinator = WeWashDataUpdateCoordinator(hass, mock_config_entry)
    coordinator.access_token = "test_access_token"
    
    with patch("aiohttp.ClientSession.get", side_effect=asyncio.TimeoutError):
        with pytest.raises(UpdateFailed, match="Timeout communicating with API"):
            await coordinator._async_update_data()


async def test_coordinator_error_handling_http_error(hass, mock_config_entry):
    """Test coordinator handling of HTTP errors."""
    coordinator = WeWashDataUpdateCoordinator(hass, mock_config_entry)
    coordinator.access_token = "test_access_token"
    
    with patch("aiohttp.ClientSession.get") as mock_get:
        mock_response = AsyncMock()
        mock_response.status = 500  # Server error
        
        # Create proper async context manager
        context_manager = AsyncMock()
        context_manager.__aenter__.return_value = mock_response
        context_manager.__aexit__.return_value = None
        mock_get.return_value = context_manager
        
        with pytest.raises(UpdateFailed):
            await coordinator._async_update_data()


async def test_coordinator_header_format(hass, mock_config_entry):
    """Test that coordinator formats headers correctly."""
    coordinator = WeWashDataUpdateCoordinator(hass, mock_config_entry)
    coordinator.access_token = "test_access_token"
    coordinator.refresh_token = "test_refresh_token"
    
    headers = coordinator._get_headers()
    
    assert headers["accept"] == "application/json"
    assert headers["ww-app-version"] == "2.68.0"
    assert headers["ww-client"] == "USERAPP"
    assert "ww_access=test_access_token" in headers["cookie"]
    assert "ww_refresh=test_refresh_token" in headers["cookie"]


async def test_coordinator_data_structure_validation(hass, mock_config_entry, mock_wewash_responses):
    """Test that coordinator returns data in the expected structure."""
    coordinator = WeWashDataUpdateCoordinator(hass, mock_config_entry)
    coordinator.access_token = "test_access_token"
    
    data = await coordinator._async_update_data()
    
    # Validate top-level structure
    required_keys = ["user", "laundry_rooms", "reservations", "invoices"]
    for key in required_keys:
        assert key in data, f"Missing required key: {key}"
    
    # Validate user data structure
    user = data["user"]
    user_required_keys = ["customerId", "email", "firstName", "lastName", "credits", "selectedLocationId"]
    for key in user_required_keys:
        assert key in user, f"Missing required user key: {key}"
    
    # Validate laundry rooms structure
    laundry_rooms = data["laundry_rooms"]
    assert "selectedLaundryRooms" in laundry_rooms
    assert "suggestedLaundryRooms" in laundry_rooms
    
    if laundry_rooms["selectedLaundryRooms"]:
        room = laundry_rooms["selectedLaundryRooms"][0]
        room_required_keys = ["id", "name", "washingCost", "dryingCost", "serviceAvailability", "address"]
        for key in room_required_keys:
            assert key in room, f"Missing required room key: {key}"
    
    # Validate reservations structure
    reservations = data["reservations"]
    assert "items" in reservations
    assert "timestamp" in reservations
    
    if reservations["items"]:
        reservation = reservations["items"][0]
        reservation_required_keys = ["reservationId", "status", "applianceType", "price", "currency", "laundryRoom"]
        for key in reservation_required_keys:
            assert key in reservation, f"Missing required reservation key: {key}"
    
    # Validate invoices structure
    invoices = data["invoices"]
    invoice_required_keys = ["reservations", "amount", "currency", "washingCycles", "dryingCycles"]
    for key in invoice_required_keys:
        assert key in invoices, f"Missing required invoice key: {key}"
    
    if invoices["reservations"]:
        invoice_item = invoices["reservations"][0]
        item_required_keys = ["invoiceItemId", "timestamp", "amount", "type", "invoiceItemStatus"]
        for key in item_required_keys:
            assert key in invoice_item, f"Missing required invoice item key: {key}"

"""Tests for WeWash integration scenarios and authentication flows."""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import aiohttp
import time

from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import UpdateFailed
from homeassistant.config_entries import ConfigEntryState

from custom_components.wewash.coordinator import WeWashDataUpdateCoordinator
from custom_components.wewash.const import DOMAIN


class TestIntegrationScenarios:
    """Test realistic integration scenarios."""
    
    async def test_full_integration_setup_flow(self, hass, mock_config_entry):
        """Test the complete integration setup flow."""
        # Start with empty hass data
        hass.data[DOMAIN] = {}
        
        # Mock successful authentication and data fetch
        with patch("aiohttp.ClientSession.post") as mock_post, \
             patch("aiohttp.ClientSession.get") as mock_get:
            
            # Mock authentication response
            mock_auth_response = MagicMock()
            mock_auth_response.status = 200
            mock_cookies = MagicMock()
            mock_cookies.get.side_effect = lambda key: {
                "ww_access": "test_access_token",
                "ww_refresh": "test_refresh_token"
            }.get(key)
            mock_auth_response.cookies = mock_cookies
            
            # Create proper async context manager for auth
            auth_context = AsyncMock()
            auth_context.__aenter__.return_value = mock_auth_response
            auth_context.__aexit__.return_value = None
            mock_post.return_value = auth_context
            
            # Mock data fetch responses
            def get_side_effect(*args, **kwargs):
                mock_response = MagicMock()
                mock_response.status = 200  # Ensure this is an integer, not a mock
                url = args[0]
                
                if "users/me" in url and "laundry-rooms" not in url and "reservations" not in url and "upcoming-invoices" not in url:
                    mock_response.json = AsyncMock(return_value={"email": "test@example.com"})
                elif "laundry-rooms" in url:
                    mock_response.json = AsyncMock(return_value={"selectedLaundryRooms": []})
                elif "reservations" in url:
                    mock_response.json = AsyncMock(return_value={"items": [], "timestamp": int(time.time() * 1000)})
                elif "upcoming-invoices" in url:
                    mock_response.json = AsyncMock(return_value={"amount": 0, "currency": "EUR"})
                
                # Create proper async context manager for each response
                context = AsyncMock()
                context.__aenter__.return_value = mock_response
                context.__aexit__.return_value = None
                return context
            
            mock_get.side_effect = get_side_effect
            
            # Create and initialize coordinator
            coordinator = WeWashDataUpdateCoordinator(hass, mock_config_entry)
            
            # Test initial data update
            data = await coordinator._async_update_data()
            
            # Verify data structure
            assert "user" in data
            assert "laundry_rooms" in data
            assert "reservations" in data
            assert "invoices" in data
            
            # Verify authentication was called
            mock_post.assert_called_once()            
            # Verify all endpoints were called
            assert mock_get.call_count == 4  # 4 data endpoints

    async def test_authentication_token_expiry_handling(self, hass, mock_config_entry):
        """Test handling of token expiry during operation."""
        coordinator = WeWashDataUpdateCoordinator(hass, mock_config_entry)
        coordinator.access_token = "expired_token"
        coordinator.refresh_token = "valid_refresh_token"
        
        with patch("aiohttp.ClientSession.get") as mock_get, \
             patch("aiohttp.ClientSession.post") as mock_post:
            
            call_count = 0
            def get_side_effect(*args, **kwargs):
                nonlocal call_count
                call_count += 1
                mock_response = MagicMock()
                
                # Always set a proper AsyncMock json method for all responses
                mock_response.json = AsyncMock()
                
                url = args[0]
                
                # Handle refresh token request (should fail to force POST auth)
                if "auth/refresh" in url:
                    mock_response.status = 401  # Force refresh to fail
                    mock_response.json.return_value = {}
                elif call_count == 1:
                    # First call to user endpoint - token expired
                    mock_response.status = 401
                    mock_response.json.return_value = {}
                elif call_count == 2:
                    # Second call after re-auth - success
                    mock_response.status = 200
                    mock_response.json.return_value = {"email": "test@example.com"}
                else:
                    # Subsequent calls - success
                    mock_response.status = 200
                    if "laundry-rooms" in url:
                        mock_response.json.return_value = {"selectedLaundryRooms": []}
                    elif "reservations" in url:
                        mock_response.json.return_value = {"items": [], "timestamp": int(time.time() * 1000)}
                    elif "upcoming-invoices" in url:
                        mock_response.json.return_value = {"amount": 0, "currency": "EUR"}
                
                # Create proper async context manager
                context_manager = AsyncMock()
                context_manager.__aenter__.return_value = mock_response
                context_manager.__aexit__.return_value = None
                return context_manager
            
            mock_get.side_effect = get_side_effect
            
            # Mock re-authentication
            mock_auth_response = MagicMock()
            mock_auth_response.status = 200
            mock_cookies = MagicMock()
            mock_cookies.get.side_effect = lambda key: {
                "ww_access": "new_access_token",
                "ww_refresh": "new_refresh_token"
            }.get(key)
            mock_auth_response.cookies = mock_cookies
            
            # Create proper async context manager for auth
            auth_context_manager = AsyncMock()
            auth_context_manager.__aenter__.return_value = mock_auth_response
            auth_context_manager.__aexit__.return_value = None
            mock_post.return_value = auth_context_manager
            
            # Test data update with token expiry
            data = await coordinator._async_update_data()
            
            # Verify re-authentication occurred
            mock_post.assert_called_once()            
            # Verify new tokens were set
            assert coordinator.access_token == "new_access_token"
            assert coordinator.refresh_token == "new_refresh_token"            # Verify data was fetched successfully
            assert "user" in data

    async def test_network_resilience(self, hass, mock_config_entry):
        """Test network error handling and resilience."""
        coordinator = WeWashDataUpdateCoordinator(hass, mock_config_entry)
        coordinator.access_token = "test_token"        # Test various network errors
        network_errors = [
            aiohttp.ConnectionTimeoutError(),
            aiohttp.ClientConnectionError(),
            aiohttp.ClientError(),
        ]
        
        for error in network_errors:
            with patch("aiohttp.ClientSession.get") as mock_get:
                # Create a function that raises the error
                def raise_error(*args, **kwargs):
                    raise error
                
                # Set the side_effect to raise the error when get is called
                mock_get.side_effect = raise_error
                
                with pytest.raises(UpdateFailed):
                    await coordinator._async_update_data()

    async def test_rate_limiting_handling(self, hass, mock_config_entry):
        """Test handling of rate limiting responses."""
        coordinator = WeWashDataUpdateCoordinator(hass, mock_config_entry)
        coordinator.access_token = "test_token"
        
        with patch("aiohttp.ClientSession.get") as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 429  # Too Many Requests
            
            # Create proper async context manager
            context_manager = AsyncMock()
            context_manager.__aenter__.return_value = mock_response
            context_manager.__aexit__.return_value = None
            mock_get.return_value = context_manager
            
            with pytest.raises(UpdateFailed):
                await coordinator._async_update_data()

    async def test_server_error_handling(self, hass, mock_config_entry):
        """Test handling of server errors."""
        coordinator = WeWashDataUpdateCoordinator(hass, mock_config_entry)
        coordinator.access_token = "test_token"
        
        server_errors = [500, 502, 503, 504]
        
        for error_code in server_errors:
            with patch("aiohttp.ClientSession.get") as mock_get:
                mock_response = MagicMock()
                mock_response.status = error_code
                
                # Create proper async context manager
                context_manager = AsyncMock()
                context_manager.__aenter__.return_value = mock_response
                context_manager.__aexit__.return_value = None
                mock_get.return_value = context_manager
                
                with pytest.raises(UpdateFailed):
                    await coordinator._async_update_data()

    async def test_partial_data_handling(self, hass, mock_config_entry):
        """Test handling when some endpoints fail but others succeed."""
        coordinator = WeWashDataUpdateCoordinator(hass, mock_config_entry)
        coordinator.access_token = "test_token"
        
        with patch("aiohttp.ClientSession.get") as mock_get:
            def get_side_effect(*args, **kwargs):
                mock_response = MagicMock()
                url = args[0]
                
                if "users/me" in url and "laundry-rooms" not in url:
                    # User endpoint succeeds
                    mock_response.status = 200
                    mock_response.json = AsyncMock(return_value={"email": "test@example.com"})
                elif "laundry-rooms" in url:
                    # Laundry rooms endpoint fails
                    mock_response.status = 500
                else:
                    # Other endpoints succeed
                    mock_response.status = 200
                    if "reservations" in url:
                        mock_response.json = AsyncMock(return_value={"items": []})
                    elif "upcoming-invoices" in url:
                        mock_response.json = AsyncMock(return_value={"amount": 0})
                
                # Create proper async context manager for each response
                context = AsyncMock()
                context.__aenter__.return_value = mock_response
                context.__aexit__.return_value = None
                return context
            
            mock_get.side_effect = get_side_effect
            
            # Should raise UpdateFailed due to one endpoint failing
            with pytest.raises(UpdateFailed):
                await coordinator._async_update_data()

    async def test_malformed_json_response_handling(self, hass, mock_config_entry):
        """Test handling of malformed JSON responses."""
        coordinator = WeWashDataUpdateCoordinator(hass, mock_config_entry)
        coordinator.access_token = "test_token"
        
        with patch("aiohttp.ClientSession.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(side_effect=ValueError("Invalid JSON"))
            mock_get.return_value.__aenter__.return_value = mock_response
            
            with pytest.raises(UpdateFailed):
                await coordinator._async_update_data()

    async def test_authentication_failure_scenarios(self, hass, mock_config_entry):
        """Test various authentication failure scenarios."""
        coordinator = WeWashDataUpdateCoordinator(hass, mock_config_entry)
        
        # Test invalid credentials
        with patch("aiohttp.ClientSession.post") as mock_post:
            mock_response = MagicMock()
            mock_response.status = 401
            mock_post.return_value.__aenter__.return_value = mock_response
            
            with pytest.raises(ConfigEntryAuthFailed):
                await coordinator._authenticate()
        
        # Test network error during authentication
        with patch("aiohttp.ClientSession.post", side_effect=aiohttp.ClientError):
            with pytest.raises(ConfigEntryAuthFailed):
                await coordinator._authenticate()
        
        # Test malformed authentication response
        with patch("aiohttp.ClientSession.post") as mock_post:
            mock_response = MagicMock()
            mock_response.status = 200
            mock_response.cookies = {}  # No tokens in cookies
            mock_post.return_value.__aenter__.return_value = mock_response
            
            await coordinator._authenticate()
            # Should handle missing tokens gracefully
            assert coordinator.access_token is None

    async def test_data_consistency_validation(self, hass, mock_config_entry, mock_wewash_responses):
        """Test that data remains consistent across updates."""
        coordinator = WeWashDataUpdateCoordinator(hass, mock_config_entry)
        coordinator.access_token = "test_token"
        
        # Perform multiple data updates
        data1 = await coordinator._async_update_data()
        data2 = await coordinator._async_update_data()
        
        # Data structure should remain consistent
        assert data1.keys() == data2.keys()
        
        # User data should be consistent
        assert data1["user"]["email"] == data2["user"]["email"]
        
        # Timestamps might differ, but structure should be the same
        assert type(data1["reservations"]) == type(data2["reservations"])

    async def test_concurrent_update_handling(self, hass, mock_config_entry):
        """Test handling of concurrent update requests."""
        coordinator = WeWashDataUpdateCoordinator(hass, mock_config_entry)
        coordinator.access_token = "test_token"
        
        with patch("aiohttp.ClientSession.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={"data": "test"})
            mock_get.return_value.__aenter__.return_value = mock_response
            
            # Start multiple concurrent updates
            import asyncio
            tasks = [
                coordinator._async_update_data(),
                coordinator._async_update_data(),
                coordinator._async_update_data()
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # All should succeed or fail consistently
            success_count = sum(1 for r in results if not isinstance(r, Exception))
            assert success_count > 0  # At least one should succeed

    def test_config_entry_validation(self, mock_config_entry):
        """Test that config entry data is properly validated."""
        # Test required fields
        assert "username" in mock_config_entry.data
        assert "password" in mock_config_entry.data
        
        # Test data types
        assert isinstance(mock_config_entry.data["username"], str)
        assert isinstance(mock_config_entry.data["password"], str)
        
        # Test non-empty values
        assert len(mock_config_entry.data["username"]) > 0
        assert len(mock_config_entry.data["password"]) > 0

    async def test_coordinator_lifecycle(self, hass, mock_config_entry):
        """Test coordinator initialization and cleanup."""
        coordinator = WeWashDataUpdateCoordinator(hass, mock_config_entry)
        
        # Test initial state
        assert coordinator.access_token is None
        assert coordinator.refresh_token is None
        assert coordinator.entry == mock_config_entry
        
        # Test that coordinator is properly initialized
        assert coordinator.name == DOMAIN
        assert coordinator.update_interval is not None

    async def test_header_construction(self, hass, mock_config_entry):
        """Test that request headers are properly constructed."""
        coordinator = WeWashDataUpdateCoordinator(hass, mock_config_entry)
        coordinator.access_token = "test_access"
        coordinator.refresh_token = "test_refresh"
        
        headers = coordinator._get_headers()
        
        # Test required headers
        assert "accept" in headers
        assert "ww-app-version" in headers
        assert "ww-client" in headers
        assert "cookie" in headers
        
        # Test header values
        assert headers["accept"] == "application/json"
        assert headers["ww-app-version"] == "2.68.0"
        assert headers["ww-client"] == "USERAPP"
        assert "ww_access=test_access" in headers["cookie"]
        assert "ww_refresh=test_refresh" in headers["cookie"]

    async def test_error_propagation(self, hass, mock_config_entry):
        """Test that errors are properly propagated up the call stack."""
        coordinator = WeWashDataUpdateCoordinator(hass, mock_config_entry)
          # Test that authentication errors become ConfigEntryAuthFailed
        with patch("aiohttp.ClientSession.post", side_effect=aiohttp.ClientError):
            with pytest.raises(ConfigEntryAuthFailed):
                await coordinator._authenticate()
        
        # Test that data fetch errors become UpdateFailed
        coordinator.access_token = "test_token"
        with patch("aiohttp.ClientSession.get", side_effect=aiohttp.ClientError):
            with pytest.raises(UpdateFailed):
                await coordinator._async_update_data()

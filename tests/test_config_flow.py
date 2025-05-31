"""Tests for the WeWash config flow."""
import pytest
from unittest.mock import patch, MagicMock
import aiohttp

from homeassistant import config_entries
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD
from homeassistant.data_entry_flow import FlowResultType

from custom_components.wewash.config_flow import ConfigFlow
from custom_components.wewash.const import DOMAIN, AUTH_URL

# Fixtures and test data are imported from conftest.py automatically
from conftest import AUTH_RESPONSE


async def test_config_flow_successful(hass):
    """Test a successful config flow."""
    with patch("aiohttp.ClientSession.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = MagicMock(return_value=AUTH_RESPONSE)
        mock_post.return_value.__aenter__.return_value = mock_response
        
        # Initialize the config flow
        flow = ConfigFlow()
        flow.hass = hass
        
        # Test the first step with valid credentials
        result = await flow.async_step_user({
            CONF_USERNAME: "test@example.com",
            CONF_PASSWORD: "password123"
        })
        
        # Verify that the flow completed successfully
        assert result["type"] == FlowResultType.CREATE_ENTRY
        assert result["title"] == "test@example.com"
        assert result["data"][CONF_USERNAME] == "test@example.com"
        assert result["data"][CONF_PASSWORD] == "password123"


async def test_config_flow_invalid_auth(hass):
    """Test a config flow with invalid authentication."""
    with patch("aiohttp.ClientSession.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status = 401
        mock_post.return_value.__aenter__.return_value = mock_response
        
        # Initialize the config flow
        flow = ConfigFlow()
        flow.hass = hass
        
        # Test the first step with invalid credentials
        result = await flow.async_step_user({
            CONF_USERNAME: "test@example.com",
            CONF_PASSWORD: "wrong_password"
        })
        
        # Verify that we're still in the user step with an error
        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "user"
        assert result["errors"]["base"] == "invalid_auth"


async def test_config_flow_cannot_connect(hass):
    """Test a config flow with connection error."""
    with patch("aiohttp.ClientSession.post", side_effect=aiohttp.ClientError()):
        # Initialize the config flow
        flow = ConfigFlow()
        flow.hass = hass
        
        # Test the first step with a connection error
        result = await flow.async_step_user({
            CONF_USERNAME: "test@example.com",
            CONF_PASSWORD: "password123"
        })
        
        # Verify that we're still in the user step with an error
        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "user"
        assert result["errors"]["base"] == "cannot_connect"


async def test_config_flow_unknown_error(hass):
    """Test a config flow with an unknown error."""
    with patch("aiohttp.ClientSession.post", side_effect=Exception()):
        # Initialize the config flow
        flow = ConfigFlow()
        flow.hass = hass
        
        # Test the first step with an unknown error
        result = await flow.async_step_user({
            CONF_USERNAME: "test@example.com",
            CONF_PASSWORD: "password123"
        })
        
        # Verify that we're still in the user step with an error
        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "user"
        assert result["errors"]["base"] == "unknown"


async def test_config_flow_show_form(hass):
    """Test that the form is served with no user input."""
    flow = ConfigFlow()
    flow.hass = hass
    
    result = await flow.async_step_user(user_input=None)
    
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"

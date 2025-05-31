"""Config flow for We-Wash integration."""
import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN, AUTH_URL

_LOGGER = logging.getLogger(__name__)

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for We-Wash."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            try:
                await self._test_credentials(
                    user_input[CONF_USERNAME], user_input[CONF_PASSWORD]
                )
            except aiohttp.ClientError:
                errors["base"] = "cannot_connect"
            except ValueError:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(
                    title=user_input[CONF_USERNAME], data=user_input
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_USERNAME): cv.string,
                    vol.Required(CONF_PASSWORD): cv.string,
                }
            ),
            errors=errors,
        )

    async def _test_credentials(self, username: str, password: str) -> None:
        """Validate credentials."""
        try:
            async with aiohttp.ClientSession() as session:
                data = {"username": username, "password": password}
                headers = {
                    "accept": "application/json",
                    "content-type": "application/json",
                    "ww-app-version": "2.68.0",
                    "ww-client": "USERAPP",
                }
                async with session.post(AUTH_URL, json=data, headers=headers) as resp:
                    if resp.status != 200:
                        raise ValueError("Invalid authentication")

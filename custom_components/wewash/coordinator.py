"""Data update coordinator for We-Wash."""
from datetime import timedelta
import logging
import asyncio
import aiohttp
import async_timeout

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    UPDATE_INTERVAL,
    AUTH_URL,
    USER_URL,
    LAUNDRY_ROOMS_URL,
    RESERVATIONS_URL,
    UPCOMING_INVOICES_URL,
    AUTH_REFRESH_URL,
)

_LOGGER = logging.getLogger(__name__)

class WeWashDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching We-Wash data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=UPDATE_INTERVAL),
        )
        self.access_token = None
        self.refresh_token = None
        self.entry = entry

    async def _async_update_data(self):
        """Fetch data from We-Wash API."""
        _LOGGER.debug("Starting data update from We-Wash API")
        try:
            async with async_timeout.timeout(30):
                if not self.access_token:
                    _LOGGER.debug("No access token found, authenticating...")
                    await self._authenticate()

                data = {}
                async with aiohttp.ClientSession() as session:
                    # Fetch user data
                    headers = self._get_headers()
                    _LOGGER.debug("Fetching user data...")
                    async with session.get(USER_URL, headers=headers) as resp:
                        if resp.status == 401:
                            _LOGGER.debug("Access token expired, re-authenticating...")
                            await self._authenticate()
                            headers = self._get_headers()
                            async with session.get(USER_URL, headers=headers) as resp:
                                if resp.status >= 400:
                                    raise UpdateFailed(f"API error {resp.status} from user endpoint")
                                data["user"] = await resp.json()
                        else:
                            if resp.status >= 400:
                                raise UpdateFailed(f"API error {resp.status} from user endpoint")
                            data["user"] = await resp.json()
                    
                    # Fetch laundry rooms
                    _LOGGER.debug("Fetching laundry rooms...")
                    async with session.get(LAUNDRY_ROOMS_URL, headers=headers) as resp:
                        if resp.status >= 400:
                            raise UpdateFailed(f"API error {resp.status} from laundry rooms endpoint")
                        data["laundry_rooms"] = await resp.json()
                        
                    # Fetch reservations
                    _LOGGER.debug("Fetching reservations...")
                    async with session.get(RESERVATIONS_URL, headers=headers) as resp:
                        if resp.status >= 400:
                            raise UpdateFailed(f"API error {resp.status} from reservations endpoint")
                        data["reservations"] = await resp.json()
                        
                    # Fetch upcoming invoices
                    _LOGGER.debug("Fetching upcoming invoices...")
                    async with session.get(UPCOMING_INVOICES_URL, headers=headers) as resp:
                        if resp.status >= 400:
                            raise UpdateFailed(f"API error {resp.status} from invoices endpoint")
                        data["invoices"] = await resp.json()

                _LOGGER.debug("Successfully fetched all data from We-Wash API")
                
                # Log some key metrics for debugging
                if "reservations" in data and "items" in data["reservations"]:
                    _LOGGER.debug(f"Found {len(data['reservations']['items'])} reservations")
                if "laundry_rooms" in data and "selectedLaundryRooms" in data["laundry_rooms"]:
                    rooms = data["laundry_rooms"]["selectedLaundryRooms"]
                    for room in rooms:
                        washers = room["serviceAvailability"]["availableWashers"]
                        dryers = room["serviceAvailability"]["availableDryers"]
                        _LOGGER.debug(f"Room '{room['name']}': {washers} washers, {dryers} dryers available")

                return data

        except asyncio.TimeoutError as error:
            _LOGGER.error(f"Timeout communicating with API: {error}")
            raise UpdateFailed(f"Timeout communicating with API: {error}") from error
        except aiohttp.ClientError as error:
            _LOGGER.error(f"Error communicating with API: {error}")
            raise UpdateFailed(f"Error communicating with API: {error}") from error
        except (ValueError, KeyError) as error:
            _LOGGER.error(f"Error parsing API response: {error}")
            raise UpdateFailed(f"Error parsing API response: {error}") from error
            
    async def _authenticate(self):
        """Authenticate with the We-Wash API."""
        try:
            async with aiohttp.ClientSession() as session:
                # If we have a refresh token, try to use it first
                if self.refresh_token:
                    try:
                        headers = {
                            "accept": "application/json",
                            "ww-app-version": "2.68.0",
                            "ww-client": "USERAPP",
                            "cookie": f"ww_refresh={self.refresh_token}",
                        }
                        async with session.get(AUTH_REFRESH_URL, headers=headers) as resp:
                            if resp.status == 200:
                                # Extract tokens from cookies
                                cookies = resp.cookies
                                self.access_token = cookies.get("ww_access")
                                self.refresh_token = cookies.get("ww_refresh")
                                return
                    except aiohttp.ClientError:
                        # If refresh fails, fall back to full authentication
                        pass
                
                # Full authentication with username/password
                data = {
                    "username": self.entry.data["username"],
                    "password": self.entry.data["password"],
                }
                headers = {
                    "accept": "application/json",
                    "content-type": "application/json",
                    "ww-app-version": "2.68.0",
                    "ww-client": "USERAPP",
                }
                async with session.post(AUTH_URL, json=data, headers=headers) as resp:
                    if resp.status != 200:
                        raise ConfigEntryAuthFailed("Invalid authentication")
                    
                    # Extract tokens from cookies
                    cookies = resp.cookies
                    self.access_token = cookies.get("ww_access")
                    self.refresh_token = cookies.get("ww_refresh")

        except aiohttp.ClientError as error:
            raise ConfigEntryAuthFailed from error

    def _get_headers(self):
        """Get headers for API requests."""
        return {
            "accept": "application/json",
            "ww-app-version": "2.68.0",
            "ww-client": "USERAPP",
            "cookie": f"ww_access={self.access_token}; ww_refresh={self.refresh_token}",
        }

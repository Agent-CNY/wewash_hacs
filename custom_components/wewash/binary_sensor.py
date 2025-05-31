"""Binary sensor platform for We-Wash."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import WeWashDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up We-Wash binary sensors."""
    # Based on entities.md, no binary sensors are defined
    # Only the 4 sensor entities should be created
    async_add_entities([])

"""Binary sensor platform for We-Wash."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, ICON_RESERVATION, MANUFACTURER, MODEL
from .coordinator import WeWashDataUpdateCoordinator

@dataclass
class WeWashBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Class describing We-Wash binary sensor entities."""
    is_on_fn: callable = None

class WeWashBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Representation of a We-Wash binary sensor."""

    entity_description: WeWashBinarySensorEntityDescription

    def __init__(
        self,
        coordinator: WeWashDataUpdateCoordinator,
        description: WeWashBinarySensorEntityDescription,
        reservation_id: str | None = None,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._reservation_id = reservation_id
        self._attr_unique_id = f"{coordinator.entry.entry_id}_{description.key}"
        if reservation_id:
            self._attr_unique_id += f"_{reservation_id}"

        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.entry.entry_id)},
            "name": "We-Wash Laundry System",
            "manufacturer": MANUFACTURER,
            "model": MODEL,
        }

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        if self.entity_description.is_on_fn is not None:
            return self.entity_description.is_on_fn(self.coordinator.data, self._reservation_id)
        return None

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up We-Wash binary sensors."""
    coordinator: WeWashDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    def is_reservation_ready(data: dict[str, Any], reservation_id: str) -> bool:
        """Check if the reservation is ready."""
        for reservation in data["reservations"]["items"]:
            if str(reservation["reservationId"]) == reservation_id:
                return reservation["status"] == "READY"
        return False

    entities = []

    # Add binary sensors for each active reservation
    for reservation in coordinator.data["reservations"]["items"]:
        reservation_id = str(reservation["reservationId"])
        appliance_type = reservation["applianceType"]
        appliance_name = reservation["applianceShortName"]
        
        entities.append(
            WeWashBinarySensor(
                coordinator,
                WeWashBinarySensorEntityDescription(
                    key="reservation_ready",
                    name=f"{appliance_type} {appliance_name} Ready",
                    device_class=BinarySensorDeviceClass.RUNNING,
                    icon=ICON_RESERVATION,
                    is_on_fn=is_reservation_ready,
                ),
                reservation_id,
            )
        )

    async_add_entities(entities)

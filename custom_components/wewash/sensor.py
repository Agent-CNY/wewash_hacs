"""Sensor platform for We-Wash."""
from __future__ import annotations

from typing import Any
from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from .const import (
    DOMAIN,
    ICON_BALANCE,
    ICON_WASHER,
    ICON_DRYER,
    MANUFACTURER,
    MODEL,
)
from .coordinator import WeWashDataUpdateCoordinator

@dataclass
class WeWashSensorEntityDescription(SensorEntityDescription):
    """Class describing We-Wash sensor entities."""
    value_fn: callable = None

class WeWashSensor(CoordinatorEntity, SensorEntity):
    """Representation of a We-Wash sensor."""

    entity_description: WeWashSensorEntityDescription

    def __init__(
        self,
        coordinator: WeWashDataUpdateCoordinator,
        description: WeWashSensorEntityDescription,
        laundry_room_id: str | None = None,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._laundry_room_id = laundry_room_id
        self._attr_unique_id = f"{coordinator.entry.entry_id}_{description.key}"
        if laundry_room_id:
            self._attr_unique_id += f"_{laundry_room_id}"

        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.entry.entry_id)},
            "name": "We-Wash Laundry System",
            "manufacturer": MANUFACTURER,
            "model": MODEL,
        }

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        if self.entity_description.value_fn is not None:
            return self.entity_description.value_fn(self.coordinator.data, self._laundry_room_id)
        return None

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up We-Wash sensors."""
    coordinator: WeWashDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    def get_balance(data: dict[str, Any], _) -> float:
        """Get user balance."""
        return data["user"]["credits"]["amount"]

    def get_available_washers(data: dict[str, Any], room_id: str) -> int:
        """Get number of available washers."""
        for room in data["laundry_rooms"]["selectedLaundryRooms"]:
            if room["id"] == room_id:
                return room["serviceAvailability"]["availableWashers"]
        return 0

    def get_available_dryers(data: dict[str, Any], room_id: str) -> int:
        """Get number of available dryers."""
        for room in data["laundry_rooms"]["selectedLaundryRooms"]:
            if room["id"] == room_id:
                return room["serviceAvailability"]["availableDryers"]
        return 0

    entities = [
        WeWashSensor(
            coordinator,
            WeWashSensorEntityDescription(
                key="balance",
                name="Balance",
                native_unit_of_measurement="EUR",
                device_class=SensorDeviceClass.MONETARY,
                entity_category=EntityCategory.DIAGNOSTIC,
                icon=ICON_BALANCE,
                value_fn=get_balance,
            ),
        )
    ]

    # Add sensors for each laundry room
    for room in coordinator.data["laundry_rooms"]["selectedLaundryRooms"]:
        room_id = room["id"]
        room_name = room["name"]
        
        entities.extend([
            WeWashSensor(
                coordinator,
                WeWashSensorEntityDescription(
                    key="available_washers",
                    name=f"{room_name} Available Washers",
                    native_unit_of_measurement="machines",
                    icon=ICON_WASHER,
                    value_fn=get_available_washers,
                ),
                room_id,
            ),
            WeWashSensor(
                coordinator,
                WeWashSensorEntityDescription(
                    key="available_dryers",
                    name=f"{room_name} Available Dryers",
                    native_unit_of_measurement="machines",
                    icon=ICON_DRYER,
                    value_fn=get_available_dryers,
                ),
                room_id,
            ),
        ])

    async_add_entities(entities)

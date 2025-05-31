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
    ICON_RESERVATION,
    ICON_INVOICE,
    ICON_COST,
    ICON_TIMER,
    ICON_MACHINE,
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

    def get_washing_cost(data: dict[str, Any], room_id: str) -> float:
        """Get washing cost for a laundry room."""
        for room in data["laundry_rooms"]["selectedLaundryRooms"]:
            if room["id"] == room_id:
                return room["washingCost"]["costOnActive"]
        return 0.0

    def get_drying_cost(data: dict[str, Any], room_id: str) -> float:
        """Get drying cost for a laundry room."""
        for room in data["laundry_rooms"]["selectedLaundryRooms"]:
            if room["id"] == room_id:
                return room["dryingCost"]["costOnActive"]
        return 0.0

    def get_reservation_status(data: dict[str, Any], reservation_id: str | None = None) -> str:
        """Get current reservation status."""
        if "items" in data.get("reservations", {}):
            # If a specific reservation ID is provided, get status for that reservation
            if reservation_id:
                for item in data["reservations"]["items"]:
                    if str(item["reservationId"]) == reservation_id:
                        return item["status"]
                return "NOT_FOUND"
            # Otherwise, return the status of the first reservation (legacy behavior)
            elif data["reservations"]["items"]:
                return data["reservations"]["items"][0]["status"]
        return "NO_RESERVATION"
        
    def get_reservation_machine(data: dict[str, Any], reservation_id: str | None = None) -> str:
        """Get current reservation machine info."""
        if "items" in data.get("reservations", {}):
            # If a specific reservation ID is provided, get machine info for that reservation
            if reservation_id:
                for item in data["reservations"]["items"]:
                    if str(item["reservationId"]) == reservation_id:
                        return f"{item['applianceType']} - {item['applianceShortName']}"
                return None
            # Otherwise, return info of the first reservation (legacy behavior)
            elif data["reservations"]["items"]:
                item = data["reservations"]["items"][0]
                return f"{item['applianceType']} - {item['applianceShortName']}"
        return None

    def get_reservation_timeout(data: dict[str, Any], reservation_id: str | None = None) -> str:
        """Get current reservation timeout."""
        if "items" in data.get("reservations", {}):
            # If a specific reservation ID is provided, get timeout for that reservation
            if reservation_id:
                for item in data["reservations"]["items"]:
                    if str(item["reservationId"]) == reservation_id and "timeoutTimestamp" in item:
                        return item["timeoutTimestamp"]
                return None
            # Otherwise, return timeout of the first reservation with a timeout (legacy behavior)
            else:
                for item in data["reservations"]["items"]:
                    if "timeoutTimestamp" in item:
                        return item["timeoutTimestamp"]
        return None

    def get_upcoming_invoice_amount(data: dict[str, Any], _) -> float:
        """Get upcoming invoice amount."""
        # The API directly provides the total amount in the response
        if "amount" in data.get("invoices", {}):
            return data["invoices"]["amount"]
        # Fallback to calculating from individual reservation items if needed
        elif "reservations" in data.get("invoices", {}):
            total = 0.0
            for item in data["invoices"]["reservations"]:
                total += item["amount"]
            return total
        return 0.0

    entities = [
        WeWashSensor(
            coordinator,
            WeWashSensorEntityDescription(
                key="balance",
                name="Balance",
                native_unit_of_measurement="EUR",
                device_class=SensorDeviceClass.MONETARY,
                icon=ICON_BALANCE,
                value_fn=get_balance,
            ),
        )
    ]

    # Add laundry room specific sensors
    for room in coordinator.data["laundry_rooms"]["selectedLaundryRooms"]:
        room_id = room["id"]
        room_name = room["name"]
        
        entities.extend([
            WeWashSensor(
                coordinator,
                WeWashSensorEntityDescription(
                    key=f"available_washers_{room_id}",
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
                    key=f"available_dryers_{room_id}",
                    name=f"{room_name} Available Dryers",
                    native_unit_of_measurement="machines",
                    icon=ICON_DRYER,
                    value_fn=get_available_dryers,
                ),
                room_id,
            ),
            WeWashSensor(
                coordinator,
                WeWashSensorEntityDescription(
                    key=f"washing_cost_{room_id}",
                    name=f"{room_name} Washing Cost",
                    native_unit_of_measurement="EUR",
                    device_class=SensorDeviceClass.MONETARY,
                    icon=ICON_COST,
                    value_fn=get_washing_cost,
                ),
                room_id,
            ),
            WeWashSensor(
                coordinator,
                WeWashSensorEntityDescription(
                    key=f"drying_cost_{room_id}",
                    name=f"{room_name} Drying Cost",
                    native_unit_of_measurement="EUR",
                    device_class=SensorDeviceClass.MONETARY,
                    icon=ICON_COST,
                    value_fn=get_drying_cost,
                ),
                room_id,
            ),
        ])    # Add reservation sensors - both legacy generic sensors and individual machine-specific sensors
    
    # Add legacy sensors for backward compatibility
    entities.extend([
        WeWashSensor(
            coordinator,
            WeWashSensorEntityDescription(
                key="reservation_status",
                name="Reservation Status",
                icon=ICON_RESERVATION,
                value_fn=get_reservation_status,
            ),
        ),
        WeWashSensor(
            coordinator,
            WeWashSensorEntityDescription(
                key="reservation_machine",
                name="Reserved Machine",
                icon=ICON_MACHINE,
                value_fn=get_reservation_machine,
            ),
        ),
        WeWashSensor(
            coordinator,
            WeWashSensorEntityDescription(
                key="reservation_timeout",
                name="Reservation Timeout",
                device_class=SensorDeviceClass.TIMESTAMP,
                icon=ICON_TIMER,
                value_fn=get_reservation_timeout,
            ),
        ),
    ])
    
    # Add machine-specific sensors for each active reservation
    if "items" in coordinator.data.get("reservations", {}):
        for reservation in coordinator.data["reservations"]["items"]:
            reservation_id = str(reservation["reservationId"])
            appliance_type = reservation["applianceType"]
            appliance_name = reservation["applianceShortName"]
            
            entities.extend([
                WeWashSensor(
                    coordinator,
                    WeWashSensorEntityDescription(
                        key=f"reservation_status_{reservation_id}",
                        name=f"{appliance_type} {appliance_name} Status",
                        icon=ICON_RESERVATION,
                        value_fn=get_reservation_status,
                    ),
                    reservation_id,
                ),
                WeWashSensor(
                    coordinator,
                    WeWashSensorEntityDescription(
                        key=f"reservation_timeout_{reservation_id}",
                        name=f"{appliance_type} {appliance_name} Timeout",
                        device_class=SensorDeviceClass.TIMESTAMP,                        icon=ICON_TIMER,
                        value_fn=get_reservation_timeout,
                    ),
                    reservation_id,
                ),
            ])
    
    # Add the upcoming invoice sensor
    entities.append(
        WeWashSensor(
            coordinator,
            WeWashSensorEntityDescription(
                key="upcoming_invoice",
                name="Upcoming Invoice Amount",
                native_unit_of_measurement="EUR",
                device_class=SensorDeviceClass.MONETARY,
                icon=ICON_INVOICE,
                value_fn=get_upcoming_invoice_amount,
            ),
        )
    )

    async_add_entities(entities)

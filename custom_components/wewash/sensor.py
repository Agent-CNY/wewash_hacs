"""Sensor platform for We-Wash."""
from __future__ import annotations

from typing import Any, Optional
from datetime import datetime

from homeassistant.components.sensor import (
    SensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from .const import (
    DOMAIN,
    ICON_WASHER,
    ICON_DRYER,
    ICON_INVOICE,
    ICON_LAUNDRY_ROOM,
    MANUFACTURER,
    MODEL,
)
from .coordinator import WeWashDataUpdateCoordinator


def get_machine_status(data: dict[str, Any], appliance_short_name: str) -> str:
    """Get machine status based on reservations and laundry room data."""
    # Check reservations first
    reservations = data.get("reservations", {}).get("items", [])
    for reservation in reservations:
        if reservation.get("applianceShortName") == appliance_short_name:
            status = reservation.get("status")
            if status == "ACTIVE":
                return "running"
            elif status == "READY":
                return "reserved"
    
    # Check laundry room availability
    laundry_rooms = data.get("laundry_rooms", {}).get("selectedLaundryRooms", [])
    if laundry_rooms:
        room = laundry_rooms[0]
        if appliance_short_name == "W1":
            available = room.get("serviceAvailability", {}).get("availableWashers", 0)
            return "available" if available > 0 else "reserved"
        elif appliance_short_name == "T1":
            available = room.get("serviceAvailability", {}).get("availableDryers", 0)
            return "available" if available > 0 else "reserved"
    
    return "available"


def get_machine_reservation_data(data: dict[str, Any], appliance_short_name: str) -> dict[str, Any]:
    """Get reservation data for a specific machine."""
    reservations = data.get("reservations", {}).get("items", [])
    for reservation in reservations:
        if reservation.get("applianceShortName") == appliance_short_name:
            return reservation
    return {}


class WeWashBaseSensor(CoordinatorEntity, SensorEntity):
    """Base class for WeWash sensors."""

    def __init__(
        self,
        coordinator: WeWashDataUpdateCoordinator,
        entity_id: str,
        name: str,
        icon: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_id = f"sensor.{entity_id}"
        self._attr_unique_id = f"{coordinator.entry.entry_id}_{entity_id}"
        self._attr_name = name
        self._attr_icon = icon
        
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.entry.entry_id)},
            "name": "We-Wash Laundry System",
            "manufacturer": MANUFACTURER,
            "model": MODEL,
        }


class WeWashWasherSensor(WeWashBaseSensor):
    """Washer W1 sensor entity."""

    def __init__(self, coordinator: WeWashDataUpdateCoordinator) -> None:
        """Initialize the washer sensor."""
        super().__init__(coordinator, "washer_w1", "Washer W1", ICON_WASHER)

    @property
    def native_value(self) -> StateType:
        """Return the state of the washer."""
        return get_machine_status(self.coordinator.data, "W1")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        attrs = {}
        
        # Get laundry room data
        laundry_rooms = self.coordinator.data.get("laundry_rooms", {}).get("selectedLaundryRooms", [])
        if laundry_rooms:
            room = laundry_rooms[0]
            attrs["is_enabled"] = room.get("serviceAvailability", {}).get("washing") == "ENABLED"
            attrs["price"] = room.get("washingCost", {}).get("costOnActive")
            attrs["currency"] = room.get("washingCost", {}).get("currencyCode")
        
        # Get reservation data
        reservation_data = get_machine_reservation_data(self.coordinator.data, "W1")
        if reservation_data:
            attrs["is_online"] = reservation_data.get("applianceOnline")
            attrs["reservation_id"] = reservation_data.get("reservationId")
            attrs["queue_position"] = reservation_data.get("queuePosition")
            attrs["timestamp"] = reservation_data.get("statusChangedTimestamp")
            attrs["timeout"] = reservation_data.get("timeoutTimestamp")
        
        return attrs


class WeWashDryerSensor(WeWashBaseSensor):
    """Dryer T1 sensor entity."""

    def __init__(self, coordinator: WeWashDataUpdateCoordinator) -> None:
        """Initialize the dryer sensor."""
        super().__init__(coordinator, "dryer_t1", "Dryer T1", ICON_DRYER)

    @property
    def native_value(self) -> StateType:
        """Return the state of the dryer."""
        return get_machine_status(self.coordinator.data, "T1")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        attrs = {}
        
        # Get laundry room data
        laundry_rooms = self.coordinator.data.get("laundry_rooms", {}).get("selectedLaundryRooms", [])
        if laundry_rooms:
            room = laundry_rooms[0]
            attrs["is_enabled"] = room.get("serviceAvailability", {}).get("drying") == "ENABLED"
            attrs["price"] = room.get("dryingCost", {}).get("costOnActive")
            attrs["currency"] = room.get("dryingCost", {}).get("currencyCode")
        
        # Get reservation data
        reservation_data = get_machine_reservation_data(self.coordinator.data, "T1")
        if reservation_data:
            attrs["is_online"] = reservation_data.get("applianceOnline")
            attrs["reservation_id"] = reservation_data.get("reservationId")
            attrs["queue_position"] = reservation_data.get("queuePosition")
            attrs["timestamp"] = reservation_data.get("statusChangedTimestamp")
            attrs["timeout"] = reservation_data.get("timeoutTimestamp")
        
        return attrs


class WeWashLaundryRoomSensor(WeWashBaseSensor):
    """Laundry room sensor entity."""

    def __init__(self, coordinator: WeWashDataUpdateCoordinator) -> None:
        """Initialize the laundry room sensor."""
        super().__init__(coordinator, "laundry_room", "Laundry Room", ICON_LAUNDRY_ROOM)

    @property
    def native_value(self) -> StateType:
        """Return the state of the laundry room."""
        laundry_rooms = self.coordinator.data.get("laundry_rooms", {}).get("selectedLaundryRooms", [])
        if laundry_rooms:
            room = laundry_rooms[0]
            avail_washers = room.get("serviceAvailability", {}).get("availableWashers", 0)
            avail_dryers = room.get("serviceAvailability", {}).get("availableDryers", 0)
            return f"{avail_washers} washer(s), {avail_dryers} dryer(s) available"
        return "Unknown"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        attrs = {}
        
        laundry_rooms = self.coordinator.data.get("laundry_rooms", {}).get("selectedLaundryRooms", [])
        if laundry_rooms:
            room = laundry_rooms[0]
            attrs["id"] = room.get("id")
            attrs["name"] = room.get("name")
            
            # Combine address
            address_parts = room.get("address", {})
            if address_parts:
                full_address = f"{address_parts.get('street', '')} {address_parts.get('houseNumber', '')}, {address_parts.get('postalCode', '')} {address_parts.get('city', '')}"
                attrs["address"] = full_address.strip()
            
            attrs["available_washers"] = room.get("serviceAvailability", {}).get("availableWashers")
            attrs["available_dryers"] = room.get("serviceAvailability", {}).get("availableDryers")
            attrs["note"] = room.get("note")
            attrs["critical_note"] = room.get("criticalNote")
            attrs["last_update"] = room.get("sendingTime")
        
        return attrs


class WeWashNextInvoiceSensor(WeWashBaseSensor):
    """Next invoice sensor entity."""

    def __init__(self, coordinator: WeWashDataUpdateCoordinator) -> None:
        """Initialize the next invoice sensor."""
        super().__init__(coordinator, "next_invoice", "Next Invoice", ICON_INVOICE)

    @property
    def native_value(self) -> StateType:
        """Return the total amount of all active reservations."""
        total_amount = 0.0
        
        reservations = self.coordinator.data.get("upcoming_invoices", {}).get("reservations", [])
        for reservation in reservations:
            if reservation.get("invoiceItemStatus") == "NEW":
                total_amount += reservation.get("amount", 0.0)
        
        return total_amount

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        attrs = {}
        
        reservations = self.coordinator.data.get("upcoming_invoices", {}).get("reservations", [])
        if reservations:
            # Get currency from first reservation
            attrs["currency"] = reservations[0].get("currency", "EUR")
        
        return attrs


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up We-Wash sensors."""
    coordinator: WeWashDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    # Create the 4 entities as defined in entities.md
    entities = [
        WeWashWasherSensor(coordinator),
        WeWashDryerSensor(coordinator),
        WeWashLaundryRoomSensor(coordinator),
        WeWashNextInvoiceSensor(coordinator),
    ]
    
    async_add_entities(entities)

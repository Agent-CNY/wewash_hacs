"""Sensor platform for We-Wash."""
from __future__ import annotations

from typing import Any, Optional
from dataclasses import dataclass
import time
from datetime import datetime

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
    ICON_LAUNDRY_ROOM,
    ICON_CYCLE_COUNT,
    MANUFACTURER,
    MODEL,
    SENSOR_LAUNDRY_ROOM,
    SENSOR_INVOICE,
    SENSOR_WASHING_MACHINE,
    SENSOR_DRYER,
    STATUS_MAPPING,
)
from .coordinator import WeWashDataUpdateCoordinator

def get_machine_status_with_time(data: dict[str, Any], machine_type: str, machine_shortname: str) -> tuple[str, Optional[int]]:
    """Get machine status with running time if active."""
    if "items" not in data.get("reservations", {}):
        return "AVAILABLE", None
        
    for item in data["reservations"]["items"]:
        if item["applianceType"] == machine_type and item["applianceShortName"] == machine_shortname:
            status = item["status"]
            # Calculate running time in minutes if active
            if status == "ACTIVE":
                if "statusChangedTimestamp" in item and item["statusChangedTimestamp"]:
                    current_time_ms = int(time.time() * 1000)
                    elapsed_ms = current_time_ms - item["statusChangedTimestamp"]
                    elapsed_minutes = int(elapsed_ms / 60000)
                    return status, elapsed_minutes
                else:
                    # Return status without time if timestamp is missing
                    return status, None
            # Return any other status found (including RESERVATION_TIMED_OUT, RESERVED, etc.)
            return status, None
            
    # If machine not found in reservations, check laundry room data for availability
    for room in data.get("laundry_rooms", {}).get("selectedLaundryRooms", []):
        if machine_type == "WASHING_MACHINE" and room["serviceAvailability"]["availableWashers"] > 0:
            return "AVAILABLE", None
        elif machine_type == "DRYER" and room["serviceAvailability"]["availableDryers"] > 0:
            return "AVAILABLE", None
            
    return "AVAILABLE", None

def format_timestamp_to_datetime(timestamp_ms: int) -> datetime:
    """Convert millisecond timestamp to datetime."""
    return datetime.fromtimestamp(timestamp_ms / 1000)

def friendly_status_name(status: str) -> str:
    """Convert technical status to user-friendly name."""
    return STATUS_MAPPING.get(status, status)

@dataclass
class WeWashSensorEntityDescription(SensorEntityDescription):
    """Class describing We-Wash sensor entities."""
    value_fn: callable = None
    attr_fn: callable = None  # Function to get additional attributes
    translation_key: str = None

class WeWashSensor(CoordinatorEntity, SensorEntity):
    """Representation of a We-Wash sensor."""

    entity_description: WeWashSensorEntityDescription

    def __init__(
        self,
        coordinator: WeWashDataUpdateCoordinator,
        description: WeWashSensorEntityDescription,
        laundry_room_id: str | None = None,
        machine_type: str | None = None,
        machine_shortname: str | None = None,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._laundry_room_id = laundry_room_id
        self._machine_type = machine_type
        self._machine_shortname = machine_shortname
        
        # Build a unique ID based on the provided parameters
        self._attr_unique_id = f"{coordinator.entry.entry_id}_{description.key}"
        if laundry_room_id:
            self._attr_unique_id += f"_{laundry_room_id}"
        if machine_type and machine_shortname:
            self._attr_unique_id += f"_{machine_type}_{machine_shortname}"
            
        # Set translation key if provided
        if description.translation_key:
            self._attr_translation_key = description.translation_key

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
            params = [self.coordinator.data]
            
            # Add additional parameters based on what's available
            if self._laundry_room_id:
                params.append(self._laundry_room_id)
            elif self._machine_type and self._machine_shortname:
                params.append(self._machine_type)
                params.append(self._machine_shortname)
            else:
                # Always ensure we have at least a second parameter for functions that expect it
                params.append(None)
                
            return self.entity_description.value_fn(*params)
        return None    @property
    def extra_state_attributes(self):
        """Return additional state attributes."""
        if self.entity_description.attr_fn is not None:
            params = [self.coordinator.data]
            
            # Add additional parameters based on what's available
            if self._laundry_room_id:
                params.append(self._laundry_room_id)
            elif self._machine_type and self._machine_shortname:
                params.append(self._machine_type)
                params.append(self._machine_shortname)
            else:
                # Always ensure we have at least a second parameter for functions that expect it
                params.append(None)
                
            result = self.entity_description.attr_fn(*params)
            return result if isinstance(result, dict) else {}
        return {}

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up We-Wash sensors."""
    coordinator: WeWashDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    # Legacy value functions (kept for backward compatibility)
    def get_balance(data: dict[str, Any], _=None) -> float:
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
                return None            # Otherwise, return info of the first reservation (legacy behavior)
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
        
    def get_upcoming_invoice_amount(data: dict[str, Any], _=None) -> float:
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

    entities = []
    
    # 1. Add balance sensor
    entities.append(
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
    )
    
    # 2. Add comprehensive invoice sensor with more details
    entities.append(
        WeWashInvoiceSensor(
            coordinator,
            WeWashSensorEntityDescription(
                key="upcoming_invoice",
                name="Upcoming Invoice",
                native_unit_of_measurement="EUR",
                device_class=SensorDeviceClass.MONETARY,
                icon=ICON_INVOICE,
            ),
        )
    )
    
    # 3. Add dedicated cycling count sensors for easier use in UI
    entities.extend([
        WeWashSensor(
            coordinator,
            WeWashSensorEntityDescription(
                key="washing_cycles",
                name="Washing Cycles This Month",
                native_unit_of_measurement="cycles",
                icon=ICON_CYCLE_COUNT,
                value_fn=lambda data, _=None: data.get("invoices", {}).get("washingCycles", 0),
            ),
        ),
        WeWashSensor(
            coordinator,
            WeWashSensorEntityDescription(
                key="drying_cycles",
                name="Drying Cycles This Month",
                native_unit_of_measurement="cycles",
                icon=ICON_CYCLE_COUNT,
                value_fn=lambda data, _=None: data.get("invoices", {}).get("dryingCycles", 0),
            ),
        ),
        WeWashSensor(
            coordinator,
            WeWashSensorEntityDescription(
                key="invoice_due",
                name="Days Until Invoice",
                native_unit_of_measurement="days",
                icon=ICON_TIMER,                value_fn=lambda data, _=None: max(0, int(
                    (datetime.fromtimestamp(data.get("invoices", {}).get(
                        "cumulativeInvoicingDate", time.time() * 1000) / 1000) - 
                     datetime.now()).days
                ))
            ),
        ),
    ])
    
    # 4. Add laundry room overview sensor
    if coordinator.data["laundry_rooms"]["selectedLaundryRooms"]:
        entities.append(
            WeWashLaundryRoomSensor(
                coordinator,
                WeWashSensorEntityDescription(
                    key="laundry_room",
                    name=SENSOR_LAUNDRY_ROOM,
                    icon=ICON_LAUNDRY_ROOM,
                ),
            )
        )    # 5. Add enhanced machine status sensors for each machine type found in reservations
    machine_types = {}  # Dictionary to track unique machines
    
    # Get all machine types from reservations (including all statuses, not just active)
    if "items" in coordinator.data.get("reservations", {}):
        for reservation in coordinator.data["reservations"]["items"]:
            machine_key = f"{reservation['applianceType']}_{reservation['applianceShortName']}"
            if machine_key not in machine_types:
                machine_types[machine_key] = {
                    "type": reservation["applianceType"],
                    "shortname": reservation["applianceShortName"],
                }
    
    # Only add machines if we found them in reservations data
    # Don't create generic W1, W2, etc. unless we have evidence they exist
    
    # Add dedicated sensor for each machine
    for machine in machine_types.values():
        machine_type = machine["type"]
        shortname = machine["shortname"]
        friendly_type = SENSOR_WASHING_MACHINE if machine_type == "WASHING_MACHINE" else SENSOR_DRYER
        icon = ICON_WASHER if machine_type == "WASHING_MACHINE" else ICON_DRYER
        
        entities.append(
            WeWashMachineSensor(
                coordinator,
                WeWashSensorEntityDescription(
                    key=f"{machine_type.lower()}_{shortname.lower()}",
                    name=f"{friendly_type} {shortname}",
                    icon=icon,
                ),
                None,  # no laundry room id
                machine_type,
                shortname,
            )
        )
    
    # 6. Add original sensors for backward compatibility
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
        ])
    
    # Add legacy reservation sensors for backward compatibility
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
        # Keep legacy upcoming invoice sensor for backward compatibility
        WeWashSensor(
            coordinator,
            WeWashSensorEntityDescription(
                key="upcoming_invoice_amount",
                name="Upcoming Invoice Amount",
                native_unit_of_measurement="EUR",
                device_class=SensorDeviceClass.MONETARY,
                icon=ICON_INVOICE,
                value_fn=get_upcoming_invoice_amount,
            ),
        ),
    ])
    
    # Add machine-specific sensors for each active reservation for backward compatibility
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
                        device_class=SensorDeviceClass.TIMESTAMP,
                        icon=ICON_TIMER,
                        value_fn=get_reservation_timeout,
                    ),
                    reservation_id,
                ),
            ])

    async_add_entities(entities)

class WeWashMachineSensor(WeWashSensor):
    """Representation of a WeWash machine sensor with enhanced status information."""

    @property
    def native_value(self) -> str:
        """Return the user-friendly state of the machine."""
        status, minutes = get_machine_status_with_time(
            self.coordinator.data, self._machine_type, self._machine_shortname)
            
        # Convert technical status to user-friendly message
        friendly_status = friendly_status_name(status)
        
        if status == "ACTIVE" and minutes is not None:
            return f"{friendly_status} ({minutes} min)"
        return friendly_status
        
    @property
    def extra_state_attributes(self):
        """Return the machine attributes."""
        attrs = {}
        
        # Find the machine in the reservations data
        machine_found = False
        for item in self.coordinator.data.get("reservations", {}).get("items", []):
            if (item["applianceType"] == self._machine_type and 
                item["applianceShortName"] == self._machine_shortname):
                
                machine_found = True
                attrs["online"] = item["applianceOnline"]
                attrs["price"] = item["price"]
                attrs["currency"] = item["currency"]
                attrs["raw_status"] = item["status"]
                attrs["reservation_id"] = item["reservationId"]
                
                # Add timestamp information
                if "statusChangedTimestamp" in item and item["statusChangedTimestamp"]:
                    timestamp = item["statusChangedTimestamp"]
                    attrs["status_changed"] = format_timestamp_to_datetime(timestamp).isoformat()
                    
                    # If active, add elapsed time
                    if item["status"] == "ACTIVE":
                        current_time_ms = int(time.time() * 1000)
                        elapsed_ms = current_time_ms - timestamp
                        attrs["elapsed_minutes"] = int(elapsed_ms / 60000)
                
                if "timeoutTimestamp" in item and item["timeoutTimestamp"]:
                    attrs["timeout_at"] = format_timestamp_to_datetime(
                        item["timeoutTimestamp"]).isoformat()
                
                # Add laundry room info
                if "laundryRoom" in item:
                    attrs["laundry_room"] = item["laundryRoom"]["name"]
                
                break
                
        if not machine_found:
            # If not found in reservations, check laundry room for availability info
            attrs["available"] = True
            attrs["raw_status"] = "AVAILABLE"
            attrs["online"] = True  # Assume available machines are online
            
            # Add pricing from laundry room data
            for room in self.coordinator.data.get("laundry_rooms", {}).get("selectedLaundryRooms", []):
                if self._machine_type == "WASHING_MACHINE":
                    attrs["price"] = room["washingCost"]["costOnActive"]
                    attrs["currency"] = room["washingCost"]["currencyCode"]
                elif self._machine_type == "DRYER":
                    attrs["price"] = room["dryingCost"]["costOnActive"]
                    attrs["currency"] = room["dryingCost"]["currencyCode"]
                attrs["laundry_room"] = room["name"]
                break
                
        return attrs

class WeWashLaundryRoomSensor(WeWashSensor):
    """Representation of a WeWash laundry room availability sensor."""
    
    @property
    def native_value(self) -> str:
        """Return the state of the laundry room."""
        rooms_data = self.coordinator.data.get("laundry_rooms", {})
        selected_rooms = rooms_data.get("selectedLaundryRooms", [])
        
        if not selected_rooms:
            return "No laundry rooms available"
            
        room = selected_rooms[0]
        avail_washers = room["serviceAvailability"]["availableWashers"]
        avail_dryers = room["serviceAvailability"]["availableDryers"]
        return f"{avail_washers} washer(s), {avail_dryers} dryer(s) available"
        
    @property
    def extra_state_attributes(self):
        """Return detailed laundry room information."""
        attrs = {}
        rooms_data = self.coordinator.data.get("laundry_rooms", {})
        selected_rooms = rooms_data.get("selectedLaundryRooms", [])
        
        if selected_rooms:
            room = selected_rooms[0]
            attrs["name"] = room["name"]
            attrs["address"] = f"{room['address']['street']} {room['address']['houseNumber']}"
            attrs["postal_code"] = room['address']['postalCode']
            attrs["city"] = room['address']['city']
            attrs["washing_cost"] = room["washingCost"]["costOnActive"]
            attrs["washing_currency"] = room["washingCost"]["currencyCode"]
            attrs["drying_cost"] = room["dryingCost"]["costOnActive"]
            attrs["drying_currency"] = room["dryingCost"]["currencyCode"]
            attrs["washer_slot_duration"] = int(room["durations"]["defaultSlotWasher"] / 60000)  # minutes
            attrs["dryer_slot_duration"] = int(room["durations"]["defaultSlotDryer"] / 60000)  # minutes
            
            # Add service availability info
            attrs["available_washers"] = room["serviceAvailability"]["availableWashers"]
            attrs["available_dryers"] = room["serviceAvailability"]["availableDryers"]
            attrs["washing_enabled"] = room["serviceAvailability"]["washing"] == "ENABLED"
            attrs["drying_enabled"] = room["serviceAvailability"]["drying"] == "ENABLED"
            
        return attrs

class WeWashInvoiceSensor(WeWashSensor):
    """Representation of a WeWash upcoming invoice sensor."""
    
    @property
    def native_value(self) -> float:
        """Return the upcoming invoice amount."""
        invoice_data = self.coordinator.data.get("invoices", {})
        if "amount" in invoice_data:
            return invoice_data["amount"]
        return 0.0
        
    @property
    def extra_state_attributes(self):
        """Return detailed invoice information."""
        invoice_data = self.coordinator.data.get("invoices", {})
        attrs = {}
        
        # Basic info
        if "currency" in invoice_data:
            attrs["currency"] = invoice_data["currency"]
        
        # Add cycle counts
        if "washingCycles" in invoice_data:
            attrs["washing_cycles"] = invoice_data["washingCycles"]
        if "dryingCycles" in invoice_data:
            attrs["drying_cycles"] = invoice_data["dryingCycles"]
            
        # Add payment threshold
        if "selectedPaymentMethodThreshold" in invoice_data:
            attrs["payment_threshold"] = invoice_data["selectedPaymentMethodThreshold"]
            
        # Add due date in human-readable format
        if "cumulativeInvoicingDate" in invoice_data:
            invoice_date = format_timestamp_to_datetime(invoice_data["cumulativeInvoicingDate"])
            now = datetime.now()
            days_until = (invoice_date - now).days
            attrs["invoice_date"] = invoice_date.isoformat()
            attrs["days_until_invoice"] = max(0, days_until)
            
        # Add individual items - limited to avoid excessive data
        if "reservations" in invoice_data:
            attrs["item_count"] = len(invoice_data["reservations"])
            
            # Include last item details
            if invoice_data["reservations"]:
                latest_item = invoice_data["reservations"][-1]
                attrs["latest_item"] = {
                    "type": latest_item["type"],
                    "shortName": latest_item["shortName"],
                    "amount": latest_item["amount"],
                    "timestamp": format_timestamp_to_datetime(latest_item["timestamp"]).isoformat(),
                }
            
        return attrs

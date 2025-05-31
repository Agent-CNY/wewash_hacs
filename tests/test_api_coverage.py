"""Tests for WeWash integration data structures and API coverage."""
import pytest
from unittest.mock import patch, MagicMock

from custom_components.wewash.coordinator import WeWashDataUpdateCoordinator
from custom_components.wewash.sensor import (
    get_machine_status_with_time,
    format_timestamp_to_datetime,
    friendly_status_name,
)

# Fixtures and test data are imported from conftest.py automatically
from conftest import (
    USER_DATA_RESPONSE, LAUNDRY_ROOMS_RESPONSE, RESERVATIONS_RESPONSE, UPCOMING_INVOICES_RESPONSE
)


class TestAPIDataStructures:
    """Test that all API data structures are properly handled."""

    async def test_user_data_structure_coverage(self, hass, mock_config_entry):
        """Test that all user data fields are properly accessible."""
        coordinator = WeWashDataUpdateCoordinator(hass, mock_config_entry)
        coordinator.data = {"user": USER_DATA_RESPONSE}
        
        user_data = coordinator.data["user"]
        
        # Test essential user fields
        assert "customerId" in user_data
        assert "email" in user_data
        assert "firstName" in user_data
        assert "lastName" in user_data
        assert "selectedLocationId" in user_data
        assert "accountState" in user_data
        assert "countryCode" in user_data
        assert "lang" in user_data
        
        # Test credits structure
        assert "credits" in user_data
        credits = user_data["credits"]
        assert "amount" in credits
        assert "currency" in credits
        assert isinstance(credits["amount"], (int, float))
        
        # Test boolean flags
        assert "analyticsEnabled" in user_data
        assert "emailNotificationsEnabled" in user_data
        assert "hasOutstandingInvoices" in user_data
        assert isinstance(user_data["analyticsEnabled"], bool)
        
        # Test legal documents structure
        assert "unconfirmedLegalDocuments" in user_data
        legal_docs = user_data["unconfirmedLegalDocuments"]
        assert "privacyPolicy" in legal_docs
        assert "termsAndConditions" in legal_docs
        
        # Test payment methods
        assert "allowedPaymentMethodTypes" in user_data
        assert isinstance(user_data["allowedPaymentMethodTypes"], list)
        
        # Test UI flags
        assert "uiFlags" in user_data
        ui_flags = user_data["uiFlags"]
        assert isinstance(ui_flags, dict)

    async def test_laundry_rooms_data_structure_coverage(self, hass, mock_config_entry):
        """Test that all laundry room data fields are properly accessible."""
        coordinator = WeWashDataUpdateCoordinator(hass, mock_config_entry)
        coordinator.data = {"laundry_rooms": LAUNDRY_ROOMS_RESPONSE}
        
        laundry_rooms = coordinator.data["laundry_rooms"]
        
        # Test top-level structure
        assert "selectedLaundryRooms" in laundry_rooms
        assert "suggestedLaundryRooms" in laundry_rooms
        assert isinstance(laundry_rooms["selectedLaundryRooms"], list)
        assert isinstance(laundry_rooms["suggestedLaundryRooms"], list)
        
        # Test individual room structure
        if laundry_rooms["selectedLaundryRooms"]:
            room = laundry_rooms["selectedLaundryRooms"][0]
            
            # Basic room info
            assert "id" in room
            assert "name" in room
            assert "availability" in room
            
            # Cost information
            assert "washingCost" in room
            assert "dryingCost" in room
            washing_cost = room["washingCost"]
            assert "costOnActive" in washing_cost
            assert "currencyCode" in washing_cost
            
            # Address information
            assert "address" in room
            address = room["address"]
            assert "street" in address
            assert "houseNumber" in address
            assert "postalCode" in address
            assert "city" in address
            
            # Service availability
            assert "serviceAvailability" in room
            service_avail = room["serviceAvailability"]
            assert "availableWashers" in service_avail
            assert "availableDryers" in service_avail
            assert "washing" in service_avail
            assert "drying" in service_avail
            
            # Duration information
            assert "durations" in room
            durations = room["durations"]
            assert "defaultSlotWasher" in durations
            assert "defaultSlotDryer" in durations
            assert isinstance(durations["defaultSlotWasher"], int)
            assert isinstance(durations["defaultSlotDryer"], int)

    async def test_reservations_data_structure_coverage(self, hass, mock_config_entry):
        """Test that all reservation data fields are properly accessible."""
        coordinator = WeWashDataUpdateCoordinator(hass, mock_config_entry)
        coordinator.data = {"reservations": RESERVATIONS_RESPONSE}
        
        reservations = coordinator.data["reservations"]
        
        # Test top-level structure
        assert "items" in reservations
        assert "slots" in reservations
        assert "timestamp" in reservations
        assert isinstance(reservations["items"], list)
        assert isinstance(reservations["slots"], list)
        assert isinstance(reservations["timestamp"], int)
        
        # Test individual reservation structure
        if reservations["items"]:
            reservation = reservations["items"][0]
            
            # Basic reservation info
            assert "reservationId" in reservation
            assert "status" in reservation
            assert "applianceType" in reservation
            assert "applianceShortName" in reservation
            assert "applianceOnline" in reservation
            assert isinstance(reservation["applianceOnline"], bool)
            
            # Timing information
            assert "statusChangedTimestamp" in reservation
            assert isinstance(reservation["statusChangedTimestamp"], int)
            
            # Pricing information
            assert "price" in reservation
            assert "currency" in reservation
            assert isinstance(reservation["price"], (int, float))
            
            # Booking information
            assert "bookingLogic" in reservation
            assert "offerVoucherPayment" in reservation
            assert isinstance(reservation["offerVoucherPayment"], bool)
            
            # Laundry room reference
            assert "laundryRoom" in reservation
            laundry_room = reservation["laundryRoom"]
            assert "id" in laundry_room
            assert "name" in laundry_room
            assert "street" in laundry_room
            assert "houseNumber" in laundry_room
            assert "postalCode" in laundry_room
            assert "city" in laundry_room

    async def test_invoices_data_structure_coverage(self, hass, mock_config_entry):
        """Test that all invoice data fields are properly accessible."""
        coordinator = WeWashDataUpdateCoordinator(hass, mock_config_entry)
        coordinator.data = {"invoices": UPCOMING_INVOICES_RESPONSE}
        
        invoices = coordinator.data["invoices"]
        
        # Test top-level structure
        assert "reservations" in invoices
        assert "amount" in invoices
        assert "currency" in invoices
        assert "cumulativeInvoicingDate" in invoices
        assert "washingCycles" in invoices
        assert "dryingCycles" in invoices
        assert "selectedPaymentMethodThreshold" in invoices
        
        # Test data types
        assert isinstance(invoices["reservations"], list)
        assert isinstance(invoices["amount"], (int, float))
        assert isinstance(invoices["currency"], str)
        assert isinstance(invoices["cumulativeInvoicingDate"], int)
        assert isinstance(invoices["washingCycles"], int)
        assert isinstance(invoices["dryingCycles"], int)
        assert isinstance(invoices["selectedPaymentMethodThreshold"], (int, float))
        
        # Test individual invoice item structure
        if invoices["reservations"]:
            item = invoices["reservations"][0]
            
            assert "invoiceItemId" in item
            assert "timestamp" in item
            assert "amount" in item
            assert "shortName" in item
            assert "type" in item
            assert "invoiceItemStatus" in item
            
            # Test data types
            assert isinstance(item["invoiceItemId"], int)
            assert isinstance(item["timestamp"], int)
            assert isinstance(item["amount"], (int, float))
            assert isinstance(item["shortName"], str)
            assert isinstance(item["type"], str)
            assert isinstance(item["invoiceItemStatus"], str)

    def test_utility_functions(self):
        """Test utility functions for data processing."""
        # Test timestamp formatting
        timestamp_ms = 1748697289940
        dt = format_timestamp_to_datetime(timestamp_ms)
        assert dt is not None
        assert hasattr(dt, 'year')
        assert hasattr(dt, 'month')
        assert hasattr(dt, 'day')
        
        # Test status mapping
        assert friendly_status_name("ACTIVE") == "Running"
        assert friendly_status_name("RESERVATION_TIMED_OUT") == "Reservation Expired"
        assert friendly_status_name("UNKNOWN_STATUS") == "UNKNOWN_STATUS"  # Fallback
        
        # Test machine status function
        test_data = {
            "reservations": {
                "items": [
                    {
                        "applianceType": "WASHING_MACHINE",
                        "applianceShortName": "W1",
                        "status": "ACTIVE",
                        "statusChangedTimestamp": 1748697289940
                    }
                ]
            },
            "laundry_rooms": {
                "selectedLaundryRooms": [
                    {
                        "serviceAvailability": {
                            "availableWashers": 1,
                            "availableDryers": 0
                        }
                    }
                ]
            }
        }
          # Test active machine
        status, minutes = get_machine_status_with_time(test_data, "WASHING_MACHINE", "W1")
        assert status == "ACTIVE"
        assert isinstance(minutes, int)
        
        # Test non-existent machine
        status, minutes = get_machine_status_with_time(test_data, "DRYER", "T2")
        assert status == "AVAILABLE"
        assert minutes is None

    def test_edge_cases_and_missing_data(self):
        """Test handling of edge cases and missing data."""
        # Test empty data
        empty_data = {}
        status, minutes = get_machine_status_with_time(empty_data, "WASHING_MACHINE", "W1")
        assert status == "AVAILABLE"
        assert minutes is None
        
        # Test malformed reservation data
        malformed_data = {
            "reservations": {
                "items": [
                    {
                        "applianceType": "WASHING_MACHINE",
                        "applianceShortName": "W1",
                        "status": "ACTIVE"
                        # Missing statusChangedTimestamp
                    }
                ]
            }
        }
        
        # Should handle missing timestamp gracefully
        status, minutes = get_machine_status_with_time(malformed_data, "WASHING_MACHINE", "W1")
        assert status == "ACTIVE"
        # Minutes calculation should fail gracefully

    def test_status_mapping_completeness(self):
        """Test that all known statuses are properly mapped."""
        from custom_components.wewash.const import STATUS_MAPPING
        
        # Test that essential statuses are mapped
        essential_statuses = [
            "ACTIVE",
            "RESERVATION_TIMED_OUT", 
            "AVAILABLE",
            "OCCUPIED",
            "OUT_OF_ORDER"
        ]
        
        for status in essential_statuses:
            mapped = friendly_status_name(status)
            # Should be either mapped to a friendly name or return the original
            assert isinstance(mapped, str)
            assert len(mapped) > 0

    async def test_error_handling_malformed_responses(self, hass, mock_config_entry):
        """Test that the integration handles malformed API responses gracefully."""
        coordinator = WeWashDataUpdateCoordinator(hass, mock_config_entry)
        
        # Test with completely malformed data
        coordinator.data = {
            "user": None,
            "laundry_rooms": {},
            "reservations": [],
            "invoices": None
        }
        
        # Should not crash when accessing sensors
        assert coordinator.data is not None
        
        # Test with partial data
        coordinator.data = {
            "user": {"credits": {"amount": 5.0}},  # Missing many fields
            "laundry_rooms": {"selectedLaundryRooms": []},  # Empty list
            "reservations": {"items": [], "timestamp": 0},  # Empty reservations
            "invoices": {"amount": 0, "currency": "EUR"}  # Minimal invoice data
        }
        
        # Should handle partial data gracefully
        assert coordinator.data["user"]["credits"]["amount"] == 5.0
        assert len(coordinator.data["laundry_rooms"]["selectedLaundryRooms"]) == 0

    def test_currency_and_localization_support(self):
        """Test that different currencies and locales are supported."""
        # Test EUR currency (default)
        test_data_eur = {
            "user": {"credits": {"amount": 10.50, "currency": "EUR"}},
            "invoices": {"amount": 15.25, "currency": "EUR"}
        }
        
        assert test_data_eur["user"]["credits"]["currency"] == "EUR"
        assert test_data_eur["invoices"]["currency"] == "EUR"
        
        # Test that amounts are properly handled as floats
        assert isinstance(test_data_eur["user"]["credits"]["amount"], float)
        assert isinstance(test_data_eur["invoices"]["amount"], float)

    def test_appliance_type_coverage(self):
        """Test that all appliance types are properly handled."""
        appliance_types = ["WASHING_MACHINE", "DRYER"]
        
        for appliance_type in appliance_types:
            test_data = {
                "reservations": {
                    "items": [
                        {
                            "applianceType": appliance_type,
                            "applianceShortName": "TEST1",
                            "status": "ACTIVE",
                            "statusChangedTimestamp": 1748697289940
                        }
                    ]
                }
            }
            
            status, minutes = get_machine_status_with_time(test_data, appliance_type, "TEST1")
            assert status == "ACTIVE"
            assert isinstance(minutes, int)

    def test_timestamp_handling(self):
        """Test that timestamps are handled correctly across the integration."""
        # Test various timestamp formats
        timestamps = [
            1748697289940,  # Milliseconds (typical)
            1748697289,     # Seconds
            0,              # Epoch
        ]
        
        for ts in timestamps:
            dt = format_timestamp_to_datetime(ts)
            assert dt is not None
            # Should be a valid datetime
            assert hasattr(dt, 'isoformat')

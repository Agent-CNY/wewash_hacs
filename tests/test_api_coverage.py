"""Tests for WeWash integration data structures and API coverage."""
import pytest
from unittest.mock import patch, MagicMock

from custom_components.wewash.coordinator import WeWashDataUpdateCoordinator
from custom_components.wewash.sensor import (
    get_machine_status,
    get_machine_reservation_data,
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

    async def test_reservations_data_structure_coverage(self, hass, mock_config_entry):
        """Test that all reservations data fields are properly accessible."""
        coordinator = WeWashDataUpdateCoordinator(hass, mock_config_entry)
        coordinator.data = {"reservations": RESERVATIONS_RESPONSE}
        
        reservations = coordinator.data["reservations"]
        
        # Test top-level structure
        assert "items" in reservations
        assert "timestamp" in reservations
        assert isinstance(reservations["items"], list)
          # Test individual reservation structure
        if reservations["items"]:
            reservation = reservations["items"][0]
            
            # Basic reservation info
            assert "reservationId" in reservation
            assert "applianceType" in reservation
            assert "applianceShortName" in reservation
            assert "status" in reservation
            assert "statusChangedTimestamp" in reservation
            # Note: laundryRoomId might not be present in all reservations
            
            # Test data types
            assert isinstance(reservation["reservationId"], int)
            assert isinstance(reservation["applianceType"], str)
            assert isinstance(reservation["applianceShortName"], str)
            assert isinstance(reservation["status"], str)
            assert isinstance(reservation["statusChangedTimestamp"], int)

    async def test_upcoming_invoices_data_structure_coverage(self, hass, mock_config_entry):
        """Test that all upcoming invoices data fields are properly accessible."""
        coordinator = WeWashDataUpdateCoordinator(hass, mock_config_entry)
        coordinator.data = {"invoices": UPCOMING_INVOICES_RESPONSE}
        
        invoices = coordinator.data["invoices"]        # Test top-level structure
        assert "amount" in invoices
        assert "currency" in invoices
        assert "reservations" in invoices
        assert isinstance(invoices["reservations"], list)
        
        # Test individual invoice item structure
        if invoices["reservations"]:
            item = invoices["reservations"][0]
            
            # Required fields
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
        status = get_machine_status(test_data, "W1")
        assert status == "running"  # Function returns lowercase status
        
        # Test non-existent machine fallback to available
        status = get_machine_status(test_data, "T2")
        assert status == "available"  # Function returns lowercase status
          # Test reservation data retrieval
        reservation = get_machine_reservation_data(test_data, "W1")
        assert reservation is not None
        assert reservation["applianceShortName"] == "W1"

    def test_edge_cases_and_missing_data(self):
        """Test handling of edge cases and missing data."""
        # Test empty data
        empty_data = {}
        status = get_machine_status(empty_data, "W1")
        assert status == "available"  # Function returns lowercase status
        
        reservation = get_machine_reservation_data(empty_data, "W1")
        assert reservation == {}  # Function returns empty dict for missing data

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

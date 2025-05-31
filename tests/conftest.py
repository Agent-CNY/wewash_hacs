"""Fixtures for testing."""
import asyncio
import sys
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from custom_components.wewash.const import DOMAIN
from custom_components.wewash.coordinator import WeWashDataUpdateCoordinator

# Fix for Windows aiodns issues
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Setup Home Assistant for testing
@pytest.fixture
def hass():
    """Set up a Home Assistant instance for testing."""
    hass = MagicMock()
    hass.data = {}
    return hass

# Sample test data - Based on actual API responses
AUTH_RESPONSE = {
    "accessToken": "test_access_token",
    "refreshToken": "test_refresh_token"
}

# Based on /v3/users/me endpoint
USER_DATA_RESPONSE = {
    "customerId": 153534214,
    "externalId": "zNUGPbeb",
    "email": "philipp.cserny@gmail.com",
    "firstName": "Philipp",
    "lastName": "Cserny",
    "roomNumber": None,
    "roleId": 2,
    "userType": "APP_USER",
    "selectedLocationId": "lGG6MaVX",
    "accountState": "ACTIVE",
    "countryCode": "AT",
    "lang": "en",
    "analyticsEnabled": False,
    "emailNotificationsEnabled": False,
    "credits": {
        "amount": 0.00,
        "currency": "EUR"
    },
    "vouchersForUse": 0,
    "appFeedbackQuestionId": None,
    "hasOutstandingInvoices": False,
    "unconfirmedLegalDocuments": {
        "privacyPolicy": False,
        "termsAndConditions": False
    },
    "allowedPaymentMethodTypes": ["externalDebit", "externalCreditcard", "checkout", "paypal"],
    "requestAnalytics": False,
    "requestStoreRating": False,
    "paymentMethodCard": None,
    "upgradeUser": None,
    "skipDirectDebitVerification": False,
    "cardsForSelectedLaundryRoom": [],
    "uiFlags": {
        "showFiscalInformationMissingCard": False,
        "showFiscalInformationItaly": False
    },
    "voucherFallbackBookingLogic": "USER_DIRECT_BOOKING"
}

# Based on /v3/users/me/laundry-rooms endpoint
LAUNDRY_ROOMS_RESPONSE = {
    "selectedLaundryRooms": [
        {
            "id": "lGG6MaVX",
            "washingCost": {
                "costOnActive": 1.50,
                "currencyCode": "EUR"
            },
            "dryingCost": {
                "costOnActive": 1.50,
                "currencyCode": "EUR"
            },
            "note": None,
            "showCriticalNote": False,
            "criticalNote": None,
            "advancedNote": {
                "severity": "LOW",
                "template": "DEFAULT_WWB",
                "value": None
            },
            "name": "Waschraum",
            "address": {
                "street": "Mühlbergstrasse",
                "houseNumber": "18",
                "postalCode": "1140",
                "city": "Wien"
            },
            "feedbackMode": False,
            "availability": "AVAILABLE",
            "serviceAvailability": {
                "availableWashers": 1,
                "availableDryers": 0,
                "washing": "ENABLED",
                "drying": "ENABLED"
            },
            "sendingTime": 1748697289940,
            "chatbotEnable": False,
            "showCalendar": False,
            "durations": {
                "defaultSlotDryer": 7200000,
                "defaultSlotWasher": 7200000
            }
        }
    ],
    "suggestedLaundryRooms": []
}

# Based on /v3/users/me/reservations endpoint
RESERVATIONS_RESPONSE = {
    "items": [
        {
            "reservationId": 20158191,
            "status": "RESERVATION_TIMED_OUT",
            "applianceType": "WASHING_MACHINE",
            "applianceShortName": "W1",
            "applianceOnline": True,
            "statusChangedTimestamp": 1748695512245,
            "timeoutTimestamp": None,
            "queuePosition": None,
            "sendingTime": 1748697289942,
            "price": 1.50,
            "currency": "EUR",
            "notMyLaundry": "ALLOWED",
            "laundryLesson": None,
            "bookingLogic": "APPLIANCE_START",
            "offerVoucherPayment": False,
            "checkoutUrl": None,
            "paymentClause": "OTHER",
            "cleaningCycle": None,
            "reservationSlot": None,
            "laundryRoom": {
                "id": "lGG6MaVX",
                "name": "Waschraum",
                "street": "Mühlbergstrasse",
                "houseNumber": "18",
                "postalCode": "1140",
                "city": "Wien"
            }
        },
        {
            "reservationId": 20157655,
            "status": "ACTIVE",
            "applianceType": "DRYER",
            "applianceShortName": "T1",
            "applianceOnline": True,
            "statusChangedTimestamp": 1748693555615,
            "timeoutTimestamp": None,
            "queuePosition": None,
            "sendingTime": 1748697289953,
            "price": 1.50,
            "currency": "EUR",
            "notMyLaundry": "ALLOWED",
            "laundryLesson": None,
            "bookingLogic": "APPLIANCE_START",
            "offerVoucherPayment": False,
            "checkoutUrl": None,
            "paymentClause": None,
            "cleaningCycle": None,
            "reservationSlot": None,
            "laundryRoom": {
                "id": "lGG6MaVX",
                "name": "Waschraum",
                "street": "Mühlbergstrasse",
                "houseNumber": "18",
                "postalCode": "1140",
                "city": "Wien"
            }
        }
    ],
    "slots": [],
    "timestamp": 1748697289958
}

# Based on /v3/users/me/upcoming-invoices endpoint
UPCOMING_INVOICES_RESPONSE = {
    "reservations": [
        {
            "invoiceItemId": 12207486,
            "timestamp": 1746771311308,
            "amount": 1.50,
            "shortName": "W1",
            "type": "WASHING_MACHINE",
            "invoiceItemStatus": "NEW"
        },
        {
            "invoiceItemId": 12208363,
            "timestamp": 1746776029556,
            "amount": 1.50,
            "shortName": "T1",
            "type": "DRYER",
            "invoiceItemStatus": "NEW"
        },
        {
            "invoiceItemId": 12309512,
            "timestamp": 1747569873941,
            "amount": 1.50,
            "shortName": "W1",
            "type": "WASHING_MACHINE",
            "invoiceItemStatus": "NEW"
        }
    ],
    "amount": 10.5,
    "currency": "EUR",
    "cumulativeInvoicingDate": 1748736000000,
    "washingCycles": 4,
    "dryingCycles": 3,
    "selectedPaymentMethodThreshold": 20.0000
}

@pytest.fixture
def mock_config_entry():
    """Create a mock config entry."""
    # Use MagicMock instead of actual ConfigEntry
    config_entry = MagicMock()
    config_entry.domain = DOMAIN
    config_entry.data = {
        CONF_USERNAME: "test@example.com",
        CONF_PASSWORD: "password123"
    }
    config_entry.title = "test@example.com"
    config_entry.entry_id = "testentry"
    return config_entry


@pytest.fixture
async def mock_coordinator(hass, mock_config_entry):
    """Create a mock coordinator with mocked data."""
    coordinator = WeWashDataUpdateCoordinator(hass, mock_config_entry)
    coordinator.access_token = "test_access_token"
    coordinator.refresh_token = "test_refresh_token"
    
    # Mock the data with correct structure
    coordinator.data = {
        "user": USER_DATA_RESPONSE,
        "laundry_rooms": LAUNDRY_ROOMS_RESPONSE,
        "reservations": RESERVATIONS_RESPONSE,
        "invoices": UPCOMING_INVOICES_RESPONSE
    }
    
    return coordinator


@pytest.fixture
def mock_auth_response():
    """Mock authentication response."""
    with patch("aiohttp.ClientSession.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = MagicMock(return_value=AUTH_RESPONSE)
        
        # Mock cookies properly for authentication
        mock_cookies = MagicMock()
        mock_cookies.get.side_effect = lambda key: {
            "ww_access": "test_access_token", 
            "ww_refresh": "test_refresh_token"
        }.get(key)
        mock_response.cookies = mock_cookies
        
        mock_post.return_value.__aenter__.return_value = mock_response
        yield mock_post


@pytest.fixture
def mock_wewash_responses():
    """Mock all WeWash API responses."""
    with patch("aiohttp.ClientSession.get") as mock_get:
        
        def mock_response_handler(*args, **kwargs):
            """Create appropriate mock response based on URL."""
            url = args[0]
            
            mock_response = AsyncMock()
            mock_response.status = 200
            
            if "users/me" in url and "laundry-rooms" not in url and "reservations" not in url and "upcoming-invoices" not in url:
                mock_response.json.return_value = USER_DATA_RESPONSE
            elif "laundry-rooms" in url:
                mock_response.json.return_value = LAUNDRY_ROOMS_RESPONSE
            elif "reservations" in url:
                mock_response.json.return_value = RESERVATIONS_RESPONSE
            elif "upcoming-invoices" in url:
                mock_response.json.return_value = UPCOMING_INVOICES_RESPONSE
            else:
                # Default empty response
                mock_response.json.return_value = {}
            
            # Create a proper async context manager
            context_manager = AsyncMock()
            context_manager.__aenter__.return_value = mock_response
            context_manager.__aexit__.return_value = None
            
            return context_manager
        
        # Set up the mock to use our handler
        mock_get.side_effect = mock_response_handler
        
        yield mock_get

"""Constants for the We-Wash integration."""

DOMAIN = "wewash"

# API endpoints
AUTH_URL = "https://backend.we-wash.com/auth"
USER_URL = "https://backend.we-wash.com/v3/users/me"
LAUNDRY_ROOMS_URL = "https://backend.we-wash.com/v3/users/me/laundry-rooms"
RESERVATIONS_URL = "https://backend.we-wash.com/v3/users/me/reservations"
UPCOMING_INVOICES_URL = "https://backend.we-wash.com/v3/users/me/upcoming-invoices"
AUTH_REFRESH_URL = "https://backend.we-wash.com/auth/refresh"

# Update interval (5 minutes)
UPDATE_INTERVAL = 300

# Configuration
CONF_USERNAME = "username"
CONF_PASSWORD = "password"

# Icons
ICON_WASHER = "mdi:washing-machine"
ICON_DRYER = "mdi:tumble-dryer"
ICON_BALANCE = "mdi:cash"
ICON_RESERVATION = "mdi:calendar-clock"
ICON_INVOICE = "mdi:invoice"
ICON_COST = "mdi:currency-eur"
ICON_TIMER = "mdi:timer"
ICON_MACHINE = "mdi:washing-machine"

# Default device info
MANUFACTURER = "We-Wash"
MODEL = "Laundry System"

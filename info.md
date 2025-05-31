# We-Wash Integration

Monitor and control your We-Wash laundry machines directly from Home Assistant.

## Features

- 👕 Monitor available washers and dryers
- 💰 Track your account balance
- 🔔 Get notifications when machines are ready
- 🔄 Auto-updates every 5 minutes

## Entities

### Sensors
- Account balance (EUR)
- Available washers per laundry room
- Available dryers per laundry room

### Binary Sensors
- Reservation status indicators

## Setup

1. Add your We-Wash credentials in the configuration
2. The integration will automatically discover your laundry rooms
3. Entities will be created for all your available machines

{% if installed %}
## Thanks for installing!

Having issues? Please report them [here](https://github.com/philipp-cserny/wewash_hacs/issues).
{% endif %}

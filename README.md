# We-Wash Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

This is a Home Assistant custom component for We-Wash laundry systems. It allows you to monitor your laundry machines, reservations, and account balance directly in Home Assistant.

## Features

- Monitor available washers and dryers in your laundry rooms
- Track your We-Wash account balance
- Get notifications when your reserved machines are ready
- View upcoming invoice amounts and due dates
- Track washing and drying cycle counts
- Enhanced machine status display with running time
- Comprehensive laundry room information
- Automatic updates every 5 minutes

## Installation

1. Install via HACS:
   - Add this repository as a custom repository in HACS
   - Select "Integration" as the category
   - Click "Download"

2. Restart Home Assistant

3. Add the integration:
   - Go to Settings -> Devices & Services
   - Click "Add Integration"
   - Search for "We-Wash"
   - Follow the configuration steps

## Configuration

You'll need your We-Wash account credentials:
- Username (email)
- Password

## Entities Created

### Sensors

#### Balance and Invoicing
- Account balance (EUR)
- Upcoming invoice amount (EUR)
- Days until invoice due
- Washing cycles this month
- Drying cycles this month

#### Laundry Room Information
- Laundry room status (shows available machines)
- Available washers per laundry room
- Available dryers per laundry room
- Washing and drying costs per laundry room

#### Machine Status (Enhanced)
- Washing machine status with running time
- Dryer status with running time
- Machine online status and pricing

### Binary Sensors
- Reservation status (indicates when your reserved machine is ready)

## Dashboard

A sample Lovelace dashboard configuration is provided in the [wewash_lovelace_card.md](wewash_lovelace_card.md) file.

## Support

For issues and feature requests, please use the [GitHub issue tracker](https://github.com/philipp-cserny/wewash_hacs/issues).

## Disclaimer

This integration is not affiliated with We-Wash GmbH. Use at your own risk.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

# We-Wash Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub release](https://img.shields.io/github/v/release/Agent-CNY/wewash_hacs?include_prereleases&style=flat-square)](https://github.com/Agent-CNY/wewash_hacs/releases)
[![GitHub license](https://img.shields.io/github/license/Agent-CNY/wewash_hacs?style=flat-square)](LICENSE)
[![GitHub issues](https://img.shields.io/github/issues/Agent-CNY/wewash_hacs?style=flat-square)](https://github.com/Agent-CNY/wewash_hacs/issues)
[![GitHub stars](https://img.shields.io/github/stars/Agent-CNY/wewash_hacs?style=flat-square)](https://github.com/Agent-CNY/wewash_hacs/stargazers)
[![GitHub activity](https://img.shields.io/github/commit-activity/m/Agent-CNY/wewash_hacs?style=flat-square)](https://github.com/Agent-CNY/wewash_hacs/commits)
[![Maintenance](https://img.shields.io/maintenance/yes/2025?style=flat-square)](https://github.com/Agent-CNY/wewash_hacs/commits)
[![GitHub last commit](https://img.shields.io/github/last-commit/Agent-CNY/wewash_hacs?style=flat-square)](https://github.com/Agent-CNY/wewash_hacs/commits)

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

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Agent-CNY&repository=wewash_hacs&category=integration)

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

For issues and feature requests, please use the [GitHub issue tracker](https://github.com/Agent-CNY/wewash_hacs/issues).

## Disclaimer

This integration is not affiliated with We-Wash GmbH. Use at your own risk.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

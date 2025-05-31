# We-Wash for Home Assistant

<p align="center">
  <img src="https://raw.githubusercontent.com/Agent-CNY/wewash_hacs/main/custom_components/wewash/icons/logo.png" alt="We-Wash Logo" width="200"/>
</p>

<p align="center">
  <a href="https://github.com/hacs/integration"><img src="https://img.shields.io/badge/HACS-Custom-41BDF5.svg" alt="HACS Custom"></a>
  <a href="https://github.com/Agent-CNY/wewash_hacs/releases"><img src="https://img.shields.io/github/v/release/Agent-CNY/wewash_hacs?include_prereleases&style=flat-square" alt="Releases"></a>
  <a href="LICENSE"><img src="https://img.shields.io/github/license/Agent-CNY/wewash_hacs?style=flat-square" alt="License"></a>
  <a href="https://github.com/Agent-CNY/wewash_hacs/issues"><img src="https://img.shields.io/github/issues/Agent-CNY/wewash_hacs?style=flat-square" alt="Issues"></a>
  <br>
  <a href="https://github.com/Agent-CNY/wewash_hacs/stargazers"><img src="https://img.shields.io/github/stars/Agent-CNY/wewash_hacs?style=flat-square" alt="Stars"></a>
  <a href="https://github.com/Agent-CNY/wewash_hacs/commits"><img src="https://img.shields.io/maintenance/yes/2025?style=flat-square" alt="Maintenance"></a>
  <a href="https://github.com/Agent-CNY/wewash_hacs/commits"><img src="https://img.shields.io/github/last-commit/Agent-CNY/wewash_hacs?style=flat-square" alt="Last Commit"></a>
</p>

Seamlessly integrate your We-Wash laundry system with Home Assistant. Monitor machine availability, track your usage, get notified when your laundry is ready, and stay on top of your upcoming invoices.

## ✨ Features

- **Real-time Machine Status** - Know which washers and dryers are available, running, or reserved
- **Smart Notifications** - Get alerts when your laundry is ready or when machines become available
- **Financial Tracking** - Monitor your account balance and view upcoming invoices with payment due dates
- **Usage Statistics** - Track your washing and drying cycle counts
- **Enhanced Display**:
  - User-friendly timestamps for reservations
  - Remaining time indicators for active cycles
  - Clear machine status with human-readable values
- **Comprehensive Laundry Room Info** - View all details about your laundry facilities
- **Automatic Updates** - Stay current with regular data refreshes

## 📋 Quick Start Guide

### Installation

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Agent-CNY&repository=wewash_hacs&category=integration)

1. **HACS Installation:**
   - Add this repository as a custom repository in HACS
   - Select "Integration" as the category
   - Click "Download"

2. **Restart Home Assistant**

3. **Setup the Integration:**
   - Go to Settings → Devices & Services
   - Click "Add Integration" and search for "We-Wash"
   - Enter your We-Wash account credentials (email and password)

### Dashboard Example

<p align="center">
  <img src="https://raw.githubusercontent.com/Agent-CNY/wewash_hacs/main/assets/dashboard_example.png" alt="Dashboard Example" width="600"/>
</p>

A sample Lovelace dashboard configuration is provided in [wewash_lovelace_card.md](wewash_lovelace_card.md).

## 🔍 Entities & Attributes

The integration creates several entities to give you comprehensive information about your We-Wash setup:

### 1. Machine Entities

**Washer and Dryer Sensors** show the current status along with detailed information:

- **Status**: available, running, reserved, offline
- **Cost Information**: Price per cycle and currency
- **Reservation Details**: ID and queue position (if applicable)

### 2. Laundry Room Entity

Provides overall information about your laundry facility:

- Available machines count
- Facility name and address
- Any service notes or alerts

### 3. Next Invoice Entity

Keeps track of your billing information:

- Total amount due
- Payment due date with status ("Due today", "Due tomorrow", "Due in X days")
- Usage statistics (washing and drying cycles)
- Payment threshold information

## 🔧 Advanced Configuration

### Automation Examples

**Get Notified When Your Laundry is Done:**

```yaml
automation:
  - alias: "Laundry Machine Finished"
    trigger:
      - platform: state
        entity_id: sensor.washing_machine_w1
        from: "running"
        to: "available"
    action:
      - service: notify.mobile_app
        data:
          title: "Laundry Ready!"
          message: "Your washing is complete. Time to move it to the dryer!"
```

**Monitor Available Machines:**

```yaml
automation:
  - alias: "Dryer Available Notification"
    trigger:
      - platform: state
        entity_id: sensor.dryer_t1
        to: "available"
    condition:
      - condition: state
        entity_id: input_boolean.want_dryer_notification
        state: "on"
    action:
      - service: notify.mobile_app
        data:
          title: "Dryer Available"
          message: "A dryer is now available in your laundry room!"
```

## 🆕 Recent Updates (June 2025)

- **Enhanced Timestamp Formatting**: All timestamps now display in user-friendly format
- **Remaining Time Calculation**: Active reservations show minutes remaining until completion
- **Improved Invoice Entity**: Better organization of payment information with human-readable status messages
- **UI Optimizations**: Enhanced entity attributes for better dashboard display

## 🔍 Troubleshooting

If you're experiencing issues:

1. **Enable Debug Logging**:
   ```yaml
   logger:
     logs:
       custom_components.wewash: debug
   ```

2. **Data Refresh**: The integration updates every 5 minutes by default. You can manually refresh from the Devices & Services page.

3. **Missing Entities?** Try restarting the integration or check your We-Wash account for any changes to your laundry room setup.

4. **API Connection Issues**: Verify your We-Wash credentials and ensure you have an active internet connection.

## 📝 Support and Contributions

- **Issue Reporting**: [GitHub Issue Tracker](https://github.com/Agent-CNY/wewash_hacs/issues)
- **Feature Requests**: Feel free to suggest enhancements through issues
- **Pull Requests**: Contributions are welcome!

## ⚠️ Disclaimer

This integration is not affiliated with or endorsed by We-Wash GmbH. It's a community-developed project to enhance the We-Wash experience for Home Assistant users.

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

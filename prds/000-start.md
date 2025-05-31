# We-Wash Home Assistant Integration PRD

## Overview
This document outlines the requirements for a Home Assistant integration that connects to We-Wash's laundry management system, allowing users to monitor and control their laundry appliances through Home Assistant.

## Problem Statement
Users of We-Wash laundry systems currently need to use a separate app to check appliance availability and make reservations. Integration with Home Assistant would provide a more streamlined experience and enable automation possibilities.

## User Stories

### Authentication
- As a user, I want to securely authenticate with my We-Wash credentials  
- As a user, I want my login session to persist until logout  
- As a user, I want to be notified when my authentication expires  

### Appliance Discovery and Status
- As a user, I want to see all appliances (washers/dryers) in each washroom  
- As a user, I want to know the current status of each appliance:  
  - Available  
  - In Use
  - Out of Order  
- As a user, I want to see my reservation queue position
- As a user, I want to see pricing information for each appliance  

### Reservations
- As a user, I want to reserve an available appliance 
- As a user, I want to cancel my existing reservations  
- As a user, I want to receive notifications when:  
  - My reservation is about to start  
  - My reserved machine becomes available  
  - My laundry cycle is complete  

## Integration Features
- As a user, I want the appliance data to update automatically every 5 minutes  
- As a user, I want to trigger a manual refresh of appliance status  
- As a user, I want appliances to appear as entities in Home Assistant  
- As a user, I want to see my current balance and payment status  

## Technical Requirements

### API Integration
- Reverse engineer We-Wash web app API endpoints for:  
  - Authentication  
  - Location/washroom discovery  
  - Appliance status  
  - Reservation management  
- Implement proper error handling and rate limiting  
- Handle API versioning and changes gracefully  

### Home Assistant Integration
- Create custom entities for:  
  - Washers  
  - Dryers  
  - Washrooms  
- Implement config flow for setup  
- Support HACS installation  
- Follow HA integration best practices  

### Security
- Secure storage of credentials  
- Token-based authentication  
- Compliance with We-Wash terms of service  

## Constraints
- API rate limits must be respected  
- Integration must handle network issues gracefully  
- Must maintain compatibility with future We-Wash API changes  

## Future Considerations
- Support for multiple locations/buildings  
- Integration with HA calendars for reservations  
- Automated workflows (e.g., notifications when preferred machines become available)  
- Payment integration if API supports it  

## Success Metrics
- Successful installation rate  
- API reliability and uptime  
- User engagement metrics  
- Error rates and types  
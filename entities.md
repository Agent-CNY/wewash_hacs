# WeWash Entities and Attributes

## 1. Washer Entity
**Entity ID:** `washer_w1`

| Attribute | Description | JSON Path |
|-----------|-------------|-----------|
| status | Current status of washer (available, running, reserved) | Determined from both endpoints:<br>- If in reservations with "ACTIVE" status: running<br>- If in reservations with "READY" status: reserved<br>- If not in reservations and availableWashers > 0: available<br>- If not in reservations and availableWashers = 0: reserved by someone else |
| is_enabled | Whether washer is enabled for use | laundry-rooms.selectedLaundryRooms[0].serviceAvailability.washing |
| is_online | Whether washer is online | From reservation where applianceShortName = "W1": items[x].applianceOnline |
| price | Cost to use washer | laundry-rooms.selectedLaundryRooms[0].washingCost.costOnActive |
| currency | Currency for price | laundry-rooms.selectedLaundryRooms[0].washingCost.currencyCode |
| reservation_id | ID of current reservation (if any) | From reservation where applianceShortName = "W1": items[x].reservationId |
| queue_position | Position in queue (if any) | From reservation where applianceShortName = "W1": items[x].queuePosition |
| timestamp | Human-readable time of last status change | Formatted from items[x].statusChangedTimestamp |
| timestamp_raw | Raw Unix timestamp (ms) of last status change | From reservation where applianceShortName = "W1": items[x].statusChangedTimestamp |
| timeout | Human-readable time when reservation will end | Formatted from items[x].timeoutTimestamp |
| timeout_raw | Raw Unix timestamp (ms) when reservation times out | From reservation where applianceShortName = "W1": items[x].timeoutTimestamp |
| remaining_minutes | Minutes remaining until the reservation ends | Calculated from current time and timeout timestamp |

## 2. Dryer Entity
**Entity ID:** `dryer_t1`

| Attribute | Description | JSON Path |
|-----------|-------------|-----------|
| status | Current status of dryer (available, running, reserved) | Determined from both endpoints:<br>- If in reservations with "ACTIVE" status: running<br>- If in reservations with "READY" status: reserved<br>- If not in reservations and availableDryers > 0: available<br>- If not in reservations and availableDryers = 0: reserved by someone else |
| is_enabled | Whether dryer is enabled for use | laundry-rooms.selectedLaundryRooms[0].serviceAvailability.drying |
| is_online | Whether dryer is online | From reservation where applianceShortName = "T1": items[x].applianceOnline |
| price | Cost to use dryer | laundry-rooms.selectedLaundryRooms[0].dryingCost.costOnActive |
| currency | Currency for price | laundry-rooms.selectedLaundryRooms[0].dryingCost.currencyCode |
| reservation_id | ID of current reservation (if any) | From reservation where applianceShortName = "T1": items[x].reservationId |
| queue_position | Position in queue (if any) | From reservation where applianceShortName = "T1": items[x].queuePosition |
| timestamp | Human-readable time of last status change | Formatted from items[x].statusChangedTimestamp |
| timestamp_raw | Raw Unix timestamp (ms) of last status change | From reservation where applianceShortName = "T1": items[x].statusChangedTimestamp |
| timeout | Human-readable time when reservation will end | Formatted from items[x].timeoutTimestamp |
| timeout_raw | Raw Unix timestamp (ms) when reservation times out | From reservation where applianceShortName = "T1": items[x].timeoutTimestamp |
| remaining_minutes | Minutes remaining until the reservation ends | Calculated from current time and timeout timestamp |

## 3. Laundry Room Entity
**Entity ID:** `laundry_room`

| Attribute | Description | JSON Path |
|-----------|-------------|-----------|
| id | Laundry room ID | laundry-rooms.selectedLaundryRooms[0].id |
| name | Name of the laundry room | laundry-rooms.selectedLaundryRooms[0].name |
| address | Full address | Combined from laundry-rooms.selectedLaundryRooms[0].address.* |
| available_washers | Number of available washers | laundry-rooms.selectedLaundryRooms[0].serviceAvailability.availableWashers |
| available_dryers | Number of available dryers | laundry-rooms.selectedLaundryRooms[0].serviceAvailability.availableDryers |
| note | Any notes about the laundry room | laundry-rooms.selectedLaundryRooms[0].note |
| critical_note | Any critical notes/alerts | laundry-rooms.selectedLaundryRooms[0].criticalNote |
| last_update | Timestamp of last data update | laundry-rooms.selectedLaundryRooms[0].sendingTime |

## 4. Next Invoice Entity
**Entity ID:** `next_invoice`

| Attribute | Description | JSON Path |
|-----------|-------------|-----------|
| amount | Total amount of the next invoice | invoices.amount |
| currency | Currency for the invoice | invoices.currency |
| payment_threshold | Payment threshold amount | invoices.selectedPaymentMethodThreshold |
| usage_washing_cycles | Number of washing cycles | invoices.washingCycles |
| usage_drying_cycles | Number of drying cycles | invoices.dryingCycles |
| reservations_total | Total number of reservations | Count of invoices.reservations |
| reservations_washer | Number of washer reservations | Count of reservations with type="WASHING_MACHINE" |
| reservations_dryer | Number of dryer reservations | Count of reservations with type="DRYER" |
| due_date | User-friendly formatted due date | Formatted from invoices.cumulativeInvoicingDate |
| due_in_days | Number of days until the invoice is due | Calculated from current time and due date |
| payment_status | Human-readable payment status | "Due today", "Due tomorrow", or "Due in X days" |
| currency | Currency code | From any reservation: items[x].currency |
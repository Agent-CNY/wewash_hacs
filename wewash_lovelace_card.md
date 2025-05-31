# WeWash Lovelace Card Sample

This is a sample Lovelace card configuration for your WeWash integration with the new enhanced sensors.

```yaml
type: vertical-stack
cards:
  - type: entities
    title: WeWash Status
    entities:
      - entity: sensor.balance
        name: Account Balance
        icon: mdi:cash
      - entity: sensor.upcoming_invoice
        name: Next Invoice
        icon: mdi:invoice
      - entity: sensor.invoice_due
        name: Due In
        icon: mdi:calendar
      - entity: sensor.washing_cycles
        name: Washing Cycles
        icon: mdi:counter
      - entity: sensor.drying_cycles
        name: Drying Cycles
        icon: mdi:counter
  - type: horizontal-stack
    cards:
      - type: custom:mushroom-template-card
        primary: Washing Machine
        secondary: >-
          {{ states('sensor.washing_machine_w1') }}
          {% if 'Running' in states('sensor.washing_machine_w1') %}
            {% set mins = states.sensor.washing_machine_w1.attributes.elapsed_minutes %}
            ({{ mins }} min)
          {% endif %}
        icon: mdi:washing-machine
        icon_color: >-
          {% if 'Running' in states('sensor.washing_machine_w1') %}
            blue
          {% elif 'Available' in states('sensor.washing_machine_w1') %}
            green
          {% elif 'Expired' in states('sensor.washing_machine_w1') %}
            orange
          {% else %}
            grey
          {% endif %}
      - type: custom:mushroom-template-card
        primary: Dryer
        secondary: >-
          {{ states('sensor.dryer_t1') }}
          {% if 'Running' in states('sensor.dryer_t1') %}
            {% set mins = states.sensor.dryer_t1.attributes.elapsed_minutes %}
            ({{ mins }} min)
          {% endif %}
        icon: mdi:tumble-dryer
        icon_color: >-
          {% if 'Running' in states('sensor.dryer_t1') %}
            blue
          {% elif 'Available' in states('sensor.dryer_t1') %}
            green
          {% elif 'Expired' in states('sensor.dryer_t1') %}
            orange
          {% else %}
            grey
          {% endif %}
  - type: entities
    title: Laundry Room Details
    entities:
      - entity: sensor.laundry_room
        name: Status
      - type: attribute
        entity: sensor.laundry_room
        attribute: washing_cost
        name: Washing Cost
        icon: mdi:currency-eur
      - type: attribute
        entity: sensor.laundry_room
        attribute: drying_cost  
        name: Drying Cost
        icon: mdi:currency-eur
      - type: attribute
        entity: sensor.laundry_room
        attribute: name
        name: Room Name
      - type: attribute
        entity: sensor.laundry_room
        attribute: address
        name: Address
```

## Installation

1. Install the [Mushroom Cards](https://github.com/piitaya/lovelace-mushroom) custom components from HACS
2. Copy the above YAML to a new dashboard or add it to an existing one
3. Adjust entity names if needed based on your specific installation

## Features

This card provides:
- Account balance and upcoming invoice information
- Days until next invoice is due
- Washing and drying cycle counts for the month
- Status of machines with color indicators
- Running time display for active machines
- Detailed laundry room information

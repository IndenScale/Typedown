# Entity: Standard Cabinet

> 标准 42U 机柜定义（PDU 和规格，机柜定义在 deployment_plan.td 中）。

## 类型定义

```entity EquipmentType:type-server
category: "server"
vendor: "Dell"
model: "PowerEdge R750"
```

```entity EquipmentType:type-switch
category: "switch"
vendor: "Cisco"
model: "Nexus 93108TC-FX"
```

```entity EquipmentType:type-pdu
category: "pdu"
vendor: "APC"
model: "APDU9959"
```

## 机柜规格

```entity CabinetSpec:spec-42u-standard
total_units: 42
max_static_load_kg: 1500.0
max_dynamic_load_kg: 1200.0
power_capacity_kw: 12.0
pdu_count: 2
```

## PDU 设备

```entity PDU:pdu-left
asset_id: "PDU-0001"
name: "Left Side PDU"
equipment_type: [[type-pdu]]
rack_units: 0
mounting_depth: 0
weight: 5.0
power:
  rated_power: 7200.0
  typical_power: 5000.0
  max_power: 7200.0
  voltage: "AC220"
  redundancy: "none"
pdu_type: "vertical"
phases: 1
input_connector: "iec_60309"
input_current_a: 32.0
input_voltage_v: 220.0
c13_outlets: 18
c19_outlets: 6
current_load_a: 0
network_ports: []
power_ports:
  - port_id: "input"
    port_type: "power_c19"
    status: "occupied"
management_ports: []
```

```entity PDU:pdu-right
asset_id: "PDU-0002"
name: "Right Side PDU"
equipment_type: [[type-pdu]]
rack_units: 0
mounting_depth: 0
weight: 5.0
power:
  rated_power: 7200.0
  typical_power: 5000.0
  max_power: 7200.0
  voltage: "AC220"
  redundancy: "none"
pdu_type: "vertical"
phases: 1
input_connector: "iec_60309"
input_current_a: 32.0
input_voltage_v: 220.0
c13_outlets: 18
c19_outlets: 6
current_load_a: 0
network_ports: []
power_ports:
  - port_id: "input"
    port_type: "power_c19"
    status: "occupied"
management_ports: []
```

> 注：机柜实体 `cabinet-a01-01` 在 deployment_plan.td 中定义，包含完整的设备和槽位信息。

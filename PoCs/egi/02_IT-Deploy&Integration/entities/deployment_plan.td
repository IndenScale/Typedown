# Entity: Deployment Plan

> 具体的 IT 设备上架方案示例。

## ToR 交换机

```entity NetworkSwitch:switch-tor-01
asset_id: "SW-1001"
name: "ToR-Switch-A01-01"
equipment_type:
    category: "switch"
    vendor: "Cisco"
    model: "Nexus 93108TC-FX"
rack_units: 1
mounting_depth: 600.0
weight: 8.5
power:
  rated_power: 450.0
  typical_power: 300.0
  max_power: 450.0
  voltage: "AC220"
  redundancy: "n+1"
switch_type: "tor"
layer: 2
total_ports: 48
uplink_ports: 6
network_ports:
  - port_id: "eth1/1"
    port_type: "rj45"
    max_speed_gbps: 10.0
  - port_id: "eth1/2"
    port_type: "rj45"
    max_speed_gbps: 10.0
  # ... 省略中间端口
  - port_id: "eth1/48"
    port_type: "rj45"
    max_speed_gbps: 10.0
  - port_id: "eth1/49"
    port_type: "qsfp28"
    max_speed_gbps: 100.0
  - port_id: "eth1/50"
    port_type: "qsfp28"
    max_speed_gbps: 100.0
  - port_id: "eth1/51"
    port_type: "qsfp28"
    max_speed_gbps: 100.0
  - port_id: "eth1/52"
    port_type: "qsfp28"
    max_speed_gbps: 100.0
  - port_id: "eth1/53"
    port_type: "qsfp28"
    max_speed_gbps: 100.0
  - port_id: "eth1/54"
    port_type: "qsfp28"
    max_speed_gbps: 100.0
power_ports:
  - port_id: "psu0"
    port_type: "power_c14"
  - port_id: "psu1"
    port_type: "power_c14"
management_ports:
  - port_id: "mgmt0"
    port_type: "rj45"
deployed_in: [[cabinet-a01-01]]
start_u: 42
```

## 计算服务器

```entity Server:server-compute-01
asset_id: "SRV-2001"
name: "Compute-Node-01"
equipment_type:
    category: "server"
    vendor: "Dell"
    model: "PowerEdge R750"
rack_units: 2
mounting_depth: 800.0
weight: 28.5
power:
  rated_power: 1200.0
  typical_power: 800.0
  max_power: 1200.0
  voltage: "AC220"
  redundancy: "n+1"
cpu_model: "Intel Xeon Gold 6348"
cpu_cores: 28
cpu_count: 2
memory_total_gb: 512
storage_type: "nvme"
storage_capacity_gb: 3840
network_ports:
  - port_id: "eth0"
    port_type: "rj45"
    max_speed_gbps: 10.0
  - port_id: "eth1"
    port_type: "rj45"
    max_speed_gbps: 10.0
  - port_id: "eth2"
    port_type: "rj45"
    max_speed_gbps: 10.0
  - port_id: "eth3"
    port_type: "rj45"
    max_speed_gbps: 10.0
power_ports:
  - port_id: "psu0"
    port_type: "power_c14"
  - port_id: "psu1"
    port_type: "power_c14"
management_ports:
  - port_id: "idrac"
    port_type: "rj45"
deployed_in: [[cabinet-a01-01]]
start_u: 40
```

```entity Server:server-compute-02
asset_id: "SRV-2002"
name: "Compute-Node-02"
equipment_type:
    category: "server"
    vendor: "Dell"
    model: "PowerEdge R750"
rack_units: 2
mounting_depth: 800.0
weight: 28.5
power:
  rated_power: 1200.0
  typical_power: 800.0
  max_power: 1200.0
  voltage: "AC220"
  redundancy: "n+1"
cpu_model: "Intel Xeon Gold 6348"
cpu_cores: 28
cpu_count: 2
memory_total_gb: 512
storage_type: "nvme"
storage_capacity_gb: 3840
network_ports:
  - port_id: "eth0"
    port_type: "rj45"
    max_speed_gbps: 10.0
  - port_id: "eth1"
    port_type: "rj45"
    max_speed_gbps: 10.0
  - port_id: "eth2"
    port_type: "rj45"
    max_speed_gbps: 10.0
  - port_id: "eth3"
    port_type: "rj45"
    max_speed_gbps: 10.0
power_ports:
  - port_id: "psu0"
    port_type: "power_c14"
  - port_id: "psu1"
    port_type: "power_c14"
management_ports:
  - port_id: "idrac"
    port_type: "rj45"
deployed_in: [[cabinet-a01-01]]
start_u: 38
```

## 线缆类型

```entity CableType:type-cat6a
category: "network"
type_name: "CAT6A Ethernet"
gauge: "23AWG"
max_length_m: 100.0
bandwidth_gbps: 10.0
```

```entity CableType:type-power-c13-c14
category: "power"
type_name: "C13-C14 Power Cord"
gauge: "14AWG"
max_length_m: 3.0
```

## 网线连接

```entity Cable:cab-server01-eth0
cable_id: "CAB-0001"
name: "Server01-Eth0 to ToR"
cable_type: [[type-cat6a]]
length_m: 1.5
endpoint_a:
  equipment: [[server-compute-01]]
  port_id: "eth0"
  connector:
    connector_type: "rj45"
    gender: "male"
endpoint_b:
  equipment: [[switch-tor-01]]
  port_id: "eth1/1"
  connector:
    connector_type: "rj45"
    gender: "male"
status: "planned"
```

```entity Cable:cab-server02-eth0
cable_id: "CAB-0002"
name: "Server02-Eth0 to ToR"
cable_type: [[type-cat6a]]
length_m: 1.5
endpoint_a:
  equipment: [[server-compute-02]]
  port_id: "eth0"
  connector:
    connector_type: "rj45"
    gender: "male"
endpoint_b:
  equipment: [[switch-tor-01]]
  port_id: "eth1/2"
  connector:
    connector_type: "rj45"
    gender: "male"
status: "planned"
```

## 电源连接

```entity Cable:cab-server01-psu0
cable_id: "PWR-0001"
name: "Server01-PSU0 Power"
cable_type: [[type-power-c13-c14]]
length_m: 1.0
endpoint_a:
  equipment: [[server-compute-01]]
  port_id: "psu0"
  connector:
    connector_type: "c13"
    gender: "female"
endpoint_b:
  equipment: [[pdu-left]]
  port_id: "outlet-1"
  connector:
    connector_type: "c14"
    gender: "male"
status: "planned"
```

```entity Cable:cab-server01-psu1
cable_id: "PWR-0002"
name: "Server01-PSU1 Power"
cable_type: [[type-power-c13-c14]]
length_m: 1.0
endpoint_a:
  equipment: [[server-compute-01]]
  port_id: "psu1"
  connector:
    connector_type: "c13"
    gender: "female"
endpoint_b:
  equipment: [[pdu-right]]
  port_id: "outlet-1"
  connector:
    connector_type: "c14"
    gender: "male"
status: "planned"
```

## 更新机柜部署（添加设备和槽位信息）

```entity Cabinet:cabinet-a01-01
cabinet_id: "A01-01"
name: "Row A01, Rack 01"
room: "DC-Room-A"
row: "A01"
position: 1
spec: [[spec-42u-standard]]
slots:
  - unit_number: 37
    status: "empty"
  - unit_number: 38
    status: "occupied"
    occupied_by: [[server-compute-02]]
  - unit_number: 39
    status: "occupied"
    occupied_by: [[server-compute-02]]
  - unit_number: 40
    status: "occupied"
    occupied_by: [[server-compute-01]]
  - unit_number: 41
    status: "occupied"
    occupied_by: [[server-compute-01]]
  - unit_number: 42
    status: "occupied"
    occupied_by: [[switch-tor-01]]
equipments:
  - [[switch-tor-01]]
  - [[server-compute-01]]
  - [[server-compute-02]]
pdus:
  - [[pdu-left]]
  - [[pdu-right]]
```

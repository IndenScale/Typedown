# 基础设施安装记录表 (Installation Manifest)

本文件记录了 2024-12-05 当天的安装施工详情。


## 1. 机柜落位

```entity Rack: rack_prod_alpha_01
room_code: "ROOM_SHOP_2"
code: "RACK-A-01"
type: "42U Standard"
location_grid: "Column-C3"
```

## 2. 设备上架

```entity NetworkDevice: dev_sw_core_01
rack_id: "rack_prod_alpha_01"
u_position: 40
u_height: 1
hostname: "CN-SUZ-SHOP2-SW01"
brand_model: "Cisco C9300-48P"
status: "Online"
```

```entity NetworkDevice: dev_edge_gw_01
rack_id: "rack_prod_alpha_01"
u_position: 38
u_height: 2
hostname: "CN-SUZ-SHOP2-EDGE01"
brand_model: "Dell 5200"
status: "Online"
```

## 3. 关键接线记录 (Cabling Matrix)

> **注意**: 机器人控制器必须使用屏蔽线 (STP)，以防电磁干扰。

```entity CablingRecord: cable_robot_01
source_device_id: "dev_sw_core_01"
source_port: "Gi1/0/1"
target_device_id: "ext_robot_ctrl_01" # 外部设备ID，暂未定义，逻辑上指向现场
target_port: "LAN1"
cable_type: "Cat6 STP"
installer_id: "emp_alpha_mem_001" # K
connected_at: "2024-12-05 14:30"
```

```entity CablingRecord: cable_camera_01
source_device_id: "dev_sw_core_01"
source_port: "Gi1/0/5"
target_device_id: "ext_camera_01"
target_port: "ETH"
cable_type: "Cat6 UTP"
installer_id: "emp_alpha_mem_001"
connected_at: "2024-12-05 15:15"
```

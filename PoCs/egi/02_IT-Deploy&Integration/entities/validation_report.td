# Entity: Validation Report

> IT 设备部署方案的约束验证报告。

## 验证 Spec 汇总

### 机柜部署验证

```spec:validate_cabinet_deployment
@target(type="Cabinet", scope="local")
def validate_cabinet_deployment(subject: Cabinet):
    """机柜部署验证"""
    # 基础字段检查
    assert subject.cabinet_id, "机柜 ID 不能为空"
    assert subject.room, "机房位置不能为空"
    assert len(subject.slots) > 0, "机柜必须有槽位定义"
    
    print(f"✅ 机柜 {subject.cabinet_id} 验证通过")
```

### 服务器部署验证

```spec:validate_server_deployment
@target(type="Server", scope="local")
def validate_server_deployment(subject: Server):
    """服务器部署验证"""
    assert subject.asset_id, "资产 ID 不能为空"
    assert subject.rack_units >= 1, "U 数必须大于等于 1"
    assert subject.power.rated_power > 0, "额定功率必须大于 0"
    
    print(f"✅ 服务器 {subject.asset_id} 验证通过")
```

### 线缆数量验证

```spec:validate_cabling
@target(type="Cable", scope="global")
def validate_cabling(subject):
    """全局线缆验证"""
    result = sql("SELECT COUNT(*) as count FROM Cable")
    total_cables = result[0]['count']
    
    print(f"📊 线缆统计: {total_cables} 条线缆")
    assert total_cables >= 4, f"演示需要至少 4 条线缆，当前只有 {total_cables} 条"
```

## 验证结果示例

运行 `typedown check` 后预期输出：

```
✅ 机柜 A01-01 验证通过
✅ 服务器 SRV-2001 验证通过
✅ 服务器 SRV-2002 验证通过
📊 线缆统计: 4 条线缆

───────────────────────────────────────
总体状态: ✅ 全部通过
```

## 机柜部署拓扑

```
机柜 A01-01 部署拓扑

 U42 ┌───────────────────────┐  ← ToR 交换机 (SW-1001)
     │  eth1/1  eth1/2       │
     │    │       │          │
     └────┼───────┼──────────┘
          │       │
 U41 ┌────┴───────┴──────────┐  ← 服务器 01 (SRV-2001) - 2U
     │  eth0    eth1         │
     │  psu0    psu1         │
 U40 │   │       │           │
     └───┼───────┼───────────┘
         │       │
 U39 ┌───┴───────┴───────────┐  ← 服务器 02 (SRV-2002) - 2U
     │  eth0    eth1         │
     │  psu0    psu1         │
 U38 │   │       │           │
     └───┼───────┼───────────┘
         │       │
 U37 ┌───┴───────┴───────────┐  ← 空槽位
     │                       │
     └───────────────────────┘
     ...
 U01 └───────────────────────┘

电源连接:
  PDU-Left  → Server01-PSU0, Server02-PSU0, Switch-PSU0
  PDU-Right → Server01-PSU1, Server02-PSU1, Switch-PSU1

网络连接:
  Switch-Uplink → Core Network
  Server01-Eth0 → Switch-Eth1/1
  Server02-Eth0 → Switch-Eth1/2
```

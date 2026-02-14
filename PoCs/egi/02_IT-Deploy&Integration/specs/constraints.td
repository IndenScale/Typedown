# Model: Constraints

> 全局约束定义：物理、电气、逻辑约束的跨模型验证。

## 机柜数量验证

```spec:cabinet_count_check
@target(type="Cabinet", scope="global")
def cabinet_count_check(subject):
    """验证至少有一个机柜"""
    result = sql("SELECT COUNT(*) as count FROM Cabinet")
    count = result[0]['count']
    assert count >= 1, f"至少需要 1 个机柜，当前只有 {count} 个"
```

## 设备数量验证

```spec:server_count_check
@target(type="Server", scope="global")
def server_count_check(subject):
    """验证服务器数量"""
    result = sql("SELECT COUNT(*) as count FROM Server")
    count = result[0]['count']
    print(f"📊 服务器统计: {count} 台")
    assert count >= 2, f"演示需要至少 2 台服务器，当前只有 {count} 台"
```

## PDU 数量验证

```spec:pdu_count_check
@target(type="PDU", scope="global")
def pdu_count_check(subject):
    """验证 PDU 配置"""
    result = sql("SELECT COUNT(*) as count FROM PDU")
    count = result[0]['count']
    assert count >= 2, f"冗余需要至少 2 个 PDU，当前只有 {count} 个"
```

## 线缆数量验证

```spec:cable_count_check
@target(type="Cable", scope="global")
def cable_count_check(subject):
    """验证线缆配置"""
    result = sql("SELECT COUNT(*) as count FROM Cable")
    count = result[0]['count']
    assert count >= 4, f"演示需要至少 4 条线缆，当前只有 {count} 条"
```

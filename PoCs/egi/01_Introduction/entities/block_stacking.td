# Entity: Block Stacking

> 方块堆叠碰撞检测示例。

## 基础方块定义

```entity Vector3:pos-block-a
x: 0.0
y: 0.0
z: 50.0
```

```entity Dimension:dim-block-a
length: 100.0
width: 100.0
height: 100.0
```

```entity Mass:mass-block-a
value: 78.5
```

```entity PhysicalObject:block-a
name: "Base Block A"
position: [[pos-block-a]]
dimension: [[dim-block-a]]
material: [[steel-q235]]
mass: [[mass-block-a]]
```

```entity Vector3:pos-block-b
x: 0.0
y: 0.0
z: 150.0
```

```entity Dimension:dim-block-b
length: 80.0
width: 80.0
height: 80.0
```

```entity Mass:mass-block-b
value: 40.2
```

```entity PhysicalObject:block-b
name: "Stacked Block B"
position: [[pos-block-b]]
dimension: [[dim-block-b]]
material: [[steel-q235]]
mass: [[mass-block-b]]
```

```entity Vector3:pos-block-c
x: 120.0
y: 0.0
z: 50.0
```

```entity Dimension:dim-block-c
length: 60.0
width: 60.0
height: 60.0
```

```entity Mass:mass-block-c
value: 16.96
```

```entity PhysicalObject:block-c
name: "Side Block C"
position: [[pos-block-c]]
dimension: [[dim-block-c]]
material: [[steel-q235]]
mass: [[mass-block-c]]
```

## 方块数量验证

```spec:block_count_check
@target(type="PhysicalObject", scope="global")
def block_count_check(subject):
    """验证方块数量"""
    result = sql("SELECT COUNT(*) as count FROM PhysicalObject")
    count = result[0]['count']
    assert count >= 3, f"至少需要 3 个方块用于堆叠演示，当前只有 {count} 个"
    print(f"✅ 方块数量检查通过: {count} 个方块")
```

## 边界框可视化

```
场景: 合法堆叠

     z
     ↑
     │    ┌────────┐ 190  ← Block B
     │    │   ●    │
     │    └────────┘ 110
     │         
     │    ┌────────────┐ 100  ← Block A
     │    │     ●      │
     │    └────────────┘ 0
     │         
     └──────────────────────→ x
        -50   0   50
```

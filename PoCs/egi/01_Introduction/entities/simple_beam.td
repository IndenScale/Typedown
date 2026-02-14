# Entity: Simple Beam

> 简支梁承重计算示例。

## 依赖实体（需先定义）

```entity Vector3:origin
x: 0.0
y: 0.0
z: 0.0
```

```entity Vector3:support-left-pos
x: -2500.0
y: 0.0
z: -150.0
```

```entity Vector3:support-right-pos
x: 2500.0
y: 0.0
z: -150.0
```

```entity Vector3:load-pos
x: 0.0
y: 0.0
z: 150.0
```

```entity Vector3:load-dir
x: 0.0
y: 0.0
z: -1.0
```

```entity Dimension:beam-dim
length: 5000.0
width: 200.0
height: 300.0
```

```entity Material:steel-q235
name: "Q235 Steel"
density: 7850
youngs_modulus: 200.0
yield_strength: 235.0
```

```entity Mass:beam-mass
value: 2355.0
```

```entity Support:support-left
position: [[support-left-pos]]
max_load: 20000.0
current_load: 0
```

```entity Support:support-right
position: [[support-right-pos]]
max_load: 20000.0
current_load: 0
```

```entity Load:center-load
force: 9810.0
position: [[load-pos]]
direction: [[load-dir]]
```

## 梁实体

```entity PhysicalObject:beam-main
name: "Main Support Beam"
position: [[origin]]
dimension: [[beam-dim]]
material: [[steel-q235]]
mass: [[beam-mass]]
supports:
  - [[support-left]]
  - [[support-right]]
applied_loads:
  - [[center-load]]
```

## 验证 Spec

```spec:beam_basic_check
@target(type="PhysicalObject", scope="local")
def beam_basic_check(subject: PhysicalObject):
    """验证梁基本信息"""
    assert subject.name, "梁名称不能为空"
    assert subject.position, "位置引用不能为空"
    assert subject.dimension, "尺寸引用不能为空"
    assert subject.mass, "质量引用不能为空"
    print(f"✅ 梁 {subject.name} 基本检查通过")
```

## 验证结果

| 检查项 | 计算值 | 限制 | 状态 |
|--------|--------|------|------|
| 梁自重 | 23,102 N | - | ✅ |
| 集中载荷 | 9,810 N | - | ✅ |
| 总载荷 | 32,912 N | - | ✅ |
| 单支撑反力 | 16,456 N | 20,000 N | ✅ |

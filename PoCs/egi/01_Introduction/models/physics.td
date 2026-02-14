# Model: Physics

> 基础物理约束建模，演示如何使用 Typedown 表达碰撞检测和承重计算。

## BoundingBox

轴对齐包围盒 (AABB)，用于快速碰撞检测。

```model:BoundingBox
class BoundingBox(BaseModel):
    center: Ref["Vector3"]
    dimension: Ref["Dimension"]
```

## Load

载荷定义（力或重量）。

```model:Load
class Load(BaseModel):
    force: float = Field(..., ge=0)  # N
    position: Ref["Vector3"]
    direction: Ref["Vector3"]  # 单位向量
```

## Support

支撑点定义，用于承重分析。

```model:Support
class Support(BaseModel):
    position: Ref["Vector3"]
    max_load: float = Field(..., gt=0)  # N
    current_load: float = Field(default=0)  # N
```

## PhysicalObject

物理实体基类。

```model:PhysicalObject
class PhysicalObject(BaseModel):
    name: str
    
    # 几何属性
    position: Ref["Vector3"]
    dimension: Ref["Dimension"]
    bbox: Optional[Ref["BoundingBox"]] = None
    
    # 物理属性
    material: Ref["Material"]
    mass: Ref["Mass"]
    
    # 支撑与载荷
    supports: List[Ref["Support"]] = Field(default_factory=list)
    applied_loads: List[Ref["Load"]] = Field(default_factory=list)
```

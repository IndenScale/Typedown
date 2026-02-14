# Model: Primitives

> 基础几何与物理类型定义，演示 Typedown 的基本数据建模能力。

## Vector3

三维空间向量，用于表示位置、尺寸、力等。

```model:Vector3
class Vector3(BaseModel):
    x: float = Field(..., ge=-10000, le=10000)
    y: float = Field(..., ge=-10000, le=10000)
    z: float = Field(..., ge=-10000, le=10000)
```

## Dimension

物体尺寸（长×宽×高）。

```model:Dimension
class Dimension(BaseModel):
    length: float = Field(..., gt=0)
    width: float = Field(..., gt=0)
    height: float = Field(..., gt=0)
    
    # volume 作为普通属性（非 computed_field）
    @property
    def volume(self) -> float:
        return self.length * self.width * self.height
```

## Material

基础材料属性。

```model:Material
class Material(BaseModel):
    name: str
    density: float = Field(..., gt=0)  # kg/m³
    youngs_modulus: float = Field(..., gt=0)  # GPa
    yield_strength: float = Field(..., gt=0)  # MPa
```

## Mass

质量属性。

```model:Mass
class Mass(BaseModel):
    value: float = Field(..., ge=0)  # kg
    
    @field_validator('value')
    @classmethod
    def check_reasonable_mass(cls, v: float) -> float:
        if v > 1000000:
            raise ValueError('质量不能超过 1000 吨')
        return v
```

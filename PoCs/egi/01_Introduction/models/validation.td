# Model: Validation

> 演示 Typedown 的三层验证体系。

## 验证层级说明

### 1. 字段级 (Field Level)

在字段定义处声明的约束，验证单个字段值。

```model:ExampleFieldValidation
class ExampleFieldValidation(BaseModel):
    # 基础类型约束
    identifier: int = Field(..., ge=1, le=999999)
    
    # 字符串约束
    code: str = Field(..., pattern=r'^[A-Z]{3}-\d{4}$', max_length=8, min_length=8)
    
    # 数值精度
    ratio: float = Field(..., ge=0, le=1, decimal_places=4)
    
    # 枚举约束
    status: str = Field(default="draft", pattern=r'^(draft|review|approved|archived)$')
    
    # 单位标注（通过 description）
    weight: float = Field(..., gt=0, description="单位: kg")
```

### 2. 模型级 (Model Level)

使用 `@field_validator` 和 `@model_validator` 定义实体内部一致性约束。

```model:Beam
class Beam(BaseModel):
    length: float = Field(..., gt=0)
    width: float = Field(..., gt=0)
    height: float = Field(..., gt=0)
    span: float = Field(..., gt=0)
    
    @model_validator(mode='after')
    def check_dimension_consistency(self):
        # 跨度不能超过长度
        if self.span > self.length:
            raise ValueError('跨度不能超过长度')
        
        # 高宽比检查
        aspect_ratio = self.height / self.width
        if aspect_ratio < 0.1 or aspect_ratio > 10:
            raise ValueError('高宽比必须在 0.1 到 10 之间')
        
        return self
```

### 3. 全局级 (Global Level)

跨实体引用验证，通过 `spec` 块实现（见下文）。

## 关键概念速查表

| 语法 | 说明 | 示例 |
|------|------|------|
| `Field(ge=x)` | 最小值 | `age: int = Field(..., ge=0)` |
| `Field(le=x)` | 最大值 | `score: float = Field(..., le=100)` |
| `Field(pattern=r'...')` | 正则匹配 | `code: str = Field(..., pattern=r'^[A-Z]+$')` |
| `str = Field(default="X")` | 枚举值替代 | `type: str = Field(default="A")` |
| `@property` | 计算属性 | `def volume(self) -> float` |
| `@field_validator` | 字段验证器 | 单字段校验 |
| `@model_validator` | 模型验证器 | 跨字段校验 |
| `Ref["Type"]` | 实体引用 | `owner: Ref["User"]` |
| `resolve(ref)` | 解析引用 | 获取引用实体的实际值 |

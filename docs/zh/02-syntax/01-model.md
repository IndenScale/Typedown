---
title: 模型定义
---

# 模型定义 (Model)

`model` 块用于定义数据的结构（Schema）。它是 Typedown 系统的基石，决定了实体（Entity）必须遵循的形状和约束。

## 语法签名

```markdown
```model:<ClassName>
class <ClassName>(BaseModel):
    ...
```
```

- **关键字**: `model`
- **标识符**: `<ClassName>` 必须与代码块内部定义的 Pydantic 类名完全一致。
- **内容**: 标准的 Python 代码，预加载了 `pydantic`, `typing`, `typedown.types` 等基础库。

## Pydantic 集成

Typedown 的模型层完全构建在 [Pydantic V2](https://docs.pydantic.dev/) 之上。你可以使用 Pydantic 的所有特性：

### 基础字段

```python
class User(BaseModel):
    name: str
    age: int = Field(..., ge=0, description="年龄必须非负")
    is_active: bool = True
    tags: List[str] = []
```

### 校验器 (Validators)

你可以使用 `@field_validator` 和 `@model_validator` 来定义更复杂的约束。

```python
class Order(BaseModel):
    item_id: str
    quantity: int
    price: float

    @field_validator('quantity')
    @classmethod
    def check_qty(cls, v: int) -> int:
        if v <= 0:
            raise ValueError('数量必须大于 0')
        return v
```

## 引用类型 (Reference)

Typedown 引入了特殊的泛型 `Reference[T]` 来处理实体间的链接。这是构建知识图谱的关键。

### 单一类型引用

```python
class Task(BaseModel):
    # assignee 必须指向一个 User 类型的实体
    assignee: Reference["User"]
```

### 多态引用 (Union Reference)

```python
class AccessLog(BaseModel):
    # subject 可以是 User 或 ServiceAccount
    subject: Reference["User", "ServiceAccount"]
```

### 自身引用 (Self Reference)

```python
class Node(BaseModel):
    parent: Optional[Reference["Node"]] = None
```

> **注意**: 在定义 Reference 时，如果目标类型尚未定义（或定义在后文），请使用字符串形式的 Forward Reference（如 `"User"`）。

## 作用域

- 在 `model` 块中定义的类会被注册到**当前文件**的符号表中。
- 如果需要在其他文件中复用该模型，该文件必须位于同一目录或子目录中（遵循词法作用域规则）。

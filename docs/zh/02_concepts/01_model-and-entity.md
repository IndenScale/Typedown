---
title: 模型与实体
---

# 模型与实体

Typedown 的数据层由两个核心概念构成：**Model（模型）**定义结构，**Entity（实体）**承载数据。

## 代码块签名规范

> **签名严格性要求**
>
> - **签名一致性**：代码块 ID 必须与内部定义的类名/函数名**完全匹配**
> - **字符限制**：ID 只能包含字母、数字、下划线 `_`、连字符 `-` 和点 `.`
> - **空格不敏感**：`model:User`、`model : User`、`model: User` 等价

## Model（模型）

`model` 代码块定义数据结构，是 Typedown 系统的基石。

### 语法

````typedown
```model:<ClassName>
class <ClassName>(BaseModel):
    ...
```
````

### Pydantic 集成

基于 [Pydantic V2](https://docs.pydantic.dev/)，支持所有原生特性：

```python
class User(BaseModel):
    name: str
    age: int = Field(..., ge=0, description="年龄必须非负")
    is_active: bool = True
    tags: List[str] = []
```

### 验证器

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

### 引用类型

使用 `Ref[T]` 建立实体间关系：

```python
class Task(BaseModel):
    # 单类型引用
    assignee: Ref["User"]
    
    # 多态引用
    subject: Ref["User", "ServiceAccount"]
    
    # 自引用
    parent: Optional[Ref["Node"]] = None
```

> **注意**：使用字符串形式的正向引用 `"User"` 避免循环依赖。

### 导入限制

`model` 块**禁止显式 import**，只能使用预加载的符号：
- 所有核心 `pydantic` 类
- 常用 `typing` 泛型
- Typedown 特有类型如 `Ref`

复杂逻辑应移至 `spec` 块。

---

## Entity（实体）

`entity` 代码块是实例化数据的主要方式，每个实体是知识图谱中的一个节点。

### 语法

````typedown
```entity <TypeName>: <SystemID>
<YAML Body>
```
````

- **TypeName**: 必须是当前上下文中定义的 Model 类名
- **SystemID**: 全局唯一标识符（主键）

### ID 规则

- **字符限制**：仅允许字母、数字、`_`、`-`、`.`
- **命名风格**：推荐使用 `slug-style`（如 `user-alice-v1`）
- **全局唯一**：整个项目范围内必须唯一

### 数据体（YAML）

采用**严格 YAML** 格式：

```yaml
name: 'Alice'
age: 30
role: 'admin'
```

### 引用语法糖

`List[Ref[T]]` 字段支持简化列表语法：

```yaml
# Model: friends: List[Ref[User]]
friends:
  - [[bob]]
  - [[charlie]]

# 内联写法
reviewers: [[[bob]], [[alice]]]
```

编译器自动将 `[[bob]]` 解析为 `Ref` 对象。

### 演进声明

使用 `former` 字段声明历史版本：

```yaml
former: [[user-alice-v0]]
name: 'Alice (Updated)'
```

详见 [演进语义](./evolution)。

---

## 作用域

- Model 类注册在**当前文件**的符号表中
- 如需在其他文件复用，目标文件必须位于同一目录或子目录（词法作用域规则）

# 语法指南

Typedown 将标准 Markdown 与可执行代码块结合，创造了一个“文学建模”环境。

## 1. 定义模型 (`model`)

使用 `model` 代码块来定义数据的结构 (Schema)。这使用的是标准的 **Python** 语法配合 **Pydantic**。

**核心特性：**
*   **自动导入：** `BaseModel`, `Field`, `List`, `Optional` 等已预先导入，无需手动 import。
*   **校验：** 你可以直接使用 Pydantic 的校验器。

````markdown
```model
class RPGCharacter(BaseModel):
    name: str
    level: int = Field(default=1, ge=1, le=100)
    tags: List[str] = []

    @validator('name')
    def name_must_be_capitalized(cls, v):
        if not v[0].isupper():
            raise ValueError("Name must start with a capital letter")
        return v
```
````

## 2. 实例化实体 (`entity`)

使用 `entity:<Type>` 代码块来创建数据实例。内容格式为 **YAML** (或 JSON)。

**核心特性：**
*   **类型绑定：** `<Type>` 必须匹配在 `model` 块中定义的类（或通过 `config` 导入的类）。
*   **ID：** 每个实体都需要一个唯一的 `id`。

````markdown
```entity:RPGCharacter
id: "hero_01"
name: "Aragorn"
level: 10
tags: ["ranger", "human"]
```
````

### 演进 (`former` / `derived_from`)
Typedown 支持追踪数据的演变过程。

*   `former`: 表示当前实体替代了之前的某个版本。
*   `derived_from`: 表示当前实体是由另一个实体变换而来的。

````markdown
```entity:RPGCharacter
id: "hero_01_v2"
former: "hero_01"  # 此块取代了 "hero_01"
name: "King Aragorn"
level: 50
```
````

## 3. 引用 (`[[...]]`)

你可以使用双中括号引用其他实体或其属性。

*   **语法：** `[[EntityID]]` 或 `[[EntityID.property]]`
*   **用途：** 可在普通 Markdown 文本中使用，创建超链接（LSP 支持跳转）。

> 角色 [[hero_01]] 是主要的主角。

## 4. 配置 (`config`)

使用 `config:python` 来设置环境、导入库或加载外部模型。

````markdown
```config:python
import math
from my_lib.models import Weapon
```
````

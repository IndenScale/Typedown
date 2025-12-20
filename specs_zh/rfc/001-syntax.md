# 基础语法

Typedown 使用标准的 Markdown 语法，并通过特定的代码块标识符扩展其功能。

## 1. 模型定义 (Model)

为了支持“渐进式形式化”，Typedown 允许直接在 Markdown 文档中定义数据模型。这通常用于初始阶段或测试阶段（Inception Phase）。

使用 `model` 标签。内容支持标准 Python 语法。你可以可选地提供一个 `id`。

````markdown
```model id=UserAccount
class User(BaseModel):
    name: str
    age: int = Field(..., ge=0)
```
````

### 特性

1. **多类定义**：你可以在单个 `model` 块中定义多个相关的类。
2. **自动导入**：为了减少模板代码，执行环境默认预加载以下符号：
   - **Pydantic**: `BaseModel`, `Field`, `validator`, `model_validator`
   - **Typing**: `List`, `Dict`, `Optional`, `Union`, `Any`
3. **全局注册**：带有 `id` 的模型块会被注册到全局符号表中，可供其他地方引用。

## 2. 实体实例化 (Entity)

使用 `entity:<ClassName>` 标签。你可以在 Header 中指定 `id`，也可以在 YAML 主体中指定。

````markdown
# 在 Header 中指定 ID

```entity:User id=alice
name: "Alice"
age: 30
```

# 在主体中指定 ID (YAML)

```entity:User
id: "bob"
name: "Bob"
age: 25
```
````

## 3. 上下文配置

Typedown 使用灵活的 **可执行配置脚本** 来管理上下文。

在 `config.td` 或任何文档中，使用 `config:python` 标签。该脚本在加载文档前执行，用于注入路径或导入模型。

````markdown
```config:python
import sys
from pathlib import Path

# 1. 注入自定义库路径
project_root = Path(__file__).parents[2]
sys.path.insert(0, str(project_root / "src"))

# 2. 显式导入模型
from my_app.models import Product, Order
```
````

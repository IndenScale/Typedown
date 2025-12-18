# 基础语法

Typedown 使用标准的 Markdown 语法，并通过特定的代码块标识符来扩展其功能。

## 1. 模型定义 (Model Definition)

为了支持“渐进式形式化”，Typedown 允许直接在 Markdown 文档中定义数据模型。这通常用于项目初期或测试阶段（Inception Phase）。

使用 `model` 标记代码块。该块内支持标准的 Python 语法，但经过了增强，预加载了常用的类型定义。

````markdown
```model
# 无需手动导入 BaseModel, Field, List 等，直接使用
class Address(BaseModel):
    city: str
    zip_code: str

class User(BaseModel):
    name: str
    age: int = Field(..., ge=0)
    role: str = "guest"
    address: Optional[Address] = None
```
````

### 特性

1. **多类定义**: 一个 `model` 块中可以定义多个相关的类。
2. **自动注入 (Auto-imports)**:为了减少样板代码，执行环境默认预加载了以下符号：
   - **Pydantic**: `BaseModel`, `Field`, `validator`, `model_validator`, `PrivateAttr`
   - **Typing**: `List`, `Dict`, `Optional`, `Union`, `Any`, `ClassVar`
   - **Enum**: `Enum`
3. **覆盖机制**: 此处定义的类会自动注册到当前文档的上下文中。如果名称与已有模型冲突，将覆盖旧定义。

## 2. 实体实例化 (Entity Instantiation)

使用 `entity:<ClassName>` 标记代码块，以声明一个该类的实例（数据）。

````markdown
# 这是一个 Entity 代码块，实例化了上面的 User 类

```entity:User
name: "Alice"
age: 30
role: "admin"
```
````

## 3. 上下文配置 (Context Configuration)

Typedown 使用更灵活的**可执行配置脚本**来管理上下文配置。

在 `config.td` 文件（或任意文档）中，使用 `config:python` 标记代码块。该脚本将在加载文档前执行，用于注入环境变量或导入模型。

````markdown
# config.td

```config:python
import sys
from pathlib import Path

# 1. 注入自定义库路径
project_root = Path(__file__).parents[2]
sys.path.insert(0, str(project_root / "src"))

# 2. 显式导入模型
# 这些模型将自动注册到当前目录及其子目录的上下文中
from my_app.models import Product, Order
```
````

### 自动注入策略 (Auto-injection Policy)

为了保持上下文的明确性和避免意外的命名冲突，Typedown **默认关闭**自动扫描和加载目录中 `.py` 文件的行为。

- **默认行为**: 只有在 `config:python` 中显式导入（`import`）或定义（`class ...`）的模型才会被加载。
- **未来扩展**: 可以通过 CLI 的全局配置文件（如 `pyproject.toml`）来通过白名单/黑名单模式开启特定目录的自动注入功能。

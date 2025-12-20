# 类上下文与导入 (Class Context & Imports)

Typedown 需要知道在 Markdown 文档中使用 `entity:ClassName` 时，这个 `ClassName` 对应哪个 Python Pydantic 模型。我们称之为 **类上下文 (Class Context)**。

为了保持构建的可预测性和性能，Typedown 采用 **显式导入** 机制，而非隐式的全目录扫描。

## 1. 全局预加载 (`typedown.toml`)

对于在整个项目中通用的模型，可以在 `typedown.toml` 清单文件的 `[linker]` 部分进行定义。

```toml
# typedown.toml
[linker]
# 这些符号会自动预加载到每一个文档的上下文中
prelude = [
    "models.schema.User",       # 单个类
    "models.constants",         # 整个模块
    "@lib.common.Workflow"      # 映射依赖中的符号
]
```

**优势**:

- **单一事实来源**: 集中管理依赖。
- **零模板代码**: 常用模型全局可用，无需在每个文档中重复导入。
- **高性能**: 编译器仅加载明确声明的模块。

## 2. 目录级配置 (`config.td`)

对于特定目录的需求，可以在 `config.td` 文件中使用 `config:python` 块。子目录会继承父目录 `config.td` 的上下文。

````markdown
# config.td

```config:python
# 1. 本地特化继承
from models.schema import Project as BaseProject

class Project(BaseProject):
    budget_code: str  # 仅针对此目录树的特化字段

# 2. 手动导入工具类
from my_utils import Helpers
```
````

## 3. 行内原型 (Inline Prototyping)

你可以使用 `model` 块直接在任何文档中定义模型。这非常适合快速原型设计。

````markdown
```model id=DraftModel
class Draft(BaseModel):
    note: str
```
````

---

## 最佳实践

1. **生产模型**: 保存在标准的 `.py` 文件中，并通过 `typedown.toml` 的 `prelude` 进行注册。
2. **上下文特化**: 使用 `config.td` 对基础模型进行覆盖或扩展，以适应特定的子项目。
3. **避免隐式扫描**: Typedown **不会** 自动扫描目录下的所有模型，以确保构建的可确定性并提升性能。

# 类上下文与导入 (Class Context & Imports)

Typedown 需要知道在当前 Markdown 文档中使用 `entity:ClassName` 时，这个 `ClassName` 对应哪个 Python Pydantic 模型。我们称之为**类上下文 (Class Context)**。

从 v0.1.0 开始，Typedown 引入了**可执行配置脚本 (Executable Configuration Scripts)**，通过在 `config.td` 中编写标准 Python 代码来灵活地定义上下文。

## 机制：可执行配置脚本

在任意目录的 `config.td` 文件中，你可以使用标记为 `config:python` 的代码块。Typedown 会在解析文档时执行这些代码块。

**核心特性：**

1. **自动发现 (Auto-discovery)**: 脚本中定义的、或者导入到当前命名空间的所有 `pydantic.BaseModel` 子类，都会自动注册到当前的类上下文中。
2. **级联上下文 (Cascading Context)**: 子目录会继承父目录脚本执行后的环境。这允许你在根目录定义通用模型，而在子目录进行特定的扩展。

## 最佳实践与模式

我们推荐以下三种使用模式，分别对应不同的开发阶段和需求。

### 1. 标准导入模式 (Standard Import) - ✅ 推荐

这是生产环境和长期维护项目的**最佳实践**。

- **做法**: 将模型定义在项目根目录的 `models/` 包中（标准的 `.py` 文件），然后在 `config.td` 中导入。
- **优势**: 享受完整的 IDE 支持（自动补全、重构、类型检查）；模型可被后端代码复用。

````markdown
# config.td

---

---

```config:python
import sys
from pathlib import Path

# 技巧：将项目根目录添加到 sys.path，以便可以导入 models
# 注意：Typedown 运行时通常会自动处理路径，但显式添加更稳健
sys.path.append(str(Path(__file__).parent / "../../"))

from models.user import User
from models.order import Order
```
````

`````markdown
### 2. 原型与临时模式 (Inline Prototyping)

适合快速验证想法，或者定义仅在当前目录有意义的临时结构。

- **做法**: 直接在 `config.td` 的 Python 代码块中定义 Pydantic 类。
- **优势**: 极其快速，无需创建额外的 `.py` 文件，保持思维连贯。

````markdown
# config.td

---

---

```config:python
from pydantic import BaseModel

# 直接在这里定义，立即就能在同级 Markdown 中使用
class MeetingNote(BaseModel):
    attendees: list[str]
    summary: str
```
````
`````

### 3. 继承与特化模式 (Inherit & Specialize)

这是 Python 配置脚本最强大的地方。你可以导入通用模型，然后根据当前目录的上下文需求进行修改。

- **场景**: 全局有一个通用的 `Project` 定义，但在 `finance/` 目录下，所有的项目都需要额外的预算字段。

````markdown
# use_cases/finance/config.td

---

---

```config:python
from common.models import Project as BaseProject

# 继承并扩展
class Project(BaseProject):
    budget_code: str
    is_audited: bool = False

# 在这个目录下，entity:Project 指向的是这里的子类
# 原有的 BaseProject 依然可用，但默认的 Project 符号被覆盖了
```
````

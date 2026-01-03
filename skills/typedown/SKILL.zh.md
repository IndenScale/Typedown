---
name: typedown-expert
description: 编写正确的 Typedown 代码的专家指南，专注于语法、最佳实践和常见陷阱。
---

# Typedown 专家版

本技能提供编写 **Typedown** 文件 (`.td`) 的专家级知识。Typedown 是一门共识建模语言（Consensus Modeling Language），它将 Pydantic 模型和 Pytest 逻辑嵌入到 Markdown 中。

## 核心语法规则

1. **文件结构**:

   - Typedown 文件是有效的 Markdown 文件。
   - 它们由自然语言文本和特殊的代码块交织而成。
   - **至关重要**：每个 `.td` 文件必须以一级标题（`# 标题`）和简短的文本描述开始。严禁以代码块作为文件开头。

2. **模型块 (`model:<Name>`)**:

   - 用于定义 Pydantic 模型。
   - **单代码块单模型**：不要在一个代码块中定义多个类。每个类都必须有自己独立的 `model:ClassName` 块。
   - **块内禁止导入**：除非是特殊的、非标准的库，否则不要在块内导入 `typing` 或 `pydantic`。环境已预加载标准类型。
   - **类名匹配**：定义的类名必须与块参数一致（例如，` ```model:User ` 块内必须定义 `class User`）。

3. **配置块 (`config`)**:

   - 用于全局配置和符号导出。
   - **位置限制**：严格限制在 `config.td` 文件中使用。严禁在普通的 `.td` 文件中使用 `config` 块。
   - **作用域**：`config` 中定义的所有符号会自动暴露给当前目录作用域，并被子目录继承。

4. **实体块与标识符**:

- 每个实体（Entity）必须拥有唯一身份。
- **语法**：`entity <Type>: <Identifier>`
- **标识符**：
  - 冒号后的字符串是 **System ID (L1)**。
  - **风格**：可以是简单的名称（`alice`）、Slug 风格（`user-alice-v1`）或 UUID（`550e84...`）。
- **内容**：符合 Pydantic 模型的有效 YAML。
  - **引用规则**：在实体块内引用其他实体时，**必须**使用 `[[标识符]]` (Wiki Link) 语法。

5. **引用 (`[[...]]`)**:

- Typedown 采用**三重解析策略 (L0 → L2)** 来处理引用。
- **优先级**：
  1. **L0 (哈希真理)**：`[[sha256:...]]`
     - 精确匹配内容哈希。不可变且绝对鲁棒。
  2. **L1 (精确 System ID)**：`[[<ID>]]`
     - 精确匹配定义的 System ID（例如 `[[user-alice-v1]]` 或 `[[alice]]`）。
     - **建议**：对于稳定的长期引用，始终使用 **Slug 风格**。
  3. **L2 (上下文句柄)**：`[[<Handle>]]`
     - 在当前作用域内通过**模糊查找**匹配 System ID。
     - 示例：如果在 `config.td` 中配置了，`[[alice]]` 可能会解析为 `user-alice-v1`。

6. **演进语义 (`former`)**:

当追踪对象随时间的变化时：

- **语法**：`former: [[<Identifier>]]`
- **规则**：`former` 字段**必须**使用引用语法 `[[]]`。
- **规则**：优先使用 **全局标识符 (L1)** 或 **哈希 (L0)** 作为 `former` 指针，以确保历史稳定性。严禁在历史记录中使用转瞬即逝的局部句柄 (L2)。

7. **校验块 (`spec`)**:

- 用于编写校验逻辑。
- 包含使用 `@target` 装饰的 Python 函数。

## Typedown 核心思维：共识建模

Typedown 不仅仅是一种语法，它是一套将松散的自然语言转化为严谨系统共识的严密方法。在使用 Typedown 时，请遵循以下五个认知步骤：

### 1. 实体发现 (Identification)

扫描非结构化文本或需求，识别关键实体。立即使用 `entity` 块对其实例化，锚定其存在。

- **动作**：创建带有 YAML 内容的 `entity:<Type>` 块。
- **目标**：将“用户 Alice”转化为数据。

### 2. 模型抽象 (Structure)

分析刚创建的 `entity` 块。将它们的共同特征抽象为 Pydantic 模型 (`model`)。

- **动作**：定义 `model:<Type>` 块。
- **上下文**：将共享模型放置在父目录的 `config.td` 或 `common.td` 中，如果跨文件使用，请务必 `export`。

### 3. 约束工程 (Logic)

分析这些实体的业务规则。通过三层防御体系来实施约束：

- **第一层 (字段类型)**：使用严格类型（如 `EmailStr`, `PositiveInt`）。
- **第二层 (校验器)**：使用 Pydantic 的 `@field_validator` 或 `@model_validator` 实现自足的一致性。
- **第三层 (Specs)**：使用带有 `@target` 标签的 `spec` 块进行跨实体或图级别的校验（例如，“特定用户必须存在于管理员组中”）。

### 4. 参考与学习 (Research)

如果你对高级语法不确定（例如如何使用 `former` 进行版本控制，或使用 `tags` 进行过滤）：

- **动作**：创建一个 `_reference` 目录（该目录已被 git-ignored）。
- **动作**：克隆官方仓库：`git clone https://github.com/IndenScale/typedown.git _reference/typedown`。
- **动作**：阅读参考仓库中的 `docs/` 或 `examples/` 以巩固知识。

### 5. 持续验证 (Feedback)

永远不要假设你的代码是正确的。始终通过编译器进行验证。

- **动作**：编辑后立即运行 `uvx typedown check <path>`。
- **动作**：将所有警告视为错误处理。

## 示例：建模循环

- 步骤 1：原始草稿
  “我们需要一台符合 ISO-27001 标准的服务器 'Alpha'。”

- 步骤 2：Typedown 建模

```model:ComplianceStandard
from enum import Enum
class ComplianceStandard(str, Enum):
    ISO_27001 = "ISO-27001"
    SOC2 = "SOC2"
```

```model:Server
from pydantic import model_validator
class Server(BaseModel):
    hostname: str
    compliance: List[ComplianceStandard]

    @model_validator(mode='after')
    def check_security(self):
        if ComplianceStandard.ISO_27001 in self.compliance:
            # 执行某些逻辑...
            pass
        return self
```

```entity Server: alpha-01
hostname: "alpha-01"
compliance:
  - "ISO-27001"
```

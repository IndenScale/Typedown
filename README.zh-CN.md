# <img src="assets/brand/logo.svg" height="30" alt="Typedown Logo" /> Typedown: 渐进式形式化 Markdown

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Linter: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

> [English](./README.md) | **简体中文**

**Typedown** 是一种用于**文学建模 (Literate Modeling)** 的共识建模语言 (CML)。它弥合了人类思维的流动性 (Markdown) 与工程严谨性 (Pydantic + Pytest) 之间的鸿沟。

> **"在你建立模型之前，你并不真正了解它。"**

---

## 三位一体 (The Trinity)

Typedown 将 Markdown 视为**代码化共识 (Consensus as Code, CaC)** 的一等公民，建立在三大支柱之上：

1.  **Markdown (界面)**：保留自然语言的表达力。它是人类和 AI 的栖息地。
2.  **Pydantic (结构)**：通过 `model` 块定义严谨的数据架构 (Schema)。
3.  **Pytest (逻辑)**：通过 `spec` 块强制执行业务规则和约束。

## 为什么选择 Typedown？

传统工具迫使我们在二者之间做出非此即彼的选择：

- **液体 (文本/Markdown)**：高流动性但零结构完整性。文档瞬间腐烂。
- **晶体 (代码/JSON/SQL)**：高完整性但零灵活性。人类难以浏览，AI 难以领会意图。

Typedown 是**活性软物质 (Active Soft Matter)**。它允许信息在同一文档中从松散的笔记“相变”为坚固、经过验证的模型。

## 核心特性

- **规模化 Markdown**：管理数千个相互关联的实体，具备 IDE 级的导航和验证。
- **渐进式形式化**：从草图开始，以验证过的系统结束。
- **三重解析**：通过 **Hash** (L0)、**Handle** (L1) 和 **Logical ID** (L2) 解析引用 `[[ref]]`。
- **演进语义**：使用 `former` (版本控制) 追踪时间以管理历史。
- **上下文感知作用域**：通过 `config.td` 和目录继承实现的隐式层级。
- **质量控制流水线**：从语法 (Lint) 到外部事实 (Test) 的四层校验。

## 快速开始

### 1. 定义模型 (Define a Model)

使用 Python 直接在 Markdown 中定义你的架构：

````markdown
```model:UserAccount
class UserAccount(BaseModel):
    name: str
    age: int = Field(..., ge=18)
    role: str = "member"
```
````

### 2. 声明实体 (Declare an Entity)

使用 YAML 实例化数据，支持智能引用拆箱：

````markdown
```entity UserAccount: alice
id: "iam/user/alice-v1"
name: "Alice"
age: 30
role: "admin"
```
````

### 3. 编写规范 (Write a Specification)

添加针对你的数据的业务逻辑：

````markdown
```spec id=check_roles
@target(type="UserAccount")
def validate_admin(subject: UserAccount):
    if subject.role == "admin":
        assert subject.age >= 25, "Admins must be senior"
```
````

## CLI 用法

`td` 工具是你开发循环中的得力助手：

- **`td lint`**：(L1) 检查 Markdown 语法和 YAML 格式。
- **`td check`**：(L2) 针对 Pydantic 模型验证实体。
- **`td validate`**：(L3) 检查引用并运行 `spec` 块（内部逻辑）。
- **`td test`**：(L4) 运行外部验证（Oracle/API）。
- **`td run <script>`**：执行 Front Matter 中定义的脚本。

## 安装

Typedown 专为 [uv](https://docs.astral.sh/uv/) 生态系统设计。我们推荐使用 `uv` 或 `uvx`，而不是标准的 pipe 安装。

### 🚀 即时运行 (推荐)

使用 `uvx` 即时执行 Typedown，无需管理环境：

```bash
uvx typedown --help
```

### 🛠️ 全局工具

将其安装为随处可用的独立工具：

```bash
uv tool install typedown
```

### 📦 项目依赖

将其添加到你的 Python 项目中：

```bash
uv add typedown
```

### ⌨️ VS Code 扩展

从以下位置安装 **Typedown Integration**：

- [VS Code Marketplace](https://marketplace.visualstudio.com/items?itemName=Typedown.typedown-vscode)
- [Open VSX](https://open-vsx.org/extension/Typedown/typedown-vscode)

## 文档

- **[GEMINI.md](GEMINI.md)**：AI Agent 指南（AI 开发从这里开始）。
- **[英文文档](docs/en/index.md)**：探索更多关于 Typedown 的信息。
- **[中文文档](docs/zh/index.md)**：核心中文文档。
- **[宣言](docs/en/manifesto.md)**：我们为何构建它。

---

## 许可证

MIT © [IndenScale](https://github.com/IndenScale)

# <picture><source media="(prefers-color-scheme: dark)" srcset="assets/brand/logo-dark.svg"><img alt="Typedown Logo" src="assets/brand/logo-light.svg" height="30"></picture> Typedown: 规模化 Markdown

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Linter: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

> [English](./README.md) | **简体中文**

**Typedown** 将你的**团队文档**进化为经过验证的知识库。它将代码的严谨性引入了自然语言的流动性之中。

> **"拒绝腐烂的文档。"**

## 问题：Markdown 难以规模化

Markdown 是“技术文档”的通用标准。但当你的文档仓库从 10 个文件增长到 10,000 个文件时，它就变成了一个“只写”的坟场：

- **链接断裂 (Links Break)**：移动文件需要 `grep` 和祈祷。
- **数据漂移 (Data Drifts)**："Status: Active" vs "status: active" vs "Status: ON"。
- **上下文衰减 (Context Decays)**：你脑海中的隐性模型没有在文本中强制执行。

## 方案：Typedown

Typedown 将你的**文档仓库**转化为一个**数据库**。它为 Markdown 添加了一个语义层，使其能够从松散的文本“相变”为结构化的数据。

关键在于，Typedown 不追求**无摩擦的写作体验**。 它是质量的守门人，会阻止任何违反团队既定约束的新内容进入。

### 1. 结构 (Schema)

使用 Python (Pydantic) 定义你的数据**应该**长什么样。

````markdown
<!-- 定义在代码块中 -->

```model:User
class User(BaseModel):
    name: str
    role: Literal["admin", "member"]
```
````

### 2. 空间 (Graph)

使用永不断裂的**坚固引用**。Typedown 通过 **内容哈希 (L0)**、**句柄 (L1)** 或 **全局 ID (L2)** 来解析链接。

```markdown
这份报告由 [[users/alice]] 撰写。
```

### 3. 逻辑 (Validation)

**在文档中强制执行不变性**。确保你的架构规则得到遵守。

````markdown
```spec
def check_admin_policy(user: User):
    if user.role == "admin":
        assert user.has_mfa, "管理员必须开启 MFA"
```
````

## 安装

Typedown 旨在主要在编辑器中使用，并由强大的命令行工具提供支持。

### 1. 编辑器集成 (推荐)

为了获得真正的“编写即验证”体验，请安装 VS Code 扩展：

- [**VS Code Marketplace**](https://marketplace.visualstudio.com/items?itemName=Typedown.typedown-vscode)
- [**Open VSX**](https://open-vsx.org/extension/Typedown/typedown-vscode)

### 2. 全局 CLI (用于 CI/CD)

```bash
# 即时运行 (无需安装)
uvx typedown check

# 全局安装
uv tool install typedown
```

### 3. 对于贡献者

如果你想修改编译器本身：

```bash
git clone https://github.com/IndenScale/typedown.git
```

## 核心哲学

Typedown 建立在**代码化共识 (Consensus as Code, CaC)** 的概念之上。

- **Markdown (界面)**：人类和 LLM 说自然语言。
- **Pydantic (结构)**：机器需要架构。
- **Pytest (律法)**：系统需要不变量。

我们将此称为**“文学建模 (Literate Modeling)”**——你无需离开文档去定义系统；文档**本身就是**系统。

## 文档

- **[快速开始](docs/zh/index.md)**：构建你的第一个模型。
- **[宣言](docs/en/manifesto.md)**：我们为何构建它。
- **[GEMINI.md](GEMINI.md)**：AI Agent 指南。

---

## 许可证

MIT © [IndenScale](https://github.com/IndenScale)

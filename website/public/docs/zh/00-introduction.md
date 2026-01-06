---
title: 项目介绍
---

# <picture><source media="(prefers-color-scheme: dark)" srcset="/logo-dark.svg"><img alt="Typedown Logo" src="/logo-light.svg" height="30"></picture> Typedown

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Linter: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

> [English](/en/docs/introduction) | **简体中文**

**Typedown** 是一个基于 Markdown 的结构化文档工具，旨在通过语义层将松散的文本转化为结构化的数据。

## 简介

Markdown 是技术文档的通用标准，但在大规模使用时面临链接断裂、数据格式不一致和上下文丢失等问题。

Typedown 通过为 Markdown 添加语义层来解决这些问题：

### 1. 结构 (Schema)

使用 Python (Pydantic) 定义数据结构。

```markdown
<!-- 定义在代码块中 -->

```model:User
class User(BaseModel):
    name: str
    role: Literal["admin", "member"]
```
```

### 2. 空间 (Graph)

使用 **内容哈希 (L0)**、**句柄 (L1)** 或 **全局 ID (L2)** 来解析链接。

```markdown
这份报告由 [[users/alice]] 撰写。
```

### 3. 逻辑 (Validation)

在文档中强制执行架构规则。

```markdown
```spec
def check_admin_policy(user: User):
    if user.role == "admin":
        assert user.has_mfa, "管理员必须开启 MFA"
```
```

## 安装

### 1. 编辑器集成 (推荐)

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

```bash
git clone https://github.com/IndenScale/typedown.git
```

## 文档

- **[快速开始](./quick-start)**：构建你的第一个模型。
- **[GEMINI.md](https://github.com/IndenScale/typedown/blob/main/GEMINI.md)**：AI Agent 指南。

---

## 许可证

MIT © [IndenScale](https://github.com/IndenScale)

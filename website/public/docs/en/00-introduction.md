---
title: Introduction
---

# <picture><source media="(prefers-color-scheme: dark)" srcset="/logo-dark.svg"><img alt="Typedown Logo" src="/logo-light.svg" height="30"></picture> Typedown

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Linter: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

> **English** | [简体中文](/zh/docs/introduction)

**Typedown** is a structured documentation tool based on Markdown, designed to transform loose text into structured data through a semantic layer.

## Introduction

Markdown is the universal standard for technical documentation, but it faces challenges like broken links, inconsistent data formats, and lost context when used at scale.

Typedown addresses these issues by adding a semantic layer to Markdown:

### 1. Structure (Schema)

Define data structures using Python (Pydantic).

```markdown
<!-- Defined in a code block -->

```model:User
class User(BaseModel):
    name: str
    role: Literal["admin", "member"]
```
```

### 2. Space (Graph)

Resolve links using **Content Hash (L0)**, **Handle (L1)**, or **Global ID (L2)**.

```markdown
This report was written by [[users/alice]].
```

### 3. Logic (Validation)

Enforce schema rules within documentation.

```markdown
```spec
def check_admin_policy(user: User):
    if user.role == "admin":
        assert user.has_mfa, "Admins must enable MFA"
```
```

## Installation

### 1. Editor Integration (Recommended)

- [**VS Code Marketplace**](https://marketplace.visualstudio.com/items?itemName=Typedown.typedown-vscode)
- [**Open VSX**](https://open-vsx.org/extension/Typedown/typedown-vscode)

### 2. Global CLI (For CI/CD)

```bash
# Run instantly (no installation required)
uvx typedown check

# Global installation
uv tool install typedown
```

### 3. For Contributors

```bash
git clone https://github.com/IndenScale/typedown.git
```

## Documentation

- **[Quick Start](./quick-start)**: Build your first model.
- **[GEMINI.md](https://github.com/IndenScale/typedown/blob/main/GEMINI.md)**: AI Agent Guide.

---

## License

MIT © [IndenScale](https://github.com/IndenScale)

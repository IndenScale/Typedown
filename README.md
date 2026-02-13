# <picture><source media="(prefers-color-scheme: dark)" srcset="assets/brand/logo-dark.svg"><img alt="Typedown Logo" src="assets/brand/logo-light.svg" height="30"></picture> Typedown

> **Progressive Formalization for Markdown**

[**🚀 Install VS Code Extension**](https://marketplace.visualstudio.com/items?itemName=Typedown.typedown-vscode) · [**Documentation**](https://typedown.io/docs) · [**Issues**](https://github.com/IndenScale/Typedown/issues)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/) [![PyPI](https://img.shields.io/pypi/v/typedown.svg)](https://pypi.org/project/typedown/)

> **English** | [简体中文](./README.zh-CN.md)

**Typedown** adds a semantic layer to Markdown, transforming it from loose text into a validated knowledge base.

> 💡 **Typedown files (`.td`) are designed to be experienced in an IDE.** Install the [VS Code Extension](https://marketplace.visualstudio.com/items?itemName=Typedown.typedown-vscode) to get real-time validation, intelligent navigation, and semantic highlighting.

## The Problem: Markdown Doesn't Scale

Markdown is the universal standard for technical documentation. But as your repository grows from 10 to 10,000 files, it becomes a "write-only" graveyard:

| Problem | Description | Typedown Solution |
| --- | --- | --- |
| **Schema Errors** | Inconsistent data: `Status: Active` vs `status: active`, missing required fields | **Model** - Define structure with Pydantic, validate at compile time |
| **Broken References** | Links break after moving files: `[[./old-path]]` points nowhere | **Reference** - Content-addressed links that auto-track entity changes |
| **Constraint Violations** | Rules are broken: admins without MFA, inventory over limit | **Spec** - Executable business rules for complex constraints |

## Core Concepts

### 1. Model (Schema)

Define data structures using Pydantic:

````typedown
```model:User
class User(BaseModel):
    name: str
    role: Literal["admin", "member"]
    mfa_enabled: bool = False
```
````

### 2. Entity (Data)

Instantiate data with strict YAML:

````typedown
```entity User: user-alice-v1
name: "Alice"
role: "admin"
mfa_enabled: true
```
````

### 3. Reference (Graph)

Link entities with `[[...]]` syntax:

```typedown
This task is assigned to [[user-alice-v1]].
```

Supports **ID references** (`[[entity-id]]`) and **content hash** (`[[sha256:...]]`).

### 4. Spec (Validation)

Three layers of validation:

````typedown
# 1. Field-level - @field_validator
class User(BaseModel):
    @field_validator('email')
    def check_email(cls, v):
        assert '@' in v, "Invalid email"
        return v

# 2. Model-level - @model_validator
class Order(BaseModel):
    @model_validator(mode='after')
    def check_dates(self):
        assert self.end > self.start, "End must be after start"
        return self

# 3. Global-level - spec
```spec:check_admin_mfa
@target(type="User", scope="local")
def check_admin_mfa(user: User):
    if user.role == "admin":
        assert user.mfa_enabled, f"Admin {user.name} must enable MFA"
```
````

## Quick Start

### Option 1: VS Code Extension (Recommended)

The best way to experience Typedown is through the IDE extension, which provides real-time validation, go-to-definition, and semantic highlighting.

1. **Install the [VS Code Extension](https://marketplace.visualstudio.com/items?itemName=Typedown.typedown-vscode)**
2. **Clone this repository** and open the `cookbook/01_getting_started/` folder in VS Code
3. Open any `.td` file to see Typedown in action

> ⚠️ **Note:** Typedown files (`.td`) appear as plain Markdown on GitHub. The full experience requires the VS Code extension.

### Option 2: CLI (For CI/CD)

For validating Typedown files in CI pipelines or automation:

```bash
# Using uv (recommended)
uv tool install typedown

# Using pip
pip install typedown

# Validate a project
typedown check .
```

## CLI Commands

```bash
# Validate the project
typedown check .

# Check with JSON output
typedown check --json

# Run specific validation
typedown check --target User
```

## Documentation

- [**Getting Started**](https://typedown.io/docs/getting-started/) - Build your first model
- [**Concepts**](https://typedown.io/docs/concepts/) - Model, Entity, Reference, Spec
- [**Guides**](https://typedown.io/docs/guides/) - Best practices and advanced topics

## Cookbook

The [`cookbook/`](./cookbook/) directory contains learning resources designed to be used with the VS Code extension:

- **`cookbook/01_getting_started/`** - Progressive tutorials (English & 中文)
- **`cookbook/02_use_cases/`** - Real-world examples (bid evaluation, PMO SaaS, ERP)

> 💡 **Tip:** Clone the repo and open it in VS Code with the Typedown extension installed for the best learning experience.

## License

MIT © [IndenScale](https://github.com/IndenScale)

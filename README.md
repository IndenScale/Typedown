# <picture><source media="(prefers-color-scheme: dark)" srcset="assets/brand/logo-dark.svg"><img alt="Typedown Logo" src="assets/brand/logo-light.svg" height="30"></picture> Typedown

> **Progressive Formalization for Markdown**

[**Website**](https://typedown.io) · [**Documentation**](https://typedown.io/docs) · [**Issues**](https://github.com/IndenScale/Typedown/issues)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![PyPI](https://img.shields.io/pypi/v/typedown.svg)](https://pypi.org/project/typedown/)

> **English** | [简体中文](./README.zh-CN.md)

**Typedown** adds a semantic layer to Markdown, transforming it from loose text into a validated knowledge base.

## The Problem: Markdown Doesn't Scale

Markdown is the universal standard for technical documentation. But as your repository grows from 10 to 10,000 files, it becomes a "write-only" graveyard:

| Problem | Description | Typedown Solution |
|---------|-------------|-------------------|
| **Schema Errors** | Inconsistent data: `Status: Active` vs `status: active`, missing required fields | **Model** - Define structure with Pydantic, validate at compile time |
| **Broken References** | Links break after moving files: `[[./old-path]]` points nowhere | **Reference** - Content-addressed links that auto-track entity changes |
| **Constraint Violations** | Rules are broken: admins without MFA, inventory over limit | **Spec** - Executable business rules for complex constraints |

## Core Concepts

### 1. Model (Schema)

Define data structures using Pydantic:

````markdown
```model:User
class User(BaseModel):
    name: str
    role: Literal["admin", "member"]
    mfa_enabled: bool = False
```
````

### 2. Entity (Data)

Instantiate data with strict YAML:

````markdown
```entity User: user-alice-v1
name: "Alice"
role: "admin"
mfa_enabled: true
```
````

### 3. Reference (Graph)

Link entities with `[[...]]` syntax:

```markdown
This task is assigned to [[user-alice-v1]].
```

Supports **ID references** (`[[entity-id]]`) and **content hash** (`[[sha256:...]]`).

### 4. Spec (Validation)

Three layers of validation:

````markdown
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

## Installation

### CLI (For CI/CD)

```bash
# Using uv (recommended)
uv tool install typedown

# Using pip
pip install typedown
```

### VS Code Extension

- [**VS Code Marketplace**](https://marketplace.visualstudio.com/items?itemName=Typedown.typedown-vscode)
- [**Open VSX**](https://open-vsx.org/extension/Typedown/typedown-vscode)

## Quick Start

Create a `hello.td` file (Typedown uses `.td` extension, fully compatible with Markdown):

````markdown
```model:User
class User(BaseModel):
    name: str
    email: str
```

```entity User: alice
name: "Alice"
email: "alice@example.com"
```
````

Run validation:

```bash
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

## License

MIT © [IndenScale](https://github.com/IndenScale)

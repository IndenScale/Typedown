# <img src="assets/brand/logo.svg" height="30" alt="Typedown Logo" /> Typedown: Markdown that scales

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Linter: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

> **English** | [简体中文](./README.zh-CN.md)

**Typedown** is a Consensus Modeling Language (CML) designed for **Literate Modeling**. It bridges the gap between the fluidity of human thought (Markdown) and the rigor of engineering (Pydantic + Pytest).

> **"You don't know it until you model it."**

---

## The Trinity

Typedown treats Markdown as a first-class language for **Consensus as Code (CaC)**, built on three pillars:

1. **Markdown (Interface)**: Retains natural language expressiveness. It's the habitat for humans and AI.
2. **Pydantic (Structure)**: Defines strict data schemas via `model` blocks.
3. **Pytest (Logic)**: Enforces business rules and constraints via `spec` blocks.

## Why Typedown?

Traditional tools force a binary choice:

- **Liquids (Text/Markdown)**: High fluidity but zero structural integrity. Documentation rots instantly.
- **Crystals (Code/JSON/SQL)**: High integrity but zero flexibility. Hard for humans to browse and for AI to grasp intent.

Typedown is **Active Soft Matter**. It allows information to "phase transition" from loose notes into solid, validated models within the same document.

## Core Features

- **Markdown that scales**: Manage thousands of interconnected entities with IDE-grade navigation and validation.
- **Progressive Formalization**: Start with a sketch, end with a verified system.
- **Triple Resolution**: Resolve references `[[ref]]` through **Hash** (L0), **Handle** (L1), and **Logical ID** (L2).
- **Evolution Semantics**: Track time using `former` (versioning) to manage history.
- **Context-Aware Scoping**: Implicit hierarchy via `config.td` and directory inheritance.
- **QC Pipeline**: Four-layered validation from syntax (Lint) to external facts (Test).

## Quick Start

### 1. Define a Model

Define your schema directly in Markdown using Python:

````markdown
```model:UserAccount
class UserAccount(BaseModel):
    name: str
    age: int = Field(..., ge=18)
    role: str = "member"
```
````

### 2. Declare an Entity

Instantiate data using YAML with smart reference unboxing:

````markdown
```entity UserAccount: alice
id: "iam/user/alice-v1"
name: "Alice"
age: 30
role: "admin"
```
````

### 3. Write a Specification

Add business logic that targets your data:

````markdown
```spec id=check_roles
@target(type="UserAccount")
def validate_admin(subject: UserAccount):
    if subject.role == "admin":
        assert subject.age >= 25, "Admins must be senior"
```
````

## CLI Usage

The `td` tool is your companion for the development loop:

- **`td lint`**: (L1) Check Markdown syntax and YAML formatting.
- **`td check`**: (L2) Validate entities against Pydantic models.
- **`td validate`**: (L3) Check references and run `spec` blocks (Internal Logic).
- **`td test`**: (L4) Run external verification (Oracles/APIs).
- **`td run <script>`**: Execute scripts defined in Front Matter.

## Installation

Typedown is designed for the [uv](https://docs.astral.sh/uv/) ecosystem. We recommend using `uv` or `uvx` over standard piping.

### 🚀 Instant Run (Recommended)

Use `uvx` to execute Typedown instantly without managing environments:

```bash
uvx typedown --help
```

### 🛠️ Global Tool

Install it as a standalone tool available everywhere:

```bash
uv tool install typedown
```

### 📦 Project Dependency

Add it to your Python project:

```bash
uv add typedown
```

### ⌨️ VS Code Extension

Install **Typedown Integration** from:

- [VS Code Marketplace](https://marketplace.visualstudio.com/items?itemName=Typedown.typedown-vscode)
- [Open VSX](https://open-vsx.org/extension/Typedown/typedown-vscode)

## Documentation

- **[GEMINI.md](GEMINI.md)**: AI Agent Guidance (Start here for AI dev).
- **[English Documentation](docs/en/index.md)**: Explore more about Typedown.
- **[Chinese Documentation](docs/zh/index.md)**: 核心中文文档.
- **[Manifesto](docs/en/manifesto.md)**: Why we built this.

---

## License

MIT © [IndenScale](https://github.com/IndenScale)

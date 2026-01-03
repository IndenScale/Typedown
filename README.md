# <picture><source media="(prefers-color-scheme: dark)" srcset="assets/brand/logo-dark.svg"><img alt="Typedown Logo" src="assets/brand/logo-light.svg" height="30"></picture> Typedown: Markdown that scales

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Linter: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

> **English** | [简体中文](./README.zh-CN.md)

**Typedown** evolves your **team's documentation** into a validated knowledge base. It brings the rigor of code to the fluidity of natural language.

> **"Docs that don't rot."**

## The Problem: Markdown Doesn't Scale

Markdown is the universal standard for **technical documentation**. But as your repository grows from 10 to 10,000 files, it becomes a "Write-Only" graveyard:

- **Links Break**: Moving a file requires `grep` and prayer.
- **Data Drifts**: "Status: Active" vs "status: active" vs "Status: ON".
- **Context Decays**: The implicit model in your head isn't enforced in the text.

## The Solution: Typedown

Typedown transforms your **documentation repository** into a **Database**. It adds a semantic layer to Markdown, allowing it to "phase transition" from loose text to structured data.

### 1. Structure (Schema)

Define what your data _should_ look like using Python (Pydantic).

````markdown
<!-- Defined in a code block -->

```model:User
class User(BaseModel):
    name: str
    role: Literal["admin", "member"]
```
````

### 2. Space (Graph)

Use **Solid References** that never break. Typedown resolves links by **Content Hash (L0)**, **Handle (L1)**, or **Global ID (L2)**.

```markdown
This report is authored by [[users/alice]].
```

### 3. Logic (Validation)

**Enforce invariants** directly in your documentation. Ensure your architecture rules are respected.

````markdown
```spec
def check_admin_policy(user: User):
    if user.role == "admin":
        assert user.has_mfa, "Admins need MFA"
```
````

## Installation

Typedown is designed to be used primarily in your editor, backed by a powerful CLI.

### 1. Editor Integration (Recommended)

For the true "Write-and-Validate" experience, install the VS Code extension:

- [**VS Code Marketplace**](https://marketplace.visualstudio.com/items?itemName=Typedown.typedown-vscode)
- [**Open VSX**](https://open-vsx.org/extension/Typedown/typedown-vscode)

### 2. Global CLI (For CI/CD)

Verify your knowledge base in CI pipelines using `uv` (recommended) or `pip`:

```bash
# Instant run (no install needed)
uvx typedown check

# Install globally
uv tool install typedown
```

### 3. For Contributors

If you want to hack on the compiler itself:

```bash
git clone https://github.com/IndenScale/typedown.git
```

## Core Philosophy

Typedown is built on the concept of **Consensus as Code (CaC)**.

- **Markdown (The Interface)**: Humans and LLMs speak natural language.
- **Pydantic (The Structure)**: Machines need schemas.
- **Pytest (The Law)**: Systems need invariants.

We call this **"Literate Modeling"**—you don't leave the document to define the system; the document _is_ the system.

## Documentation

- **[Quick Start](docs/en/index.md)**: Build your first model.
- **[Manifesto](docs/en/manifesto.md)**: Why we built this.
- **[GEMINI.md](GEMINI.md)**: Instructions for AI Agents.

---

## License

MIT © [IndenScale](https://github.com/IndenScale)

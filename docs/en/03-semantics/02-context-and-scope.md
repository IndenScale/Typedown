---
title: Context and Scope
---

# Context and Scope

Typedown's execution relies on a powerful context environment. Understanding the composition and resolution order of context is key to mastering Typedown's modular capabilities.

## 1. Context Definition

**Context** refers to the set of **Symbols** visible in the runtime environment when parsing a specific Typedown file (e.g., `.td` or `.md`).

Main symbol types:

- **Handles**: Fuzzy matching names for entities available in the current scope (L2).
- **Models**: Pydantic class definitions.
- **Variables**: Python objects injected via `config` blocks.

## 2. Scope Hierarchy

Typedown adopts **Lexical Scoping**. The parser looks up symbols in the following order (highest to lowest priority):

1. **Local Scope (Current File)**:
   - `model`, `entity` (L2 Handles) defined in the current file.
   - Symbols imported by inline `config` blocks.
2. **Directory Scope (Current Directory)**:
   - Symbols exported by `config.td`.
3. **Parent Scopes (Parent Directories)**:
   - Recursive up to the root directory's `config.td`.
   - *Shadowing*: Handles defined in subdirectories shadow Handles with the same name in parent directories.
4. **Global Scope (Global Preset)**:
   - Global configuration defined in `typedown.yaml`.
   - Runtime built-in symbols (Built-ins).

```mermaid
graph BT
    Global[Global Scope (typedown.yaml)]
    Parent[Parent Directory (config.td)] -->|Inherits| Global
    Dir[Current Directory (config.td)] -->|Overrides| Parent
    Local[Local File] -->|Extends| Dir
```

## 3. Resolution Strategy

When the compiler encounters `[[ref]]`, it not only looks up the context but also involves the global index and content addressing.

See the **Triple Resolution** mechanism in [References](../syntax/references):

1. **L0 Hash Check**: Is it a content digest? (`sha256:...`)
2. **L1 Exact Match**: Exact lookup for **System ID** in the global index.
3. **L2 Context Match**: Fuzzy match lookup for **Handle** in the current scope chain.

## 4. Handle vs System ID

To support environment isolation and polymorphic configuration, Typedown strictly distinguishes between an entity's **Reference Handle** and **System ID**.

| Concept | Term | Example | Scope | Responsibility |
| :----------------- | :------ | :----------------- | :--------------------------- | :-------------------------------------------------------- |
| **Handle (L2)** | Handle | `db_primary` | **Lexical** (Varies by file location) | **Dependency Injection (DI)**. Allows code to reference abstract names rather than concrete instances. |
| **System ID (L1)** | System ID | `infra/db-prod-v1` | **Global** (Globally unique) | **Version Control**. Points to a specific, immutable entity evolution stream. |

### Scenario: Environment Overlay

By defining different `config.td` in different directories, we can reuse the same business logic across different environments.

```text
/
├── config.td          -> entity Database: db (Defines production DB handle)
└── staging/
    ├── config.td      -> entity Database: db (Defines testing DB handle)
    └── app.td         -> References [[db]]
```

- In `/app.td`, `[[db]]` resolves to the production DB handle.
- In `/staging/app.td`, `[[db]]` resolves to the testing DB handle.
- **No code modification required**, just changing the running context.

## 5. Observability & Alignment

To understand and debug context, developers can use the following tools.

### Core Tools

- **LSP Doc Lens**:
  - In the editor, the Lens should display the current Block's Environment overlay status (Inherited Configs, Available Handles) in real-time.

- **`td get block query`**:
  - When you are confused about the context of the current Block, run this command.
  - It simulates the compiler's resolution logic and outputs the final target of the current Block under triple resolution.
  - **Workflow**: Write -> Query -> Correct.

### Debugging Advice

If you are unsure where `[[Ref]]` points to, or what the currently effective Schema is, use the tool to query.

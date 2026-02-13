---
title: Context and Scope
---

# Context and Scope

Typedown's execution relies on a powerful context environment. Understanding the composition and resolution order of context is key to mastering Typedown's modular capabilities.

## 1. Context Definition

**Context** refers to the set of **Symbols** visible in the runtime environment when parsing a specific Typedown file (e.g., `.td` or `.md`).

Main symbol types:

- **ID**: Names of entities available in the current scope.
- **Models**: Pydantic class definitions.
- **Variables**: Python objects injected via `config` blocks.

## 2. Scope Hierarchy

Typedown adopts **Lexical Scoping**. The parser looks up symbols in the following order (highest to lowest priority):

1. **Local Scope (Current File)**:
   - `model`, `entity` defined in the current file.
   - Symbols imported by inline `config` blocks.
2. **Directory Scope (Current Directory)**:
   - Symbols exported by `config.td`.
3. **Parent Scopes (Parent Directories)**:
   - Recursive up to the project root or filesystem root's `config.td`.
   - **Project Boundary**: `.tdproject` file marks the project boundary, blocking upward inheritance.
   - _Shadowing_: IDs defined in subdirectories shadow IDs with the same name in parent directories.
4. **Global Scope (Global Preset)**:
   - Global configuration defined in `typedown.yaml`.
   - **Runtime built-in symbols (Built-ins)**:
     - `query()`: Global symbol lookup (supports ID and property paths).
     - `sql()`: (Spec blocks only) DuckDB-based global SQL queries.
     - `blame()`: (Spec blocks only) Diagnostic error attribution.

```mermaid
graph BT
    Global[Global Scope (typedown.yaml)]
    Parent[Parent Directory (config.td)] -->|Inherits| Global
    Boundary[.tdproject Boundary] -->|Blocks| Parent
    Dir[Current Directory (config.td)] -->|Overrides| Boundary
    Local[Local File] -->|Extends| Dir
```

## 3. Resolution Strategy

When the compiler encounters `[[ref]]`, it first determines the reference type:

- **Hash Reference** (`sha256:...`): Lookup directly in the global hash index.
- **ID Reference**: Lookup by name in the current scope chain, fallback to global index if not found.

See [References](../syntax/references) for more details.

## 4. Scoped vs Global Resolution

To support environment isolation and polymorphic configuration, Typedown distinguishes between **Scoped IDs** and **Global IDs**.

| Concept | Example | Scope | Responsibility |
| :------ | :------ | :---- | :------------- |
| **Scoped ID** | `db_primary` | **Lexical** (Varies by file location) | **Dependency Injection (DI)**. Allows code to reference abstract names rather than concrete instances. |
| **Global ID** | `infra/db-prod-v1` | **Global** (Globally unique) | **Version Control**. Points to a specific, immutable entity. |

### Scenario: Environment Overlay

By defining different `config.td` in different directories, we can reuse the same business logic across different environments.

```text
/
├── config.td          -> entity Database: db (Defines production DB)
└── staging/
    ├── config.td      -> entity Database: db (Defines testing DB)
    └── app.td         -> References [[db]]
```

- In `/app.td`, `[[db]]` resolves to the production DB.
- In `/staging/app.td`, `[[db]]` resolves to the testing DB.
- **No code modification required**, just changing the running context.

### Scenario: Project Boundary Isolation

Use `.tdproject` files to enable multi-project coexistence and resolve global namespace conflicts.

```text
workspace/
├── project-a/
│   ├── .tdproject     # Project boundary marker
│   ├── config.td
│   └── models.td      -> entity User: alice
└── project-b/
    ├── .tdproject     # Project boundary marker
    ├── config.td
    └── models.td      -> entity User: bob  # Same ID, no conflict
```

**Boundary Rules**:
- **File Scanning**: Recursion stops when `.tdproject` is encountered in subdirectories
- **Scope Inheritance**: The directory containing `.tdproject` serves as project root, blocking upward inheritance of parent `config.td`
- **Multi-project Safety**: Allows independent development of multiple projects in the same workspace without ID conflicts

**Typical Use Cases**: cookbook examples, multiple services in a monorepo, multi-language (en/zh) examples with identical IDs.

## 5. Observability & Alignment

To understand and debug context, developers can use the following tools.

### Core Tools

- **LSP Doc Lens**:
  - In the editor, the Lens should display the current Block's Environment overlay status (Inherited Configs, Available IDs) in real-time.

- **`td get block query`**:
  - When you are confused about the context of the current Block, run this command.
  - It simulates the compiler's resolution logic and outputs the final target of the current Block.
  - **Workflow**: Write -> Query -> Correct.

### Debugging Advice

If you are unsure where `[[Ref]]` points to, or what the currently effective Schema is, use the tool to query.

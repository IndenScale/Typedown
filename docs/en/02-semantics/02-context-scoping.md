# Context & Scoping

Typedown's execution relies on a powerful context environment. Understanding the composition and resolution order of context is key to mastering Typedown's modular capabilities.

## 1. Context Definition

**Context** refers to the collection of **Symbols** visible in the runtime environment when parsing a specific Typedown file (like `.td` or `.md`).

Primary Symbol Types:

- **Handles**: Variable names for entities within the current scope (e.g., `alice`).
- **Models**: Pydantic class definitions.
- **Variables**: Python objects injected via `config` blocks.

## 2. Scope Hierarchy

Typedown employs **Lexical Scoping**. The parser searches for symbols in the following order (from highest to lowest priority):

1. **Local Scope (Current File)**:
   - `model`s and `entity` Handles defined in the current file.
   - Symbols imported by inline `config` blocks.
2. **Directory Scope (Current Directory)**:
   - Symbols exported by `config.td`.
3. **Parent Scopes (Parent Directories)**:
   - Recursively upwards until `config.td` in the root directory.
   - _Shadowing_: Handles defined in subdirectories shadow those with the same name in parent directories.
4. **Global Scope (Global Presets)**:
   - Global configurations defined in `typedown.yaml`.
   - Built-in runtime symbols (Built-ins).

```mermaid
graph BT
    Global[Global Scope (typedown.yaml)]
    Parent[Parent Directory (config.td)] -->|Inherits| Global
    Dir[Current Directory (config.td)] -->|Overrides| Parent
    Local[Local File] -->|Overrides| Dir
```

## 3. Resolution Strategy

When the compiler encounters `[[ref]]`, it not only looks up the context but also involves the global index and content addressing.

See the **Triple Resolution** mechanism in [References](../01-syntax/02-references.md):

1. **Hash Check**: Is it a content digest?
2. **Context Lookup**: Look for a matching **Handle** in the scope chain above.
3. **Global Index Lookup**: Look for a matching **Logical ID** in the full database index.

## 4. Handle vs Logical ID

To support environment isolation and polymorphic configuration, Typedown strictly distinguishes between an entity's **Reference Handle** and **Logical Identifier**.

| Concept        | Term       | Example            | Scope                                   | Responsibility                                                                                         |
| :------------- | :--------- | :----------------- | :-------------------------------------- | :----------------------------------------------------------------------------------------------------- |
| **Handle**     | Handle     | `db_primary`       | **Lexical** (Varies with file location) | **Dependency Injection (DI)**. Allows code to reference abstract names rather than concrete instances. |
| **Logical ID** | Logical ID | `infra/db-prod-v1` | **Global** (Globally unique)            | **Version Control**. Points to a specific, immutable entity evolution stream.                          |

### Scenario: Environment Overlay

By defining different `config.td` files in different directories, we can reuse the same business logic across different environments.

```text
/
├── config.td          -> entity Database: db (Defines Handle for Production DB)
└── staging/
    ├── config.td      -> entity Database: db (Defines Handle for Test DB)
    └── app.td         -> References [[db]]
```

- In `/app.td`, `[[db]]` resolves to the Production DB handle.
- In `/staging/app.td`, `[[db]]` resolves to the Test DB handle.
- **No code modification required**, just a change in the running context.

## 5. Observability & Alignment

Implicit context is powerful but introduces cognitive friction. To survive in "fragile" fields, developers must rely on the toolchain for continuous **Cognitive Alignment**.

### Core Tools

- **LSP Code Lens**:

  - This is the primary window into the current Context.
  - In the editor, Code Lenses display the Environment overlay status (Inherited Configs, Available Handles) in real-time.
  - **Principle**: "Invisible context" must be made visible through Code Lenses.

- **`td get block query`**:
  - Invoke this command whenever you have doubts about the current "field."
  - It simulates the compiler's resolution logic and outputs the final target of the Block under Triple Resolution.
  - **Workflow**: Write -> Doubt -> Query -> Align -> Commit.

### Debugging Philosophy

In Typedown, we do not guess. If you are unsure where `[[Ref]]` points or which Schema is currently in effect, query the system immediately. This **"Write-Query-Align"** loop is the core experience of development in Typedown.

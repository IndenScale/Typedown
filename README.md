# Typedown: Progressive Formalization for Markdown

**Typedown** is a new document format, toolchain, and product experience designed to bridge the gap between free-form Markdown and strict data schemas. It integrates **Markdown**, **Pydantic**, **Pytest**, and **Assets** into a cohesive package, reducing the cognitive friction in the process of "Progressive Formalization."

## The Vision

> **You don't know it until you model it.** — [**Read the full Typedown Manifesto**](docs/manifesto.md)

In software engineering and complex system design, knowledge often evolves from vague concepts to strict specifications. Current tools force a binary choice: unstructured text (Markdown/Google Docs) or rigid structures (Database/JSON/Code).

Typedown allows you to treat Markdown as the primary interface while gradually imposing constraints via Python's ecosystem:

1. **Markdown** is the host language.
2. **Pydantic** defines the structure (Schema) and local validation.
3. **Pytest** defines global constraints and relationship verification.

## Core Concepts

### 1. The Trinity: Markdown + Pydantic + Pytest

- **Markdown**: The human-readable layer.
- **Pydantic**: The schema layer. Defines classes and field-level validation.
- **Pytest**: The logic layer. Defines constraints that require access to the global variable table (e.g., "Referenced ID must exist").

### 2. Configuration & Inheritance

- **Front Matter**: Used for file metadata (e.g., title, author, status).
- **Scoped Configuration**: Each directory can contain a `config.td`. Code blocks tagged with `config:python` in `config.td` are executed to build context (e.g. importing models) and are inherited by subdirectories.
- **Override Rule**: Deepest (most specific) definition wins.

### 3. Entities & Data Blocks

Variables are expressed using code blocks with a specific language identifier: `entity:<class_name>`.

````markdown
# User Definition

Here we define the admin user.

```model
class User(BaseModel):
    id: str
    name: str
    role: str
```

```entity:User
id: "u_001"
name: "Alice"
role: "admin"
```
````

### 4. Evolution & Derivation (The "Desugar" Process)

Typedown supports minimal writing for evolving data.

- **`former`**: Represents the same entity (conceptually) at a different point in time or state.
- **`derived_from`**: Represents a variant of a base object.

**Input (Syntactic Sugar):**

````markdown
# Version 2

```entity:User
former: "u_001"  # References the previous object
email: "alice@example.com" # Only new/changed fields needed
```
````

**Output (Desugared/Materialized):**
The compiler merges the previous state with the new fields to create a complete object for validation.

### 5. Compilation & Materialization

The CLI supports a "compile" operation that can:

- **Validate**: Check all Pydantic models and Pytest constraints.
- **Materialize**: Rewrite documents to fill in missing fields from `former` or `derived_from` sources, optimizing the reading experience for consumers while keeping the writing experience minimal.

### 6. Directory Structure

A standard Typedown project looks like this:

```text
.
├── docs/       # The content. Markdown files (.md / .td)
│   ├── arch/
│   │   ├── config.td  # Scoped config for this dir
│   │   └── design.md
│   └── ...
├── models/     # The Schema. Python Pydantic classes
│   └── user.py
├── specs/      # The Constraints. Pytest files
│   └── test_consistency.py
└── assets/     # Images, diagrams, static files
```

## Documentation

For more detailed information, please refer to the following directories:

- **[Specs](specs/)**: Formal language specifications, RFCs, and data models.
- **[Docs](docs/)**: User guides and feature documentation.
- **[Dev Docs](dev-docs/)**: Architecture decisions (ADRs) and implementation details.

## Architecture & Toolchain

The ecosystem consists of several decoupled components:

### 1. Typedown Compiler (`tdc`)

The core library responsible for processing the project.

- **Analyze**: Parse Markdown AST, resolve imports, build the symbol table, and handle `config.td` inheritance.
- **Desugar**: Resolve `former` (temporal) and `derived_from` (inheritance) links, flattening the data into pure Pydantic instances.
- **Lint**: Static analysis for broken links, unused imports, and style conventions.
- **Validate**: Execute Pydantic validators and invoke Pytest runner on the extracted dataset.

### 2. Typedown CLI (`td`)

The user interface for the terminal.

- `td init`: Scaffold a new project.
- `td build`: Compile docs to static HTML/PDF (optional integration).
- `td check`: Run the full Validate pipeline.
- `td materialize`: Update source files to expand "sugared" blocks.

### 3. Typedown LSP (Language Server)

Provides the IDE experience (VS Code extension).

- **Autocompletion**: For `entity:Class` fields based on Pydantic definitions.
- **Go to Definition**: Jump from a usage in Markdown to the Python class definition.
- **Real-time Diagnostics**: Show validation errors (red squiggles) directly in the Markdown editor.

## Installation & Usage

Typedown is built with Python. We recommend using `uv` for lightning-fast environment management.

### Method 1: Run directly with `uvx`

You can run the Typedown CLI directly without manual installation using `uvx` (part of the `uv` toolchain). This is great for trying it out or running one-off commands.

```bash
# Run in any directory
uvx typedown check
```

### Method 2: Development Setup

If you want to contribute or use it in a local project:

1. **Install `uv`**:

   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Initialize Virtual Environment & Install**:

   ```bash
   # In the project root
   uv sync
   ```

3. **Run the CLI**:

   ```bash
   uv run td --help
   ```

## License

This project is licensed under the [MIT License](LICENSE).

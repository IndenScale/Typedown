# Architecture

Typedown operates like a compiler for your documentation.

## The Compilation Pipeline

1.  **Parse (Lexical Analysis):**
    *   Reads Markdown files.
    *   Extracts fenced code blocks (`model`, `entity`, `spec`).
    *   Identifies references (`[[...]]`).

2.  **Resolve (Semantic Analysis):**
    *   **Import Resolution:** Loads configuration and Python modules.
    *   **Symbol Table Construction:** Maps all Entity IDs to their definitions.
    *   **Reference Linking:** Connects `former`, `derived_from`, and `[[...]]` references to their targets.

3.  **Validate (Execution):**
    *   **Structural Validation:** Pydantic models validate the raw data of each Entity.
    *   **Logical Validation:** Pytest executes `spec` blocks against the fully resolved Workspace.

## The Workspace

The **Workspace** is the in-memory representation of your entire project. It holds the "Single Source of Truth" that all tests and tools interact with.

# 0008. Executable Configuration Scripts

Date: 2025-12-11

## Status

Proposed

## Context

The current mechanism for loading Pydantic models into Typedown's context relies on an `imports` field within `config.td` front matter. This approach presents several challenges:
1.  **Impedance Mismatch**: YAML is not designed for expressing complex module import logic, leading to clunky or ambiguous syntax (as seen with the `from X import Y` string parsing issues).
2.  **Limited Flexibility**: It's difficult to handle dynamic `sys.path` modifications, conditional imports, aliasing, or other advanced Python import scenarios directly within YAML.
3.  **Monorepo Challenges**: In multi-project or monorepo setups (e.g., `use_cases/` examples), where multiple subdirectories might define their own `models/` packages, the global `sys.path` injection becomes problematic due to namespace conflicts if packages share the same base name (e.g., multiple `models` packages).
4.  **Cognitive Overhead**: Users familiar with Python's import system are forced to learn a specialized YAML-based import syntax.

The goal is to provide a more flexible, powerful, and Pythonic way to define the "class context" for a given Typedown document or directory, reducing friction and supporting complex project structures.

## Decision

We will introduce the concept of "Executable Configuration Scripts" within `config.td` files (and potentially other Markdown documents). These will be standard Python code blocks that the Typedown CLI will execute during the parsing and context-building phase.

### Mechanism

1.  **Python Code Blocks**: `config.td` files can contain standard Markdown fenced code blocks with the `config:python` info string. The content of these blocks will be treated as executable Python code.
    ```markdown
    # config.td
    ---
    ---

    ```config:python
    # Example Python setup script
    import sys
    from pathlib import Path
    
    # Dynamically add specific paths to PYTHONPATH for this context
    sys.path.insert(0, str(Path(__file__).parent.parent / "my_local_lib"))

    # Import Pydantic models directly. These will become available in the Typedown context.
    from my_app.models import User, Order
    from another_app.shared_models import Product as InventoryProduct
    
    # Typedown will (implicitly or explicitly) collect these defined classes.
    ```
2.  **Cascading Context Execution**:
    *   When processing a document `docs/A/B/file.md`, the Typedown CLI will identify all relevant `config.td` files in its ancestry (e.g., `config.td` in `docs/`, `docs/A/`, `docs/A/B/`).
    *   These Python code blocks will be executed sequentially, starting from the outermost `config.td` and progressing inwards.
    *   Each execution step will augment/modify the Python execution environment (`globals()` and `locals()`), effectively forming a cascading context.
    *   The environment from a parent `config.td` is inherited by child `config.td` scripts.

3.  **Class Context Building**: After executing all relevant Python scripts for a given document's scope, the Typedown system will inspect the final execution environment. Any `pydantic.BaseModel` subclasses found directly within this environment (e.g., `User`, `Order`, `InventoryProduct` from the example above) will be automatically registered into the "class context" for that document and its children. This eliminates the need for an explicit `typedown.api.register` function for Pydantic models.

### Impacts

*   **`Parser`**: Must be enhanced to identify and extract Python fenced code blocks from `config.td` files.
*   **`Workspace`/`Loader`**:
    *   The `Loader`'s `load_imports` method (which processes YAML `imports`) will become deprecated and eventually removed.
    *   A new "Context Manager" or "Scope Builder" component will be introduced. This component will be responsible for:
        *   Identifying `config.td` files in the ancestral path of a document.
        *   Executing their Python code blocks in a controlled, cascading manner.
        *   Inspecting the execution environment to discover and register Pydantic `BaseModel` subclasses.
        *   Each `Document` (or more broadly, each directory scope) will be associated with its own derived class context.
*   **`Validator`**: Will query the class context associated with the document being validated, instead of a global `ClassRegistry`.
*   **`main.py` & CLI**: The `validate` command's pipeline will integrate the new context-building phase.
*   **User Experience**: Greatly simplified for Python developers, as they use familiar Python syntax for imports and setup.

## Consequences

*   **Increased Flexibility**: Users can leverage the full power of Python for setting up their Typedown environment.
*   **Improved Monorepo Support**: Each sub-project can define its own `sys.path` adjustments and imports without global conflicts.
*   **Security Considerations**: Executing arbitrary user-provided Python code requires a trust boundary. This will be documented as a build-tool behavior (similar to `setup.py`) that assumes developer trust in the codebase.
*   **Deprecation**: The YAML `imports` field in `config.td` will be deprecated.
*   **Refactoring Effort**: This change requires significant refactoring in the `Loader` and `Workspace` components.

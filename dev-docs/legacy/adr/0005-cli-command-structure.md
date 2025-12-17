# 0005-cli-command-structure.md

## Status

Accepted

## Context

As Typedown evolves from a simple parser to a proper compiler/build tool, we need a clear and intuitive Command Line Interface (CLI) structure. 
Initially, we introduced `td check` to run the analysis pipeline. However, as we distinguish between different stages of processing (Syntax vs. Semantics vs. Artifact Generation), the single `check` command became ambiguous.

We need to define a standard set of verbs that align with user expectations in the "Configuration as Code" and "Doc-as-Code" domains (similar to Terraform, Cargo, npm).

## Decision

We will adopt a three-tier command structure: **Lint**, **Validate**, and **Build**.

### 1. `lint` (Static Analysis)
*   **Scope**: Single file or independent file scan.
*   **Operations**: 
    *   Check for valid YAML syntax in Front Matter and `entity:` blocks.
    *   Check for valid Markdown syntax suitable for Typedown.
    *   Does NOT load Python modules or resolve cross-file references.
*   **Speed**: Fast (ms). Suitable for continuous running in IDEs or pre-commit hooks.
*   **Output**: Syntax errors, format warnings.

### 2. `validate` (Semantic Analysis)
*   **Scope**: Project-wide.
*   **Operations**:
    *   Loads all configuration and Python models (`models/`).
    *   Builds the Dependency Graph.
    *   Resolves References (`[[...]]`).
    *   Validates Data against Pydantic Schemas (**Type Checking**).
    *   Checks Business Constraints (Logic Checking).
*   **Speed**: Medium (sec). Suitable for CI/CD pipelines or "Save & Check" loops.
*   **Output**: Semantic errors (broken refs, type mismatches), logic violations.
*   **Note**: This replaces the previous `check` command.

### 3. `build` (Artifact Generation)
*   **Scope**: Project-wide.
*   **Definition**: A superset of `validate`. `build` = `validate` + `serialize`.
*   **Operations**:
    *   **Step 1**: Run `validate`. **On failure, abort. Do not generate artifacts.**
    *   **Step 2**: Materialize the final "Resolved Data".
    *   **Step 3**: Serialize the data to output formats (JSON, Recursive JSON, HTML Docs, etc.).
*   **Speed**: Slow. Suitable for deployment or release.
*   **Output**: Files in `dist/` or equivalent.
*   **Error Handling**: Must use standard "Diagnostic Style" reporting (Source File + Line Number + Context) instead of raw stack traces.

## Consequences

1.  **Rename**: `td check` will be renamed to `td validate`.
2.  **Implementation**: We need to refactor `typedown/commands/check.py` to `validate.py`.
3.  **Future Work**: `lint` and `build` commands are currently placeholders/concepts and need to be implemented separately. `validate` is the current priority.

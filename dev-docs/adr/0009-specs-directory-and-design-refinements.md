# 0009. Specs Directory and Design Refinements

Date: 2025-12-16

## Status

Accepted

## Context

The project's initial documentation and core concepts were spread across `README.md`, `docs/`, and `dev-docs/adr/`. While this provided a general overview, it lacked a formal, machine-readable, and language-agnostic specification for Typedown as a standard. The growing complexity of model definition, context management, and testing methodologies necessitated a clearer, more robust definition of the "Typedown Standard" distinct from its Python implementation.

Furthermore, several key concepts and their implementation details were either underspecified, ambiguously named, or inconsistently applied, leading to potential confusion and hindering future multi-language implementations.

## Decision

We have decided to formalize the Typedown specification by introducing a dedicated `specs/` directory at the project root. This directory will serve as the single source of truth for the Typedown Standard, encompassing its syntax, core concepts, architecture, and testing mechanisms.

Accompanying this, a comprehensive refinement and clarification of core Typedown design principles and terminology have been undertaken, specifically addressing:

1.  **Creation of `specs/` Directory**:
    *   **Purpose**: To house formal specifications (RFCs) for Typedown's syntax, evolution, structure, import mechanisms, referencing, testing, and core architectural data models.
    *   **Structure**: Organized into `meta/` (core concepts), `rfc/` (Request For Comments for various features), and `architecture/` (internal compiler data models).
    *   **Multilingual Support**: Mirrored in `specs_zh/` for Chinese documentation.

2.  **Terminology Clarification**:
    *   **Model vs. Entity**: Explicitly defined "Model" as the class blueprint (Pydantic) and "Entity" as its instance (data in Markdown).
    *   **Validator vs. Specification**: Distinguished between internal Pydantic-based validation (Validator) and complex cross-entity business logic validation using Pytest (Specification).
    *   **Desugar & Materialize**: Clarified their roles in the data processing pipeline.
    *   **Context**: Defined the layered injection and override mechanism for model definitions (Python Code -> Root `config.td` -> Nested `config.td` -> Local `model` block).

3.  **Refinement of Model/Context Definition Syntax**:
    *   **`model` Block Simplification**: The `model:<ClassName>` syntax has been replaced with a simpler `model` block, allowing multiple class definitions and automatic injection of common Pydantic/Typing symbols, reducing boilerplate.
    *   **`config:python` for Context**: Formalized `config:python` blocks within `config.td` (and other Markdown files) as the primary mechanism for dynamic context injection and external model imports, deprecating YAML `imports` in Front Matter.
    *   **Auto-injection Policy**: Default to OFF for automatic `.py` file scanning, emphasizing explicit imports via `config:python`.

4.  **Integration of Pytest for Specification Testing**:
    *   **`spec` Block as Python Test Code**: The `spec` block is now explicitly defined as a standard Python code block containing Pytest test functions, completely replacing any previous DSL-based `spec` definitions.
    *   **Pytest Fixtures & Markers**: Leveraged native Pytest features like `session` (auto-injected project context fixture) and `@pytest.mark` for flexible test organization and execution.
    *   **`check` Block**: Introduced as an optional inline assertion mechanism for specific Entities.

5.  **Archiving Legacy ADRs**:
    *   The existing `dev-docs/adr/` content has been moved to `dev-docs/legacy/adr/` to preserve historical thought processes while preventing confusion with current, formalized specifications.

## Consequences

*   **Clearer Standard**: Typedown now possesses a formal, centralized specification, significantly improving clarity for users, tool developers, and future maintainers.
*   **Enhanced Developer Experience**: Simplified `model` definitions and explicit `config:python` mechanisms streamline the authoring of Typedown documents.
*   **Robust Testing Framework**: Deep integration with Pytest provides a powerful, familiar, and flexible framework for defining and executing complex business rules and validations.
*   **Improved Multilingual Support**: The parallel `specs/` and `specs_zh/` directories ensure consistent specification definitions across languages.
*   **Maintenance Overhead**: Initial overhead in updating existing documentation and code to align with new specifications, but long-term benefits in consistency and maintainability.

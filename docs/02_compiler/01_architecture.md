# Compiler Architecture

The `tdc` (Typedown Compiler) workflow is divided into three main phases:

## 1. Analyze

*   **File Discovery**: Scan the `docs/` directory.
*   **Config Loading**: Parse `config.td` at all levels and build the inheritance tree.
*   **Symbol Table**: Parse all Markdown files, extract `entity` blocks, and build a preliminary Symbol Table.

## 2. Desugar

This is the core logic of the compiler.

*   **Dependency Graph**: Build a dependency graph based on `former` and `derived_from` relationships.
*   **Topological Sort**: Topologically sort the dependency graph to determine the resolution order.
*   **Merge & Resolve**: Instantiate objects in order, merging parent object attributes into child objects to generate flattened data structures.

## 3. Validate

*   **Pydantic Check**: Run Pydantic validators on each "desugared" complete object.
*   **Pytest Runner**: Collect all data objects, inject them into the Pytest context, and run test cases in `specs/`.

# Example 06: Modular Project (System Architecture)

Real-world projects are split across multiple files. Typedown supports this naturally through its directory-based scoping.

## Concepts

1.  **File Separation**: Keep Models, Specs, and Entities in different files for maintainability.
2.  **Shared Scope**: Files in the same directory (and subdirectories) share the same `symbol_table`.
3.  **`config.td`**: A special file to export common libraries/symbols to the whole directory tree.

## Structure

- `config.td`: Exports `datetime` module.
- `models.td`: Defines the `Task` model.
- `data.td`: Defines actual tasks.

## How to Run

Pass the **directory** to the CLI using `--path`.

```bash
td check --path examples/06_modular_project
```

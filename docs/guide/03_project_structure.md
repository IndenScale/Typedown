# Project Structure

A Typedown project is simply a directory containing Markdown files (`.md` or `.td`).

## The Root Directory

The project root is typically identified by the presence of a `.git` directory or a root-level `config.td`.

## Configuration (`config.td`)

You can place a `config.td` file in any directory to configure the context for that directory and its subdirectories.

**Cascading Rules:**
1.  Typedown loads the `config.td` in the root directory first.
2.  It then traverses down the directory tree, loading `config.td` files in each subdirectory.
3.  New configurations override or merge with parent configurations.

This allows you to set global imports in the root and specific imports in sub-modules.

## File Organization

You are free to organize your files however you like. Typedown scans all files recursively.

*   **`models/`**: A common pattern is to keep Python model definitions in separate `.py` files and import them via `config.td`, or define them in dedicated `.md` files using `model` blocks.
*   **`specs/`**: You might want to group high-level validation rules in a dedicated folder.

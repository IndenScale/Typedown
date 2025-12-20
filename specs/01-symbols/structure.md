# Project Structure Overview

Typedown recommends adopting a clear layered directory structure to organize documentation, models, and constraints.

## Standard Directory Structure

A typical Typedown project contains the following four core directories:

```text
.
├── docs/       # [Content Layer] Markdown Documentation (.md, .td)
│   ├── arch/
│   │   ├── config.td  # Directory-level Configuration
│   │   └── design.md
│   └── ...
├── models/     # [Schema Layer] Pydantic Data Model Definitions (.py)
│   └── user.py
├── specs/      # [Logic Layer] Pytest Constraints and Test Scripts (.py)
│   └── test_consistency.py
└── assets/     # [Resource Layer] Images, Charts, Static Files
```

## Configuration and Metadata (`config.td`)

Typedown uses a **filesystem-based configuration inheritance mechanism**.
Each directory can contain a `config.td` file to define shared configurations (such as common Imports, metadata defaults) for all documents in that directory and its subdirectories.

*   **Import Mechanism**: For detailed rules on how to import classes (local paths, URIs, aliases, etc.) and configuration inheritance, please refer to [04_import.md](./04_import.md).
*   **Reference Mechanism**: For how to reference entities and handle versions across documents via `[[]]` syntax, please refer to [05_reference.md](./05_reference.md).

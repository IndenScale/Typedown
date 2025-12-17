# 0006-build-artifacts-and-expansion.md

## Status

Accepted

## Context

We defined the `build` command in ADR-0005, but we need to specify exactly *what* it produces. Two key questions arose:
1.  Should `build` generate HTML directly?
2.  Should `build` output a "Single JSON Blob" or a "Self-Contained Bundle"?
3.  Should we support "In-place Expansion" (writing resolved values back to source Markdown) for easier review?

## Decision

### 1. No HTML Generation
Typedown will **NOT** function as a Static Site Generator (SSG). 
*   **Reason**: There are better tools for rendering (VitePress, Hugo, Obsidian). Typedown focuses on **Data Compilation**.
*   **Alternative**: Users should consume Typedown's data artifacts in their preferred frontend or game engine.

### 2. Artifact Format: Self-Contained Bundle
The `build` command will generate a **Distribution Package** in a `dist/` directory (or user-specified output). This package is designed to be self-sufficient for downstream consumers (Game Engines, AI Agents, Static Sites).

**Structure:**
```text
dist/
├── data.json           # Complete Resolved AST (Machine Readable)
├── assets/             # Collected image/media assets
├── content/            # Processed Markdown files (Machine/Human Readable)
└── models/             # (Optional) Schema definitions
```

### 3. Expansion Strategy (Desugaring)
We will **NOT** modify the source Markdown files in the `src/` directory. 
*   **Source Integrity**: Source files must remain "clean" and use references (`[[...]]`) to maintain Single Source of Truth.
*   **Review Experience**:
    *   **Human Review**: Should be handled by **IDE Extensions (LSP)** using Hover, Inlay Hints, or Code Lens to show resolved values dynamically.
    *   **AI/Machine Consumption**: The `dist/content/` directory MAY contain "Expanded Markdown" where references are replaced by their resolved values, making it easier for RAG systems or simple readers to consume without parsing logic.

## Consequences

1.  We need to implement the `build` command to create the directory structure described above.
2.  We need to ensure `data.json` contains the `resolved_data` of all entities.
3.  We will explicitly scope "In-Editor Preview" features to the VS Code Extension roadmap, keeping the CLI focused on batch processing.

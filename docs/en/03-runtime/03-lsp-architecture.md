# LSP & IDE Integration (Language Server Protocol)

Typedown's core value lies in transforming text documents into a structured knowledge base. The immediate feedback for this transformation relies entirely on the Language Server (LSP) design.

This document elucidates Typedown LSP's architectural philosophy, core responsibilities, and the division of labor with the VS Code extension.

## 1. Core Architectural Philosophy

### A. Omniscience

The LSP should not just be a Syntax Highlighter. It must be the **Brain** of the entire project. It should know:

- What files exist?
- What are their dependencies (Dependency Graph)?
- Does the current project violate any consistency rules?

### B. Editor Agnostic

All intelligent logic (jumps, completion, refactoring, diagnostics) must be sunk into the LSP Server (`typedown/server/`). The VS Code Extension (Client) should remain **Extremely Lightweight (Thin Client)**, responsible only for:

1. Starting the LSP process.
2. Forwarding user input and configuration.
3. Rendering UI returned by LSP (Definition, Hover, Decorations).

This ensures Typedown can easily adapt to Vim, Emacs, or JetBrains IDEs in the future.

### C. Hybrid Driven

To ensure response speed and data freshness, LSP adopts a dual-drive mode:

1. **Editor Events (Fast path)**: Responds to `textDocument/didChange`. Every keystroke in the editor updates the in-memory AST. Used for millisecond-level completion and syntax checking.
2. **Filesystem Watcher (Truth Path)**: Responds to `FileModified` events. Monitors the entire project directory via `watchdog`. This captures external changes (like `git pull`, script-generated code), ensuring the LSP's worldview aligns with the disk.

## 2. Feature Matrix

| Feature                    | Method (LSP Method)               | Implementation Strategy                                           | Dependent Core Components    |
| :------------------------- | :-------------------------------- | :---------------------------------------------------------------- | :--------------------------- |
| **Real-time Diagnostics**  | `textDocument/publishDiagnostics` | Trigger full validation (Validator) 300ms after user stops typing | `Validator`, `Parser`        |
| **Definition Jump**        | `textDocument/definition`         | Reference in `EntityBlock.raw_data` -> Lookup `SymbolTable`       | `SymbolTable`, `QueryEngine` |
| **Intelligent Completion** | `textDocument/completion`         | Identify current AST node context -> Filter available Handle/ID   | `SymbolTable`                |
| **Hover Tooltip**          | `textDocument/hover`              | Render Markdown summary of referenced entity                      | `EntityBlock.data`           |
| **Find References**        | `textDocument/references`         | Reverse lookup dependency graph (`DependencyGraph`)               | `DependencyGraph`            |

## 3. Implementation Details

### 3.1 Virtual File System (VFS)

LSP maintains a `Workspace` instance containing:

- **Document Map**: `Path -> Document (AST)`.
- **Symbol Table**: `ID -> EntityBlock`.
- **Dependency Graph**: Topology of references between entities.

### 3.2 Incremental Update & Debounce

For performance, we should not recompile the entire project on every keystroke.

1. **Single File Update**: `didChange` only triggers `Parser.parse()` for the current file.
2. **Partial Reconnection**: Only recalculate symbol tables and connections for affected files.
3. **Debounce**: Expensive `Validator` (L3 Check) should be executed with debounce.

### 3.3 External (Project-Level) Listening

The `watchdog` thread runs independently. When it detects changes not triggered by the editor, it actively calls `Server.update_document_from_disk(path)`.

### 3.4 Concurrency Model

To ensure state consistency, the LSP Server adopts a strict thread-safe design:

- **Main Thread (LSP Loop)**: Handles all requests from Client (VS Code) (`textDocument/*`). This is the main thread for reading/writing Compiler state.
- **Watchdog Thread**: Independently monitors disk changes.
- **Locking Strategy**: `Compiler` and its internal state (`documents`, `symbol_table`, `dependency_graph`) are protected by a global **Read-Write Lock (`threading.Lock`)**.
  - Main Thread acquires the lock when processing requests.
  - Watchdog Thread acquires the lock when updating disk state.
  - This prevents race conditions during the compilation process.

## 4. VS Code Extension Responsibilities

The VS Code plugin's responsibilities are limited to:

- Registering `.td` / `.typedown` file associations.
- Providing syntax highlighting rules (`tmLanguage.json`) — _Note: LSP can also provide Semantic Tokens, but tmLanguage is faster and has better compatibility for Markdown_.
- Starting the command `td lsp`.

---

> **Design Principle Summary**: LSP is the Daemonized Core of Typedown. It serves not only the editor but is essentially a compiler service with instant response capabilities.

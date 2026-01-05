---
title: LSP Architecture
---

# LSP and IDE Integration (Language Server Protocol)

Typedown's core value lies in transforming text documentation into a structured knowledge base. The instant feedback for this transformation relies entirely on the design of the Language Server (LSP).

This document explains the architectural philosophy, core responsibilities, and division of labor with the VS Code extension of Typedown LSP.

## 1. Core Architectural Philosophy

### A. Omniscience

The LSP should not just be a Syntax Highlighter. It must be the **brain** of the entire project. It should know:

- Which files exist?
- What is the dependency graph between them?
- Does the current project violate any consistency rules?

### B. Editor Agnostic

All intelligent logic (jump to definition, completion, refactoring, diagnostics) must be pushed down to the LSP Server (`typedown/server/`) implementation. The VS Code extension (Client) should remain **extremely lightweight (Thin Client)**, responsible only for:

1. Starting the LSP process.
2. Forwarding user input and configuration.
3. Rendering UI returned by LSP (Definition, Hover, Decorations).

This ensures Typedown can easily adapt to Vim, Emacs, or JetBrains IDEs in the future.

### C. Hybrid Driven

To ensure response speed and data freshness, LSP adopts a dual-drive mode:

1.  **Editor Events (Fast path)**: Responds to `textDocument/didChange`. Every keystroke by the user in the editor updates the AST in memory. This is used for millisecond-level completion and syntax checking.
2.  **Filesystem Watcher (Truth Path)**: Responds to `FileModified` events. Listens to the entire project directory via `watchdog`. This is to capture external changes (such as `git pull`, script-generated code), ensuring the LSP's worldview aligns with the disk.

## 2. Feature Matrix

| Feature | Method (LSP Method) | Implementation Strategy | Dependent Core Component |
| :----------- | :-------------------------------- | :--------------------------------------------------------- | :--------------------------- |
| **Real-time Diagnostics** | `textDocument/publishDiagnostics` | Trigger full validation (Validator) 300ms after user stops typing | `Validator`, `Parser` |
| **Jump to Definition** | `textDocument/definition` | Based on reference in `EntityBlock.raw_data` -> Lookup `SymbolTable` | `SymbolTable`, `QueryEngine` |
| **Smart Completion** | `textDocument/completion` | Identify current AST node context -> Filter available Handle/ID | `SymbolTable` |
| **Hover Tooltip** | `textDocument/hover` | Render Markdown summary of the referenced entity | `EntityBlock.data` |
| **Find References** | `textDocument/references` | Reverse lookup dependency graph (`DependencyGraph`) | `DependencyGraph` |

## 3. Implementation Details

### 3.1 Virtual File System

The LSP maintains a `Workspace` instance containing:

- **Document Map**: `Path -> Document (AST)`.
- **Symbol Table**: `ID -> EntityBlock`.
- **Dependency Graph**: Topology of references between entities.

### 3.2 Incremental Update & Debounce

For performance, we should not recompile the entire project on every keystroke.

1.  **Single File Update**: `didChange` only triggers `Parser.parse()` for the current file.
2.  **Partial Reconnection**: Only recalculate symbol tables and connections for affected files.
3.  **Debounce**: Expensive `Validator` (L3 Check) should be debounced.

### 3.3 External (Project-Level) Listening

The `watchdog` thread runs independently. When it detects changes not triggered by the editor, it actively calls `Server.update_document_from_disk(path)`.

### 3.4 Concurrency Model

To ensure state consistency, the LSP Server adopts a strict thread-safe design:

- **Main Thread (LSP Loop)**: Handles all requests (`textDocument/*`) from the Client (VS Code). This is the main thread for reading/writing Compiler state.
- **Watchdog Thread**: Independently listens for disk changes.
- **Locking Strategy**: `Compiler` and its internal state (`documents`, `symbol_table`, `dependency_graph`) are protected by a global **Read-Write Lock (`threading.Lock`)**.
  - The Main Thread acquires the lock when processing requests.
  - The Watchdog Thread acquires the lock when updating disk state.
  - This prevents Race Conditions during the compilation process.

## 4. VS Code Extension Division of Labor

The VS Code extension responsibilities are limited to:

- Registering `.td` / `.typedown` file associations.
- Providing syntax highlighting rules (`tmLanguage.json`) — *Note: LSP can also provide Semantic Tokens, but tmLanguage is faster and has better compatibility due to Markdown.*
- Launching the command `td lsp`.

---

> **Design Principle Summary**: LSP is the Daemonized Core of Typedown. It not only serves the editor but is essentially a compiler service with instant response capabilities.

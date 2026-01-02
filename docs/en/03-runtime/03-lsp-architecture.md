# LSP & IDE Integration

Typedown's core value lies in transforming text documents into a structured, verifiable knowledge base. The immediate feedback loop required for this transformation relies entirely on the **Language Server Protocol (LSP)** implementation.

This document outlines the architectural philosophy of the Typedown LSP and the division of labor between the server and its clients.

## 1. Core Architectural Philosophy

### A. Global Visibility (High-Fidelity Context)

The LSP is more than a syntax highlighter; it is the **Brain** of the project. It maintains a holistic view of:

- The entire project file structure.
- The Dependency Graph between entities.
- Consistency and validity across the entire "Semantic Field."

### B. Editor Agnostic (Thin Client)

All intelligence (jumps, completion, refactoring, diagnostics) resides in the LSP Server (`typedown/server/`). The VS Code Extension (the Client) is kept **Extremely Lightweight**, responsible only for:

1. Orchestrating the LSP process.
2. Forwarding user input and configuration.
3. Rendering the server's responses (Definitions, Hovers, Decorations).

This ensures Typedown can be easily integrated into Vim, Emacs, or any other IDE as the community grows.

### C. The Dual-Path Strategy

To balance responsiveness with accuracy, the LSP employs two distinct synchronization paths:

1. **The Fast Path (Memory)**: Responds to `textDocument/didChange`. Every keystroke updates the in-memory AST, providing sub-millisecond completion and syntax checking.
2. **The Truth Path (Disk)**: Responds to `FileModified` events via a filesystem watcher (`watchdog`). This captures external changes (like `git pull` or script-generated content), ensuring the server's worldview remains aligned with the disk.

## 2. Feature Matrix

| Feature                    | LSP Method                        | Implementation Strategy                                           | Components                   |
| :------------------------- | :-------------------------------- | :---------------------------------------------------------------- | :--------------------------- |
| **Real-time Diagnostics**  | `textDocument/publishDiagnostics` | Triggers L3 Validation (Validator) after a short typing debounce. | `Validator`, `Parser`        |
| **Go to Definition**       | `textDocument/definition`         | Resolves references via the Triple Resolution mechanism.          | `SymbolTable`, `QueryEngine` |
| **Intelligent Completion** | `textDocument/completion`         | Identifies AST context and suggests available Handles or IDs.     | `SymbolTable`                |
| **Hover Tooltips**         | `textDocument/hover`              | Renders a Markdown summary of the referenced entity.              | `EntityBlock.data`           |
| **Find References**        | `textDocument/references`         | Performs a reverse lookup on the Dependency Graph.                | `DependencyGraph`            |

## 3. Implementation Details

### 3.1 Workspace Snapshot

LSP maintains a consistent state of the project:

- **Document Map**: Path-to-AST mapping.
- **Symbol Table**: Resolution index for Handles and IDs.
- **Dependency Graph**: Topology of inter-entity relationships.

### 3.2 Concurrency & Performance

The LSP Server is strictly thread-safe:

- **Main Thread**: Handles Client requests and updates the memory AST.
- **Watchdog Thread**: Independently monitors disk changes.
- **Locking**: The `Compiler` state is protected by a global **Read-Write Lock**. This ensures that the Truth Path and the Fast Path never cause race conditions.

## 4. Client Responsibilities (e.g., VS Code)

- Registering `.td` and `.typedown` file associations.
- Providing core syntax highlighting (`tmLanguage.json`) for immediate visual feedback.
- Executing the `td lsp` command to bootstrap the server.

---

> **Summary**: The LSP is the daemonized engine of Typedown. It is more than an editor aid; it is a live compiler service that ensures the "Consensus" in Consensus Modeling is always verified and visible.

# 0002. Adopt Embedded Workspace Library Model

Date: 2025-12-11

## Status

Accepted

## Context

We needed to decide on the runtime model for the Typedown toolchain (`td`). The main options were:
1.  **Client-Daemon Model (Docker-like)**: A persistent background process (`td-daemon`) holding state, with a thin CLI client.
2.  **Embedded Workspace Model (Git/Cargo-like)**: The CLI imports the core logic as a library. State is transient for CLI runs but persistent for the LSP process (which also imports the library).

Key considerations included startup latency, complexity of implementation (IPC, process management), and the "unsaved buffer" synchronization problem in LSP.

## Decision

We will adopt the **Embedded Workspace Model** (Library-based).

*   We will implement a `typedown.core.Workspace` class that encapsulates the state (AST, Symbol Table, Dependency Graph).
*   The CLI (`td`) will instantiate a `Workspace` on demand for one-off tasks.
*   The LSP server (`td lsp`) will instantiate a long-lived `Workspace` to serve editor requests.
*   We explicitly reject the Daemon model for the MVP phase to avoid system-level complexity and synchronization issues between disk and editor memory.

## Consequences

*   **Positive**: Implementation will be simpler (no socket IPC code). LSP integration is standard (State lives in the LSP process).
*   **Negative**: CLI commands will have a "cold start" penalty as they re-parse the project.
*   **Mitigation**: We will design the `Workspace` to be performant enough for medium-sized projects, and reserve the option to wrap it in a Daemon in the future if performance demands it (since the logic is decoupled in a library).

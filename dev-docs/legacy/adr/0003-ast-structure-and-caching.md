# 0003. AST Structure and Caching Strategy

Date: 2025-12-11

## Status

Accepted

## Context

We need a robust data structure to represent the parsed Typedown project, supporting both Markdown content and the specific Graph data (Relations, Queries). We also need to decide on a caching strategy to handle performance as projects grow.

## Decision

### 1. Hybrid AST
We defined a custom AST in `typedown.core.ast` that combines:
*   **Document Structure**: `Document` node containing `config` and raw content.
*   **Data Nodes**: `EntityBlock` representing structured data extracted from code blocks.
*   **Graph Nodes**: `Reference` nodes representing `[[query]]` and relations (`former`, `derived_from`).

### 2. No Persistent Cache (MVP)
For the MVP, we will **not** implement a persistent cache (SQLite/Pickle).
*   The compiler will perform a full parse on every run.
*   The LSP will maintain state in memory.

### 3. Preparation for Incrementality
To support future incremental parsing, we added a `content_hash` field to the `Document` node. The `Parser` interface will be designed to accept this hash, allowing us to swap in a caching layer (e.g., "if hash matches DB, skip parse") in a future iteration without changing the core AST.

## Consequences

*   **Positive**: Initial development is faster and less error-prone (no cache invalidation bugs).
*   **Negative**: Performance on very large projects may be suboptimal initially.
*   **Future Work**: Implement SQLite-based caching layer when AST is stable.

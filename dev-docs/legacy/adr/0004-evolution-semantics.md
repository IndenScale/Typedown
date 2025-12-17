# 0004. Evolution Semantics

Date: 2025-12-11

## Status

Accepted

## Context

Typedown allows defining entities that evolve over time (`former`) or derive from others (`derived_from`). We needed to strictly define the semantics to avoid ambiguity and "code smells."

## Decision

### 1. Immutability & New IDs
**Rule**: Any state change *must* result in a new Entity with a new unique ID.
*   `former` points to the ID of the previous state.
*   This ensures that references to historical states (e.g., `[[Hero_v1]]`) remain valid and immutable.

### 2. Linear vs. Branching
*   **`former` (Time)**: Must be strictly **Linear**. Branching (one ID having multiple `former` successors) is considered a **Code Smell**.
    *   1st degree fork: Info
    *   2nd degree fork: Warning
    *   3rd degree+: Error
*   **`derived_from` (Type)**: Naturally **Branching** (Tree structure). It is normal for a base class to have multiple variants.

### 3. Reference Resolution
*   **Implicit**: `[[ID]]` (without version suffix) resolves to the **Latest** version in the `former` chain at compile time.
*   **Explicit**: Users can link to specific versions if needed.
*   **Query**: References are treated as Queries (`[[query]]`), supporting fuzzy matching and validation.

## Consequences

*   The compiler must implement a check for `former` branching depth.
*   The compiler needs a "Resolve to Latest" pass to rewriting implicit references.
*   Users are forced to adopt a disciplined naming convention (e.g., `_v1`, `_v2`), which improves project maintainability.

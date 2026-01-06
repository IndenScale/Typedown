---
title: Evolution Semantics
---

# Evolution Semantics (Evolution)

Typedown does not treat data as a static artifact, but as a timeline that is constantly evolving.

## 1. Linear Evolution (`former`)

The `former` keyword links a new entity state to its previous version.

- **Syntax**: Use `former: [[QueryString]]` in the entity body.
- **Constraints**: **Must use Global Addressing**.
  - 🚫 **Prohibited**: Local Handles (e.g., `alice`). Evolution relationships must remain stable across files and contexts.
  - 🚫 **Prohibited**: Pure String IDs (e.g., `"slug-id"`). According to the latest Typedown specification, explicit reference syntax must be used.
  - ✅ **Allowed**:
    - **Slug ID Reference**: `[[user-alice-v1]]` (Most common)
    - **UUID Reference**: `[[550e84...]]` (Machine-generated unique identifier)
    - **Block Fingerprint**: `[[sha256:8f4b...]]` (Content-based hash, most precise)
- **Semantics**:
  - **Identity Consistency**: The new entity logically represents different points in time of the same object.
  - **Pure Pointer**: `former` exists only as a metadata link to build the timeline. The compiler **does not** perform data merging.
  - **Incrementality Principle**: The new entity must contain the full property definition (or be explicitly copied by the user).
  - **Immutability**: The old ID remains a valid, immutable snapshot. Once an Entity is pointed to (as it has become history), it should not be modified again (Append Only).

Example

````markdown
## Version 1

```entity Feature: id=login_v1
status: planned
```

## Version 2

```entity Feature: id=login_v2
former: [[login_v1]]
status: in_progress
```
````

## 2. Source vs. Materialized

- **Explicitness**: Source code is truth. Do not expect the compiler to perform invisible field injection behind the scenes.
- **Traceability**: Through the `former` chain, you can use tools (like LSP or CLI) to quickly compare differences between versions.

---

## 3. Divergence and Convergence Rules

- **Evolution Fork (Error)**: An ID cannot be the `former` of two different entities. The timeline cannot split.
- **Evolution Convergence**: Multiple old versions can evolve into a new version (representing a merge), but semantic conflicts must be handled carefully.

# Evolution (Evolution Semantics)

Typedown does not treat data as static artifacts, but as a timeline of constant evolution.

## 1. Linear Evolution (`former`)

The `former` keyword links a new entity state to its previous version.

- **Syntax**: Use `former: "QueryString"` in the entity body.
- **Constraints**: **Must use Global Addressing**.
  - 🚫 **Prohibited**: Local Handles (like `alice`). Evolution relationships must remain stable across files and contexts.
  - ✅ **Allowed**:
    - **Slug ID**: `user-alice-v1` (Most common)
    - **UUID**: `550e84...` (Machine-generated unique ID)
    - **Block Fingerprint**: `sha256:8f4b...` (Content-based hash, most precise)
- **Semantics**:
  - **Identity Consistency**: The new entity logically represents the same object at a different point in time.
  - **Pure Pointer**: `former` exists only as a metadata link for building the timeline. The compiler **does not perform** data merging.
  - **Increment Principle**: The new entity must contain the complete attribute definitions (or be explicitly copied by the user).
  - **Immutability**: The old ID remains a valid, immutable snapshot. Once an Entity is pointed to (because it has become history), it should no longer be modified (Append Only).

Example

````markdown
## Version 1

```entity Feature: id=login_v1
status: planned
```

## Version 2

```entity Feature: id=login_v2
former: "login_v1"
status: in_progress
```
````

## 2. Structure Derivation (`derived_from`)

> ⚠️ **Status**: **Deprecated / Removed**
>
> In the early evolution of Typedown, we decided to remove the `derived_from` feature based on prototype inheritance.
>
> **Reasons**:
>
> 1. **AI Empowerment**: As AI Agents make large-scale data population extremely cheap and accurate, the need to save characters via complex inheritance trees is no longer a top priority.
> 2. **Explicit over Implicit**: Explicit data definitions (Flattened Data) are more readable and easier for compilers to perform static analysis on than deep nested merging logic.
> 3. **Simplified Mental Model**: Removing the Merging Strategy greatly reduces the mental burden on the user and implementation complexity.
>
> Currently, the compiler may recognize the field but will not execute any merge operations. If data reuse is needed, it is recommended to use AI tools for explicit population or refactor at the Model level.

## 3. Merging Strategy

**Removed**.

Typedown currently adopts an **Explicit Definition** strategy. All entities should be treated as independent, complete snapshots after materialization. `former` acts only as a metadata Pointer for tracing the timeline and triggers no property merging.

---

## 4. Source vs. Materialized

- **Explicitness**: Source is Truth. Do not expect the compiler to perform invisible field injection behind the scenes.
- **Traceability**: Through the `former` chain, you can use tools (like LSP or CLI) to quickly compare differences between versions.

---

## 5. Divergence and Convergence Rules

- **Evolution Divergence (Error)**: An ID cannot be the `former` of two different entities. The timeline cannot split.
- **Evolution Convergence**: Multiple old versions can evolve into a new version (representing a merge), but semantic conflicts must be handled carefully.

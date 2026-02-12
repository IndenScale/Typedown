---
title: Evolution Semantics
---

# Evolution Semantics

Typedown does not treat data as a static product, but as an evolving timeline.

## Linear Evolution (`former`)

The `former` keyword links a new entity state to its previous version.

### Syntax

```yaml
former: [[target-id]]
```

### Constraints

**Must use global addressing**:

| Method | Example | Status |
|--------|---------|--------|
| ID reference | `[[user-alice-v1]]` | ✅ Allowed (most common) |
| Hash reference | `[[sha256:8f4b...]]` | ✅ Allowed (most precise) |

### Semantic Rules

- **Identity Consistency**: The new entity logically represents the same object at a different point in time
- **Pure Pointer**: `former` only serves as metadata link; compiler does **not** perform data merging
- **Incremental Principle**: New entity must contain complete property definitions (or explicit copies)
- **Immutability**: Old ID remains valid and immutable; the pointed entity should no longer be modified (Append Only)

### Example

````typedown
## Version 1

```entity Feature: login_v1
status: planned
```

## Version 2

```entity Feature: login_v2
former: [[login_v1]]
status: in_progress
```
````

## Divergence Rules

- **Evolution Forking (Error)**: One ID cannot become the `former` of two different entities; timelines cannot split
- **Evolution Convergence**: Multiple old versions can merge into one new version, but semantic conflicts must be handled carefully

## Source as Truth

- **Explicitness**: Do not expect the compiler to perform invisible field injection behind the scenes
- **Traceability**: Through the `former` chain, LSP or CLI tools can quickly compare version differences

---
title: References
---

# References

Typedown uses double brackets `[[ ]]` as the unified reference syntax.

## 1. Core Mechanism: Reference as Query

`[[query]]` represents a "query intent", not an absolute physical address.

When using `[[alice]]`, the compiler looks for the best matching target in the current context. This mechanism supports **progressive development**:

- In early drafts, you can use fuzzy Handles (`[[alice]]`).
- The compiler resolves them into precise entities via **Triple Resolution**.

If absolute precision is needed, you should lock specific versions via **Content Hash** instead of relying on opaque UUIDs.

## 2. Reference Forms

Typedown supports three reference forms, and the compiler automatically infers your intent based on context.

- **Slug (Logical ID)**: `[[user-alice-v1]]`

  - **Semantics**: Points to a specific entity in the global index.
  - **Recommended Scenario**: Cross-file references, formal documentation links. This is the most common human-readable anchor.

- **Handle (Local Handle)**: `[[alice]]`

  - **Semantics**: Points to a temporary variable name defined in the current file or current code block (Scope).
  - **Recommended Scenario**: Rapid prototyping, dependency injection within modules.

- **Hash (Content Fingerprint)**: `[[sha256:8f4b...]]`
  - **Semantics**: Points to an absolute snapshot of content.
  - **Recommended Scenario**: System-level locking, releasing Immutable Packages. It is safer than human-named IDs and better than randomly generated UUIDs.

> See [Identifiers](./identifiers) for full definitions of identifier types.

## 3. Content Addressing

Typedown supports content-based hash references. This allows references to point to a **deterministic** data snapshot rather than a mutable entity.

### Calculation Logic

The hash value is calculated from the **Canonical Body** of the Entity code block.

> Algorithm: `SHA-256( Trim( YAML_Content ) )`

This means: as long as the effective data content of two blocks is identical (excluding Handles, comments, or formatting differences), their Hash is identical.

### Syntax Example

```markdown
# Reference a specific version snapshot of configuration, fearless of original ID modification

base_config: [[sha256:a1b2c3d4...]]
```

## 4. Usage in YAML Data

Typedown adopts a **"YAML with Sugar"** strategy. Although standard YAML parsers treat `[[ ]]` as nested lists, the Typedown compiler performs **Smart Unboxing** at the AST level.

### A. Single Reference

```yaml
# Here [[leader]] is ["leader"] (List<String>) in standard YAML
# Compiler smartly converts it to a Reference object
manager: [[leader]]
```

### B. List of References

This is the most significant syntax optimization. You don't need to write cumbersome nested list structures.

````markdown
```entity Project: death_star
# Recommended (Block Style)
contributors:
  - [[vader]]
  - [[tarkin]]

# Flow Style is also supported
reviewers: [ [[emperor]], [[thrawn]] ]
```
````

**Underlying Logic**:

1. YAML Parser reads it as `[['vader'], ['tarkin']]`.
2. Typedown Validate finds the field defined as `List[Reference[T]]`.
3. Automatically performs Flatten operation, converting to `[Ref('vader'), Ref('tarkin')]`.

## 5. Type Safety (`Reference[T]`)

In Pydantic models, use the `Reference` generic to enforce type constraints.

```python
from typedown.types import Reference

class Task(BaseModel):
    title: str
    # Constraint: assignee must reference a User type entity
    assignee: Reference["User"]
    # Constraint: can also be one of multiple types
    subscribers: List[Reference["User", "Team"]]
```

### Compile-time Check

When users write an Entity Block, the compiler performs four layers of checks:

1. **Existence**: Is `[[alice]]` visible in the current scope?
2. **Type Safety**: Does `[[alice]]` point to a `User`? If it is a `Device`, a compile error occurs.
3. **Data Correctness**: Validates if the data in the Entity Block conforms to the Model's Schema and passes all validators.

## 6. Referencing Other Objects

`[[ ]]` is a universal link syntax, supporting pointing to any first-class citizen in the system:

- **Model**: `type: [[User]]` (Reference model/type definition)
- **Entity**: `manager: [[users/alice]]` (Reference concrete data instance)
- **Spec**: `validates: [[check_age]]` (Reference logic spec or function)
- **File**: `assets: [[specs/design.pdf]]` (Files must be treated as first-class citizens and **must** use `[[ ]]` syntax to be included in dependency management)

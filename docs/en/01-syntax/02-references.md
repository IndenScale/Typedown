# References

In Typedown, references are the neural synapses connecting isolated entities. We use double brackets `[[ ]]` as the unified reference syntax.

## 1. Core Philosophy: Reference as Query

We need to reconstruct the traditional understanding of `[[...]]`: **It does not represent an absolute physical address (Addressing), nor is it just a pointer.**

**`[[query]]` represents a "Query Intent".**

When you write `[[alice]]`, you are actually saying to the compiler: _"Please find the thing most likely to be called alice in the current context."_

This design serves **Progressive Formalization of Cognition**:

- In early drafts, `[[alice]]` might just be a vague reference.
- As the system evolves, the compiler collapses it into a precise single entity through the **Triple Resolution** mechanism.
- This **Ambiguity** is a core feature of Typedown, allowing humans to write intuitively while offloading the burden of precise matching to the toolchain.

If absolute precision is needed, you should lock onto a specific version via **Content Hash**, rather than relying on opaque UUIDs.

## 2. Reference Forms

Typedown supports three reference forms, and the compiler automatically infers your intent based on context.

- **Slug (Logical ID)**: `[[user-alice-v1]]`

  - **Semantics**: Points to a specific entity in the global index.
  - **Recommended Usage**: Cross-file references, formal documentation links. This is the most common human-readable anchor.

- **Handle (Local Handle)**: `[[alice]]`

  - **Semantics**: Points to a temporary variable name defined within the current file or current code block (Scope).
  - **Recommended Usage**: Rapid prototyping, dependency injection within modules.

- **Hash (Content Fingerprint)**: `[[sha256:8f4b...]]`

  - **Semantics**: Points to an absolute snapshot of content.
  - **Recommended Usage**: System-level locking, publishing Immutable Packages. It is safer than human-named IDs and superior to randomly generated UUIDs.

> See [03-identifiers.md](03-identifiers.md) for full definitions of identifier types.

## 3. Content Addressing

Typedown supports content-based hash references. This allows references to point to a **deterministic** data snapshot rather than a mutable entity.

### Calculation Logic

The hash value is calculated from the Entity code block's **Canonical Body**.

> Algorithm: `SHA-256( Trim( YAML_Content ) )`

This means: as long as the valid data content of two Blocks is identical (excluding Handle, comments, or formatting differences), their Hash is identical.

### Syntax Example

```markdown
# Reference a specific version snapshot of config, fearless of original ID modification

base_config: [[sha256:a1b2c3d4...]]
```

## 4. Usage in YAML Data

Typedown adopts a **"YAML with Sugar"** strategy. Although standard YAML parsers treat `[[ ]]` as nested lists, the Typedown compiler performs **Smart Unboxing** at the AST level.

### A. Single Reference

```yaml
# Here [[leader]] is ["leader"] (List<String>) in standard YAML
# The compiler smartly converts it to a Reference object
manager: [[leader]]
```

### B. List of References

This is the most significant syntax optimization. You don't need to write cumbersome nested list structures.

````markdown
```entity Project: death_star
# Recommended Style (Block Style)
contributors:
  - [[vader]]
  - [[tarkin]]

# Also supports Flow Style
reviewers: [ [[emperor]], [[thrawn]] ]
```
````

**Underlying Logic**:

1. YAML Parser reads as `[['vader'], ['tarkin']]`.
2. Typedown Validate finds the field defined as `List[Reference[T]]`.
3. Automatically executes Flatten operation, converting to `[Ref('vader'), Ref('tarkin')]`.

## 5. Type Safety (`Reference[T]`)

In Pydantic models, use the `Reference` generic to enforce type constraints.

```python
from typedown.types import Reference

class Task(BaseModel):
    title: str
    # Constraint: assignee must reference an entity of User type
    assignee: Reference["User"]
    # Constraint: can be one of multiple types
    subscribers: List[Reference["User", "Team"]]
```

### Compile-Time Checks

When users write an Entity Block, the compiler performs four layers of checks:

1. **Existence**: Is `[[alice]]` visible in the current scope?
2. **Type Safety**: Does `[[alice]]` point to a `User`? If it is a `Device`, compile error.
3. **Data Correctness**: Validates if data inside the Entity Block conforms to the Model's Schema and passes all validators.

## 6. Referencing Other Objects

`[[ ]]` is a universal link syntax, supporting pointing to any first-class citizen in the system:

- **Model**: `type: [[User]]` (Referencing model/type definition)
- **Entity**: `manager: [[users/alice]]` (Referencing concrete data instance)
- **Spec**: `validates: [[check_age]]` (Referencing logic spec or function)
- **File**: `assets: [[specs/design.pdf]]` (Files must be first-class citizens and **only** use `[[ ]]` syntax to be included in dependency management)

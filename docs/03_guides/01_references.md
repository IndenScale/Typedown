---
title: Reference System
---

# Reference System

Typedown uses `[[ ]]` syntax to establish links between entities, supporting **ID references** and **content hash references**.

## Reference Syntax

```typedown
[[entity-id]]           # ID reference
[[sha256:abc123...]]    # Content hash reference
```

## Identifier Types

| Type | Format Example | Purpose |
|------|----------------|---------|
| **ID** | `[[user-alice-v1]]` | Globally unique identifier, precise indexing |
| **Hash** | `[[sha256:a1b2...]]` | Content addressing, absolute anchoring |

## ID Specification

- **Character Restrictions**: Letters, numbers, underscores `_`, hyphens `-`, dots `.`
- **Naming Style**: Recommend using `domain-type-name-version` format
  - Examples: `iam-user-alice-v1`, `infra-db-primary-v3`
- **Global Uniqueness**: Must be unique across the entire project

## Content Addressing

Content hash-based reference, pointing to deterministic data snapshots:

```yaml
# Reference a specific version of configuration snapshot
base_config: [[sha256:a1b2c3d4...]]
```

**Hash calculation**: `SHA-256( Trim( YAML_Content ) )`

Same valid data → same hash (ignoring comments or formatting differences)

## Usage in YAML

### Single-value Reference

```yaml
# Compiler converts [[user-alice-v1]] to Ref object
manager: [[user-alice-v1]]
```

### List References

```yaml
# Block Style
contributors:
  - [[user-vader-v1]]
  - [[user-tarkin-v1]]

# Flow Style
reviewers: [[[user-emperor-v1]], [[user-thrawn-v1]]]
```

**Underlying processing**:
1. YAML parses to `[['user-vader-v1'], ['user-tarkin-v1']]`
2. Discovers field type is `List[Ref[T]]`
3. Automatically flattens to `[Ref('user-vader-v1'), Ref('user-tarkin-v1')]`

## Type Safety

Use `Ref` generics to enforce type constraints:

```python
from typedown.types import Ref

class Task(BaseModel):
    # Must reference User type
    assignee: Ref["User"]
    
    # Allows multiple types
    subscribers: List[Ref["User", "Team"]]
    
    # Self-reference
    parent: Optional[Ref["Task"]] = None
```

### Compile-time Checks

1. **Existence**: Does `[[user-alice-v1]]` point to an existing entity?
2. **Type Safety**: Is the referenced entity of the expected `User` type?
3. **Data Correctness**: Does the entity data conform to Model Schema?

## Referencable Objects

`[[ ]]` is a universal linking syntax:

| Target Type | Example | Description |
|-------------|---------|-------------|
| Model | `type: [[User]]` | Type definition |
| Entity | `manager: [[user-alice-v1]]` | Data instance |
| Spec | `validates: [[check-age-v1]]` | Validation rule |
| File | `assets: [[specs/design.pdf]]` | File resource |

> Files must use `[[ ]]` syntax to be included in dependency management.

## Evolution References

Used in the `former` field:

```yaml
former: [[user-alice-v0]]  # ID reference (most common)
former: [[sha256:8f4b...]] # Hash reference (most precise)
```

See [Evolution Semantics](../concepts/evolution) for details.

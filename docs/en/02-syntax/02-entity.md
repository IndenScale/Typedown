---
title: Data Entity
---

# Data Entity (Entity)

The `entity` block is the primary way to instantiate data in Typedown. Each entity block represents a node in the knowledge graph.

## Syntax Signature

```markdown
```entity <TypeName>: <SystemID>
<YAML Body>
```
```

- **Keyword**: `entity`
- **Type**: `<TypeName>` must be a Model class name defined in the current context.
- **Identifier**: `<SystemID>` is the globally unique identifier (L1 ID) for this entity.
- **Separator**: Use a colon `:` to separate the type and ID.

## Identifier Rules

System ID is the **primary key** of the entity.

- **Recommended Format**: `slug-style` (e.g., `user-alice-v1`).
- **Constraints**:
  - Globally unique.
  - Can only contain letters, numbers, hyphens `-`, underscores `_`, and dots `.`.
  - **Prohibited**: Spaces or slashes `/`.

## Data Body (YAML Body)

The content part of the entity adopts **Strict YAML** format.

```yaml
name: "Alice"
age: 30
role: "admin"
```

### Reference Syntax Sugar

When a field type is `List[Reference[T]]`, Typedown supports simplified list syntax:

```yaml
# Model Definition: friends: List[Reference[User]]

# Recommended (Block Style)
friends:
  - [[bob]]
  - [[charlie]]

# Inline (Flow Style)
reviewers: [ [[bob]], [[alice]] ]
```

### Automatic Unpacking

The compiler automatically handles the `[[ ]]` syntax. Under the hood, `[[bob]]` is parsed as a `Reference` object, not a simple string.

## Evolution

Use the `former` field to declare historical versions of an entity.

```yaml
former: [[user-alice-v0]]
name: "Alice (Updated)"
```

See [Evolution Semantics](/en/docs/semantics/evolution) for details.

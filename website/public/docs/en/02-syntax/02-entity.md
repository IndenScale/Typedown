# Data Entity (Entity)

The `entity` block is the primary way to instantiate data in Typedown. Each entity block represents a node in the knowledge graph.

## Syntax Signature (Block Signature)

````typedown
```entity <TypeName>: <SystemID>
<YAML Body>
```
````

- **Keyword**: `entity`
- **Type**: `<TypeName>` must be a Model class name defined in the current context.
- **Identifier**: `<SystemID>` is the globally unique identifier (L1 ID) for this entity.
- **Space Insensitivity**: Spaces between the keywords, colons, and identifiers are no longer sensitive. For example, `entity User:alice` is equivalent to `entity User : alice`.

## Identifier Rules

System ID is the **primary key** of the entity, following these strict restrictions in v0.2.13+:

- **Character Restrictions**: Identifiers are only allowed to contain letters, numbers, underscores `_`, and hyphens `-` (regex: `[a-zA-Z0-9_\-]+`). Dot `.` is no longer supported.
- **Naming Style**: Recommended to use `slug-style` (e.g., `user-alice-v1`).
- **Globally Unique**: Must be unique across the entire project.
- **Prohibited Characters**: Spaces, slashes `/`, or other special symbols are prohibited.

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
reviewers: [[[bob]], [[alice]]]
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

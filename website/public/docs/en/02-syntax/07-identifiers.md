---
title: Identifiers
---

# Identifier System

Typedown supports two identifier forms: **ID** and **Content Hash**.

## ID

An ID is the name of an entity, used to reference entities within a scope.

### Format

- Any string that doesn't start with `sha256:`
- Allowed characters: letters, numbers, underscores `_`, hyphens `-`
- Not allowed: spaces, slashes `/`, dots `.`

### Styles

| Style | Example | Use Case |
| :---- | :------ | :------- |
| **Simple Name** | `alice` | Small projects, local scope |
| **Slug Style** | `user-alice-v1` | Recommended, namespace clear, globally unique |

### Scoping

ID lookup follows lexical scoping rules:
1. Current file
2. Current directory (`config.td`)
3. Parent directories (recursively upward)
4. Global index

## Content Hash

Content Hash is a SHA-256 hash computed from the entity's content, used for content addressing.

### Format

```
sha256:<64-character hexadecimal string>
```

### Calculation

```
SHA-256( Trim( YAML_Content ) )
```

### Usage

- **Immutable References**: Lock specific versions of content
- **Integrity Verification**: Verify content has not been tampered with
- **History Tracking**: Reference historical versions in `former` field

## Resolution Priority

When a reference `[[target]]` occurs, the resolver processes it in the following order:

1. **Hash Check**: Check if it matches `sha256:...` format. If so, use content addressing directly.
2. **ID Lookup**: Lookup by name in the current scope chain, fallback to global index if not found.

> **Design Intent**: Precise (Hash) beats fuzzy (ID), ensuring reference determinism.

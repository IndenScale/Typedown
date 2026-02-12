---
title: Best Practices
---

# Best Practices

## Identity Layering

| Type | Example | Nature | Purpose |
|------|---------|--------|---------|
| **ID** | `user-alice-v1` | Stable | System identity, cross-system interaction |
| **Hash** | `sha256:8f4b...` | Immutable | Integrity anchor, immutable reference |

## ID Conventions

Recommend using **hierarchical Slug**:

- **Format**: `domain-type-name-version`
- **Examples**:
  - `iam-user-alice-v1`
  - `infra-db-primary-v3`
  - `content-post-hello-world`

## Version Evolution

When modifying entities, link to old versions via `former`:

````typedown
```entity User: user-alice-v2
former: [[user-alice-v1]]
name: "Alice (Updated)"
```
````

## Robust References

Use Hash when publishing immutable configuration packages:

```yaml
base_policy: [[sha256:e3b0c442...]]
```

## Project Structure

```
project/
├── typedown.yaml          # Project configuration
├── config.td              # Root-level config
├── models/                # Model definitions
│   ├── user.td
│   └── config.td          # models directory-level config
├── entities/              # Entity data
│   ├── users/
│   │   ├── alice.td
│   │   └── bob.td
│   └── config.td
└── specs/                 # Validation rules
    └── validation.td
```

## UUID Mapping

When integrating with existing databases, use UUID as metadata field:

```yaml
meta:
  db_uuid: '550e8400-e29b-41d4-a716-446655440000'
```

Keep the `id` field human-readable.

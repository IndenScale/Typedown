---
title: Identity Management
---

# Identity Management Best Practices

Clear **identity strategy** is key to managing complexity in Typedown projects.

## 1. Two Reference Forms

Typedown supports two identifier forms: **ID** and **Content Hash**.

| Form | Example | Nature | Responsibility |
| :--- | :--- | :--- | :--- |
| **ID** | `user-alice-v1` | **Stable** | **System Identity**. Globally unique logical identifier. Used for daily development and cross-entity references. |
| **Content Hash** | `sha256:8f4b...` | **Immutable** | **Integrity Anchor**. Deterministic fingerprint calculated based on content. Used for version locking and history tracking. |

## 2. Robust Addressing Strategy

While daily development mainly uses **ID** for quick writing, **Content Hash** provides unparalleled robustness in high-reliability scenarios.

### Scenario: Baseline Snapshots

When releasing an "immutable configuration package", don't rely on IDs that might be modified. Instead, lock the content Hash.

```yaml
# Reference a specific, tamper-proof configuration version
# Even if users/admin-v1's definition is modified, this reference still points to the old content
base_policy: [[sha256:e3b0c442...]]
```

This **Deterministic Algorithm** ensures that references never point to tampered data.

## 3. ID Assignment Workflow

### Phase 1: Prototyping

Developers use short IDs to quickly write drafts.

````markdown
```entity User: alice
name: "Alice"
```
````

### Phase 2: Hardening

When the entity's structure stabilizes, or it needs to be referenced externally, **use a more explicit ID**.
IDE plugins should provide a `Fix ID` feature to automatically generate Slug-style IDs.

````markdown
```entity User: user-alice-v1
name: "Alice"
```
````

### Phase 3: Evolution

When modifying an entity, link to the old version via `former`.

````markdown
```entity User: users-alice-v2
former: "user-alice-v1"
name: "Alice (Updated)"
```
````

## 4. ID Naming Conventions

We recommend using **Hierarchical Slugs** as IDs.

- **Format**: `domain-type-name-version`
- **Examples**:
  - `iam-user-alice-v1`
  - `infra-db-primary-v3`
  - `content-post-hello-world-draft`

This format naturally supports Namespace management by directory structure and has excellent readability in Git Diffs.

## 5. External System Integration

If Typedown serves as a configuration source for an existing SQL database, database UUIDs can be stored in the entity content.

```yaml
# Signature: entity User: user-alice-v1
# Body:
# Use a dedicated extension field to store physical ID
meta:
  db_uuid: '550e8400-e29b-41d4-a716-446655440000'
```

This maintains the readability of Typedown files while maintaining an anchor to the physical world.

---
title: Identity Management
---

# Identity Management Best Practices

In Typedown projects, clear **Identity Layering** is the key to managing complexity.

## 1. The Identity Layers

We recommend dividing identity into three distinct layers, from the lowest physical hash to the highest logical handle (L0 - L2).

| Level | Term | Example | Nature | Responsibility |
| :----- | :--------------- | :--------------- | :------------- | :---------------------------------------------------------------------------------------------------------------- |
| **L0** | **Content Hash** | `sha256:8f4b...` | **Immutable** | **Integrity Anchor**. Deterministic fingerprint calculated based on content. Regardless of how the ID changes, as long as the content is unchanged, the Hash remains unchanged. |
| **L1** | **System ID** | `user-alice-v1` | **Stable** | **System Identity**. Globally unique logical identifier (Slug) or machine identifier (UUID). It is a stable contract for cross-system interaction. |
| **L2** | **Handle** | `alice` | **Contextual** | **Developer Experience (DX)**. Semantic, short, and locally valid. Use Handle for Dependency Injection (DI) in code as much as possible, but solidify it as L1 during persistence. |

## 2. Robust Addressing

Although daily development mainly uses **L2 (Handle)** for rapid writing, **L0 (Content Hash)** provides unparalleled robustness in high-reliability scenarios.

### Scenario: Baseline Snapshots

When releasing an "immutable configuration package", one should not rely on Slug IDs that might be modified, but should lock the Content Hash instead.

```yaml
# Reference a specific, tamper-proof configuration version
# Even if the definition of users/admin-v1 is modified, this reference still points to the old content
base_policy: [[sha256:e3b0c442...]]
```

This guarantees through a **Deterministic Algorithm** that the reference will never point to tampered data.

## 3. The Promotion Workflow

It is recommended to use IDE plugins to achieve smooth promotion from L2 (Handle) to L1 (System ID).

### Phase 1: Prototyping

Developers only use Handle (L2) to quickly write drafts.

````markdown
```entity User: alice
name: "Alice"
```
````

At this point, the entity has no explicit ID, and the compiler will generate a temporary unstable internal ID.

### Phase 2: Hardening

When the structure of the entity is stable, or it needs to be referenced externally, an **Explicit L1 ID** should be assigned.
The IDE plugin should provide a `Fix ID` function to automatically generate a Slug based on the Handle.

````markdown
```entity User: user-alice-v1
# Uniquify: Assign global, stable logical ID (L1)
# ID has been promoted to Block Signature, id field is no longer included in Body
name: "Alice"
```
````

### Phase 3: Evolution

When modifying an entity, link the old version via `former`.

````markdown
```entity User: users-alice-v2
# Upgrade ID to v2
former: "user-alice-v1"  # Link to old L1 ID
name: "Alice (Updated)"
```
````

## 4. Naming Conventions

We recommend using **Hierarchical Slugs** as Logical IDs.

- **Format**: `domain-type-name-version`
- **Example**:
  - `iam-user-alice-v1`
  - `infra-db-primary-v3`
  - `content-post-hello-world-draft`

This format naturally supports Namespace management by directory structure and has excellent readability in Git Diff.

## 5. UUID Mapping

If Typedown serves as a configuration source for an existing SQL database, UUIDs are essential.
**Do not write UUIDs in the ID field**. It is recommended to store them as hidden metadata or special fields.

```yaml
# Signature: entity User: user-alice-v1
# Body:
# Use a special extension field to store physical ID
meta:
  db_uuid: "550e8400-e29b-41d4-a716-446655440000"
```

This maintains the readability of Typedown files while preserving anchors to the physical world.

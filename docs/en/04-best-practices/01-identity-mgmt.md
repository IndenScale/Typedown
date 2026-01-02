# Identity Management Best Practices

In a Typedown project, clear **Identity Layering** is key to managing complexity.

## 1. The Identity Quadrant

We recommend dividing identity into four clear levels, from physical hashes at the bottom to logical handles at the top.

| Level  | Term             | Example          | Property        | Responsibility                                                                                                                                                                    |
| :----- | :--------------- | :--------------- | :-------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **L0** | **Content Hash** | `sha256:8f4b...` | **Immutable**   | **Integrity Anchor**. A deterministic fingerprint based on content calculation. Regardless of how the ID changes, as long as the content is unchanged, the Hash remains the same. |
| **L1** | **Handle**       | `alice`          | **Contextual**  | **Developer Experience (DX)**. Semantic, short, valid locally. Use Handles for Dependency Injection (DI) in code whenever possible.                                               |
| **L2** | **Slug ID**      | `users/alice-v1` | **Mutable**     | **Versioning**. Human-readable global unique identifier. It is a pointer to a specific Hash.                                                                                      |
| **L3** | **UUID**         | `550e84...`      | **Foreign Key** | **External Anchor (Linking)**. Machine unique. Exists only as Metadata when interfacing with external DBs.                                                                        |

## 2. Robust Addressing Strategy

Although daily development mainly uses **L1 (Handle)** and **L2 (Slug ID)**, **L0 (Content Hash)** provides unparalleled robustness in high-reliability scenarios.

### Scenario: Baseline Snapshots

When you release an "Immutable Configuration Package", you should not rely on Slug IDs that might be modified, but instead lock onto the content Hash.

```yaml
# Reference a specific, tamper-proof configuration version
# Even if the definition of users/admin-v1 is modified, this reference still points to the old content
base_policy: [[sha256:e3b0c442...]]
```

This guarantees that a reference will never point to tampered data through a **Deterministic Algorithm**.

## 3. The Promotion Workflow

We recommend using IDE plugins to achieve smooth promotion from L1 to L2.

### Phase 1: Prototyping

Developers only use Handles to quickly write drafts.

````markdown
```entity User: alice
name: "Alice"
```
````

At this point, the entity has no explicit ID, and the compiler will temporarily generate an unstable ID (e.g., `file_path::alice`).

### Phase 2: Hardening

When the entity structure stabilizes or needs to be referenced externally, you should **explicitly assign a Logical ID**.
The IDE plugin should provide a `Fix ID` feature to automatically generate a Slug based on the Handle.

````markdown
```entity User: alice
# Uniquify: Assign a global, stable logical ID
id: "users/alice-v1"
name: "Alice"
```
````

### Phase 3: Evolution

When you need to modify an entity, link the old version via `former`.

````markdown
```entity User: alice
id: "users/alice-v2"
former: "users/alice-v1"  # Link to the old Logical ID
name: "Alice (Updated)"
```
````

## 4. ID Naming Conventions

We recommend using **Hierarchical Slugs** as Logical IDs.

- **Format**: `domain/type/name-version`
- **Example**:
  - `iam/user/alice-v1`
  - `infra/db/primary-v3`
  - `content/post/hello-world-draft`

This format naturally supports Namespace management by directory structure and has excellent readability in Git Diff.

## 5. UUID Mapping

If Typedown serves as a configuration source for an existing SQL database, UUIDs are essential.
**Do not write UUIDs in the ID field**. It is recommended to store them as hidden metadata or dedicated fields.

```yaml
id: "users/alice-v1"
# Use a dedicated extension field to store the physical ID
meta:
  db_uuid: "550e8400-e29b-41d4-a716-446655440000"
```

This maintains the readability of Typedown files while preserving anchors to the physical world.

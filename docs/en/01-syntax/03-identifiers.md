# Identifiers

The core philosophy of Typedown is **Progressive Formalization**, which is deeply reflected in its identifier system. We use identifiers of varying precision to refer to things at different stages and in different scenarios.

## The Identifier Spectrum

We define four core identifiers, with their precision increasing and ease of use decreasing:

| Type   | Name                   | Location               | Characteristics                    | Typical Scenario                                               |
| :----- | :--------------------- | :--------------------- | :--------------------------------- | :------------------------------------------------------------- |
| **L1** | **Handle**             | Code Block Header      | Local, Volatile, Short             | Development phase, code block declaration, local reference     |
| **L2** | **Slug (Logical ID)**  | Entity Body (`id`)     | Global, Stable, Readable           | Cross-file reference, long-term maintenance, version evolution |
| **L3** | **UUID**               | Entity Body (`uuid`)   | Global, Unique, No Semantics       | Database primary key, scenarios without manual intervention    |
| **L0** | **Hash (Fingerprint)** | Immutable (Calculated) | Absolute, Deterministic, Immutable | Release artifacts, dependency locking, content addressing      |

### 1. Handle (L1)

**Handle** is the first interface for developers interacting with code blocks. Defined via colon syntax.

- **Syntax**: `BlockType: Handle`
- **Scope**: Defaults to file-level private (Local Scope), unless explicitly exported.
- **Usage**: Provides a memorable name for quick reference in the current context.

````markdown
<!-- "User" and "alice" are Handles -->

```model:User
...
```

```entity User: alice
...
```
````

### 2. Slug (Logical ID, L2)

**Slug** is the stable anchor of an entity in space-time. When an entity matures, it should have an explicit logical ID.

- **Syntax**: Define `id: "path/to/identity"` in Entity Body.
- **Constraint**: Globally unique. Usually adopts a URL-like path structure.
- **Evolution**: Use `former: ["old-slug"]` to track ID renaming, ensuring continuity of historical references.

````markdown
```entity User: alice
# This is a Slug, it is the official ID card of this entity
id: "users/alice-v1"
name: "Alice"
```
````

### 3. Hash (Content Fingerprint, L0)

**Hash** is the mathematical digest of content. It is objective truth, independent of human will.

- **Generation**: `SHA-256(Canonical_Body)`.
- **Usage**: Ensures the reference points to **a specific state at a specific moment**.

When you use a Hash in a reference (`[[sha256:abc...]]`), you are no longer referencing "that person called Alice" (she might change), but referencing "the snapshot of Alice's data at that moment in that state".

### 4. UUID (L3)

**UUID** is the final fallback identifier.

- **Usage**: Use UUID when you are too lazy to name (Handle), don't want to maintain a logical path (Slug), and content changes frequently (Hash is unstable).
- **Automation**: Usually generated automatically by tools; humans should avoid manual handling.

## Identifier Resolution Priority

When a reference `[[target]]` occurs, the parser follows this priority:

1. **Hash Check**: If it is `sha256:...`, perform content addressing (L0) directly.
2. **Handle Lookup**: Look for a matching Handle in the current file and Context (L1).
3. **Slug/UUID Lookup**: Look for a matching ID in the global index (L2/L3).

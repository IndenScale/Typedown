---
title: Identifiers
---

# Identifier System (Identifiers)

Typedown uses identifiers of varying precision at different stages.

## Identifier Types

We define identifiers as three different **Resolution States**:

| Level | Strategy | Stage | Characteristics |
| :--- | :--- | :--- | :--- |
| **L0** | Hash | Runtime | **Absolute**. Content-based hash validation. |
| **L1** | Exact | Compiler | **Precise**. Unique string indexing. |
| **L2** | Fuzzy | Editing | **Inference**. Context-based derivation. |

> **Tip**: The essential difference between L2 (Handle) and L1 (System ID) is **whether fuzzy matching is allowed**.
>
> - During **IDE Input**, you type `alice` (L2), and the completion tool recognizes it as `user-alice-v1`.
> - During **File Save**, it must be solidified as `user-alice-v1` (L1) in the code for precise parsing by the compiler.

### System ID Styles

For the compiler kernel, **Name, Slug, and UUID are essentially no different**; they are all string keys for **L1 System ID**. The choice of style depends purely on project conventions:

- **Name Style**: `alice` (Short, but prone to conflicts in large projects)
- **Slug Style**: `user-alice-v1` (Recommended, clear namespace)
- **UUID Style**: `550e84...` (Machine-generated, no semantics)

Whichever style is chosen, as long as it is globally unique and precisely referenced, it is an **L1 System ID**.

## Identifier Resolution Priority

When a reference `[[target]]` occurs, the parser strictly follows the **L0 -> L1 -> L2** order:

1. **L0 Check (Hash)**: Checks if it matches `sha256:...` format. If so, proceeds with content addressing directly.
2. **L1 Check (ID)**: Exact lookup for corresponding `id` or `uuid` in the global index.
3. **L2 Check (Handle)**: Fuzzy match lookup for Handle in the local context.

> **Design Intent**: Precision over fuzziness, global over local. This ensures the determinism of references while preserving the flexibility of the development experience.

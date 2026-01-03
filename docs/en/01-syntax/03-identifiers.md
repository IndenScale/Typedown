# Identifiers

The core philosophy of Typedown is **Progressive Formalization**, which is deeply reflected in its identifier system. We use identifiers of varying precision to refer to things at different stages and in different scenarios.

## The Identifier Spectrum

We define identifiers as three distinct **Resolution States**, rather than just differences in format.

| Level  | Resolution Strategy | Phase                | Behavior                                                                                    |
| :----- | :------------------ | :------------------- | :------------------------------------------------------------------------------------------ |
| **L0** | **Hash Match**      | Runtime / Distribute | **Absolute Anchor**. Exact verification based on content Hash.                              |
| **L1** | **Exact Match**     | Persist / Compile    | **Exact Index**. Requires a globally unique string match.                                   |
| **L2** | **Fuzzy Match**     | Edit / IDE           | **Fuzzy Inference**. Temporary state during developer input, relying on context derivation. |

> **Core Insight**: The essential difference between L2 (Handle) and L1 (System ID) lies in **whether fuzzy matching is allowed**.
>
> - During **IDE Input**, you type `alice` (L2), and the completion tool identifies it as `user-alice-v1`.
> - During **File Save**, the code must settle into `user-alice-v1` (L1) for precise compiler resolution.

### System ID Styles

For the compiler kernel, **Name, Slug, and UUID make no difference**; they are all string Keys serving as **L1 System ID**. The choice of style depends purely on project conventions:

- **Name Style**: `alice` (Short, but prone to conflict in large projects)
- **Slug Style**: `user-alice-v1` (Recommended, clear namespace)
- **UUID Style**: `550e84...` (Machine-generated, no semantics)

Regardless of the style chosen, as long as it is globally unique and precisely referenced, it is an **L1 System ID**.

## Resolution Priority

When a reference `[[target]]` occurs, the parser strictly follows the **L0 -> L1 -> L2** sequence:

1. **L0 Check (Hash)**: Checks if it matches `sha256:...` format. If so, performs content addressing.
2. **L1 Check (ID)**: Performs an exact lookup for a matching `id` or `uuid` in the global index.
3. **L2 Check (Handle)**: Performs a fuzzy match for a Handle in the local context.

> **Design Intent**: Precision over vagueness, Global over Local. This ensures reference determinism while preserving flexibility in developer experience.

# Entity Reference & Linking

Typedown supports powerful entity reference functionality via `[[]]` syntax, which is the core of building a connected documentation network. It treats references as a **`query`**.

## Basic Reference Syntax (`[[query]]`)

Use double brackets `[[query]]` to reference other Entities. This `query` can be an ID, name, or a more complex condition expression.
This is not just a hyperlink, but a semantically **strong association**. The compiler verifies the validity of the `query`.

*   **Reference Entity**: `[[Query Condition]]`
*   **Reference Entity Field**: `[[Query Condition.Field Name]]`

```markdown
# Reference Example

Here references admin [[Alice]].
Admin [[Alice]].name's name is [[Alice.name]].
```

## Reference Resolution Mechanism

### 1. Fuzzy Matching

Typedown's powerful reference resolution engine supports fuzzy matching. When `[[query]]` is not completely precise, the compiler and LSP will attempt to search for the most likely match in the symbol table.

*   **ID Fuzzy Matching**: `[[feat_login]]` can match `feat_login_v3`.
*   **Name Fuzzy Matching**: `[[Alice]]` can match an Entity with `id: u_001` and `name: "Alice"`.
*   **Field Fuzzy Matching**: `[[hero.hp]]` can intelligently match the `hit_points` field of the `hero` Entity, if aliases or fuzzy matching settings exist.

This mechanism greatly facilitates writers, reducing the need for hardcoded IDs.

### 2. Ambiguity Check & Reporting

Due to fuzzy matching, a `[[query]]` may match zero, one, or multiple entities.
*   **Zero Matches**: Compiler reports `ReferenceNotFound` error.
*   **Multiple Matches**: Compiler reports `AmbiguousReferenceError` error.
    *   The LSP plugin will display squiggly lines and error hints in the editor to guide the user to fix the `query`.
    *   `extension` and `compiler` work together to ensure all references have a unique and clear resolution path.

## Reference Version Strategy

In evolution chains using the `former` mechanism, references to the same concept (e.g., `[[feat_login]]`) may correspond to multiple historical versions.

**Default Behavior: Resolve to Latest**
*   When a `[[query]]` matches multiple versions of an entity family, the Typedown compiler defaults to resolving to the **Tip of the Chain** of that entity family.
*   **Pros**:
    *   **Semantic Consistency**: Ensures documentation validation logic is always based on the latest facts. If documentation logic becomes inconsistent due to latest data, this usually means the documentation itself needs updating or `spec` needs adjustment, promoting "progressive formalization".
    *   **Simplified Writing**: Authors don't need to manually update all references to point to the latest `_v3`, `_v4`.
*   **Cons**:
    *   Historical documents, when read, may have their reference content change with the latest version if not version-locked.

### Explicitly Referencing Specific Versions

If you must reference a specific snapshot in history, use a `query` that uniquely identifies that version.
*   `[[feat_login_v1]]`: Explicitly points to version V1.
*   `[[User where id="u_001_v2"]]`: Uses a more precise query condition.

## Complex Reference Maintenance

As the project scales, reference relationships become complex. Typedown suggests and supports the following maintenance strategies:

### Version Suffix Naming Convention

It is recommended to use the `_v<Version Number>` suffix format to manage Entity ID evolution to improve readability and traceability.

*   `u_001_v1`
*   `u_001_v2`
*   `u_001_v2.1`

### Historical Query & Refactoring

IDE plugins should support `Find All References` and `Rename Symbol`.
When an Entity ID changes (e.g., fixing spelling), the toolchain should be able to automatically update all `[[query]]` references pointing to that Entity via LSP, keeping semantics invariant as much as possible.

# Entity Reference & Linkage

Typedown supports powerful entity reference functionality via `[[]]` syntax. References are resolved during the **Validate (Stage 3)** phase of the compiler pipeline using topological sorting to ensure all dependencies are materialized.

## 1. Reference Modes

Depending on the query structure, a reference resolves to different types of data:

### 1.1 Symbolic Link (`[[ID]]`)

- **Behavior**: Returns the **ID string** of the target symbol.
- **Usage**: Used to establish relations/pointers without duplicating data.
- **Example**: `owner: [[Alice]]` resolves to `owner: "Alice"`.

### 1.2 Value Lookup (`[[ID.path]]`)

- **Behavior**: Navigates through the target's data and returns the **specific value**.
- **Indexing**: Supports list indexing via `[n]`.
- **Example**:
  - `[[Project.version]]` -> `"1.0.0"`
  - `[[Farm.apples[0].weight]]` -> `0.5`

### 1.3 Data Inlining (`[[ID.path.*]]`)

- **Behavior**: Serializes the target object (or sub-object) into a **full dictionary/object**.
- **Example**: `config: [[GlobalConfig.*]]` deep-copies the entire configuration object.

## 2. Reference Resolution

### 2.1 ID-Based Precision

References must match a unique `id` defined in the global symbol table. IDs can be defined in:

- Entity block headers or bodies.
- Model block headers (`model id=X`).
- Spec block headers (`spec id=Y`).

### 2.2 Compilation Pipeline

1. **Scanner (Stage 1)**: Collects all symbols and builds the initial symbol table.
2. **Linker (Stage 2)**: Resolves types and executes models.
3. **Validator (Stage 3)**:
   - Builds a **Dependency Graph** of all `[[ ]]` references.
   - Performs **Topological Sort**.
   - Detects and reports **Circular Dependencies**.
   - Materializes data in order.

## 3. Toolchain Support

The LSP (Language Server Protocol) implementation provides:

- **Go to Definition**: Jump from `[[ID]]` to the source code block.
- **Find All References**: See where a symbol is being used.
- **Autocomplete**: Suggest IDs from the symbol table while typing `[[`.

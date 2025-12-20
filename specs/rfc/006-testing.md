# Testing & Validation Pipeline

In Typedown, "testing" is not merely running unit tests. It is the execution of the full **Compiler Pipeline**. The command `td test` performs a comprehensive static and dynamic analysis of the entire project, ensuring structural integrity, reference correctness, and logical validity.

## 1. The Compilation Pipeline

When you run `td test`, Typedown executes a rigorous 4-stage process:

### Phase 1: Scanning (Symbols)

**Goal**: Discovery and Indexing.

- Scans the project directory for `.td`, `.md`, and `.py` files.
- Parses all Markdown/Typedown files to extract code blocks:
  - `entity`: Data instances.
  - `model`: Type definitions (Python/Pydantic).
  - `spec`: Test logic.
- Builds a raw **Symbol Table**, identifying every resource by its unique ID.

### Phase 2: Linking (Resolution)

**Goal**: Context Construction.

- **Config Loading**: Executes `typedown.toml` and project-level Python configurations.
- **Import Hooks**: Activates the custom Import Hook to allow virtual imports (e.g., `from typedown.entities import ...`).
- **Model Execution**: Runs all `model` blocks to register Pydantic classes and validators in the memory space.
- **Graph Construction**: Scans all `entity` data for `[[Reference]]` syntax and builds a **Dependency Graph**.

### Phase 3: Validation (Entities)

**Goal**: Data Integrity.

- **Topological Resolution**: Resolves dependencies in order. If Entity A references Entity B, B is processed first.
- **Reference Injection**: Replaces `[[ID]]` or `[[ID.field]]` placeholders with actual values from the target entity.
- **Schema Validation**: (Planned) Instantiates the corresponding Pydantic Model for each Entity. This runs all `field_validator` and `model_validator` checks defined in your `model` blocks.
- **Dangling Reference Check**: Ensures no reference points to a non-existent ID.

### Phase 4: Execution (Specs)

**Goal**: Logic Verification.

- Only if the previous 3 phases pass does Typedown proceed to this stage.
- Extracts `spec` blocks into temporary Python files.
- Injects the fully compiled **Compiler Context** (often called `session` or `compiler` in fixtures).
- Invokes **Pytest** to run these files.

---

## 2. Writing Specs

Specs are Python code blocks tagged with `spec`. They are the place for cross-entity logic and complex business rule verification.

### The `session` Fixture

The test runner automatically injects a `session` fixture (or `compiler`), which provides access to the fully resolved Symbol Table and Entity Graph.

```python
# The 'session' object is the Compiler instance from the pipeline above
def test_all_monsters_have_valid_drops(session):
    # Query the resolved data
    # .get_entities_by_type() returns a list of attribute-accessible objects
    items = session.get_entities_by_type("Item")
    monsters = session.get_entities_by_type("Monster")

    item_ids = {item.id for item in items}

    for monster in monsters:
        for drop_id in monster.drops:
            assert drop_id in item_ids, f"Monster {monster.name} drops unknown item {drop_id}"
```

### Implicit Imports

The environment is pre-configured with standard testing libraries.

- `pytest`: Available globally (no need to `import pytest`).
- Project Modules: All paths defined in `typedown.toml` or the project root are added to `sys.path`.

---

## 3. Inline Checks

For simple, single-entity assertions, you can use the `check` block. This is syntactic sugar that compiles down to a test case running in Phase 4.

````markdown
```entity:User
id: "admin"
age: 30
```

```check
# 'entity' is bound to the immediately preceding entity
assert entity.age >= 18
assert "admin" in entity.roles
```
````

## 4. CLI Usage

The `td test` command is the entry point for this pipeline.

```bash
# Run the full pipeline (Scan -> Link -> Validate -> Execute)
td test

# Run only specific specs matching a tag/marker
td test -t smoke

# Run on a specific directory (recursive)
td test ./content/rpg
```

If any stage fails (e.g., a broken reference in Phase 3), the pipeline halts immediately, and no specs (Phase 4) are executed. This ensures you never test against broken data.

## 5. Manifest & Scope Control

For large projects, running the full pipeline every time is inefficient. You can define named execution scopes in `typedown.toml` under the `[scripts]` section.

### Script Definition

A script acts as a preset for the Compiler. It distinguishes between the **Target Set** (files to fully validate and test) and the **Context Set** (files needed for reference resolution).

```toml
# typedown.toml

[scripts]
# 'td test :core'
core = { include = ["src/core"], exclude = ["**/deprecated"], tags = ["critical"] }

# 'td test :isolated' - Strict mode (no global context)
isolated = { include = ["src/utils"], strict = true }
```

### Reference Resolution Strategy

You might ask: *If I limit scope to `src/core`, but it references `[[User]]` in `src/auth`, does the build fail?*

Typedown handles this via a **Hybrid Scanning Strategy**:

1.  **Global Shallow Scan (Default)**: 
    *   The compiler performs a fast, lightweight scan of the *entire project* to build the **Symbol Index**. 
    *   It knows where `[[User]]` exists but does not validate `src/auth` or run its tests.
    *   **Result**: References work seamlessly. `src/core` is fully validated, while `src/auth` serves as read-only context.

2.  **Strict Mode (`strict = true`)**:
    *   The compiler *only* looks at files in `include`.
    *   References to outside entities become **Dangling Reference Errors**.
    *   Use this for isolated modules that must be self-contained.

### Usage

Use the `:` syntax to invoke a script definition from the CLI.

```bash
# Run the 'core' script definition
td test :core
```

This effectively tells the compiler: "Resolve symbols globally, but only **Validate** and **Test** files in `src/core`."

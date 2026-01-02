# Example 01: RPG Game (Lite)

This example demonstrates a more complex Typedown setup for a small RPG game.
It introduces:

1. **References**: Linking Entities using `[[slug]]` syntax.
2. **Specs**: Defining validation rules to ensure data integrity.

## Contents

- `00_models.td`: Defines `Character` and `Item` models.
- `01_world.td`: Instantiates characters and items with stable IDs.
- `02_rules.td`: Contains validation logic (Specs) using inline Python.
- `03_narrative.td`: Demonstrates **Evolution Semantics** (`former`) and how narrative prose surrounds structured data.

## How to Run

### 1. Inspect Data & References

Parse the world and see how references are resolved.

```bash
td inspect examples/01_rpg_game/01_world.td
```

### 2. Validate Rules

Run the specs to ensure all characters and items obey the rules defined in `02_rules.td`.

```bash
td validate examples/01_rpg_game
```

If you modify `01_world.td` to set a Character's HP to -10, `td validate` will report an error!

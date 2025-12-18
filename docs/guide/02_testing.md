# Testing & Validation

Typedown allows you to write tests directly alongside your documentation. This ensures that your specifications are not just text, but executable contracts.

## 1. The `spec` Block

Use the `spec` block to write test logic using **Python** and **Pytest**.

````markdown
```spec
def test_character_level_limit(workspace):
    # Retrieve all instances of RPGCharacter
    chars = workspace.get_entities_by_type("RPGCharacter")
    
    for char in chars:
        assert char.level <= 100, f"Character {char.id} exceeds level limit"
```
````

## 2. The `workspace` Fixture

Typedown automatically injects a `workspace` fixture into your tests. This object provides access to the entire parsed state of your project.

**Common Methods:**
*   `workspace.get_entity(id: str) -> EntityBlock`: Get a single entity by ID.
*   `workspace.get_entities_by_type(class_name: str) -> List[Any]`: Get all entities of a specific type (resolved objects).

## 3. Running Tests

Use the CLI command to execute all spec blocks in your project.

```bash
td test .
```

This command:
1.  Parses all Markdown files.
2.  Resolves all entities and dependencies.
3.  Extracts `spec` blocks into a temporary test suite.
4.  Runs `pytest` and reports results.

# Testing Mechanism

One of Typedown's core pillars is logic verification. To handle complex business rules and cross-entity constraints, Typedown integrates **Pytest** as its testing engine.

## 1. Validation Levels

Typedown distinguishes between two levels of validation:

1.  **Internal Validation (Validator)**:
    *   **Focus**: Data correctness within a single Entity (e.g., field types, value ranges, formats).
    *   **Implementation**: Defined directly in the `model` using Pydantic's `field_validator` or `model_validator`.
    *   **Execution**: Automatically executed during compilation (when parsing the Entity).

2.  **Specification Validation (Specification)**:
    *   **Focus**: Cross-entity consistency, complex business rules, system-level constraints (e.g., foreign key existence, numerical balance).
    *   **Implementation**: Written as standard Pytest test cases using `spec` code blocks.
    *   **Execution**: Executed when running the `td test` command.

## 2. Spec Code Blocks

Use the `spec` tag on code blocks to write testing logic. These blocks are essentially Python scripts that are extracted and run as Pytest test files.

````markdown
```spec
# Auto-injected: pytest, session
# No need to manually import pytest

# Write standard Pytest test functions
# 'session' is a system-injected Fixture containing the entire project's data
def test_all_monsters_have_valid_drops(session):
    items = session.table("Item")
    monsters = session.table("Monster")
    
    for monster in monsters:
        for drop_id in monster.drops:
            assert drop_id in items, f"Monster {monster.name} drops unknown item {drop_id}"
```
````

### Auto-injection & Context
*   **Fixture**: Test functions can request system-provided Fixtures. The most critical one is `session` (or `workspace`), which provides access to all parsed Entities.
*   **Imports**: The execution environment includes `pytest` by default. You can use `@pytest.mark...` directly without writing an import statement.

## 3. Organization & Markers

Leverage Pytest's Marker mechanism to flexibly organize and filter test cases.

````markdown
```spec
# Again, the pytest module is auto-injected

@pytest.mark.smoke
def test_basic_integrity(session):
    assert len(session.entities) > 0

@pytest.mark.rpg
@pytest.mark.balance
def test_boss_difficulty(session):
    # ...
```
````

Use the CLI command `td test -m smoke` to run only tests with the `smoke` marker.

## 4. Inline Check (Optional)

For quick assertions targeting a specific Entity, use the `check` block. It automatically converts into a test case for the immediately preceding Entity.

````markdown
```entity:User
id: "admin"
age: 30
```

```check
# The 'entity' variable is automatically bound to the User instance above
assert entity.age >= 18
```
````

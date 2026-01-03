# RPG Rules

This file demonstrates how to enforce business logic using `spec` blocks.

```spec
# @target is automatically available in spec blocks
@target(type="Character")
def validate_character_stats(subject):
    # Ensure HP is logical
    assert subject.hp > 0, f"Character {subject.name} must have positive HP"
    assert subject.hp <= subject.max_hp, f"Character {subject.name} HP ({subject.hp}) cannot exceed max ({subject.max_hp})"

@target(type="Item")
def validate_item_physics(subject):
    # Ensure physical properties are logical
    assert subject.weight >= 0, f"Item {subject.name} cannot have negative weight"
```

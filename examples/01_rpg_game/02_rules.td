# RPG Rules

This file demonstrates how to enforce business logic using `spec` blocks.

```spec:game_rules
# @target is automatically available in spec blocks
@target(type="Character")
def validate_character_stats(char):
    # Ensure HP is logical
    assert char.hp > 0, f"Character {char.name} must have positive HP"
    assert char.hp <= char.max_hp, f"Character {char.name} HP ({char.hp}) cannot exceed max ({char.max_hp})"

@target(type="Item")
def validate_item_physics(item):
    # Ensure physical properties are logical
    assert item.weight >= 0, f"Item {item.name} cannot have negative weight"
```

# RPG Campaign Specifications

This file contains the Python-based spec blocks for the RPG campaign use case,
migrated from the old YAML-based `spec:Rule` definitions.

```spec
from models.schema import Monster, Item

def test_monster_hp_positive(workspace):
    """
    Test: All monsters must have positive HP.
    """
    monsters = workspace.get_entities_by_type("Monster")
    for monster_entity in monsters:
        monster = monster_entity.resolved_data
        assert monster.hp > 0, f"Monster {monster.id} ({monster.name}) has non-positive HP ({monster.hp})!"

def test_item_max_weight_limit(workspace):
    """
    Test: Items should not exceed a certain weight limit.
    This test is an example of failure, as some items might intentionally exceed the limit.
    """
    items = workspace.get_entities_by_type("Item")
    limit = 1.5 # From the old spec:Rule params
    for item_entity in items:
        item = item_entity.resolved_data
        assert item.weight <= limit, f"Item {item.id} ({item.name}) has weight {item.weight} exceeding limit {limit}!"
```

# RPG Campaign Specifications

This file contains the Python-based spec blocks for the RPG campaign use case,
migrated from the old YAML-based `spec:Rule` definitions.

```spec
from models.schema import Monster, Item
import pytest

@pytest.mark.rpg
def test_monster_hp_positive(workspace):
    """
    Test: All monsters must have positive HP.
    """
    monsters = workspace.get_entities_by_type("Monster")
    for monster in monsters:
        assert monster.hp > 0, f"Monster {monster.name} has non-positive HP: {monster.hp}"

@pytest.mark.rpg
def test_item_max_weight_limit(workspace):
    """
    Test: Items should not exceed a certain weight limit.
    This test is an example of failure, as some items might intentionally exceed the limit.
    """
    items = workspace.get_entities_by_type("Item")
    limit = 1.5 # From the old spec:Rule params
    for item in items:
        # We expect this to fail for "Sword of Iron" (weight 2.0)
        assert item.weight <= limit, f"Item {item.name} weight {item.weight} exceeds limit {limit}!"
```

# RPG Campaign Specifications

This file contains the Python-based spec blocks for the RPG campaign use case,
migrated from the old YAML-based `spec:Rule` definitions.

```spec
from models.schema import Monster, Item
import pytest

# Note: @target is handled by the framework logic.
# We don't import it because it's replaced before runtime,
# but the IDE might complain, so we can define a dummy if needed
# or just rely on Typedown's magic context.
# We will assume Typedown framework does not require importing target.

@target(type="Monster")
def test_monster_hp_positive(subject: Monster):
    """
    Test: All monsters must have positive HP.
    """
    # The framework injects 'subject' which is the matching Entity
    assert subject.hp > 0, f"Monster {subject.name} has non-positive HP: {subject.hp}"

@target(type="Item")
def test_item_max_weight_limit(subject: Item):
    """
    Test: Items should not exceed a certain weight limit.
    This test is an example of failure, as some items might intentionally exceed the limit.
    """
    limit = 1.5
    # We expect this to fail for "Sword of Iron" (weight 2.0)
    assert subject.weight <= limit, f"Item {subject.name} weight {subject.weight} exceeds limit {limit}!"
```

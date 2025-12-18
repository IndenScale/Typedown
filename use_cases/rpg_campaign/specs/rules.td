# Game Design Rules

Constraints for the RPG system.

```spec:Rule
id: "rule_monster_hp_positive"
description: "All monsters must have positive HP."
target: "entity:Monster"
check: "specs.checks.check_positive_hp"
severity: "error"
```

```spec:Rule
id: "rule_item_lightweight"
description: "Items should be light (Example of Failure)."
target: "entity:Item"
check: "specs.checks.check_max_weight"
params:
  limit: 1.5
severity: "warning"
```

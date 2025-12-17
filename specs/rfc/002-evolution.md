# Evolution Mechanism

Typedown allows describing data changes incrementally, which is one of its core features.

## Time Dimension: `former` (Linear Evolution)

When describing the state changes of the same entity over time, use `former` to point to the previous snapshot of that entity.

**Core Rule: Any state change must create a new entity and have an independent `entity id`.**
This ensures that every `entity id` is an immutable snapshot of that entity at a specific point in time. The compiler automatically merges fields based on `id` history when processing `former`.

````markdown
# V1.0: Initial State
```entity:Feature
id: "feat_login_v1"
status: "planned"
priority: "high"
```

# V1.1: State Change - Priority Adjustment
```entity:Feature
id: "feat_login_v2" # New ID
former: "feat_login_v1"
priority: "medium" # Only list changed fields
```

# V1.2: State Change - Status Update
```entity:Feature
id: "feat_login_v3" # New ID
former: "feat_login_v2"
status: "implemented"
```
````

### Divergence of `former` Chains (Code Smell)

The `former` chain describes the evolution of an entity on a single timeline. Therefore, **any divergence of a `former` chain is considered a "Code Smell"**, which usually implies semantic inaccuracy or improper usage.

*   **Degree 1 Divergence (Info)**: The same `former` is referenced by two different entities. Treated as an `info` level hint, allowed but needs attention. E.g., `A -> B` and `A -> C`.
*   **Degree 2 Divergence (Warning)**: An entity references a `former` that has already diverged once. Treated as a `warning` level hint.
*   **Degree 3+ Divergence (Error)**: Treated as an `error` level error, usually meaning serious logical issues, should be modified to `derived_from`.

**When to Avoid Divergence:**
If you find you need to create multiple independent subsequent states for the same `former`, it likely indicates you are describing a new entity rather than the evolution of the same entity. In this case, you should use `derived_from` or create a completely new ID for the new entity, breaking the `former` chain.

## Type Dimension: `derived_from` (Tree Derivation)

Use `derived_from` when describing an entity that is a variant of another entity or structurally inherits from another entity. `derived_from` itself implies diversity and branching, so chain divergence is normal.

**Core Rule: Derived entities must also have independent `entity ids`.**
The semantics of `derived_from` are closer to inheritance in Object-Oriented Programming. Derived entities inherit all fields from the base entity and can override or add new fields.

````markdown
```entity:Enemy
id: "goblin_base"
name: "Goblin"
hp: 100
attack: 10
type: "normal"
```

# Variant 1: Grunt Goblin
```entity:Enemy
id: "goblin_grunt" # New ID
derived_from: "goblin_base"
name: "Grunt Goblin"
# hp, attack inherited from goblin_base
```

# Variant 2: Goblin Boss (Override attributes and add new ones)
```entity:Enemy
id: "goblin_boss" # New ID
derived_from: "goblin_base"
name: "Goblin Boss"
hp: 500  # Override base class attribute
attack: 30
loot: ["gold_key", "goblin_crown"] # Added attribute
```
````

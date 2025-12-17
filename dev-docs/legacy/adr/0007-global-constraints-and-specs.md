# 0007-global-constraints-and-specs.md

## Status

Accepted

## Context

We need to implement **P2: Global Constraints Integration**. 
Currently, Typedown performs Schema Validation (P1) which ensures individual entities match their Pydantic models. However, we lack a mechanism to verify logic *across* entities (e.g., "Total BOSS count < 3") or enforce complex business rules (e.g., "All NPCs must have an avatar").

We need a design that:
1.  Keeps data files (`docs/*.md`) clean and readable.
2.  Allows flexible binding of rules to entities.
3.  Supports contextual severity (e.g., a rule is a Warning in Dev but an Error in Release).

## Decision

### 1. Spec as First-Class Citizen
We introduce a new block type: `spec:Rule` (or just `spec`).
Specs should be defined in dedicated files, preferably in a `specs/` directory, to separate **Data** from **Constraints**.

### 2. Spec Definition Syntax
Specs use a YAML-based configuration to bind Python logic to data entities.

```yaml
```spec:Rule
id: "rule_boss_hp_limit"
description: "Ensure Bosses have sufficient HP"

# Selector: Defines which entities this rule applies to.
# This implements Inversion of Control (Spec selects Data).
target: "entity:Monster[type='Boss']" 

# Implementation: Refers to a Python function in specs/ directory
check: "specs.combat.check_min_hp"
params:
  threshold: 5000

# Contextual Severity: Logic level depends on the running environment (tags)
severity:
  default: "warning"   # 'td validate'
  release: "error"     # 'td validate --tags release'
  dev: "info"          # 'td validate --tags dev'
```
```

### 3. Implementation Logic (Python)
Constraints are implemented as pure Python functions that accept the target entity and context.

```python
# specs/combat.py
def check_min_hp(entity, context, params):
    # logic...
    return True, "OK"
```

### 4. Runner Logic
The `validate` command will be updated to:
1.  Load all `spec` blocks.
2.  For each spec, query the `symbol_table` using the `target` selector (e.g., filter by class_name or arbitrary fields).
3.  Execute the linked Python function for each matching entity.
4.  Determine final severity based on CLI tags (`--tags`).
5.  Report results.

## Consequences

1.  **New Parser Rule**: The Parser needs to support `spec:` code blocks.
2.  **Selector Engine**: We need a simple query engine to filter entities (e.g., by class name or attribute values).
3.  **Test Runner**: `Workspace` needs a semantic validation phase that runs these specs after Pydantic validation.
4.  **Separation of Concerns**: Data remains pure; Rules are centralized. This greatly improves maintainability.

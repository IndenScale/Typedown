---
title: Validation Rules
---

# Validation Rules

Typedown provides three-layer validation, from single fields to global aggregation:

| Layer | Mechanism | Scope | Typical Scenario |
|-------|-----------|-------|------------------|
| **Field-level** | `@field_validator` | Single field | Email format, numeric range |
| **Model-level** | `@model_validator` | Single entity | Multi-field joint constraints |
| **Global-level** | `spec` | Entire graph | Aggregate statistics, cross-entity rules |

---

## 1. Field-level Validation (Field Validator)

Use Pydantic's `@field_validator` to validate single field values:

```python
from pydantic import field_validator

class User(BaseModel):
    email: str
    age: int
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        if '@' not in v:
            raise ValueError('Invalid email format')
        return v
    
    @field_validator('age')
    @classmethod
    def validate_age(cls, v: int) -> int:
        if v < 0 or v > 150:
            raise ValueError('Invalid age range')
        return v
```

---

## 2. Model-level Validation (Model Validator)

Use `@model_validator` to validate multi-field joint constraints within a single entity:

```python
from pydantic import model_validator

class TimeRange(BaseModel):
    start: datetime
    end: datetime
    
    @model_validator(mode='after')
    def check_time_order(self):
        if self.end <= self.start:
            raise ValueError('End time must be later than start time')
        return self
```

Model-level validation traverses the entity graph by reference, ensuring internal consistency of each entity instance.

---

## 3. Global-level Validation (Spec)

`spec` code blocks are used to define complex constraints requiring **global aggregate statistics**, written in Pytest style.

### Syntax

````typedown
```spec:<TestID>
@target(type="ModelName", scope="local|global")
def <TestID>(subject):
    assert condition, "Error message"
```
````

### Local Scope (Local Mode)

Execute once for each matching entity, validating entity-level business rules:

```python
@target(type="User", scope="local")
def check_admin_mfa(subject: User):
    """Every admin must enable MFA"""
    if subject.role == "admin":
        assert subject.mfa_enabled, f"Admin {subject.name} must enable MFA"
```

### Global Scope (Global Mode)

Execute once for the entire graph, suitable for **aggregate statistics** constraints:

```python
@target(type="Item", scope="global")
def check_total_weight_limit(subject):
    """Total weight of all Items must not exceed limit"""
    result = sql("SELECT sum(weight) as total FROM Item")
    total = result[0]['total']
    assert total <= 10000, f"Total weight ({total}) exceeds limit 10000"
```

### Global Validation Utilities

#### `query(selector)`

Used for simple ID queries or property access:

```python
user = query("user-alice-v1")
managers = query("users/*.manager")
```

#### `sql(query_string)`

Integrates **DuckDB** engine for SQL aggregate queries:

```python
@target(type="Order", scope="global")
def check_daily_order_limit(subject):
    # Count total orders today
    result = sql("""
        SELECT count(*) as cnt FROM Order 
        WHERE created_at >= date('now')
    """)
    assert result[0]['cnt'] <= 1000, "Today's order count exceeds limit"
```

#### `blame(entity_id, message)`

When global validation fails, specify the responsible entity:

```python
@target(type="Item", scope="global")
def check_weight_limit(subject):
    overweight = sql("SELECT id, weight FROM Item WHERE weight > 500")
    
    for item in overweight:
        blame(item['id'], f"Weight {item['weight']} exceeds threshold 500")
    
    assert not overweight
```

### Diagnostic Display

When Spec fails, the IDE marks two locations:
- **Rule view**: The specific `assert` line in the `spec` block
- **Data view**: The entity definition being `blame`d

---

## Validation Strategy Selection

| Scenario | Recommended Method | Example |
|----------|-------------------|---------|
| Single field format check | `@field_validator` | Email format, phone number |
| Multi-field joint check | `@model_validator` | End time > Start time |
| Cross-entity relationship check | `spec` + `scope="local"` | Whether referenced entity exists |
| Aggregate statistics constraint | `spec` + `scope="global"` + `sql()` | Total weight, average value |
| Global uniqueness check | `spec` + `scope="global"` | Username globally unique |

---

## CI/CD Integration

```bash
# Check and output JSON
typedown check --json

# Filter specific error codes
typedown check --json | jq '.diagnostics[] | select(.code == "E0103")'

# Show only errors (exclude warnings)
typedown check --json | jq '.diagnostics[] | select(.level == "error")'
```

### Pre-commit Hook

```yaml
- repo: local
  hooks:
    - id: typedown-check
      name: Typedown Check
      entry: typedown check
      language: system
      files: \.td$
```

# Logic Spec (Spec)

The `spec` block is used to define complex logic validation rules. Unlike field validation within a Model, Specs run after the graph construction is complete, allowing them to access the global context, verify cross-entity relationships, perform aggregation checks, and enforce complex business invariants.

## Syntax Signature (Block Signature)

````typedown
```spec:<TestID>
@target(...)
def <TestID>(subject):
    ...
```
````

### Signature Strictness Requirements

In version v0.2.13+, Typedown has strengthened the block signature validation logic:

- **Signature Consistency**: The **Block ID** (`TestID`) must **exactly match** the validation function name defined within the Python code in the block. This ensures a strong binding between the document structure and code logic.
- **ID Character Restrictions**: Identifiers are only allowed to contain letters, numbers, underscores `_`, and hyphens `-` (regex: `[a-zA-Z0-9_\-]+`).
- **Space Insensitivity**: Spaces between the keyword `spec` and the colon `:`, and between the colon and the ID, are no longer sensitive. For example, `spec:my_test` and `spec : my_test` are both considered equivalent and compliant.

- **Keyword**: `spec`
- **Identifier**: `<TestID>` is the unique name of the test case.
- **Content**: Python code, based on Pytest style.

## Target Selection (@target)

Use the `@target` decorator to declare which entities this test applies to.

```python
@target(type="User", scope="local")
def check_user_consistency(subject: User):
    ...
```

### Parameters

- **type**: Filter by model type (e.g., `"User"`).
- **tag** (Optional): Filter by entity tag.
- **scope** (Optional): Controls execution frequency and range.
  - `"local"` (Default): **Instance Mode**. Runs the test once for each matching entity; `subject` is the current entity.
  - `"global"`: **Global Mode**. Runs the test exactly once regardless of how many entities match. Ideal for aggregation checks (e.g., "Total Weight Limit"). `subject` is the first matching entity (as a representative), or can be ignored.

## Writing Assertions

Spec functions receive a `subject` parameter (the instantiated Pydantic object). You can use standard Python `assert` statements:

```python
def check_admin_mfa(subject: User):
    if subject.role == "admin":
        assert subject.mfa_enabled, f"Admin {subject.name} must have MFA enabled"
```

## Context Access

The Spec environment is injected with powerful built-in functions to break "data silos":

### `query(selector)`

Used for simple lookups or ID-based access. Supports ID references, property paths, etc.

### `sql(query_string)`

Integrates the **DuckDB** engine, enabling high-performance SQL queries over the entire entity graph. This is the preferred way to handle aggregation checks in ERP-like business logic.

```python
@target(type="Item", scope="global")
def check_total_inventory_cap(subject):
    # Query the sum of weights of all Items
    result = sql("SELECT sum(weight) as total FROM Item")
    total_weight = result[0]['total']

    limit = 10000
    assert total_weight <= limit, f"Total weight ({total_weight}) exceeds limit ({limit})"
```

## Attribution and Diagnostics

Typedown provides precise error reporting to ensure quick identification of failures in complex rules.

### 1. Blame (Attribution)

When an aggregation rule fails, you can use the `blame()` function to specify which entities are responsible, avoiding "red screens" on unrelated data.

```python
@target(type="Item", scope="global")
def check_weight_limit(subject):
    # Find all overweight items
    overweight_items = sql("SELECT id, weight FROM Item WHERE weight > 500")

    for item in overweight_items:
        # Blame only the specific items, not everyone
        blame(item['id'], f"Weight {item['weight']} exceeds warning threshold 500")

    assert not overweight_items
```

### 2. Dual-Sided Diagnostics

When a Spec fails, the IDE marks the error in two locations:

- **Rule View**: The specific `assert` line in the `spec` block (precisely located via Traceback parsing).
- **Data View**: The `entity` block definition of the blamed entities.

## Import Restrictions

To maintain flexibility, `spec` blocks allow the use of `import` statements for local modules. This differs from `model` blocks, which restrict imports to ensure schema purity.

## Best Practices

- **Prefer SQL**: Use `sql()` for statistics or filtering involving multiple entities; it is much more efficient than looping with `query()`.
- **Use Global Scope Appropriately**: Mark aggregation rules as `scope="global"` to prevent redundant executions.
- **Leverage Blame**: Always use `blame` in aggregation checks to provide precise feedback and reduce noise for users.
- **Keep it Read-only**: Never modify `subject` properties or perform any side-effect operations within a Spec.

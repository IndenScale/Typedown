---
title: Logic Spec
---

# Logic Spec (Spec)

The `spec` block is used to define complex logic validation rules. Unlike field validation within a Model, Specs run after the graph construction is complete, so they can access the global context and verify cross-entity relationships.

## Syntax Signature

```markdown
```spec:<TestID>
@target(...)
def test_function(subject):
    ...
```
```

- **Keyword**: `spec`
- **Identifier**: `<TestID>` is the unique name of the test case.
- **Content**: Python code, based on Pytest style.

## Target Selection (@target)

Use the `@target` decorator to declare which entities this test applies to.

```python
@target(type="User")
def check_user_consistency(subject: User):
    ...
```

- **type**: Filter by model type.
- **tag** (Optional): Filter by entity tag.

## Writing Assertions

Spec functions receive a `subject` parameter, which is the instantiated object (Pydantic Model Instance) of the tested entity.

You can use standard Python `assert` statements:

```python
def check_admin_mfa(subject: User):
    if subject.role == "admin":
        # If assertion fails, the compiler reports an error with this message
        assert subject.mfa_enabled, f"Admin {subject.name} must have MFA enabled"
```

## Accessing Context

Spec code runs in a restricted Python environment but can access:

- `subject`: The entity currently being tested.
- Global Symbol Table: Access other nodes in the graph via `typelib` or other injected variables.

## Best Practices

- **Keep it Pure**: Specs should be side-effect free (Read-only). Do not modify entity data in a Spec.
- **Atomicity**: Each Spec should test only one logical rule.

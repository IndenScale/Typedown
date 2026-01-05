---
title: Logic Spec
---

# Logic Spec (Spec)

The `spec` block is used to define complex logic validation rules. Unlike field validation within a Model, Specs run after the graph construction is complete, so they can access the global context and verify cross-entity relationships.

## Syntax Signature

````markdown
```spec:<TestID>
@target(...)
def test_function(subject):
    ...
```
````

````

- **Keyword**: `spec`
- **Identifier**: `<TestID>` is the unique name of the test case.
- **Content**: Python code, based on Pytest style.

## Target Selection (@target)

Use the `@target` decorator to declare which entities this test applies to.

```python
@target(type="User")
def check_user_consistency(subject: User):
    ...
````

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

## Context Access

Spec code runs in a restricted Python environment. Besides `subject`, you can use the `query()` function to look up other nodes in the graph.

### `query(selector)`

Finds an entity or resource in the global scope.

- **Arguments**: `selector` (str):
  - **ID Reference**: `"user-alice"`, `"[[user-alice]]"`
  - **Property Path**: `"user-alice.profile.email"`
  - **File Path**: `"assets/logo.png"`
- **Returns**: The matched object (Entity, Resource, or property value). Raises an exception if not found.

```python
@target(type="User")
def check_manager_relationship(subject):
    # Get Manager's ID (assuming subject.manager stores a reference string like "users/bob")
    manager_id = subject.manager

    # Use query() to find the Manager entity
    # Note: If the Reference was already resolved by the Linker, subject.manager might already be an object.
    # But if it is a raw string, or you need reverse lookup, query() is very useful.

    manager = query(manager_id)
    assert manager.department == subject.department
```

## Best Practices

- **Pure Functions**: Specs should be side-effect free (Read-only). Do not modify entity data in a Spec.
- **Atomicity**: Each Spec should test only one logical rule.
- **Avoid Over-Querying**: While `query()` is powerful, excessive use may cause performance issues. For tightly coupled objects, try to use Linker's automatic reference resolution.

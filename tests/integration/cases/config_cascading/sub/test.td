```entity:User
id: "u1"
name: "Alice"
age: 30
```

```spec
def test_config_cascading_user(workspace):
    # For now, let's assume `workspace.entities` will contain the entities from the loaded project.
    # Note: Using get_entity implies we are looking up by ID.
    # We might need to adjust based on actual API (workspace.symbol_table or get_entity helper)
    
    # In strict typedown.core.compiler.Compiler, we have get_entity helper
    user_entity = workspace.get_entity("u1")
    
    assert user_entity is not None, "User entity 'u1' should exist"
    # Accessing attributes via the AttributeWrapper provided by get_entity
    assert user_entity.name == "Alice", f"Expected name 'Alice', got {user_entity.name}"
    assert user_entity.age == 30, f"Expected age 30, got {user_entity.age}"
```

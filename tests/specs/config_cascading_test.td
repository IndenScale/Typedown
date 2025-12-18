# Config Cascading Test

This test verifies the correct behavior of configuration cascading and entity parsing.

```spec
def test_config_cascading_user(workspace):
    # Load the specific test case project
    # In a real scenario, you would structure your test projects
    # and load them accordingly. For this migration, we assume
    # the workspace fixture is configured to load the correct context.

    # For now, let's assume `workspace.entities` will contain the entities from the loaded project.
    user_entity = workspace.get_entity("u1")
    assert user_entity is not None, "User entity 'u1' should exist"
    assert user_entity.name == "Alice", f"Expected name 'Alice', got {user_entity.name}"
    assert user_entity.age == 30, f"Expected age 30, got {user_entity.age}"
```

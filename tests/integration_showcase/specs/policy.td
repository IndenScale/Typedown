# Policy Checks

```spec:check_budget_positive
@target(type="Project")
def check_budget_positive(project):
    # project is an AttributeWrapper around resolved_data
    # project.budget is accessable via dot notation
    
    amount = project.budget.amount
    assert amount > 0, f"Project {project.name}: Budget must be positive, got {amount}"
    
    # Check currency is valid (Enum check manually since it's a dict/wrapper)
    assert project.budget.currency in ["CNY", "USD", "EUR"], f"Invalid Currency: {project.budget.currency}"
```

```spec:check_manager_assigned
@target(type="Project")
def check_manager_assigned(project):
    # project.manager should be resolved to the EntityBlock (if Reference resolution worked)
    # OR it is the Reference String if validation kept it as string?
    # Validator._resolve_entity uses QueryEngine.evaluate_data.
    # If "[[employees/alice]]" was in raw_data, it becomes the EntityBlock of Alice.
    
    # Let's verify what we get.
    manager = project.manager
    
    # Ideally checking existence is enough validation, but let's assert it's not None
    assert manager is not None, f"Project {project.name} has no manager"
    
    # If it is resolved to EntityBlock/AttributeWrapper, we can check allow usage
    # Note: If it's the Slug string (because QueryEngine didn't resolve it? No, it should), 
    # we need to know. 
    # For now, let's just assert truthiness.
    pass
```

# Project Management Models

```model:Project
class Project(BaseModel):
    name: str
    code: str
    status: str = "Planning"
    
    # Reference to Entity
    manager: Ref["Employee"]
    
    # Embedded Value Object (defined in core.td)
    # Note: This requires 'Money' to be in the execution namespace or resolvable.
    # If the linker runs all models in shared globals, it works.
    budget: "Money"
```

```model:Task
class Task(BaseModel):
    title: str
    assignee: Ref["Employee"]
    parent_project: Ref["Project"]
```

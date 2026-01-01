# Project Management Models

```model:Project
from pydantic import BaseModel, Field
from typing import List, Optional
from typedown.core.base.types import Ref

# We rely on Money being available in the context or use string forward ref if Linker handles it
# Since Money is a model defined in this project, we hope it's available.
# But since they are in different files, Python execution scope might be isolated unless we use config to stitch.
# For this showcase, I will use "Money" as forward ref or Type.
# However, Pydantic needs the class for validation of embedded structure.
# Let's try string ref. If it fails validation, we know we need to fix Linker scoping.

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
from pydantic import BaseModel
from typedown.core.base.types import Ref

class Task(BaseModel):
    title: str
    assignee: Ref["Employee"]
    parent_project: Ref["Project"]
```

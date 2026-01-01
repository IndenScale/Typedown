# Organization Models

```model:Employee
from pydantic import BaseModel

class Employee(BaseModel):
    name: str
    role: str
    email: str
```

```model:Department
from pydantic import BaseModel
from typing import List
from typedown.core.base.types import Ref

class Department(BaseModel):
    name: str
    lead: Ref["Employee"]
```

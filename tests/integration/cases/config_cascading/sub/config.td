---
---

```config:python
from pydantic import BaseModel

# Override User
class User(BaseModel):
    name: str
    age: int
```

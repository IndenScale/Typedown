# Evolution Test

Testing the `former` keyword for entity evolution and field inheritance.

```model
from typing import Optional
from pydantic import BaseModel

class Feature(BaseModel):
    id: str
    status: str
    priority: str
    notes: Optional[str] = None
```

```entity:Feature
id: "feat_v1"
status: "planned"
priority: "high"
```

```entity:Feature
id: "feat_v2"
former: "feat_v1"
status: "done"
# priority should be inherited as "high"
```

```spec
def test_evolution_inheritance(workspace):
    # Depending on implementation, `former` might be processed during Scanning or validation.
    # We expect the final entity to have merged properties.
    
    v2 = workspace.get_entity("feat_v2")
    assert v2 is not None
    
    # Check explicitly set field
    assert v2.status == "done"
    
    # Check inherited field
    # If this fails, it means the `former` logic is not implemented yet.
    # The RFC 002 guarantees this behavior.
    assert v2.priority == "high", f"Expected priority 'high', got {v2.priority}"
```

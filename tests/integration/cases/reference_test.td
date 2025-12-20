# Reference System Test

Testing cross-type references and path traversal.

```model id=MyModel
from pydantic import BaseModel

class Config(BaseModel):
    version: str = "1.0.0"
```

```spec id=MySpec
import pytest

def test_placeholder():
    pass
```

```entity:Config id=c1
version: "2.0.0"
spec_ref: "[[MySpec.name]]"
model_code: "[[MyModel.code]]"
```

```spec
def test_references(workspace):
    c1 = workspace.get_entity("c1")
    assert c1.spec_ref == "MySpec"
    assert "BaseModel" in c1.model_code
```

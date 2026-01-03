```model:Skill
from typing import List, Dict, Optional
from pydantic import BaseModel, HttpUrl

class Example(BaseModel):
    description: str
    code: str

class Parameter(BaseModel):
    name: str
    type: str  # e.g., "string", "int"
    description: str
    required: bool = True

class Skill(BaseModel):
    """
    Defines a capability that an Agent can possess.
    """
    name: str
    description: str
    version: str = "1.0.0"
    author: str

    # The interface for the LLM to call this skill
    parameters: List[Parameter]

    # Guidelines that strictly constrain the skill's usage
    guidelines: List[str]

    # Zero-shot examples to prime the context
    examples: List[Example]
```

```config
export Skill
export Parameter
export Example
```

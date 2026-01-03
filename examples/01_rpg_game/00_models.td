# RPG Lite: Models

This file defines the basic data structures for our RPG game using Pydantic.

```model:Item
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    weight: float = 0.0
    value: int = 0
```

```model:Character
from typing import List
from pydantic import BaseModel, Field
from typedown.core.base.types import Ref

class Character(BaseModel):
    name: str
    class_name: str
    level: int = 1
    hp: int
    max_hp: int
    # Reference to other items defined in Typedown
    inventory: List[Ref["Item"]] = Field(default_factory=list)
```

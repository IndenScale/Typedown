from typing import List, Optional
from pydantic import BaseModel, Field

class Item(BaseModel):
    id: str
    name: str
    weight: float = 0.0
    value: int = 0

class Character(BaseModel):
    id: str
    name: str
    class_name: str
    level: int = 1
    hp: int
    max_hp: int
    inventory: List[str] = Field(default_factory=list) # List of Item IDs

class Monster(BaseModel):
    id: str
    name: str
    type: str
    hp: int
    attack: int
    loot: List[str] = Field(default_factory=list)

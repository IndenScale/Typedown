from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

class Role(str, Enum):
    DEVELOPER = "DEVELOPER"
    MANAGER = "MANAGER"
    ARCHITECT = "ARCHITECT"
    SPECIALIST = "SPECIALIST"

class Level(str, Enum):
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    P4 = "P4"
    P5 = "P5"

class Employee(BaseModel):
    id: str
    name: str
    role: Role
    level: Level
    tags: List[str] = Field(default_factory=list, description="Skills or certs")
    base_cost_per_day: float = Field(..., description="Internal cost rate")

from enum import Enum
from typing import List
from pydantic import BaseModel, Field

class ProjectStatus(str, Enum):
    PLANNING = "PLANNING"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"

class Project(BaseModel):
    id: str
    name: str
    region: str = Field(..., description="Region code, e.g., 'CN-BJ', 'CN-SH'")
    status: ProjectStatus
    budget_cap: float
    manager_id: str
    description: str = ""

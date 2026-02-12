from enum import Enum
from typing import TYPE_CHECKING
from pydantic import BaseModel, Field
from typedown.core.base.types import Ref

if TYPE_CHECKING:
    from .hr import Employee

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
    manager: Ref["Employee"]
    description: str = ""

from enum import Enum
from typing import Optional
from pydantic import Field
from ..core.primitives import BaseEntity, Money
from typedown.core.base.types import Ref

class ProjectStatus(str, Enum):
    PLANNING = "Planning"
    DELIVERY = "Delivery" # 交付阶段
    WARRANTY = "Warranty" # 质保期
    COMPLETED = "Completed" # 已结束/关闭

class Project(BaseEntity):
    name: str
    code: str
    manager: Ref["Employee"]
    description: Optional[str] = None
    status: ProjectStatus = ProjectStatus.PLANNING
    budget: Money

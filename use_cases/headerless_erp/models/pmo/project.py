from enum import Enum
from typing import Optional
from pydantic import Field
from ..core.primitives import BaseEntity, Money

class ProjectStatus(str, Enum):
    PLANNING = "Planning"
    DELIVERY = "Delivery" # 交付阶段
    WARRANTY = "Warranty" # 质保期
    COMPLETED = "Completed" # 已结束/关闭

class Project(BaseEntity):
    name: str
    code: str
    manager_id: str
    description: Optional[str] = None
    status: ProjectStatus = ProjectStatus.PLANNING
    budget: Money

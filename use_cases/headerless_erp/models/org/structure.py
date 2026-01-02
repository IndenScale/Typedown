from enum import Enum
from typing import List, Optional
from pydantic import Field
from ..core.primitives import BaseEntity
from typedown.core.base.types import Ref

class DepartmentType(str, Enum):
    FUNCTIONAL = "Functional"
    BUSINESS = "Business"

class Employee(BaseEntity):
    name: str
    email: str
    title: str
    department: Ref["Department"]
    level: int = Field(default=1, ge=1, le=20)

class Department(BaseEntity):
    name: str
    code: str
    head: Optional[Ref["Employee"]] = None
    type: DepartmentType

class FunctionalDepartment(Department):
    type: DepartmentType = DepartmentType.FUNCTIONAL
    domain_responsibility: List[str] = []

class BusinessUnit(Department):
    type: DepartmentType = DepartmentType.BUSINESS
    parent_unit: Optional[Ref["BusinessUnit"]] = None
    cost_center_code: str

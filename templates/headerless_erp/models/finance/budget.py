from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, validator
from ..core.primitives import Money, BaseEntity

class BudgetCategory(str, Enum):
    TRAVEL = "Travel"
    EQUIPMENT = "Equipment"
    SALARY = "Salary"
    MARKETING = "Marketing"

class BudgetLine(BaseModel):
    category: BudgetCategory
    limit: Money
    description: Optional[str] = None

class DepartmentBudget(BaseEntity):
    year: int
    department_code: str
    lines: List[BudgetLine]

    @validator('lines')
    def validate_total_not_exceed_cap(cls, v):
        total = sum([item.limit.amount for item in v])
        if total > 10_000_000:
            raise ValueError(f"Total budget {total} exceeds corporate cap of 10M")
        return v

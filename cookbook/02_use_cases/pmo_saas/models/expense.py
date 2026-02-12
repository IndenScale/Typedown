from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional

class ExpenseCategory(str, Enum):
    SERVICE = "SERVICE"             # Installation/Outsourcing Services
    LOGISTICS = "LOGISTICS"         # Equipment Logistics/Shipping
    TRAVEL = "TRAVEL"               # Travel/Hotel (Actual bills, separate from daily allowance)
    TEAM_BUILDING = "TEAM_BUILDING" # Team meals/events
    PROCUREMENT = "PROCUREMENT"     # Small assets/consumables
    OTHER = "OTHER"

class ExpenseItem(BaseModel):
    id: str
    project_id: str
    incurred_by_id: str             # Employee who spent the money
    date: str                       # YYYY-MM-DD
    category: ExpenseCategory
    amount: float = Field(..., gt=0)
    description: str
    vendor: Optional[str] = None    # Vendor or Merchant name

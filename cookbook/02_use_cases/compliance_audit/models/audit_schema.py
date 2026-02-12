from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

class Status(str, Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLIANT = "COMPLIANT"
    NON_COMPLIANT = "NON_COMPLIANT"
    WAIVED = "WAIVED"

class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class Requirement(BaseModel):
    id: str
    title: str
    description: str
    standard: str = "ISO27001"
    section: str

class Evidence(BaseModel):
    uri: str
    description: str
    collected_at: str

class Control(BaseModel):
    id: str
    requirement_id: str # Link to Requirement ID
    owner: str
    status: Status = Status.OPEN
    risk_level: RiskLevel = RiskLevel.MEDIUM
    evidence: List[Evidence] = Field(default_factory=list)
    mitigation_plan: Optional[str] = None

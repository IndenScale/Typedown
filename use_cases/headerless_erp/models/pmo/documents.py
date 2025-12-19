from typing import Optional, List
from pydantic import Field
from ..core.primitives import BaseEntity, Money

class RFI(BaseEntity):
    """Request for Information (RFI) document"""
    project_code: str
    title: str
    content: str = Field(..., description="Background and questions for vendors")
    vendor_list: str = Field(..., description="Comma separated list of invited vendors")
    issued_date: str
    status: str = Field(default="Closed", description="Draft, Open, Closed")

class Contract(BaseEntity):
    """Formal business contract"""
    project_code: str
    vendor_name: str
    title: str
    sign_date: str
    total_value: Money
    terms_summary: str

class FeasibilityStudy(BaseEntity):
    """Feasibility Study Report"""
    project_code: str
    title: str
    author: str
    roi_prediction: str
    conclusion: str

class DesignDocument(BaseEntity):
    """Technical Design Document"""
    project_code: str
    title: str
    version: str
    approver_id: str
    technical_summary: str

class AcceptanceReport(BaseEntity):
    """User Acceptance Testing (UAT) or Final Acceptance Report"""
    project_code: str
    title: str
    inspector_id: str
    date: str
    result: str = Field(..., description="Pass, Fail, Conditional Pass")
    issues_found: List[str] = []

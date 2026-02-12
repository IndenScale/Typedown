from enum import Enum
from typing import Optional
from datetime import date
from pydantic import Field
from ..core.primitives import BaseEntity

class CertificateType(str, Enum):
    PMP = "PMP" # Project Management Professional
    PRINCE2 = "PRINCE2"
    CPA = "CPA" # Certified Public Accountant
    CFA = "CFA"
    LEAN_SIX_SIGMA = "Lean Six Sigma"

class EmployeeCertification(BaseEntity):
    """员工持有的专业证书"""
    employee_id: str
    type: CertificateType
    cert_number: str
    issue_date: date
    expiry_date: Optional[date] = None
    issuing_body: str # e.g. "PMI", "AICPA"

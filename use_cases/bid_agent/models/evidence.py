from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import date
from .core import DocLocation

class ValidationStatus(str, Enum):
    PENDING = "PENDING"                # 待审核
    VERIFIED_MANUAL = "VERIFIED_MANUAL" # 人工审核通过 (签名比对)
    VERIFIED_AUTO = "VERIFIED_AUTO"     # 自动审核通过 (接口验证)
    REJECTED = "REJECTED"               # 审核不通过

class EvidenceSource(BaseModel):
    """证据来源指针"""
    location: DocLocation
    validation_status: ValidationStatus = ValidationStatus.PENDING
    validation_note: Optional[str] = None # 例如："人社局接口返回一致"

# --- 具体业务实体 (可根据领域动态扩展) ---

class BaseQualification(BaseModel):
    """资质基类"""
    id: str
    supplier_id: str
    evidence_source: EvidenceSource

class Certificate(BaseQualification):
    """证书 (ISO, 资质等级等)"""
    name: str
    cert_number: str
    issuer: str
    issue_date: date
    expiry_date: Optional[date]

class Achievement(BaseQualification):
    """业绩 (过往案例)"""
    project_name: str
    contract_amount: float
    contract_date: date
    client_name: str

class Person(BaseQualification):
    """人员 (项目经理, 技术骨干)"""
    name: str
    id_card_last4: str # 脱敏
    roles: List[str] # e.g. ["ProjectManager", "Architect"]
    has_social_security: bool = False # 社保是否缴纳
    certificates: List[Certificate] = [] # 人员持有的证书
    honors: List[str] = [] # 荣誉

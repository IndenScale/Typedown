from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from .core import FileResource

class VerificationMethod(str, Enum):
    OFFICIAL_WEBSITE_QUERY = "OFFICIAL_WEBSITE_QUERY" # 官网查询 (如人社局、学信网)
    PUBLIC_CREDIT_PLATFORM = "PUBLIC_CREDIT_PLATFORM" # 信用平台 (如信用中国)
    ORIGINAL_DOCUMENT_CHECK = "ORIGINAL_DOCUMENT_CHECK" # 原件核对
    PHONE_VERIFICATION = "PHONE_VERIFICATION"         # 电话核实
    THIRD_PARTY_API = "THIRD_PARTY_API"               # 自动接口验证

class ConsistencyStatus(str, Enum):
    CONSISTENT = "CONSISTENT"       # 完全一致
    INCONSISTENT = "INCONSISTENT"   # 不一致 (可能造假)
    DOUBTFUL = "DOUBTFUL"           # 存疑 (需进一步解释)
    NOT_VERIFIABLE = "NOT_VERIFIABLE" # 无法验证 (如网站崩溃)

class FactCheckRecord(BaseModel):
    """
    事实性核查记录
    用于记录对社保、资质、业绩等底层数据的客观验证过程。
    """
    id: str
    target_evidence_id: str = Field(..., description="关联的证据ID，如 CERT-ISO9001")
    target_supplier_id: str
    
    # 核查过程
    operator_id: str = Field(..., description="执行核查的操作员ID")
    checked_at: datetime = Field(default_factory=datetime.now)
    method: VerificationMethod
    
    # 核查结果
    status: ConsistencyStatus
    result_summary: str = Field(..., description="核查结果简述，如'官网查询存在，有效期一致'")
    discrepancy_details: Optional[str] = Field(None, description="如果不一致，记录差异细节")
    
    # 证据留档
    screenshot: Optional[FileResource] = Field(None, description="查询结果截图")
    query_url: Optional[str] = None
    
    # 机器辅助信息
    ocr_text_from_screenshot: Optional[str] = None # 如果有截图，OCR 提取的文字用于辅助比对

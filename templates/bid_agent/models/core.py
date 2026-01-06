from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

# --- 基础枚举 ---

class ProjectDomain(str, Enum):
    """项目领域，用于触发动态模型扩展"""
    IT_SOFTWARE = "IT_SOFTWARE"
    CONSTRUCTION = "CONSTRUCTION"
    MEDICAL_EQUIPMENT = "MEDICAL_EQUIPMENT"
    GENERAL_PURCHASE = "GENERAL_PURCHASE"

class DocumentType(str, Enum):
    TENDER_DOC = "TENDER_DOC"      # 招标文件
    BID_RESPONSE = "BID_RESPONSE"  # 投标文件
    SUPPORTING_DOC = "SUPPORTING_DOC" # 佐证材料（如扫描件）
    REPORT_DOC = "REPORT_DOC"      # 导出报告

class FileResource(BaseModel):
    """文件资源引用"""
    path: str = Field(..., description="相对路径，例如 blob/2025/tender_01.pdf")
    type: DocumentType
    md5: Optional[str] = None
    size_bytes: Optional[int] = None
    uploaded_at: datetime = Field(default_factory=datetime.now)

# --- 基础实体 ---

class Expert(BaseModel):
    id: str
    name: str
    domains: List[ProjectDomain] = []
    tags: List[str] = []

class Supplier(BaseModel):
    id: str
    name: str
    social_credit_code: str

# --- 文档与引用 ---

class DocLocation(BaseModel):
    """文档中的定位"""
    file_ref: Optional[FileResource] = None # 关联的具体文件资源
    file_name: str
    page_start: int
    page_end: Optional[int] = None
    paragraph_index: Optional[int] = None
    snippet_content: Optional[str] = Field(None, description="摘录的原文片段")

class BidProject(BaseModel):
    id: str
    title: str
    domain: ProjectDomain
    created_at: datetime = Field(default_factory=datetime.now)
    # 动态扩展字段：存储特定领域的配置
    domain_config: Dict[str, Any] = {} 
    
    # 关键文件追踪
    tender_docs: List[FileResource] = [] # 招标文件(blob)
    final_reports: List[FileResource] = [] # 评标报告(dist) 

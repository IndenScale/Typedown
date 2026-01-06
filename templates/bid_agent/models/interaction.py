from enum import Enum
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field
from datetime import datetime
from .core import Expert

class TicketStatus(str, Enum):
    OPEN = "OPEN"           # 新建工单，等待处理
    PROCESSING = "PROCESSING" # 系统正在处理
    WAITING_INPUT = "WAITING_INPUT" # 等待人工输入/确认
    RESOLVED = "RESOLVED"   # 处理完成
    CLOSED = "CLOSED"       # 归档

class TicketType(str, Enum):
    # 数据导入类
    IMPORT_TENDER_DOC = "IMPORT_TENDER_DOC"   # 导入招标文件
    IMPORT_BID_RESPONSE = "IMPORT_BID_RESPONSE" # 导入投标文件
    
    # 业务流程类
    EVALUATION_TASK = "EVALUATION_TASK"       # 专家评分任务
    AUDIT_TASK = "AUDIT_TASK"                 # 资质审核任务
    
    # 导出类
    EXPORT_REPORT = "EXPORT_REPORT"           # 导出最终报告

class Ticket(BaseModel):
    """
    交互凭证 (Ticket)
    UI 通过创建此对象来请求系统操作，系统更新此对象状态以反馈结果。
    """
    id: str = Field(..., description="全局唯一工单号，例如 TKT-20251219-001")
    type: TicketType
    status: TicketStatus = TicketStatus.OPEN
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # 上下文信息
    operator_id: str = Field(..., description="操作人ID (User/Expert/System)")
    project_id: Optional[str] = None
    
    # 数据负载 (输入)
    payload: Dict[str, Any] = Field(default={}, description="前端传递的参数，如文件路径、打分数据")
    
    # 处理结果 (输出)
    result: Optional[Dict[str, Any]] = Field(None, description="系统返回的结果，如生成的实体ID、错误信息")
    
    # 关联文件
    related_files: List[str] = Field(default=[], description="关联的 blob 或 dist 文件路径")

class EvaluationTicket(Ticket):
    """专家评分特定工单"""
    type: TicketType = TicketType.EVALUATION_TASK
    expert_id: str
    supplier_id: str
    # 评分数据可以直接嵌入，也可以引用外部 ScoreSheet
    scores: Optional[List[Dict[str, Any]]] = None 

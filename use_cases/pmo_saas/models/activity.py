from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field

class ActivityType(str, Enum):
    DELIVERY = "DELIVERY"       # 现场交付
    SUPPORT = "SUPPORT"         # 业务支撑
    MANAGEMENT = "MANAGEMENT"   # 管理活动
    TRAINING = "TRAINING"       # 学习培训
    SUMMARY = "SUMMARY"         # 方案总结
    SHARING = "SHARING"         # 技术分享

class WorkLocation(str, Enum):
    REMOTE = "REMOTE"
    ONSITE = "ONSITE"

class WorkLog(BaseModel):
    id: str
    employee_id: str
    project_id: str
    month: str # YYYY-MM
    activity_type: ActivityType
    location: WorkLocation
    work_days: float = Field(..., gt=0, le=31)
    output_link: Optional[str] = None
    description: str

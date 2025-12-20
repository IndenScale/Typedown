from enum import Enum
from typing import List, Optional, Union, Dict, Any
from pydantic import BaseModel, Field
from .core import BidProject, Supplier, Expert
from .evidence import BaseQualification, EvidenceSource

# --- 枚举定义 ---

class ReviewStage(str, Enum):
    """评审阶段"""
    # 初步评审 (Preliminary Review)
    PRELIMINARY_FORMAL = "PRELIMINARY_FORMAL"                 # 形式评审 (签字、密封)
    PRELIMINARY_QUALIFICATION = "PRELIMINARY_QUALIFICATION"   # 资格评审 (资质、业绩信誉)
    PRELIMINARY_RESPONSIVENESS = "PRELIMINARY_RESPONSIVENESS" # 响应性评审 (实质性条款)
    
    # 详细评审 (Detailed Review)
    DETAILED_EVALUATION = "DETAILED_EVALUATION"               # 详细评分/比价

class EvaluationMethod(str, Enum):
    """评标方法"""
    LOWEST_EVALUATED_PRICE = "LOWEST_EVALUATED_PRICE" # 经评审的最低投标价法
    COMPREHENSIVE_SCORING = "COMPREHENSIVE_SCORING"   # 综合评估法

class EvaluationComponent(str, Enum):
    """详细评审的细分部分"""
    NOT_APPLICABLE = "N/A" # 适用于初步评审
    TECHNICAL = "TECHNICAL" # 技术部分
    BUSINESS = "BUSINESS"   # 商务部分
    PRICE = "PRICE"         # 价格部分

class Criticality(str, Enum):
    """条款重要性"""
    NORMAL = "NORMAL"
    CRITICAL = "CRITICAL" # 关键条款 (星号条款)，不满足即废标/无效

class ScoringType(str, Enum):
    PASS_FAIL = "PASS_FAIL" # 合格/不合格 (用于初步评审)
    SCORE = "SCORE"         # 打分制 (用于详细评审)

# --- 条款定义 ---

class ReviewItem(BaseModel):
    """评审条款 (基类)"""
    id: str
    content: str = Field(..., description="条款内容")
    stage: ReviewStage
    criticality: Criticality = Criticality.NORMAL
    
    # 自动关联配置
    keywords: List[str] = []
    
class ComplianceItem(ReviewItem):
    """符合性审查项 (用于初步评审)"""
    scoring_type: ScoringType = ScoringType.PASS_FAIL
    # 如果不通过，给出的废标理由模板
    rejection_reason_template: Optional[str] = None

class ScoringItem(ReviewItem):
    """详细评分项 (用于详细评审)"""
    stage: ReviewStage = ReviewStage.DETAILED_EVALUATION
    component: EvaluationComponent
    scoring_type: ScoringType = ScoringType.SCORE
    max_score: float
    min_score: float = 0
    scoring_criteria: str = Field(..., description="具体的打分细则，如：每缺一项扣1分")

# --- 响应与评审结果 ---

class BidResponseItem(BaseModel):
    """投标方针对某一条款的响应"""
    id: str
    supplier_id: str
    review_item_id: str # 指向 ComplianceItem 或 ScoringItem
    
    # 证据
    evidences: List[Union[BaseQualification, EvidenceSource]] = []
    response_text: Optional[str] = None # 针对该条款的文字回应
    
    # 系统预判
    auto_pass: Optional[bool] = None

class ReviewResultEntry(BaseModel):
    """专家或系统的评审结果"""
    expert_id: str
    response_item_id: str
    
    # 结果
    is_passed: Optional[bool] = None # 针对 PASS_FAIL
    score: Optional[float] = None    # 针对 SCORE
    comment: Optional[str] = None
    
    # 废标标记
    is_knockout: bool = Field(False, description="是否导致废标")

class SupplierEvaluationState(BaseModel):
    """供应商当前的评审状态"""
    project_id: str
    supplier_id: str
    current_stage: ReviewStage = ReviewStage.PRELIMINARY_FORMAL
    is_disqualified: bool = False
    disqualification_reason: Optional[str] = None
    
    # 各阶段得分快照
    stage_scores: Dict[str, float] = {}
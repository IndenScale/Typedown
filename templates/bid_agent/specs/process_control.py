from typing import List, Dict
from use_cases.bid_agent.models.review import (
    SupplierEvaluationState, ReviewResultEntry, 
    ReviewStage, Criticality, ComplianceItem
)

def evaluate_preliminary_stage(
    state: SupplierEvaluationState, 
    results: List[ReviewResultEntry], 
    items: List[ComplianceItem]
) -> SupplierEvaluationState:
    """
    执行初步评审阶段的逻辑判断：
    1. 检查所有 Critical 条款是否通过。
    2. 如果有任意 Critical 条款未通过 (is_passed=False)，则废标。
    3. 更新状态。
    """
    
    # 建立 ID 映射
    item_map = {item.id: item for item in items}
    
    # 找出当前阶段的所有相关结果
    current_stage_results = [
        r for r in results 
        if item_map.get(r.response_item_id) and item_map[r.response_item_id].stage == state.current_stage
    ]
    
    # 检查废标条件
    for res in current_stage_results:
        item = item_map[res.response_item_id]
        
        # 逻辑：如果是关键条款且未通过
        if item.criticality == Criticality.CRITICAL and res.is_passed is False:
            state.is_disqualified = True
            state.disqualification_reason = f"Failed critical item {item.id}: {item.content} - {res.comment}"
            print(f"Supplier {state.supplier_id} disqualified: {state.disqualification_reason}")
            return state

    # 如果没有被废标，且所有必须项都已评审，则晋级下一阶段 (简化逻辑)
    # 实际逻辑需要定义阶段顺序的状态机
    print(f"Supplier {state.supplier_id} passed stage {state.current_stage}")
    return state

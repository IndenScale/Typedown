"""
评审汇总逻辑 (模拟)
该脚本逻辑应当被 typedown 的 Spec Runner 执行。
"""

from typing import List
from use_cases.bid_agent.models.review import ReviewResultEntry, Criticality

def generate_report(project_id: str):
    # 1. 加载所有数据 (模拟 loader)
    # tender_items = load("01_tender_requirements/*.td")
    # check_results = load("03_expert_reviews/formal_check/*.td")
    # score_results = load("03_expert_reviews/detailed_scoring/*.td")
    
    # 2. 废标检查 (Knockout Check)
    valid_suppliers = set()
    all_suppliers = ["SUP-A", "SUP-B"] # 假设
    
    for supplier in all_suppliers:
        is_knocked_out = False
        supplier_checks = [r for r in check_results if r.supplier_id == supplier]
        
        for check in supplier_checks:
            if not check.is_passed and check.is_knockout:
                print(f"Supplier {supplier} ELIMINATED due to {check.response_item_id}: {check.comment}")
                is_knocked_out = True
                break
        
        if not is_knocked_out:
            valid_suppliers.add(supplier)
            
    # 3. 计算得分 (Scoring)
    final_scores = {}
    for supplier in valid_suppliers:
        supplier_scores = [r for r in score_results if r.supplier_id == supplier]
        
        # 简单求和 (实际可能需要去掉最高最低分)
        total_score = sum(r.score for r in supplier_scores if r.score is not None)
        final_scores[supplier] = total_score
        
    # 4. 排序输出
    sorted_suppliers = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)
    return sorted_suppliers

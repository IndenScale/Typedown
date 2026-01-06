from typing import List, Dict
import statistics

# 假设这些是从 typedown 上下文加载的数据
# from use_cases.bid_agent.models.review import ExpertScoreEntry

def calculate_deviation(scores: List[float], threshold_percent: float = 0.2) -> Dict[int, bool]:
    """
    计算一组分数的偏差。
    如果某个分数与平均分的差异超过 (平均分 * 阈值)，则标记为偏差。
    
    Returns:
        Dict[index, is_deviated]: 分数在列表中的索引 -> 是否偏差
    """
    if not scores:
        return {}
        
    avg = statistics.mean(scores)
    if avg == 0:
        return {i: False for i in range(len(scores))}

    result = {}
    for i, score in enumerate(scores):
        deviation = abs(score - avg) / avg
        result[i] = deviation > threshold_percent
        
    return result

def check_expert_deviations(entries: List['ExpertScoreEntry']):
    """
    检查专家打分偏差 (业务逻辑入口)
    """
    # 1. 按 scoring_item_id 分组
    grouped_scores = {}
    for entry in entries:
        if entry.response_item_id not in grouped_scores:
            grouped_scores[entry.response_item_id] = []
        grouped_scores[entry.response_item_id].append(entry)
    
    # 2. 计算每组的偏差
    for item_id, item_entries in grouped_scores.items():
        score_values = [e.score for e in item_entries]
        deviations = calculate_deviation(score_values, threshold_percent=0.2) # 20% 偏差阈值
        
        # 3. 回填标记
        for idx, is_deviated in deviations.items():
            item_entries[idx].is_deviated = is_deviated
            if is_deviated:
                print(f"WARNING: Expert {item_entries[idx].expert_id} has a deviated score on item {item_id}: {item_entries[idx].score} (Avg: {statistics.mean(score_values):.2f})")


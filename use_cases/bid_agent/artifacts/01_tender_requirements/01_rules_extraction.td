# 招标文件规则提取表

> **状态**: 待确认
> **说明**: 此文件由 AI 初步从 `tender_doc.pdf` 识别，请招标代理机构确认条款完整性。

```config:python
from use_cases.bid_agent.models.review import (
    ComplianceItem, ScoringItem, ReviewStage, 
    Criticality, EvaluationComponent
)
```

## 1. 物理与形式约束 (AI 识别 - 需人工核对)

> 请专家在开标现场核对以下实物细节。

```entity:ComplianceItem
id: "REQ-PHY-01"
content: "投标文件须密封完好，封口处加盖骑缝章。"
stage: "PRELIMINARY_FORMAL"
criticality: "CRITICAL"
rejection_reason_template: "密封破损或未盖骑缝章"
```

```entity:ComplianceItem
id: "REQ-PHY-02"
content: "纸质标书正本 1 份，副本 4 份。"
stage: "PRELIMINARY_FORMAL"
criticality: "CRITICAL"
rejection_reason_template: "副本数量不足"
```

## 2. 关键资格与商务条款 (AI 翻译 - 确保完整)

> 对应招标文件第三章“评标办法”。

```entity:ComplianceItem
id: "REQ-QUAL-01"
content: "投标保证金 50 万元人民币，须在截标前到账。"
stage: "PRELIMINARY_QUALIFICATION"
criticality: "CRITICAL"
keywords: ["保证金", "50万", "到账"]
```

```entity:ComplianceItem
id: "REQ-QUAL-02"
content: "投标人须具备 ISO9001 质量管理体系认证。"
stage: "PRELIMINARY_QUALIFICATION"
criticality: "CRITICAL"
keywords: ["ISO9001", "质量管理"]
```

## 3. 详细评分细则 (AI 翻译 - 供专家打分)

### 技术部分

```entity:ScoringItem
id: "SCORE-TECH-01"
content: "总体设计方案架构合理，具有高可用性设计。"
stage: "DETAILED_EVALUATION"
component: "TECHNICAL"
max_score: 10.0
min_score: 0.0
scoring_criteria: "优(8-10分): 架构先进，有完善的双活设计；良(5-8分): 架构合理，有冷备方案；差(0-5分): 架构陈旧或无容灾。"
```

### 商务部分

```entity:ScoringItem
id: "SCORE-BIZ-01"
content: "近三年类似项目业绩（单项合同额 > 1000万）。"
stage: "DETAILED_EVALUATION"
component: "BUSINESS"
max_score: 15.0
min_score: 0.0
scoring_criteria: "每提供一个有效业绩得 3 分，满分 15 分。"
```

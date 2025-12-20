# 某政府采购项目 - 全流程评审规则

> 采用 **综合评估法**。
> 流程：形式评审 -> 资格评审 -> 响应性评审 -> 详细评审 (技术/商务/价格)

```config:python
from use_cases.bid_agent.models.review import (
    ComplianceItem, ScoringItem, 
    ReviewStage, EvaluationComponent, 
    Criticality, ScoringType
)
```

## 第一阶段：形式评审 (Formal Review)

> 任何一项不通过，直接废标。

```entity:ComplianceItem
id: "FORMAL-01"
content: "投标文件须加盖投标人公章及法定代表人签字。"
stage: "PRELIMINARY_FORMAL"
criticality: "CRITICAL"
rejection_reason_template: "投标文件未按要求签字盖章"
```

```entity:ComplianceItem
id: "FORMAL-02"
content: "投标保证金须在截标前到账。"
stage: "PRELIMINARY_FORMAL"
criticality: "CRITICAL"
rejection_reason_template: "未缴纳投标保证金"
```

## 第二阶段：资格评审 (Qualification Review)

> 审查企业硬性门槛。

```entity:ComplianceItem
id: "QUAL-01"
content: "投标人必须具备独立法人资格，营业执照有效。"
stage: "PRELIMINARY_QUALIFICATION"
criticality: "CRITICAL"
```

```entity:ComplianceItem
id: "QUAL-02"
content: "投标人未被列入'信用中国'失信被执行人名单。"
stage: "PRELIMINARY_QUALIFICATION"
criticality: "CRITICAL"
keywords: ["信用中国", "失信"]
```

## 第三阶段：响应性评审 (Responsiveness Review)

> 审查是否实质性响应。

```entity:ComplianceItem
id: "RESP-01"
content: "交付工期不得超过 180 个日历天。"
stage: "PRELIMINARY_RESPONSIVENESS"
criticality: "CRITICAL"
rejection_reason_template: "工期超过招标文件限制"
```

## 第四阶段：详细评审 (Detailed Evaluation)

> 仅对通过前三个阶段的投标方进行打分。

### 技术部分 (Technical, 权重 50%)

```entity:ScoringItem
id: "SCORE-TECH-01"
content: "技术实施方案的科学性与合理性"
stage: "DETAILED_EVALUATION"
component: "TECHNICAL"
max_score: 20.0
scoring_criteria: "方案完善得15-20分；方案一般得10-15分；有明显缺陷得0-10分。"
```

```entity:ScoringItem
id: "SCORE-TECH-02"
content: "项目团队人员配置"
stage: "DETAILED_EVALUATION"
component: "TECHNICAL"
max_score: 10.0
scoring_criteria: "项目经理具备 PMP 证书得 5 分，核心成员具备高级职称每人得 1 分，满分 5 分。"
```

### 商务部分 (Business, 权重 20%)

```entity:ScoringItem
id: "SCORE-BIZ-01"
content: "同类项目业绩"
stage: "DETAILED_EVALUATION"
component: "BUSINESS"
max_score: 20.0
scoring_criteria: "近三年每提供一个 500 万以上合同得 5 分，满分 20 分。"
```

### 价格部分 (Price, 权重 30%)

```entity:ScoringItem
id: "SCORE-PRICE-01"
content: "投标报价"
stage: "DETAILED_EVALUATION"
component: "PRICE"
max_score: 30.0
scoring_criteria: "满足招标文件要求且投标价格最低的投标报价为评标基准价，其价格分为满分。其他投标人的价格分统一按照下列公式计算：投标报价得分=(评标基准价／投标报价)×30"
```

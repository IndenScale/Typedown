# 招标文件解析 - 某智慧城市项目

```config:python
from use_cases.bid_agent.models.core import BidProject, ProjectDomain
from use_cases.bid_agent.models.review import ScoringItem, ScoringType
```

```entity:BidProject
id: "PROJ-SMART-CITY-001"
title: "智慧城市大脑建设一期"
domain: "IT_SOFTWARE"
domain_config:
  requires_iso27001: true
  min_team_size: 20
```

## 商务标评分标准

```entity:ScoringItem
id: "SCORE-BIZ-01"
category: "商务标"
content: "投标人具有 CMMI 5 级证书得 5 分，CMMI 3 级得 2 分，否则不得分。"
max_score: 5.0
scoring_type: "OBJECTIVE"
keywords: ["CMMI", "证书"]
```

```entity:ScoringItem
id: "SCORE-BIZ-02"
category: "商务标"
content: "项目经理具有 PMP 证书且近三年有类似业绩（合同额>500万）。"
max_score: 5.0
scoring_type: "OBJECTIVE"
keywords: ["PMP", "业绩", "项目经理"]
```

## 技术标评分标准

```entity:ScoringItem
id: "SCORE-TECH-01"
category: "技术标"
content: "系统架构设计合理性，高可用方案完善。"
max_score: 20.0
scoring_type: "SUBJECTIVE"
```

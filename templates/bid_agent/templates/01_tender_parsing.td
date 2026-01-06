# 招标文件解析 - 某智慧城市项目


```entity BidProject: PROJ-SMART-CITY-001
title: "智慧城市大脑建设一期"
domain: "IT_SOFTWARE"
domain_config:
  requires_iso27001: true
  min_team_size: 20
```

## 商务标评分标准

```entity ScoringItem: SCORE-BIZ-01
component: "BUSINESS"
content: "投标人具有 CMMI 5 级证书得 5 分，CMMI 3 级得 2 分，否则不得分。"
max_score: 5.0
scoring_type: "SCORE"
scoring_criteria: "证书等级判定"
keywords: ["CMMI", "证书"]
```

```entity ScoringItem: SCORE-BIZ-02
component: "BUSINESS"
content: "项目经理具有 PMP 证书且近三年有类似业绩（合同额>500万）。"
max_score: 5.0
scoring_type: "SCORE"
scoring_criteria: "证书及业绩核验"
keywords: ["PMP", "业绩", "项目经理"]
```

## 技术标评分标准

```entity ScoringItem: SCORE-TECH-01
component: "TECHNICAL"
content: "系统架构设计合理性，高可用方案完善。"
max_score: 20.0
scoring_type: "SCORE"
scoring_criteria: "专家主观打分"
```

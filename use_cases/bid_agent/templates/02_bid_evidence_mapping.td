# 投标文件解析 - 供应商 A

```config:python
from datetime import date
from use_cases.bid_agent.models.evidence import Certificate, Achievement, EvidenceSource, DocLocation, ValidationStatus
from use_cases.bid_agent.models.review import BidResponseItem
```

## 资质提取

```entity:Certificate
id: "CERT-CMMI5"
supplier_id: "SUP-A"
name: "CMMI Level 5"
cert_number: "CMMI-2024-001"
issuer: "CMMI Institute"
issue_date: date(2023, 1, 15)
evidence_source:
  location:
    file_name: "资质证明文件.pdf"
    page_start: 5
  validation_status: "VERIFIED_AUTO"
  validation_note: "官网查询有效"
```

## 评分项响应映射

### 条款：[SCORE-BIZ-01] CMMI 认证

```entity:BidResponseItem
id: "RESP-SUP-A-BIZ-01"
supplier_id: "SUP-A"
scoring_item_id: "SCORE-BIZ-01"
evidences: [[CERT-CMMI5]]
auto_suggested_score: 5.0
auto_check_result: true
```

### 条款：[SCORE-TECH-01] 架构设计

```entity:BidResponseItem
id: "RESP-SUP-A-TECH-01"
supplier_id: "SUP-A"
scoring_item_id: "SCORE-TECH-01"
evidences:
  - location:
      file_name: "技术方案.pdf"
      page_start: 20
      page_end: 25
      snippet_content: "本系统采用微服务架构..."
```

# 企业业绩核查记录

> **审核员**: OPERATOR-007
> **核查工具**: 原件核对 / 中标公示网查询

```config:python
from use_cases.bid_agent.models.verification import FactCheckRecord
```

## 1. 智慧城市一期项目

```entity:FactCheckRecord
id: "CHECK-SUP-A-ACH-01"
target_evidence_id: "ACHIEVEMENT-01"
target_supplier_id: "SUP-A"
operator_id: "OPERATOR-007"
method: "ORIGINAL_DOCUMENT_CHECK"
status: "CONSISTENT"
result_summary: "现场已查看中标通知书原件，金额 1200 万无涂改。"
screenshot:
  path: "blob/2025/checks/sup_a_ach_01_photo.jpg" # 示例路径
  type: "SUPPORTING_DOC"
```

# 职称证书核查记录

> **审核员**: OPERATOR-TECH-02
> **核查工具**: 职称查询系统 / 原件扫描件比对

```config:python
from use_cases.bid_agent.models.verification import FactCheckRecord
```

## 高级职称核查

```entity:FactCheckRecord
id: "CHECK-TITLE-PM-ZHANG"
target_evidence_id: "PER-PM-ZHANG"
target_supplier_id: "SUP-A"
operator_id: "OPERATOR-TECH-02"
method: "ORIGINAL_DOCUMENT_CHECK"
status: "CONSISTENT"
result_summary: "高级工程师证书（信息系统项目管理师），编号有效。"
screenshot:
  path: "blob/mock_evidence/supplier_a/titles/pm_zhang_senior.txt"
  type: "SUPPORTING_DOC"
```

```entity:FactCheckRecord
id: "CHECK-TITLE-TD-LI"
target_evidence_id: "PER-TD-LI"
target_supplier_id: "SUP-A"
operator_id: "OPERATOR-TECH-02"
method: "ORIGINAL_DOCUMENT_CHECK"
status: "CONSISTENT"
result_summary: "系统架构设计师证书，编号有效。"
screenshot:
  path: "blob/mock_evidence/supplier_a/titles/td_li_architect.txt"
  type: "SUPPORTING_DOC"
```

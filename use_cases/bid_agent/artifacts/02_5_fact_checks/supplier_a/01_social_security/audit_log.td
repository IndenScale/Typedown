# 人员社保缴纳核查记录

> **审核员**: OPERATOR-HR-01
> **核查工具**: 省人社厅公共服务平台
> **审核标准**: 缴纳单位必须为 "SUP-A (投标方)"，且连续缴纳 6 个月以上。

```config:python
from use_cases.bid_agent.models.verification import FactCheckRecord
from use_cases.bid_agent.models.core import DocumentType
```

## 1. 核心人员社保核查

```entity:FactCheckRecord
id: "CHECK-SOC-PM-ZHANG"
target_evidence_id: "PER-PM-ZHANG"
target_supplier_id: "SUP-A"
operator_id: "OPERATOR-HR-01"
method: "OFFICIAL_WEBSITE_QUERY"
status: "CONSISTENT"
result_summary: "已查到，单位一致，近6个月连续。"
screenshot:
  path: "blob/mock_evidence/supplier_a/social_security/pm_zhang.txt"
  type: "SUPPORTING_DOC"
```

```entity:FactCheckRecord
id: "CHECK-SOC-TD-LI"
target_evidence_id: "PER-TD-LI"
target_supplier_id: "SUP-A"
operator_id: "OPERATOR-HR-01"
method: "OFFICIAL_WEBSITE_QUERY"
status: "CONSISTENT"
result_summary: "已查到，单位一致。"
screenshot:
  path: "blob/mock_evidence/supplier_a/social_security/td_li.txt"
  type: "SUPPORTING_DOC"
```

## 2. 团队成员抽查 (示例)

```entity:FactCheckRecord
id: "CHECK-SOC-CORE-01"
target_evidence_id: "PER-CORE-01"
target_supplier_id: "SUP-A"
operator_id: "OPERATOR-HR-01"
method: "OFFICIAL_WEBSITE_QUERY"
status: "DOUBTFUL"
result_summary: "缴纳单位显示为'XX人力资源公司'，需提供劳务派遣协议。"
screenshot:
  path: "blob/mock_evidence/supplier_a/social_security/core_1.txt"
  type: "SUPPORTING_DOC"
```

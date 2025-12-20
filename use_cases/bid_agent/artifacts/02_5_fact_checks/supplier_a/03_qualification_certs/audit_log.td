# 执业资格证书核查记录 (PMP/建造师等)

> **审核员**: OPERATOR-EXT-03
> **核查工具**: PMI 官网 / 建造师注册查询系统

```config:python
from use_cases.bid_agent.models.verification import FactCheckRecord
```

## PMP 证书核查

```entity:FactCheckRecord
id: "CHECK-CERT-PM-ZHANG-PMP"
target_evidence_id: "PER-PM-ZHANG"
target_supplier_id: "SUP-A"
operator_id: "OPERATOR-EXT-03"
method: "OFFICIAL_WEBSITE_QUERY"
status: "CONSISTENT"
result_summary: "PMI官网查询有效，PMP Number: 1234567，有效期至 2026年。"
screenshot:
  path: "blob/mock_evidence/supplier_a/certs/pm_zhang_pmp.txt"
  type: "SUPPORTING_DOC"
```

# 企业资质核查记录 (ISO/高新等)

> **审核员**: OPERATOR-007
> **核查工具**: 认监委官网 / 高企认定网

```config:python
from use_cases.bid_agent.models.verification import FactCheckRecord
```

## 1. ISO9001 质量管理体系认证

```entity:FactCheckRecord
id: "CHECK-SUP-A-ISO9001"
target_evidence_id: "CERT-ISO9001"
target_supplier_id: "SUP-A"
operator_id: "OPERATOR-007"
method: "OFFICIAL_WEBSITE_QUERY"
status: "CONSISTENT"
result_summary: "认监委官网查询状态有效，证书编号、有效期与投标文件一致。"
query_url: "http://cx.cnca.cn/..."
screenshot:
  path: "blob/2025/checks/sup_a_iso9001_screen.png" # 示例路径
  type: "SUPPORTING_DOC"
```

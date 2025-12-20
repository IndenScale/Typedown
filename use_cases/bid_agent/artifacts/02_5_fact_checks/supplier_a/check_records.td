# 供应商 A - 事实性核查记录

> **审核员**: OPERATOR-007 (张核查)
> **核查时间**: 2025-12-19
> **状态**: 发现一处存疑，其余一致。

```config:python
from use_cases.bid_agent.models.verification import (
    FactCheckRecord, VerificationMethod, ConsistencyStatus
)
from use_cases.bid_agent.models.core import FileResource, DocumentType
```

## 1. 企业资质核查 (ISO9001)

> 关联证据: [[CERT-ISO9001]] (来自 02_bid_responses/supplier_a/01_evidence_map.td)

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
  path: "blob/2025/checks/sup_a_iso9001_screen.png"
  type: "SUPPORTING_DOC"
```

## 2. 人员社保核查 (项目经理)

> 关联证据: [[PERSON-PM-01]] (假设已提取)

```entity:FactCheckRecord
id: "CHECK-SUP-A-PM-SOCIAL"
target_evidence_id: "PERSON-PM-01"
target_supplier_id: "SUP-A"
operator_id: "OPERATOR-007"
method: "OFFICIAL_WEBSITE_QUERY"
status: "DOUBTFUL"
result_summary: "查询近6个月社保记录，显示缴纳单位为'XX劳务派遣公司'，非投标单位直缴。"
discrepancy_details: "招标文件要求必须由投标单位直缴社保，需进一步确认是否允许派遣。"
screenshot:
  path: "blob/2025/checks/sup_a_pm_social.png"
  type: "SUPPORTING_DOC"
```

## 3. 业绩核查 (智慧城市一期)

> 关联证据: [[ACHIEVEMENT-01]]

```entity:FactCheckRecord
id: "CHECK-SUP-A-ACH-01"
target_evidence_id: "ACHIEVEMENT-01"
target_supplier_id: "SUP-A"
operator_id: "OPERATOR-007"
method: "ORIGINAL_DOCUMENT_CHECK"
status: "CONSISTENT"
result_summary: "现场已查看中标通知书原件，金额 1200 万无涂改。"
screenshot:
  path: "blob/2025/checks/sup_a_ach_01_photo.jpg"
  type: "SUPPORTING_DOC"
```

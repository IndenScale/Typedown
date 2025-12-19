# 服务合同: 数据 ETL 迁移

**合同编号**: CTR-2023-ACN-ETL
**服务商**: Accenture Digital

本合同涵盖从 Salesforce 到 Titan CRM 的所有历史数据迁移工作。
服务商必须签署最严格的 NDA，因为涉及全量客户联系方式。

```config:python
import sys
import os
current_dir = os.getcwd()
erp_root = os.path.abspath(os.path.join(current_dir, "../../../../../../../.."))
if erp_root not in sys.path:
    sys.path.append(erp_root)

from use_cases.headerless_erp.models.pmo.documents import Contract
from use_cases.headerless_erp.models.core.primitives import Money
```

```entity:Contract
id: "ctr_acn_etl_001"
project_code: "PROJ-2024-088"
vendor_name: "Accenture"
title: "Salesforce Data ETL Service"
sign_date: "2024-01-15"
total_value:
    amount: 450000
    currency: "USD"
terms_summary: "Fixed Price Contract. Penalty for data leak > 10M USD."
```

# RFI: 数据迁移服务

```config:python
import sys
import os
current_dir = os.getcwd()
erp_root = os.path.abspath(os.path.join(current_dir, "../../../../../../../.."))
if erp_root not in sys.path:
    sys.path.append(erp_root)

from use_cases.headerless_erp.models.pmo.documents import RFI
```

```entity:RFI
id: "rfi_2023_data_migration"
project_code: "PROJ-2024-088"
title: "Legacy Salesforce Data Migration Service"
issued_date: "2023-12-01"
vendor_list: "Accenture, Deloitte, Capgemini"
status: "Closed"
content: """
Requirement for a partner to handle the extraction, transformation, and loading (ETL) of 10 years of sales data.
Volume: ~5TB unstructured data, ~50M records.
Critical requirement: Zero downtime migration strategy needed.
"""
```

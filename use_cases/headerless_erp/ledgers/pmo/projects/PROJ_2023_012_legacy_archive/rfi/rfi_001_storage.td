# RFI: 冷存储归档方案

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
id: "rfi_2023_cold_storage"
project_code: "PROJ-2023-012"
title: "Long-term Immutable Cold Storage Solution"
issued_date: "2023-05-15"
vendor_list: "AWS, Azure, Iron Mountain"
status: "Closed"
content: """
Evaluation of cloud vs physical storage for 10-year archival compliance.
Must support WORM (Write Once Read Many) policy to satisfy legal hold requirements.
Expected retrieval time: < 12 hours.
"""
```

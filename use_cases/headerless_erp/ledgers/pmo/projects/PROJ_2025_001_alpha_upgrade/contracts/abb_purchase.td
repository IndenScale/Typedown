# 采购合同: ABB 工业机器人

**合同编号**: CTR-2024-ABB-099
**签约方**: ABB Engineering (Shanghai) Ltd.

## 条款摘要

1.  **标的物**:
    *   IRB 6700-200/2.60 x 4 台2
    *   IRC5 控制柜 x 4 台
    *   RobotStudio 授权 x 1 License
2.  **交付条款**: DDP Suzhou Factory (2024-12-10 前).
3.  **付款方式**: 30% 预付，60% 到货验收，10% 质保金 (12个月后支付)。

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
id: "ctr_abb_001"
project_code: "PROJ-2025-001"
vendor_name: "ABB Engineering"
title: "Purchase of 4x IRB 6700 Robotic Arms"
sign_date: "2024-10-20"
total_value:
    amount: 3200000
    currency: "CNY"
terms_summary: "30-60-10 Payment Term; 24 Months Warranty"
```

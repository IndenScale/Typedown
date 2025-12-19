# 可行性对比: 云存储 vs 磁带

**日期**: 2023-04-10
**作者**: Infrastructure Team

## 方案对比

| 维度 | Option A: Amazon Glacier | Option B: Iron Mountain Tape |
| :--- | :--- | :--- |
| **初期投入** | $0 (OPEX) | $50,000 (CAPEX, 磁带机) |
| **年存储费** | $12,000 | $5,000 |
| **恢复时间** | 12 小时 | 48-72 小时 (人工取带) |
| **可靠性** | 99.999999999% | 存在发霉、消磁风险 |

## 结论

虽然磁带的年存储费更低，但考虑到 AWS 提供的 Object Lock 功能可以“开箱即用”地满足 SEC 17a-4 合规要求，而由于磁带需要复杂的物理安保程序来满足同等合规性，管理成本过高。

**推荐**: Option A (Amazon Glacier).

```config:python
import sys
import os
current_dir = os.getcwd()
erp_root = os.path.abspath(os.path.join(current_dir, "../../../../../../../.."))
if erp_root not in sys.path:
    sys.path.append(erp_root)

from use_cases.headerless_erp.models.pmo.documents import FeasibilityStudy
```

```entity:FeasibilityStudy
id: "feas_archive_cloud_vs_tape"
project_code: "PROJ-2023-012"
title: "Cold Storage Technology Selection"
author: "Infra Team"
roi_prediction: "N/A (Compliance Project)"
conclusion: "Select AWS Glacier for better compliance and data durability."
```

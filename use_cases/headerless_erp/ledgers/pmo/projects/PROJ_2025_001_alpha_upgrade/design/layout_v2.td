# 技术设计: 产线布局改造 V2

**版本**: 2.0 (Approved)
**设计师**: Chief Engineer Wong

## 设计变更说明 (V1 -> V2)

在 V1 方案中，我们将机器人直接安装在现有工位。但在仿真中发现，3 号工位的机械臂在极限姿态下会在此干涉 AGV 通道。
**V2 修改**: 将 3 号、4 号工位向北平移 1.5 米，为此需要拆除旧的工具间墙体。

```config:python
import sys
import os
current_dir = os.getcwd()
erp_root = os.path.abspath(os.path.join(current_dir, "../../../../../../../.."))
if erp_root not in sys.path:
    sys.path.append(erp_root)

from use_cases.headerless_erp.models.pmo.documents import DesignDocument
```

```entity:DesignDocument
id: "design_alpha_layout_v2"
project_code: "PROJ-2025-001"
title: "Alpha Line Layout Plan V2"
version: "2.0"
approver_id: "emp_prod_head_001"
technical_summary: "Shift station 3 & 4 by 1.5m North. Requires demolition of Tool Room wall."
```

# RFI 001: 工业机械臂采购询价

## 采购背景

为了实现 Alpha 产线的自动化目标，我们需要采购 6 轴工业机械臂。

技术团队对比了现有的主流方案，我们需要机器人在 **Payload (负载)** 和 **Reach (臂展)** 之间取得平衡。T-Series 因包含重型电机组件，单个工件重约 8.5kg，考虑到夹具重量，负载必须 > 10kg。同时，现有产线布局紧凑，要求机器人能在狭小空间内灵活作业。

## 询价单定义

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
id: "rfi_2024_robotic_arm"
project_code: "PROJ-2025-001"
title: "High-Precision Industrial Robotic Arm Procurement"
issued_date: "2024-11-10"
vendor_list: "ABB, KUKA, Fanuc, Yaskawa"
status: "Closed"
content: """
Specifications:
- 6-axis articulation
- Payload > 10kg
- Reach > 1.5m
- IP67 protection class (due to oil mist in environment)
"""
```

## 评审纪要

*   **ABB**: 优势在于 RobotStudio 仿真软件非常好用，能大幅缩短离线编程时间。报价适中。
*   **Fanuc**: 硬件极其可靠，但软件生态相对封闭，且不支持我们现有的 Siemens PLC 协议，需要额外网关。
*   **KUKA**: 精度最高，但交货期长达 6 个月，无法满足 Q3 投产要求。

**最终结论**: 选择 **ABB**。

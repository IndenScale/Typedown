# Alpha 产线升级项目档案 (Project Dossier)

## 1. 战略背景与动因

**"如果不升级，我们将在 18 个月内失去对越南工厂的成本优势。"** —— *2024年度董事会会议纪要*

Alpha 产线是我们位于苏州工厂的核心装配线，主要负责 T-Series 产品的组装。自 2018 年投产以来，它一直是公司的现金牛。然而，随着 2023 年劳动力成本的上升（同比上涨 12%），以及竞争对手（特别是位于东南亚的工厂）的激进定价，Alpha 产线的净利润率已从 15% 跌至 8%。

痛点分析：
*   **人工依赖重**：目前的装配环节自动化率仅为 45%，关键的精密焊接仍需熟练工操作。
*   **柔性不足**：切换产品线需要停机 48 小时进行重新工装。

本项目旨在引入 ABB 工业机器人手臂，配合西门子最新的 PLC 视觉控制系统，将自动化率一步跃升至 85%，并实现“一键换线”。

## 2. 项目核心数据 (Legal Manifest)

以下定义了本项目在 ERP 系统中的法定身份。任何采购、报销与工时填报均需引用此 ID。

```config:python
import sys
import os
current_dir = os.getcwd()
erp_root = os.path.abspath(os.path.join(current_dir, "../../../../../.."))
if erp_root not in sys.path:
    sys.path.append(erp_root)

from use_cases.headerless_erp.models.pmo.project import Project
```

```entity:Project
id: "proj_2025_alpha_upgrade"
name: "Alpha Production Line Upgrade"
code: "PROJ-2025-001"
manager_id: "emp_alpha_lead_001" # Rick Deckard
status: "Delivery"
budget:
    amount: 5000000
    currency: "CNY"
```

## 3. 当前进展 (Live Status)

*   **2024-12-10**: 首批 4 台 ABB IRB-6700 机械臂已运抵苏州保税区。
*   **当前阻塞点**: 现场地基加固工程延期 3 天，可能影响下周的设备进场。Rick 正在协调施工队通宵作业。

## 4. 关键风险

> ⚠️ **警告**: 如果 Q3 试运行期间出现故障，将直接影响“双十一”备货。PMO 已要求建立 24 小时现场响应机制。

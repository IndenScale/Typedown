# PMO 账本 (PMO Ledger)

PMO 账本是企业所有项目与交付事务的**单一事实来源 (Single Source of Truth)**。

## 目录结构

- `projects/`: 项目组合管理
  - `index.td`: 全量项目清单 (Project Registry)。记录项目的基础信息、状态与预算概览。
- (规划中) `resources/`: 资源分配与排期记录。
- (规划中) `milestones/`: 关键里程碑验收记录。

## 治理规则

所有进入此账本的数据必须符合 `governance/pmo` 中的 Spec 规范，特别是：

1. 项目编码必须唯一且符合命名规范 (`PROJ-YYYY-NNN`)。
2. 必须指定有效的项目经理 ID。
3. 项目预算必须包含币种。

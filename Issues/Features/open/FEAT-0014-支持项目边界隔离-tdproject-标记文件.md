---
id: FEAT-0014
type: feature
status: open
stage: doing
title: 支持项目边界隔离（.tdproject 标记文件）
created_at: '2026-02-12T20:41:14'
updated_at: '2026-02-12T20:41:57'
parent: EPIC-0000
dependencies: []
related: []
domains: []
tags:
- '#EPIC-0000'
- '#FEAT-0014'
files:
- src/typedown/core/base/utils.py
- cookbook/01_getting_started/en/00_basic_modeling/.tdproject
- cookbook/01_getting_started/en/01_schema_constraints/.tdproject
- cookbook/01_getting_started/en/02_inheritance/.tdproject
- cookbook/01_getting_started/en/03_simple_rules/.tdproject
- cookbook/01_getting_started/en/04_context_interaction/.tdproject
- cookbook/01_getting_started/en/05_global_governance/.tdproject
- cookbook/01_getting_started/en/06_modular_project/.tdproject
- cookbook/01_getting_started/zh/00_basic_modeling/.tdproject
- cookbook/01_getting_started/zh/01_schema_constraints/.tdproject
- cookbook/01_getting_started/zh/02_inheritance/.tdproject
- cookbook/01_getting_started/zh/03_simple_rules/.tdproject
- cookbook/01_getting_started/zh/04_context_interaction/.tdproject
- cookbook/01_getting_started/zh/05_global_governance/.tdproject
- cookbook/01_getting_started/zh/06_modular_project/.tdproject
- cookbook/02_use_cases/rpg_campaign/.tdproject
- cookbook/02_use_cases/bid_agent/.tdproject
- cookbook/02_use_cases/headerless_erp/.tdproject
- cookbook/02_use_cases/compliance_audit/.tdproject
- cookbook/02_use_cases/pmo_saas/.tdproject
criticality: medium
solution: null
opened_at: '2026-02-12T20:41:14'
---

## FEAT-0014: 支持项目边界隔离（.tdproject 标记文件）

## Objective
解决 cookbook 案例之间的全局命名空间冲突问题。当多个子目录（如 en/01_schema_constraints 和 zh/01_schema_constraints）定义相同 ID（如 Book）时，当前全局编译会导致 E0221/E0241 重复 ID 错误。

## Acceptance Criteria
- [x] 引入 `.tdproject` 标记文件作为强项目边界
- [x] 修改 `find_project_root()` 函数，遇到 `.tdproject` 立即停止向上查找
- [x] 为所有 cookbook 示例添加 `.tdproject` 文件

## Technical Tasks
- [x] 修改 `src/typedown/core/base/utils.py` 中的 `find_project_root()` 函数
- [x] 为 cookbook/01_getting_started 的中英文示例添加 `.tdproject`
- [x] 为 cookbook/02_use_cases 的各案例添加 `.tdproject`

## Review Comments
无

---
id: FEAT-0009
uid: 32d170
type: feature
status: closed
stage: done
title: 'Simplify LSP: Remove Code Lens and Rename features'
created_at: '2026-02-12T09:13:51'
updated_at: '2026-02-12T09:15:33'
parent: EPIC-0000
dependencies: []
related: []
domains: []
tags:
- '#EPIC-0000'
- '#FEAT-0009'
files:
- src/typedown/server/application.py
- src/typedown/server/features/code_lens.py
- src/typedown/server/features/rename.py
- tests/server/features/test_code_lens.py
- tests/server/features/test_rename.py
criticality: medium
solution: null # implemented, cancelled, wontfix, duplicate
opened_at: '2026-02-12T09:13:51'
---

## FEAT-0009: Simplify LSP: Remove Code Lens and Rename features

## Objective
简化 LSP 服务器，移除使用率低且维护成本高的特性：
- **Code Lens**: 主要用于「Run Spec」按钮，但可通过命令面板或其他方式触发
- **Rename**: 重命名功能复杂度高（跨文件扫描），但使用频率低

## Acceptance Criteria
- [x] 删除 `code_lens.py` 及相关测试
- [x] 删除 `rename.py` 及相关测试
- [x] 更新 `application.py` 移除相关导入
- [x] 确保剩余 LSP 功能正常工作

## Technical Tasks
- [x] 删除 src/typedown/server/features/code_lens.py (239行)
- [x] 删除 src/typedown/server/features/rename.py (92行)
- [x] 删除 tests/server/features/test_code_lens.py
- [x] 删除 tests/server/features/test_rename.py
- [x] 更新 src/typedown/server/application.py 移除导入
- [x] 运行测试验证 (16 tests passed)

## Review Comments
代码已删除，测试全部通过。

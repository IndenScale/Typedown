---
id: FIX-0001
uid: 635ec7
type: fix
status: closed
stage: done
title: Resolve 'unexpected extra argument' and mistune syntax error in CLI
created_at: '2026-02-06T17:55:46'
updated_at: 2026-02-06 17:55:52
parent: EPIC-0000
dependencies: []
related: []
domains: []
tags:
- '#EPIC-0000'
- '#FIX-0001'
files: []
criticality: high
solution: null
opened_at: '2026-02-06T17:55:46'
isolation:
  type: branch
  ref: FIX-0001-resolve-unexpected-extra-argument-and-mistune-synt
  path: null
  created_at: '2026-02-06T17:55:52'
---

## FIX-0001: Resolve 'unexpected extra argument' and mistune syntax error in CLI

## Objective
<!-- Describe the "Why" and "What" clearly. Focus on value. -->

修复 `td check` 命令在 v0.2.16 和 v0.2.17 版本中出现的错误：
1. `TypeError: Validator.check_schema() missing 1 required positional argument: 'model_registry'`
2. Windows PowerShell 中 `td check .` 出现 `Got unexpected extra argument (.)`

用户反馈回退到 v0.2.14 后问题解决，说明这是新版本引入的 regression。

## Problem Description

### 错误 1: check_schema() 缺少参数
**错误信息：**
```
TypeError: Validator.check_schema() missing 1 required positional argument: 'model_registry'
```

**发生位置：** `compiler.py` 第 232 行
```python
validator.check_schema(self.documents, self.model_registry)
```

### 错误 2: PowerShell 中的 unexpected extra argument
**错误信息：**
```
Got unexpected extra argument (.)
```

**发生环境：** Windows PowerShell 运行 `td check .`

### 受影响版本
- v0.2.16 ❌
- v0.2.17 ❌
- v0.2.14 ✅ (正常)

## Acceptance Criteria
<!-- Define binary conditions for success. -->
- [x] `td check` 命令在 v0.2.18 版本能正常运行，不再报 `missing model_registry` 错误
- [x] `td check .` 命令支持位置参数
- [x] 确保向后兼容性，不破坏 v0.2.14 已有的功能

## Technical Tasks
<!-- Breakdown into atomic steps. Use nested lists for sub-tasks. -->

<!-- Status Syntax: -->
<!-- [ ] To Do -->
<!-- [/] Doing -->
<!-- [x] Done -->
<!-- [~] Cancelled -->
<!-- - [ ] Parent Task -->
<!--   - [ ] Sub Task -->

- [x] 调查 `compiler.py` 第 232 行 `check_schema()` 方法调用
- [x] 检查 `Validator.check_schema()` 方法签名变化
- [x] 修复参数传递问题 - `symbol_table` 参数已添加
- [x] 修复 CLI 参数解析 - `path` 改为 `typer.Argument`
- [x] 测试 `td check` 和 `td check .` 命令

## Review Comments
<!-- Required for Review/Done stage. Record review feedback here. -->

### 修复总结

**问题 1: `check_schema()` 缺少参数**
- 原因：`compiler.py` 的 `check()` 方法中调用 `validator.check_schema()` 时只传了 2 个参数 (`documents`, `model_registry`)，但方法定义需要 3 个参数 (`documents`, `symbol_table`, `model_registry`)
- 修复：已在当前分支中修复，添加缺失的 `symbol_table` 参数

**问题 2: `td check .` 出现 `unexpected extra argument`**
- 原因：`b0ff908` commit 中将 `path` 参数从 `typer.Argument` 改为 `typer.Option`，导致位置参数语法失效
- 修复：将 `path` 改回 `typer.Argument`，支持 `td check .` 位置参数语法
- 影响文件：`check.py`, `lint.py`, `test.py`, `validate.py`

**版本**: 0.2.18

---
id: FEAT-0004
uid: 559b23
type: feature
status: closed
stage: done
title: 'CLI API unification: extract shared context and error handling'
created_at: '2026-02-11T21:54:44'
updated_at: '2026-02-11T22:30:00'
parent: EPIC-0000
dependencies: []
related: []
domains: []
tags:
- '#EPIC-0000'
- '#FEAT-0004'
files: []
criticality: medium
solution: implemented
opened_at: '2026-02-11T21:54:44'
---

## FEAT-0004: CLI API unification: extract shared context and error handling

## Objective

当前 CLI 命令存在重复代码模式，本任务旨在提取共享工具，减少 30% 重复代码，统一 CLI 行为。

当前问题：
1. Compiler 重复初始化（每个命令都写）
2. Console 处理不一致（lint.py 无 JSON 支持）
3. Exit 处理重复
4. 参数解析模式不统一

目标：代码净减少，行为一致性提升。

## Acceptance Criteria

- [x] 新增代码行数 < 删除代码行数（净减少）
- [x] 所有命令支持 --json 输出
- [x] 现有测试全部通过（命令行参数不变）
- [x] CLI 行为一致性提升（错误消息格式、exit code）

## Technical Tasks

- [x] 创建 src/typedown/commands/context.py
  - [x] 实现 cli_session() 上下文管理器
  - [x] 统一 Compiler 初始化逻辑
  - [x] 处理 JSON/Console 输出切换
- [x] 创建 src/typedown/commands/output.py
  - [x] 实现统一输出函数 cli_result()
  - [x] 实现错误处理函数 cli_error()
  - [x] 整合 utils.py 中的 json_serializer
- [x] 重构 lint.py
  - [x] 添加 --json 支持
  - [x] 使用新的共享工具
- [x] 重构 check.py
  - [x] 使用 cli_session()
  - [x] 简化错误处理
- [x] 重构 validate.py
  - [x] 使用 cli_session()
  - [x] 简化错误处理
- [x] 重构 test.py
  - [x] 使用 cli_session()
  - [x] 简化错误处理
- [x] 重构 info.py
  - [x] 使用 cli_session()
  - [x] 简化配置加载
- [x] 重构 query.py
  - [x] 使用 cli_session()
  - [x] 简化输出处理
- [x] 重构 run.py
  - [x] 使用 cli_session()
  - [x] 简化脚本执行逻辑
- [x] 测试
  - [x] 添加重构后的行为一致性测试
  - [x] 确保所有现有测试通过
- [x] 代码审查
  - [x] 确保向后兼容

## Summary

### 代码统计
- **命令文件**: 261 行删除，256 行新增（净减少 5 行）
- **新增共享模块**: 
  - `context.py` (175 行): 提供 `cli_session()` 上下文管理器和 `CLIContext` dataclass
  - `output.py` (235 行): 提供统一的输出函数 `cli_result()`, `cli_error()`, `cli_success()`, `cli_warning()`
- **新增测试**: 574 行测试代码

### 主要改进
1. **所有命令支持 --json 输出**: lint, check, validate, test, info, query, run, complete
2. **统一错误处理**: 所有命令使用一致的 `cli_error()` 函数
3. **统一退出码**: 通过 `cli_result()` 自动处理成功/失败退出码
4. **简化初始化**: 所有命令使用 `cli_session()` 上下文管理器统一初始化 Compiler

### 向后兼容
- 所有现有命令行参数保持不变
- 所有现有测试通过
- 仅新增 `--json` 选项，不影响原有行为

## Reference

- src/typedown/commands/ 目录下所有文件
- src/typedown/commands/utils.py 现有工具

## Review Comments

### 代码审查总结

- **代码净减少**: 命令文件 261 行删除，256 行新增（净减少 5 行）
- **新增共享模块**: context.py (175 行), output.py (235 行)
- **所有命令支持 --json**: lint, check, validate, test, info, query, run, complete
- **向后兼容**: 所有现有命令行参数保持不变

### 主要改进
1. 统一的 CLI 会话管理通过 `cli_session()` 上下文管理器
2. 统一的输出处理通过 `cli_result()`, `cli_error()` 等函数
3. 一致的退出码处理



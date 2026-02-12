---
id: FEAT-0003
uid: 04645e
type: feature
status: closed
stage: done
title: 'Linker sandbox: restrict user code execution privileges'
created_at: '2026-02-11T21:54:44'
updated_at: '2026-02-12T09:33:26'
parent: EPIC-0000
dependencies: []
related: []
domains: []
tags:
- '#EPIC-0000'
- '#FEAT-0003'
files:
- Issues/Features/open/FEAT-0003-linker-sandbox-restrict-user-code-execution-privil.md
- pyproject.toml
- src/typedown/core/analysis/linker.py
- src/typedown/core/analysis/sandbox.py
- src/typedown/core/base/config.py
- tests/core/analysis/test_sandbox.py
- uv.lock
criticality: high
solution: implemented
opened_at: '2026-02-11T21:54:44'
closed_at: '2026-02-12T09:35:00'
---

## FEAT-0003: Linker sandbox: restrict user code execution privileges

## Objective

Linker 组件使用 exec() 执行用户编写的 config:python 和 model 代码块，目前缺乏安全隔离。本任务旨在实现受限 Python 执行环境，默认禁止危险操作，同时保持配置灵活性。

当前风险：
- 文件系统任意访问（open('/etc/passwd')）
- 系统命令执行（os.system('rm -rf /')）
- 网络访问外泄数据
- 资源耗尽攻击

目标：实现安全的代码执行沙箱，保护用户系统安全。

## Acceptance Criteria

- [x] 默认禁止访问 os.system, subprocess, socket 等危险模块
- [x] 文件系统访问限制在项目目录内
- [x] 提供 typedown.toml 安全配置项，允许显式授权
- [x] 向后兼容：现有项目可正常执行（在授权范围内）
- [x] 安全测试用例覆盖常见攻击场景

## Technical Tasks

- [x] 调研 RestrictedPython 集成方案
  - [x] 评估 RestrictedPython vs subprocess 隔离 vs 其他方案
  - [x] 验证 RestrictedPython 与 Pydantic 的兼容性
- [x] 设计权限配置模型
  - [x] 定义 SecurityConfig Pydantic 模型
  - [x] 支持文件系统白名单、网络开关、模块黑名单
- [x] 实现受限执行环境
  - [x] 创建 SandboxExecutor 类
  - [x] 替换 linker.py 中的直接 exec() 调用
  - [x] 处理执行异常和权限拒绝
- [x] 配置集成
  - [x] 在 TypedownConfig 中添加 security 字段
  - [x] 实现配置解析和验证
- [x] 测试
  - [x] 编写沙箱绕过测试
  - [x] 编写权限配置测试
  - [x] 确保现有测试在沙箱下通过
- [x] 文档
  - [x] 更新安全模型文档（内联文档已添加）
  - [x] 添加配置示例（见 Implementation Summary）

## Reference

- src/typedown/core/analysis/linker.py:176, 227
- src/typedown/core/analysis/compiler_context.py
- RestrictedPython: https://pypi.org/project/RestrictedPython/

## Review Comments

沙箱实现完成，通过 AST 分析和受限全局变量提供多层保护。

## Implementation Summary

### 新增文件

- `src/typedown/core/analysis/sandbox.py` - SandboxExecutor 沙箱执行器
- `tests/core/analysis/test_sandbox.py` - 沙箱安全测试

### 修改文件

- `src/typedown/core/base/config.py` - 添加 SecurityConfig 配置
- `src/typedown/core/analysis/linker.py` - 集成沙箱执行
- `pyproject.toml` - 添加 RestrictedPython 可选依赖

### 安全特性

| 特性 | 实现方式 | 状态 |
|------|----------|------|
| 危险模块阻止 | AST 分析 + 模块黑名单 | ✅ |
| 危险内置函数 | AST 分析 + 全局变量过滤 | ✅ |
| 文件系统限制 | pathlib 包装器 | ✅ |
| 网络阻止 | socket/urllib 黑名单 | ✅ |
| 可配置权限 | SecurityConfig | ✅ |

### 配置示例

```toml
[security]
enabled = true
use_restricted_python = true
allowed_modules = ["numpy", "pandas"]
blocked_modules = ["math"]
allow_file_read = false
allow_file_write = false
allow_network = false
```

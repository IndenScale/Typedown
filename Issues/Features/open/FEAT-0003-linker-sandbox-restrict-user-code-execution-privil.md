---
id: FEAT-0003
uid: 04645e
type: feature
status: open
stage: doing
title: 'Linker sandbox: restrict user code execution privileges'
created_at: '2026-02-11T21:54:44'
updated_at: '2026-02-12T09:26:00'
parent: EPIC-0000
dependencies: []
related: []
domains: []
tags:
- '#EPIC-0000'
- '#FEAT-0003'
files: []
criticality: high
solution: null # implemented, cancelled, wontfix, duplicate
opened_at: '2026-02-11T21:54:44'
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

- [ ] 默认禁止访问 os.system, subprocess, socket 等危险模块
- [ ] 文件系统访问限制在项目目录内
- [ ] 提供 typedown.toml 安全配置项，允许显式授权
- [ ] 向后兼容：现有项目可正常执行（在授权范围内）
- [ ] 安全测试用例覆盖常见攻击场景

## Technical Tasks

- [ ] 调研 RestrictedPython 集成方案
  - [ ] 评估 RestrictedPython vs subprocess 隔离 vs 其他方案
  - [ ] 验证 RestrictedPython 与 Pydantic 的兼容性
- [ ] 设计权限配置模型
  - [ ] 定义 SecurityConfig Pydantic 模型
  - [ ] 支持文件系统白名单、网络开关、模块黑名单
- [ ] 实现受限执行环境
  - [ ] 创建 SandboxExecutor 类
  - [ ] 替换 linker.py 中的直接 exec() 调用
  - [ ] 处理执行异常和权限拒绝
- [ ] 配置集成
  - [ ] 在 TypedownConfig 中添加 security 字段
  - [ ] 实现配置解析和验证
- [ ] 测试
  - [ ] 编写沙箱绕过测试
  - [ ] 编写权限配置测试
  - [ ] 确保现有测试在沙箱下通过
- [ ] 文档
  - [ ] 更新安全模型文档
  - [ ] 添加配置示例

## Reference

- src/typedown/core/analysis/linker.py:176, 227
- src/typedown/core/analysis/compiler_context.py
- RestrictedPython: https://pypi.org/project/RestrictedPython/

## Review Comments


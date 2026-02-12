---
id: FEAT-0012
uid: e7e2bd
type: feature
status: open
stage: doing
title: 构建 Extension 与 Python Core 集成测试框架
created_at: '2026-02-12T14:28:24'
updated_at: '2026-02-12T14:43:35'
parent: EPIC-0000
dependencies: []
related: []
domains: []
tags:
- '#EPIC-0000'
- '#FEAT-0012'
files:
- pyproject.toml
- scripts/run-integration-tests.sh
- tests/integration/FRAMEWORK_SUMMARY.md
- tests/integration/README.md
- tests/integration/__init__.py
- tests/integration/conftest.py
- tests/integration/test_compiler_lsp.py
- tests/integration/test_e2e_scenarios.py
- tests/integration/test_lsp_server.py
- tests/integration/test_vscode_extension.py
- uv.lock
criticality: medium
solution: null # implemented, cancelled, wontfix, duplicate
opened_at: '2026-02-12T14:28:24'
---

## FEAT-0012: 构建 Extension 与 Python Core 集成测试框架

## Objective
<!-- Describe the "Why" and "What" clearly. Focus on value. -->

## Acceptance Criteria
<!-- Define binary conditions for success. -->
- [ ] Criteria 1

## Technical Tasks
<!-- Breakdown into atomic steps. Use nested lists for sub-tasks. -->

<!-- Status Syntax: -->
<!-- [ ] To Do -->
<!-- [/] Doing -->
<!-- [x] Done -->
<!-- [~] Cancelled -->
<!-- - [ ] Parent Task -->
<!--   - [ ] Sub Task -->

- [x] 构建 Extension 与 Python Core 集成测试框架

## Review Comments

集成测试框架已成功构建：
- 68 个测试通过
- 9 个测试跳过（待实现完整 LSP 协议栈支持）
- 测试覆盖 LSP 协议、Compiler 集成、端到端场景

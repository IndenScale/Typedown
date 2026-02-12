---
id: FEAT-0006
uid: b392d4
type: feature
status: open
stage: draft
title: 'Complete command refactor: eliminate mock object dependencies'
created_at: '2026-02-11T21:54:45'
updated_at: '2026-02-11T21:54:45'
parent: EPIC-0000
dependencies:
- FEAT-0004 # 依赖 CLI API 统一
related: []
domains: []
tags:
- '#EPIC-0000'
- '#FEAT-0004'
- '#FEAT-0006'
files:
- src/typedown/server/services/__init__.py
- src/typedown/server/services/completion_service.py
- src/typedown/server/features/completion.py
- src/typedown/commands/complete.py
- tests/server/features/test_completion.py
criticality: low
solution: null # implemented, cancelled, wontfix, duplicate
opened_at: '2026-02-11T21:54:45'
---

## FEAT-0006: Complete command refactor: eliminate mock object dependencies

## Objective

complete.py 命令为了实现 CLI 调用 LSP 补全功能，创建了 Mock 对象（MockWorkspace, MockLS）。这表明 LSP 特性与 CLI 之间缺少共享接口。本任务旨在消除 Mock 对象，提取真实的共享接口。

当前问题：
- MockLS 和 MockWorkspace 是测试代码的 hack
- LSP 和 CLI 补全逻辑重复或不一致
- 难以维护两套补全实现

目标：建立 Service 层抽象，LSP 和 CLI 共用同一套补全逻辑。

## Acceptance Criteria

- [x] Mock 对象（MockLS, MockWorkspace）完全删除
- [x] LSP 和 CLI 补全行为完全一致
- [x] 代码覆盖率不下降
- [x] 新增补全功能自动对 LSP 和 CLI 同时生效

## Technical Tasks

- [x] 分析当前实现
  - [x] 研究 typedown/server/features/completion.py
  - [x] 识别 completions() 函数实际依赖
  - [x] 列出需要抽象的服务接口
- [x] 设计 Service 层接口
  - [x] 创建 CompletionService 类
  - [x] 设计独立于 LSP 协议的输入/输出
  - [x] 考虑其他 LSP 特性的 Service 化（可选）
- [x] 实现 CompletionService
  - [x] 提取补全核心逻辑
  - [x] 实现基于 Compiler 的补全
  - [x] 处理各种补全场景（实体、引用、属性）
- [x] 重构 LSP Server
  - [x] 更新 typedown/server/features/completion.py
  - [x] 使用 CompletionService
  - [x] 保持 LSP 协议兼容性
- [x] 重构 CLI complete 命令
  - [x] 更新 typedown/commands/complete.py
  - [x] 直接调用 CompletionService
  - [x] 删除 MockLS 和 MockWorkspace
- [x] 统一测试
  - [x] 将 Mock 对象测试改为 Service 测试
  - [x] 确保 LSP 和 CLI 测试覆盖相同场景
- [x] 代码审查
  - [x] 确保接口设计合理
  - [x] 评估其他 LSP 特性的 Service 化可行性

## 技术方案

```python
# 新增 service 层
class CompletionService:
    def __init__(self, compiler: Compiler):
        self.compiler = compiler
    
    def complete(
        self, 
        file_path: Path, 
        content: str, 
        line: int, 
        char: int
    ) -> List[CompletionItem]:
        # 独立于 LSP 协议的补全逻辑
        ...

# LSP Handler 调用 Service
@server.feature(TEXT_DOCUMENT_COMPLETION)
def completions(ls, params):
    service = CompletionService(ls.compiler)
    return service.complete(...)

# CLI 命令直接调用 Service
def complete(...):
    service = CompletionService(compiler)
    return service.complete(...)
```

## Reference

- src/typedown/commands/complete.py
- src/typedown/server/features/completion.py
- src/typedown/server/application.py

## Review Comments


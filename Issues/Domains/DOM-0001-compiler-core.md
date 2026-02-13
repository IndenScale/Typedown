---
id: DOM-0001
type: domain
title: Compiler Core & AST
status: active
owner: IndenScale
created_at: 2026-01-19
tags: [python, ast, core]
---

# DOM-0001-compiler-core

## 1. Definition (定义)

此领域涵盖 Typedown 语言的核心编译基础设施。它是所有上层服务（CLI, LSP, WebAssembly）的基石。

**Scope**: `src/typedown/core/`

## 2. Key Components (关键组件)

- **Parser**: 负责将 Markdown/YAML 文本解析为 AST。
- **AST (Abstract Syntax Tree)**: 定义 `Model`, `Entity`, `Spec` 等节点结构。
- **Compiler**: 执行引用解析（ID 和 Hash）和 Reference 解构。
- **Runtime**: 提供轻量级执行环境 (如 Spec 校验)。

## 3. Principles (原则)

1.  **Platform Agnostic**: 核心代码必须是纯 Python，不依赖 OS 特性，以便编译为 WASM。
2.  **Zero IO implicitly**: 核心库不应执行隐式 IO 操作，所有文件访问需通过 VFS 接口。
3.  **Strict Typing**: 内部实现必须通过 MyPy 严格模式检查。

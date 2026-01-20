---
id: DOM-0002
type: domain
title: IDE Services & LSP
status: active
owner: IndenScale
created_at: 2026-01-19
tags: [lsp, vscode, typescript, rust]
---

# Domain: IDE Services & LSP

## 1. Definition (定义)

此领域关注开发者体验 (DX)，主要包含基于 LSP 协议的语言智能服务以及 VS Code 客户端实现。

**Scope**: `src/typedown/lsp/`, `editors/vscode/`

## 2. Key Components (关键组件)

- **Language Server**: 提供 Completion, Go-to-Definition, Hover, Diagnostics 等标准服务。
- **VS Code Extension**: 负责客户端 UI 交互、命令注册、Webview 渲染。
- **WASM Bridge**: 在浏览器端运行 LSP 的适配层。

## 3. Principles (原则)

1.  **Response Time**: 所有 IntelliSense 操作需在 50ms 内响应。
2.  **Graceful Degradation**: 即使编译失败，也能提供最大程度的补全和导航。
3.  **Protocol Compliant**: 严格遵循 LSP 3.17+ 协议标准，减少非标扩展。

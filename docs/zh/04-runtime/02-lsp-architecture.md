---
title: LSP 架构
---

# LSP 与 IDE 集成 (Language Server Protocol)

Typedown 的核心价值在于将文本文档转化为结构化知识库。而这一转化的即时反馈，完全依赖于 Language Server (LSP) 的设计。

本文档阐述 Typedown LSP 的架构哲学、核心职责以及与 VS Code 插件的分工边界。

## 1. 核心架构哲学

### A. 全知全能 (Omniscience)

LSP 不应仅仅是一个语法高亮器（Syntax Highlighter）。它必须是整个项目的**大脑**。它应了解：

- 哪些文件存在？
- 它们之间的依赖关系（Dependency Graph）是什么？
- 当前项目是否违反了任何一致性规则？

### B. 编辑器无关 (Editor Agnostic)

所有智能逻辑（跳转、补全、重构、诊断）必须下沉到 LSP Server (`typedown/server/`) 实现。VS Code 插件（Client）应保持**极度轻量（Thin Client）**，仅负责：

1. 启动 LSP 进程。
2. 转发用户输入与配置。
3. 渲染 LSP 返回的 UI（Definition, Hover, Decorations）。

这确保了 Typedown 未来可以轻松适配 Vim, Emacs 或 JetBrains IDE。

### C. 混合驱动 (Hybrid Driven)

为了保证响应速度与数据新鲜度，LSP 采用双重驱动模式：

1.  **Editor Events (Fast path)**: 响应 `textDocument/didChange`。用户在编辑器中的每一次击键，都会更新内存中的 AST。这用于毫秒级的补全和语法检查。
2.  **Filesystem Watcher (Truth Path)**: 响应 `FileModified` 事件。通过 `watchdog` 监听整个项目目录。这是为了捕获外部变更（如 `git pull`、脚本生成代码），确保 LSP 的世界观与磁盘对齐。

## 2. 功能矩阵

| 功能         | 方法 (LSP Method)                 | 实现策略                                                   | 依赖核心组件                 |
| :----------- | :-------------------------------- | :--------------------------------------------------------- | :--------------------------- |
| **实时诊断** | `textDocument/publishDiagnostics` | 用户停止输入 300ms 后触发全量验证 (Validator)              | `Validator`, `Parser`        |
| **定义跳转** | `textDocument/definition`         | 基于 `EntityBlock.raw_data` 中的引用 -> 查找 `SymbolTable` | `SymbolTable`, `QueryEngine` |
| **智能补全** | `textDocument/completion`         | 识别当前 AST 节点上下文 -> 过滤可用 Handle/ID              | `SymbolTable`                |
| **悬停提示** | `textDocument/hover`              | 渲染被引用实体的 Markdown 摘要                             | `EntityBlock.data`           |
| **引用查找** | `textDocument/references`         | 反向查询依赖图 (`DependencyGraph`)                         | `DependencyGraph`            |

## 3. 实现细节

### 3.1 虚拟文件系统 (Virtual File System)

LSP 维护一份 `Workspace` 实例，其中包含：

- **Document Map**: `Path -> Document (AST)`。
- **Symbol Table**: `ID -> EntityBlock`。
- **Dependency Graph**: 实体间的引用拓扑。

### 3.2 增量更新与防抖 (Incremental & Debounce)

为了性能，我们不应在每次击键时重编整个项目。

1.  **单文件更新**: `didChange` 仅触发当前文件的 `Parser.parse()`。
2.  **局部重连**: 仅重新计算受影响文件的符号表和连接。
3.  **防抖**: 昂贵的 `Validator` (L3 Check) 应防抖执行。

### 3.3 外部（Project-Level）监听

`watchdog` 线程独立运行，当检测到非编辑器触发的变更时，主动调用 `Server.update_document_from_disk(path)`。

### 3.4 并发模型 (Concurrency Model)

为了保证状态的一致性，LSP Server 采用严格的线程安全设计：

- **Main Thread (LSP Loop)**: 处理来自 Client (VS Code) 的所有请求 (`textDocument/*`)。这是读取/写入 Compiler 状态的主要线程。
- **Watchdog Thread**: 独立监听磁盘变更。
- **Locking Strategy**: `Compiler` 及其内部状态（`documents`, `symbol_table`, `dependency_graph`）受全局**读写锁 (`threading.Lock`)** 保护。
  - Main Thread 在处理请求时获取锁。
  - Watchdog Thread 在更新磁盘状态时获取锁。
  - 这防止了在编译过程中发生竞争条件 (Race Conditions)。

## 4. VS Code Extension 分工

VS Code 插件职责仅限于：

- 注册 `.td` / `.typedown` 文件关联。
- 提供语法高亮规则 (`tmLanguage.json`) —— _注：LSP 也可以提供 Semantic Tokens，但 tmLanguage 更快且由于 Markdown 兼容性更好_。
- 启动命令 `td lsp`。

---

> **设计原则总结**：LSP 是 Typedown 的驻留态核心 (Daemonized Core)。它不仅服务于编辑器，本质上它是一个具备即时响应能力的编译器服务。

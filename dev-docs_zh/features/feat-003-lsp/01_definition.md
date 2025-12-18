# Feat 003: 语言服务器 (Language Server) 与 VS Code 扩展

## 1. 背景与目标

为了提供 IDE 级别的开发体验，我们需要实现一个符合 LSP (Language Server Protocol) 标准的语言服务器。这将使 Typedown 具备实时诊断、自动补全、跳转定义等现代编辑特性。

**目标**:

1. 构建 `typedown-server`: 基于 `pygls` 的 LSP 实现。
2. 构建 `typedown-vscode`: VS Code 客户端插件（仅负责启动 Server 和通信）。
3. 改造 `typedown-core`: 支持增量更新和有状态的工作区。

## 2. 功能特性矩阵 (Feature Matrix)

### P0: 核心体验 (MVP)

| 特性                 | 描述                                 | 实现依赖                  |
| :------------------- | :----------------------------------- | :------------------------ |
| **Diagnostics**      | 实时报告语法错误、校验错误、无效引用 | `Workspace.update_file`   |
| **Go To Definition** | `[[EntityID]]` -> 跳转到定义         | `SymbolTable`             |
| **Completion**       | `former: ...` 和 `[[` 触发 ID 补全   | `SymbolTable`             |
| **Output Channel**   | 展示构建过程日志和复杂错误链         | `server.show_message_log` |

### P1: 开发效率 (Enhanced)

| 特性                  | 描述                                   | 实现依赖                 |
| :-------------------- | :------------------------------------- | :----------------------- |
| **Hover**             | 悬停显示 Entity 摘要（类型、关键字段） | `resolved_data`          |
| **Schema Completion** | `entity:Type` 块内的字段名补全         | `Pydantic` Introspection |
| **Document Symbols**  | 文件大纲视图 (Outline)                 | `AST`                    |

### P2: 高级特性

- Find References
- Rename Entity
- Code Lens (Run Specs)

## 3. 架构设计

参考 **ADR 0010: 语言服务器架构**。

### server 组件

- **技术栈**: `pygls`
- **职责**: 协议转换 + 维护 `Workspace` 实例。
- **Overlay**: 使用内存中的文件内容覆盖磁盘内容，确保针对编辑中的代码进行检查。

### core 改造

`Workspace` 类需要增强以支持 LSP 生命周期：

- `load_workspace(root)`: 初始化。
- `update_document(uri, text)`: 单文件重解析 + 影响范围重算。
- `get_diagnostics(uri)`: 返回该文件的所有 `Diagnostic` 对象。
- `get_completion_items(uri, position)`: 返回补全列表。
- `get_definition(uri, position)`: 返回定义位置。

## 4. 任务分解 (Tasks)

- [ ] **Core Refactor**: 改造 `Workspace` 支持单文件 Update 和 Overlay 机制。
- [ ] **LSP Initial**: 搭建 `pygls` 骨架，实现 `initialize` 和 `shutdown`。
- [ ] **Feature: Diagnostics**: 实现 `textDocument/didOpen`, `didChange`, `didSave` 并在 Output Channel 输出日志。
- [ ] **Feature: Completion**: 实现基础的 Entity ID 补全。
- [ ] **Feature: Definition**: 实现跳转到定义。
- [ ] **VS Code Client**: 如果需要，创建简单的 VS Code 插件外壳来启动 Server。

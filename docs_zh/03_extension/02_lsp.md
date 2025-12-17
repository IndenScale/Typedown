# Language Server Protocol (LSP)

为了支持多种编辑器（VS Code, Neovim, IntelliJ），Typedown 实现了标准的 LSP 服务。

## 功能实现

*   `textDocument/completion`: 提供基于 Schema 的字段补全。
*   `textDocument/definition`: 处理跳转到定义。
*   `textDocument/hover`: 显示 Entity 的解析后完整数据预览。
*   `textDocument/publishDiagnostics`: 推送编译错误。

LSP 服务复用了 `tdc` 编译器的核心逻辑。

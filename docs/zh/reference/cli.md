# CLI 参考手册

`td` 命令行工具是 Typedown 的主要交互界面。

## `td test`

运行验证和测试流水线。

**用法：**
```bash
td test [PATH] [OPTIONS]
```

**参数：**
*   `PATH`: 要测试的文件或目录。默认为当前目录 `.`

**选项：**
*   `--tag`, `-t`: 按标签过滤 spec（如果支持）。

## `td lsp`

启动语言服务器协议 (LSP) 服务。通常由 IDE 扩展（如 VS Code）调用，不需要手动运行。

## `td build`

(实验性) 将文档编译为其他格式。

## `td debug`

(内部) 用于调试 AST 和解析器的工具。

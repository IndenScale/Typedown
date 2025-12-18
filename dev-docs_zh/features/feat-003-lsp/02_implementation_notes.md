# LSP 实现记录

## 1. 核心重构 (Core Refactor)

为支持 LSP 的实时性和增量更新，对 `Workspace` 进行了以下改造：

### 1.1 增量更新 (Incremental Updates)

- **`reindex_file(file_path, content=None)`**:
  - 支持传入内存中的文件内容 (`content_override`)，无需保存文件即可更新 AST。
  - 在重新解析前，会自动清除该文件之前定义的 Symbols (Entities) 和 Specs，防止重复 ID 错误。

### 1.2 独立验证 (Validation Decoupling)

- **`validate_project()`**:
  - 将原 `resolve()` 中的验证逻辑提取出来。
  - 不再遇到错误即退出 (Exit)，而是收集所有 `Diagnostics` 并返回列表。
  - 能够捕获 `TypedownError`, `EvaluationError`, `ValidationError` (Pydantic)。

### 1.3 `Parser` 增强

- `parse_file` 增加了 `content_override` 参数。

## 2. Server 实现 (`typedown/server/lsp.py`)

基于 `pygls` 实现，目前支持的功能：

- **Lifecycle**: `initialize`, `shutdown`.
- **Sync**: Full Text Sync (`textDocument/didOpen`, `didChange`, `didSave`).
- **Diagnostics**:
  - 在每次文档变更时触发全量验证 (MVP 策略)。
  - 将 `TypedownError` 转换为 LSP `Diagnostic` 对象。
  - 发布 Diagnostics 到客户端。

## 3. 当前限制 (Limitations)

- **性能**: 每次按键 (didChange) 都触发全项目验证。对于大型项目可能会有延迟。后续优化方向是只验证受影响的实体。
- **定位精度**: Pydantic 校验错误目前只能定位到 Entity 块的起始位置，无法精确到具体字段的行号。需要增强 Parser 以记录字段级 CST (Concrete Syntax Tree) 信息。

## 4. 下一步 (Next Steps)

- 实现 `textDocument/definition` (跳转定义)。
- 实现 `textDocument/completion` (自动补全)。

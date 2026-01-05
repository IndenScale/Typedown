# Website Hacks & Workarounds

## 1. LSP Worker Wheel Loading (2026-01-05)

### 问题背景

为了在浏览器端运行 Typedown LSP，我们需要通过 Pyodide 的 `micropip.install()` 加载生成的 `.whl` 文件。

遇到的障碍：

1. **相对路径失效**: 在 Next.js 生产构建中，Worker 脚本的执行上下文发生变化，相对路径（`./typedown-xxx.whl`）指向错误。
2. **文件名规范严格**: `micropip` 严格遵循 PEP 427 和 PEP 440，要求文件名必须包含符合规范的版本号（如 `0.2.12`），不支持 `latest` 等非数字版本。
3. **版本更新痛点**: 每次发布新版本（如 `0.2.13`），都需要修改源码中的文件名引用。

### Hack 方案

为了解耦代码与具体版本号，我们采用了一个**固定别名**策略：

1. **文件名**: 统一重命名为 `typedown-0.0.0-py3-none-any.whl`。
   - `0.0.0`: 作为通用占位符，满足 PEP 440 版本格式要求。
   - `py3-none-any`: 满足 PEP 427 标签要求。
2. **位置**: 放置在 `website/public/` 根目录。
3. **代码引用**:
   ```javascript
   // website/public/lsp-worker.js
   await micropip.install("/typedown-0.0.0-py3-none-any.whl");
   ```

### 维护指南

当需要更新 Playground 的 Typedown 内核时，**无需修改任何代码**。

只需执行以下操作：

1. 构建新的 wheel 包。
2. 将其重命名为 `typedown-0.0.0-py3-none-any.whl`。
3. 覆盖 `website/public/` 下的同名文件。

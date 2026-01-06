---
title: Playground 架构
---

Playground 是 Typedown 的 Web 端即时运行环境，它在浏览器中完整运行了 Typedown 编译器和 LSP 服务，无需连接远程服务器。

这是一项复杂的工程挑战，涉及 WebAssembly、Web Worker、虚拟文件系统以及 LSP 协议的深度定制。

## 1. 架构总览

Playground 采用了 **"Browser-side LSP"** 架构，将 Python 后端（Typedown Core）打包为 Wheel，通过 Pyodide 加载到 WebAssembly 环境中运行。

整体数据流如下：

```mermaid
graph TD
    User[用户操作] -->|Type/Hoever| Editor[Monaco Editor (Main Thread)]
    Editor -->|JSON-RPC| Client[LSP Client (monaco-languageclient)]
    Client -->|postMessage| Worker[Web Worker (lsp-worker.js)]

    subgraph "Web Worker Realm"
        Worker -->|Intercept Writes| VFS[Pyodide MEMFS]
        Worker -->|Forward JSON| PyGlue[Python Glue Code]

        subgraph "Pyodide WASM"
            PyGlue -->|Direct Injection| Server[Typedown LSP Server]
            Server -->|Lookups| Compiler[Typedown Compiler]
            Compiler -.->|Reads| VFS
        end
    end
```

## 2. 核心组件详解

### 2.1 前端层 (Main Thread)

主要逻辑位于 `website/src/components/playground/PlaygroundEditor.tsx`。

- **Monaco Editor**: 提供代码编辑界面。
- **Language Client**: 使用 `monaco-languageclient` 库建立与 Worker 的连接。它并不感知后端是在本地 Worker 还是远程 Socket，只是单纯地通过 `MessageReader/Writer` 收发消息。
- **状态同步**: React 组件负责管理当前选中的 Demo，并将其内容同步到 Editor Model 中。

### 2.2 桥接层 (Web Worker)

主要逻辑位于 `website/public/lsp-worker.js`。这是一个标准的 Web Worker，负责模拟 OS 环境。

**关键职责：**

1. **环境引导 (Bootstrapping)**:

   - 加载 Pyodide CRT (C Runtime)。
   - 安装 Python 依赖：`micropip`, `pygls`, `pydantic` 等。
   - **Wheel Injection**: 下载 `public/typedown-0.0.0-py3-none-any.whl` 并安装到环境中。

2. **I/O 拦截 (I/O Interception)**:

   - 监听 LSP 消息。
   - **同步策略**: 当收到 `textDocument/didOpen` 或自定义的 `typedown/syncFile` 消息时，**优先**调用 `pyodide.FS.writeFile` 将文件内容写入虚拟文件系统。
   - 这是因为 Typedown Compiler 在解析 `config.td` 继承关系时，需要物理读取磁盘文件，而不仅仅依赖内存中的 `didChange` 事件。

3. **消息转发**:
   - 将 JSON-RPC 字符串传递给 Python 定义的全局函数 `consume_message`。

### 2.3 内核层 (Python/WASM)

这是运行在 WASM 中的实际 Python 代码。我们在 `lsp-worker.js` 中通过 `PYTHON_LSP_SCRIPT` 常量注入了一段胶水代码。

**关键 Hack：**

1. **Mock Watchdog**:

   - 原生 Typedown 依赖 `watchdog` 库监听文件变化。
   - WASM 环境没有真正的文件系统事件，因此我们通过 `sys.modules` 注入了一个 Dummy Watchdog，防止 Server 启动报错。

2. **WebTransport**:

   - `pygls` 默认使用 TCP/Stdio。
   - 我们实现了一个基于 `asyncio.Transport` 的 `WebTransport` 类，它重写了 `write` 方法，通过 `js.post_lsp_message` 将数据回调给 JS Worker。

3. **Direct Injection**:
   - 我们绕过了 TCP socket，直接将解析后的 JSON 对象注入到 `server.protocol.handle_message`，减少了序列化开销。

## 3. 虚拟文件系统 (Virtual File System)

Typedown 的设计假设是基于文件系统的。为了在浏览器中复用核心逻辑，我们利用了 Emscripten 的 MEMFS。

### 文件结构

Pyodide 启动后，根目录 `/` 即为虚拟文件系统的根。

- `config.td`: 位于项目根目录，通常被映射到 `/config.td` 或 `/examples/config.td`。
- `user-files`: 用户的 `.td` 文件被写入相应的虚拟路径。

### 重置机制

当用户切换 Demo 时，我们需要清除上一个 Demo 的残留文件。Client 会发送 `typedown/resetFileSystem` 消息。Worker 收到后，会调用 Python 的 `shutil.rmtree` 清空 `/` 下除了系统目录（如 `/lib`, `/tmp`）以外的所有文件。

## 4. 常见问题与调试

### Q: 为什么 `import` 报错？

A: 检查 `lsp-worker.js` 中的依赖安装列表。Pyodide 的包环境与 PyPI 不完全一致，必须显式指定版本（如 `pygls>=2.0.0`）。

### Q: 为什么找不到文件？

A: 检查 `didOpen` 消息是否正确触发了 FS 写入。可以在 Worker 控制台查看 `[LSP Worker] didOpen Sync to FS:` 日志。

### Q: 如何更新内核？

A:

1. 在本地运行 `uv build` 生成 wheel。
2. 将生成的 wheel 重命名为 `typedown-0.0.0-py3-none-any.whl`.
3. 覆盖 `website/public/` 下的同名文件。
4. 强制刷新浏览器（清除缓存）。
